# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a healthcare sales prediction ML project for sustainable medical devices. The project follows a structured workflow from data cleaning through model development to executive reporting.

## Commands

### Data Processing
```bash
# Run data cleaning pipeline
python data-cleaning-guide.py

# Generate visualizations  
python sales-visualization-guide.py
```

### Python Environment
```bash
# Install common data science packages (if needed)
pip install pandas numpy scikit-learn matplotlib seaborn plotly
```

## Architecture & Structure

### Data Pipeline Flow
1. **Raw Data**: `10000 Sales Records.csv` - Sales transaction data
2. **Cleaning**: `data-cleaning-guide.py` - Handles duplicates, missing values, outliers, feature engineering
3. **Visualization**: `sales-visualization-guide.py` - Time series, geographic, product, and correlation analysis
4. **ML Preparation**: Features engineered for predictive modeling (lag features, temporal patterns)

### Key Components

#### Data Processing Architecture
- **DataQualityChecker** class: Automated quality assessment with reporting
- **Cleaning functions**: Modular functions for specific cleaning tasks (hospital names, product codes, missing values)
- **Feature engineering**: Temporal features, customer features, lag features for time series

#### Visualization Framework
- Uses both matplotlib/seaborn for static plots and plotly for interactive dashboards
- Organized by analysis type: time series, product performance, geographic, correlations
- Executive dashboard with KPIs and high-level metrics

## Data Schema

Expected columns in sales data:
- `Order Date`: Transaction date
- `Total Revenue`, `Total Profit`, `Total Cost`: Financial metrics
- `Units Sold`, `Unit Price`, `Unit Cost`: Product metrics
- `Item Type`, `Product Code`: Product identifiers
- `Sales Channel`, `Order Priority`: Transaction attributes
- `Region`, `Country`: Geographic data
- `Customer ID`, `Customer Name`: Customer identifiers

## Development Workflow

1. **Data Quality Assessment**: Use DataQualityChecker for initial data profiling
2. **Cleaning Pipeline**: Apply standardized cleaning steps (duplicates → text → missing → outliers)
3. **Feature Engineering**: Create ML-ready features (temporal, customer, lag features)
4. **Visualization**: Generate insights through multi-perspective analysis
5. **Model Development**: Build predictive models using cleaned, engineered features

## Key Technical Patterns

- **Pandas operations**: Heavy use of groupby, rolling windows, datetime manipulation
- **Missing value strategies**: Different approaches per data type (mean/median for numerical, mode/unknown for categorical)
- **Outlier handling**: IQR-based detection with capping/removal options
- **Time series features**: Lag features, rolling statistics, seasonal indicators
- **Visualization layers**: From raw data exploration to executive dashboards

## Project Context

This is a consulting engagement where you're acting as a Business Intelligence Engineer leading a team including:
- Chief Data Officer
- Data Engineer  
- Data Scientist
- Analytics Manager

The goal is to build a sales prediction model with >85% accuracy to optimize inventory management and reduce costs for urban hospitals/clinics purchasing sustainable medical devices.