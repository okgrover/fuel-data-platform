# Fuel Data Platform API

FastAPI-based REST API for fuel price analysis and forecasting.

## Features

- **Historical Data**: Access cleaned fuel price datasets
- **Forecasting**: Generate predictions using trained ML models
- **Model Management**: List available forecasting models

## Available Models

- **ARIMA**: AutoRegressive Integrated Moving Average
- **SARIMA**: Seasonal ARIMA (best performing)
- **GradientBoosting**: Machine learning with lagged features

## API Endpoints

### GET /
Basic API information

### GET /data/historical
Get recent historical crude oil prices
- Query parameter: `limit` (default: 100)

### POST /forecast
Generate price forecasts
```json
{
  "model": "sarima",
  "steps": 12
}
```

### GET /models
List available forecasting models

## Running the API

```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn api.main:app --reload

# Or use the provided script
python run_api.py
```

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive API documentation with Swagger UI.

## Power BI Integration

Use the exported CSV files in `data/powerbi/` for Power BI dashboards:

1. Connect to CSV files in Power BI Desktop
2. Use `fuel_prices_master.csv` as the main dataset
3. Create relationships between summary and trend data
4. Build interactive dashboards with filters for region, fuel type, and time periods

## Model Performance

- SARIMA: RMSE 16.92 (best)
- ARIMA: RMSE 20.23
- GradientBoosting: RMSE 27.54

## Next Steps

- Add authentication and rate limiting
- Implement model retraining endpoints
- Add external data sources (weather, economic indicators)
- Deploy to cloud platform (AWS, Azure, GCP)