import os
import pickle
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


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
        # Raw global source is already USD; keep it as the preferred fallback.
        price_col = 'crude_oil_price'
    elif 'crude_oil_price_gbp' in source1.columns:
        source1 = source1.copy()
        source1['crude_oil_price_usd'] = pd.to_numeric(source1['crude_oil_price_gbp'], errors='coerce') * GBP_TO_USD_FALLBACK
        price_col = 'crude_oil_price_usd'
    else:
        raise KeyError('No crude oil price column found in audited source1 data.')

    ts_data = source1.set_index('date')[price_col].dropna().sort_index()
    return ts_data


def train_arima_model(ts_data, order=(1, 1, 1)):
    model = ARIMA(ts_data, order=order)
    model_fit = model.fit()
    return model_fit


def forecast_arima(model_fit, steps=48):
    return model_fit.forecast(steps=steps)


def save_model(model_fit, path):
    with open(path, 'wb') as fp:
        pickle.dump(model_fit, fp)


def load_model(path):
    with open(path, 'rb') as fp:
        return pickle.load(fp)
