import os
import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


GBP_TO_USD_FALLBACK = 1.25


def load_audited_data(audited_dir):
    source1 = pd.read_csv(os.path.join(audited_dir, 'source1_audited.csv'))
    source2 = pd.read_csv(os.path.join(audited_dir, 'source2_audited.csv'))
    source3 = pd.read_csv(os.path.join(audited_dir, 'source3_audited.csv'))
    source1['date'] = pd.to_datetime(source1['date'], errors='coerce')
    return source1, source2, source3


def prepare_crude_oil_ts(source1):
    if 'crude_oil_price_usd' in source1.columns:
        price_col = 'crude_oil_price_usd'
    elif 'crude_oil_price' in source1.columns:
        price_col = 'crude_oil_price'
    elif 'crude_oil_price_gbp' in source1.columns:
        source1 = source1.copy()
        source1['crude_oil_price_usd'] = pd.to_numeric(source1['crude_oil_price_gbp'], errors='coerce') * GBP_TO_USD_FALLBACK
        price_col = 'crude_oil_price_usd'
    else:
        raise KeyError('No crude oil price column found in audited source1 data.')

    ts_data = source1.set_index('date')[price_col].dropna().sort_index()
    return ts_data


def create_features(ts_data, lags=12):
    df = pd.DataFrame(ts_data)
    df.columns = ['y']
    for lag in range(1, lags + 1):
        df[f'lag_{lag}'] = df['y'].shift(lag)
    df = df.dropna()
    return df


def train_xgboost_model(ts_data, lags=12, test_size=0.2):
    df = create_features(ts_data, lags)
    X = df.drop('y', axis=1)
    y = df['y']
    if test_size > 0:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        print(f'GradientBoosting RMSE on test set: {rmse:.2f}')
    else:
        model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)
        rmse = None
        print('GradientBoosting trained on full data (no test RMSE calculated)')
    return model, rmse


def forecast_xgboost(model, ts_data, steps=48, lags=12):
    df = create_features(ts_data, lags)
    last_features = df.iloc[-1].drop('y').values.reshape(1, -1)
    forecasts = []
    for _ in range(steps):
        pred = model.predict(last_features)[0]
        forecasts.append(pred)
        # Update features by shifting and adding new prediction
        last_features = np.roll(last_features, -1)
        last_features[0, -1] = pred
    return pd.Series(forecasts, index=pd.date_range(start=ts_data.index[-1] + pd.DateOffset(months=1), periods=steps, freq='MS'))


def save_model(model, path):
    with open(path, 'wb') as fp:
        pickle.dump(model, fp)


def load_model(path):
    with open(path, 'rb') as fp:
        return pickle.load(fp)