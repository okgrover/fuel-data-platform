# Fuel Data Governance Platform

This project demonstrates the design of a governed data platform using global fuel price data from 1970-2026.

## Contents

- [Project Overview](#project-overview)
- [Read This In 5 Minutes](#read-this-in-5-minutes)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Notebooks and Workflow](#notebooks-and-workflow)
- [Quick Start](#quick-start)
- [Modeling Horizons](#modeling-horizons)
- [API Endpoints](#api-endpoints)
- [Power BI Integration](#power-bi-integration)
- [Data Governance and Compliance](#data-governance-and-compliance)
- [Data Sources](#data-sources)
- [Technology Stack](#technology-stack)
- [Next Steps](#next-steps)

## Project Overview

The platform ingests global and regional fuel datasets, transforms them into an audited analytical layer, and provides:

- Exploratory and comparative visual analytics
- Medium/long-horizon forecasting
- Short-term forecasting for fast-changing market conditions
- Realtime monitoring via external API pulls
- API and BI-ready outputs

Canonical analytics currency is now **USD** across modeling, API output, and Power BI export.

## Read This In 5 Minutes

If you are new to this repository, use this order:

1. Read [Notebooks and Workflow](#notebooks-and-workflow) to understand how the project is split.
2. Run `pipelines/03_transformation.ipynb` for transformation and harmonization.
3. Run `pipelines/04_governance_compliance_publish.ipynb` for governance checks and audited publishing.
4. Run `pipelines/05_visualisation.ipynb` for trend/volatility/regional analysis.
5. Run `pipelines/06_modelling.ipynb` for 5-year and 10-year forecasts.
6. Run `pipelines/07_short_term_forecasting.ipynb` for short-horizon market-sensitive forecasting.
7. Run `pipelines/08_realtime_monitoring.ipynb` for live benchmark monitoring.
8. Use `python run_api.py` and `python export_powerbi.py` for API and BI delivery.

Expected outputs after this flow:

- Audited harmonized datasets in `data/audited/`
- Forecast artifacts and model output tables/charts in notebooks
- API endpoints serving USD historical/forecast series
- Power BI-ready USD exports in `data/powerbi/`

## Key Features

- **Multi-source data ingestion**: CSV files from global, UK, and European sources
- **Data standardisation and harmonisation**: Unified date formats, currency conversion to USD, column naming
- **Data validation and quality checks**: Missing value handling, outlier detection
- **Creation of an audited system of record**: Cleaned datasets in `data/audited/`
- **Exploratory analysis**: Decadal trends, volatility analysis, regional comparisons
- **Predictive modeling**: ARIMA, SARIMA, and GradientBoosting forecasting models
- **Interactive visualizations**: Plotly charts for data exploration
- **REST API**: FastAPI endpoints for data access and forecasting
- **Power BI integration**: Exported CSV datasets for business intelligence dashboards

## Architecture

```
data/
├── raw/           # Original source files
├── processed/     # Initial cleaning and transformation
└── audited/       # Final validated datasets

models/            # Reusable ML model modules
api/               # FastAPI application
pipelines/         # Jupyter notebooks for analysis
```

## Notebooks and Workflow

- `pipelines/01_ingestion.ipynb`: source ingestion and initial loading
- `pipelines/02_exploration_eda.ipynb`: early data profiling and EDA
- `pipelines/03_transformation.ipynb`: harmonisation and transformation logic
- `pipelines/04_governance_compliance_publish.ipynb`: governance checks and audited publish step
- `pipelines/05_visualisation.ipynb`: decadal, volatility, and regional visual analysis
- `pipelines/06_modelling.ipynb`: ARIMA/SARIMA/GradientBoosting modeling (5-year and 10-year horizons)
- `pipelines/07_short_term_forecasting.ipynb`: short-window forecasting (3-6 month use case)
- `pipelines/08_realtime_monitoring.ipynb`: realtime benchmark pull and monitoring visuals

## Quick Start

1. **Setup environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run data pipeline**:
   ```bash
   jupyter notebook pipelines/01_ingestion.ipynb
   jupyter notebook pipelines/02_exploration_eda.ipynb
   jupyter notebook pipelines/03_transformation.ipynb
   jupyter notebook pipelines/04_governance_compliance_publish.ipynb
   ```

3. **Run analysis and modeling**:
   ```bash
   jupyter notebook pipelines/05_visualisation.ipynb
   jupyter notebook pipelines/06_modelling.ipynb
   jupyter notebook pipelines/07_short_term_forecasting.ipynb
   jupyter notebook pipelines/08_realtime_monitoring.ipynb
   ```

4. **Start API server**:
   ```bash
   python run_api.py
   # Visit http://localhost:8000/docs for interactive docs
   ```

5. **Export for Power BI**:
   ```bash
   python export_powerbi.py
   # Use data/powerbi/*.csv files in Power BI Desktop
   ```

## Modeling Horizons

- `06_modelling.ipynb`: medium/long-term outlooks (5-year and 10-year)
- `07_short_term_forecasting.ipynb`: short-term regime-sensitive forecasting
- `08_realtime_monitoring.ipynb`: benchmark refresh and monitoring context

## Model Performance

| Model | Test RMSE | Description |
|-------|-----------|-------------|
| SARIMA | 16.92 | Seasonal ARIMA (recommended) |
| ARIMA | 20.23 | AutoRegressive Integrated Moving Average |
| GradientBoosting | 27.54 | ML with lagged features |

Note: RMSE values are dependent on current training window and should be refreshed after reruns.

## API Endpoints

- `GET /` - API information
- `GET /data/historical` - Historical price data
- `POST /forecast` - Generate predictions
- `GET /models` - List available models

Historical series is exposed in USD-standardized form.

## Power BI Integration

Connect to the exported CSV files for interactive dashboards:
- `fuel_prices_master.csv` - Main dataset with all prices
- `fuel_prices_summary.csv` - Statistical summaries
- `yearly_trends.csv` - Annual averages by region

Power BI export is USD-standardized (`price_usd`).

## Data Governance and Compliance

This project follows lightweight governance controls suitable for analytics delivery and extension to production:

- **Canonical currency policy**: USD is the required analytics currency.
- **Lineage**: raw files remain unchanged in `data/raw`; transformations are applied in pipeline notebooks/scripts.
- **Conversion metadata**: audited outputs carry currency/unit metadata and FX assumptions.
- **Schema guardrails**: required-column and currency checks are run before publish to audited layer.
- **Notebook safety**: governance cell can detect stale in-memory notebook state and warn users to rerun full flow.

Recommended production hardening:

- Replace fixed FX assumption with time-varying governed FX source.
- Add data quality logs and versioned transformation runs.
- Add CI checks for schema drift and currency-policy violations.

## Data Sources

- **Global crude oil**: Brent/WTI benchmark prices (1970-2026)
- **UK retail**: Historic petrol prices
- **European retail**: Cross-country fuel price comparisons
- **Realtime benchmark**: FRED Brent series (`DCOILBRENTEU`) in monitoring notebook

## Technology Stack

- **Python 3.11**: Core language
- **Pandas**: Data manipulation
- **Statsmodels**: Statistical modeling
- **Scikit-learn**: Machine learning
- **Plotly**: Interactive visualizations
- **FastAPI**: REST API framework
- **Jupyter**: Interactive analysis notebooks

## Next Steps

- [ ] Deploy API to cloud (AWS/GCP/Azure)
- [ ] Add real-time data ingestion
- [ ] Implement model monitoring and retraining
- [ ] Add external data sources (weather, economic indicators)
- [ ] Create comprehensive Power BI dashboard templates
