#!/usr/bin/env python3
"""
Export data for Power BI consumption

This script creates CSV files optimized for Power BI dashboards
"""

import pandas as pd
import os
import json

GBP_TO_USD_FALLBACK = 1.25

def export_for_powerbi():
    """Export cleaned datasets and model forecasts for Power BI"""

    audited_dir = os.path.join('data', 'audited')
    powerbi_dir = os.path.join('data', 'powerbi')
    os.makedirs(powerbi_dir, exist_ok=True)

    # Load audited data
    source1 = pd.read_csv(os.path.join(audited_dir, 'source1_audited.csv'))
    source2 = pd.read_csv(os.path.join(audited_dir, 'source2_audited.csv'))
    source3 = pd.read_csv(os.path.join(audited_dir, 'source3_audited.csv'))

    # Convert dates
    source1['date'] = pd.to_datetime(source1['date'], errors='coerce')
    source2['date'] = pd.to_datetime(source2.get('month_year', source2.get('date')), errors='coerce')
    source3['date'] = pd.to_datetime(source3.get('month', source3.get('date')), errors='coerce')

    # Create master dataset for Power BI
    master_data = []

    # Global crude oil data
    global_data = source1[['date']].copy()
    if 'crude_oil_price_usd' in source1.columns:
        global_data['price_usd'] = pd.to_numeric(source1['crude_oil_price_usd'], errors='coerce')
    elif 'crude_oil_price' in source1.columns:
        global_data['price_usd'] = pd.to_numeric(source1['crude_oil_price'], errors='coerce')
    elif 'crude_oil_price_gbp' in source1.columns:
        global_data['price_usd'] = pd.to_numeric(source1['crude_oil_price_gbp'], errors='coerce') * GBP_TO_USD_FALLBACK
    else:
        global_data['price_usd'] = pd.NA

    global_data['region'] = 'Global'
    global_data['fuel_type'] = 'Crude Oil'
    global_data['price_type'] = 'Wholesale'
    master_data.append(global_data)

    # UK data from source2
    if 'date' in source2.columns and not source2['date'].isna().all():
        uk_cols = [col for col in source2.columns if 'motor' in col.lower() and 'spirit' in col.lower()]
        if uk_cols:
            uk_data = source2[['date'] + uk_cols].copy()
            uk_data = uk_data.melt(id_vars=['date'], var_name='fuel_type', value_name='price_usd')
            uk_data['region'] = 'UK'
            uk_data['price_type'] = 'Retail'
            uk_data['fuel_type'] = uk_data['fuel_type'].str.replace('_', ' ').str.title()
            if source2.get('currency', pd.Series([], dtype='object')).astype(str).str.upper().eq('GBP').any():
                uk_data['price_usd'] = pd.to_numeric(uk_data['price_usd'], errors='coerce') * GBP_TO_USD_FALLBACK
            master_data.append(uk_data)

    # European data from source3
    if 'date' in source3.columns and not source3['date'].isna().all():
        eu_cols = [col for col in source3.columns if col not in ['year', 'month', 'day_in_month_of_price_snapshot', 'currency', 'unit', 'date']]
        if eu_cols:
            eu_data = source3[['date'] + eu_cols].drop_duplicates().copy()
            eu_data = eu_data.melt(id_vars=['date'], var_name='country', value_name='price_usd')
            eu_data['region'] = 'Europe'
            eu_data['price_type'] = 'Retail'
            eu_data['fuel_type'] = 'Petrol'
            if source3.get('currency', pd.Series([], dtype='object')).astype(str).str.upper().eq('GBP').any():
                eu_data['price_usd'] = pd.to_numeric(eu_data['price_usd'], errors='coerce') * GBP_TO_USD_FALLBACK
            master_data.append(eu_data)

    # Combine all data
    combined_df = pd.concat(master_data, ignore_index=True)
    combined_df = combined_df.dropna(subset=['date', 'price_usd'])
    combined_df['year'] = combined_df['date'].dt.year
    combined_df['month'] = combined_df['date'].dt.month
    combined_df['quarter'] = combined_df['date'].dt.quarter

    # Export master dataset
    combined_df.to_csv(os.path.join(powerbi_dir, 'fuel_prices_master.csv'), index=False)

    # Create summary statistics
    summary_stats = combined_df.groupby(['region', 'fuel_type', 'price_type']).agg({
        'price_usd': ['mean', 'std', 'min', 'max', 'count']
    }).round(2)
    summary_stats.columns = ['mean_price', 'std_price', 'min_price', 'max_price', 'record_count']
    summary_stats = summary_stats.reset_index()
    summary_stats.to_csv(os.path.join(powerbi_dir, 'fuel_prices_summary.csv'), index=False)

    # Create yearly trends
    yearly_trends = combined_df.groupby(['year', 'region', 'fuel_type']).agg({
        'price_usd': 'mean'
    }).round(2).reset_index()
    yearly_trends.to_csv(os.path.join(powerbi_dir, 'yearly_trends.csv'), index=False)

    # Create metadata file
    metadata = {
        "export_date": pd.Timestamp.now().isoformat(),
        "date_range": {
            "start": combined_df['date'].min().isoformat(),
            "end": combined_df['date'].max().isoformat()
        },
        "regions": combined_df['region'].unique().tolist(),
        "fuel_types": combined_df['fuel_type'].unique().tolist(),
        "price_types": combined_df['price_type'].unique().tolist(),
        "total_records": len(combined_df)
    }

    with open(os.path.join(powerbi_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Exported data for Power BI to {powerbi_dir}")
    print(f"- Master dataset: {len(combined_df)} records")
    print(f"- Summary statistics: {len(summary_stats)} entries")
    print(f"- Yearly trends: {len(yearly_trends)} entries")

if __name__ == "__main__":
    export_for_powerbi()