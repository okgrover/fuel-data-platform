from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import pickle
import os
from datetime import datetime
from typing import List, Dict, Any

app = FastAPI(title="Fuel Data Platform API", description="API for fuel price analysis and forecasting")

GBP_TO_USD_FALLBACK = 1.25

# Load models
models_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'audited')
arima_model = pickle.load(open(os.path.join(models_dir, 'arima_crude_oil.pkl'), 'rb'))
sarima_model = pickle.load(open(os.path.join(models_dir, 'sarima_crude_oil.pkl'), 'rb'))
gb_model = pickle.load(open(os.path.join(models_dir, 'xgb_crude_oil.pkl'), 'rb'))

# Load data
audited_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'audited')
source1 = pd.read_csv(os.path.join(audited_dir, 'source1_audited.csv'))
source1['date'] = pd.to_datetime(source1['date'])


def _resolve_usd_series(df: pd.DataFrame) -> pd.Series:
    if 'crude_oil_price_usd' in df.columns:
        return pd.to_numeric(df['crude_oil_price_usd'], errors='coerce')
    if 'crude_oil_price' in df.columns:
        return pd.to_numeric(df['crude_oil_price'], errors='coerce')
    if 'crude_oil_price_gbp' in df.columns:
        return pd.to_numeric(df['crude_oil_price_gbp'], errors='coerce') * GBP_TO_USD_FALLBACK
    raise KeyError('No supported crude oil price column found.')

class ForecastRequest(BaseModel):
    model: str  # 'arima', 'sarima', 'gradientboosting'
    steps: int = 12

class ForecastResponse(BaseModel):
    model: str
    forecast_dates: List[str]
    forecast_values: List[float]
    metadata: Dict[str, Any]

@app.get("/")
def read_root():
    return {"message": "Fuel Data Platform API", "version": "1.0"}

@app.get("/data/historical")
def get_historical_data(limit: int = 100):
    """Get recent historical crude oil prices"""
    data = source1[['date']].copy()
    data['crude_oil_price_usd'] = _resolve_usd_series(source1)
    data = data.tail(limit)
    return data.to_dict('records')

@app.post("/forecast", response_model=ForecastResponse)
def forecast_prices(request: ForecastRequest):
    """Generate price forecasts using specified model"""
    if request.model == 'arima':
        model = arima_model
        from models.arima_crude_oil import forecast_arima
        forecast_func = forecast_arima
    elif request.model == 'sarima':
        model = sarima_model
        from models.sarima_crude_oil import forecast_sarima
        forecast_func = forecast_sarima
    elif request.model == 'gradientboosting':
        model = gb_model
        from models.xgboost_crude_oil import forecast_xgboost
        usd_series = _resolve_usd_series(source1)
        forecast_func = lambda m, s: forecast_xgboost(m, pd.Series(usd_series.values, index=source1['date']), s, 12)
    else:
        raise HTTPException(status_code=400, detail="Model not supported")

    forecast = forecast_func(model, request.steps)
    dates = pd.date_range(start=source1['date'].max() + pd.DateOffset(months=1),
                         periods=request.steps, freq='MS').strftime('%Y-%m-%d').tolist()

    return ForecastResponse(
        model=request.model,
        forecast_dates=dates,
        forecast_values=forecast.tolist(),
        metadata={"steps": request.steps, "generated_at": datetime.now().isoformat()}
    )

@app.get("/models")
def list_models():
    """List available forecasting models"""
    return {
        "models": ["arima", "sarima", "gradientboosting"],
        "descriptions": {
            "arima": "ARIMA (AutoRegressive Integrated Moving Average)",
            "sarima": "SARIMA (Seasonal ARIMA)",
            "gradientboosting": "Gradient Boosting Regressor with lagged features"
        }
    }