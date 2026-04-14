# Data Cleaning Pipeline for Healthcare Sales Prediction
# Author: BI Engineering Team
# Project: ML Sales Forecasting for Sustainable Medical Devices

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer, KNNImputer
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 1. INITIAL DATA LOADING & INSPECTION
# ==========================================

def load_and_inspect_data(file_paths):
    """
    Load multiple data sources and perform initial inspection
    """
    datasets = {}
    
    # Load main sales data
    sales_df = pd.read_csv(file_paths['sales'], parse_dates=['sale_date'])
    print(f"Sales data shape: {sales_df.shape}")
    
    # Load hospital/clinic master data
    customers_df = pd.read_csv(file_paths['customers'])
    print(f"Customer data shape: {customers_df.shape}")
    
    # Load product catalog
    products_df = pd.read_csv(file_paths['products'])
    print(f"Product data shape: {products_df.shape}")
    
    # Initial inspection
    print("\n=== Data Types ===")
    print(sales_df.dtypes)
    
    print("\n=== Missing Values Summary ===")
    print(sales_df.isnull().sum())
    
    print("\n=== Basic Statistics ===")
    print(sales_df.describe())
    
    return sales_df, customers_df, products_df

# ==========================================
# 2. DATA QUALITY CHECKS
# ==========================================

class DataQualityChecker:
    """
    Comprehensive data quality assessment
    """
    
    def __init__(self, df):
        self.df = df
        self.quality_report = {}
    
    def check_duplicates(self):
        """Identify duplicate records"""
        duplicates = self.df.duplicated().sum()
        duplicate_rows = self.df[self.df.duplicated(keep=False)]
        
        self.quality_report['duplicates'] = {
            'count': duplicates,
            'percentage': (duplicates / len(self.df)) * 100,
            'duplicate_ids': duplicate_rows.index.tolist()
        }
        return self
    
    def check_missing_values(self):
        """Analyze missing value patterns"""
        missing_summary = pd.DataFrame({
            'column': self.df.columns,
            'missing_count': self.df.isnull().sum().values,
            'missing_percentage': (self.df.isnull().sum().values / len(self.df)) * 100
        })
        
        self.quality_report['missing_values'] = missing_summary[missing_summary['missing_count'] > 0]
        return self
    
    def check_outliers(self, numerical_cols):
        """Detect outliers using IQR method"""
        outliers = {}
        
        for col in numerical_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            outliers[col] = {
                'count': outlier_mask.sum(),
                'percentage': (outlier_mask.sum() / len(self.df)) * 100,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            }
        
        self.quality_report['outliers'] = outliers
        return self
    
    def generate_report(self):
        """Generate comprehensive quality report"""
        return self.quality_report

# ==========================================
# 3. DATA CLEANING FUNCTIONS
# ==========================================

def clean_hospital_names(df, column='hospital_name'):
    """
    Standardize hospital and clinic names
    """
    # Convert to uppercase for consistency
    df[column] = df[column].str.upper()
    
    # Remove extra whitespace
    df[column] = df[column].str.strip()
    df[column] = df[column].str.replace(r'\s+', ' ', regex=True)
    
    # Standardize common abbreviations
    replacements = {
        'HOSP.': 'HOSPITAL',
        'HOSP': 'HOSPITAL',
        'MED CTR': 'MEDICAL CENTER',
        'MED. CTR': 'MEDICAL CENTER',
        'HLTH': 'HEALTH',
        'CNTR': 'CENTER',
        'CLN': 'CLINIC',
        'ST.': 'SAINT',
        'MT.': 'MOUNT'
    }
    
    for old, new in replacements.items():
        df[column] = df[column].str.replace(old, new, regex=False)
    
    return df

def clean_product_codes(df, column='product_code'):
    """
    Standardize product codes and extract components
    """
    # Remove special characters except hyphens and underscores
    df[column] = df[column].str.replace(r'[^A-Za-z0-9\-_]', '', regex=True)
    
    # Extract product category (first 3 chars)
    df['product_category'] = df[column].str[:3]
    
    # Extract product line (chars 4-6)
    df['product_line'] = df[column].str[3:6]
    
    # Extract version/variant (remaining)
    df['product_variant'] = df[column].str[6:]
    
    return df

def handle_missing_values(df, strategy_dict):
    """
    Handle missing values with different strategies per column
    
    strategy_dict example:
    {
        'numerical_forward_fill': ['sales_amount', 'quantity'],
        'numerical_mean': ['unit_price'],
        'numerical_median': ['discount_percentage'],
        'categorical_mode': ['payment_method', 'delivery_type'],
        'categorical_unknown': ['notes', 'special_instructions'],
        'drop': ['internal_id']
    }
    """
    df_clean = df.copy()
    
    # Numerical strategies
    if 'numerical_forward_fill' in strategy_dict:
        for col in strategy_dict['numerical_forward_fill']:
            df_clean[col] = df_clean[col].fillna(method='ffill')
    
    if 'numerical_mean' in strategy_dict:
        for col in strategy_dict['numerical_mean']:
            df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
    
    if 'numerical_median' in strategy_dict:
        for col in strategy_dict['numerical_median']:
            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
    
    if 'numerical_knn' in strategy_dict:
        # KNN imputation for correlated numerical features
        imputer = KNNImputer(n_neighbors=5)
        cols = strategy_dict['numerical_knn']
        df_clean[cols] = imputer.fit_transform(df_clean[cols])
    
    # Categorical strategies
    if 'categorical_mode' in strategy_dict:
        for col in strategy_dict['categorical_mode']:
            df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0])
    
    if 'categorical_unknown' in strategy_dict:
        for col in strategy_dict['categorical_unknown']:
            df_clean[col] = df_clean[col].fillna('UNKNOWN')
    
    # Drop columns with too many missing values
    if 'drop' in strategy_dict:
        df_clean = df_clean.drop(columns=strategy_dict['drop'])
    
    return df_clean

def handle_outliers(df, numerical_cols, method='cap'):
    """
    Handle outliers using capping or removal
    """
    df_clean = df.copy()
    
    for col in numerical_cols:
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        if method == 'cap':
            # Cap outliers at boundaries
            df_clean[col] = df_clean[col].clip(lower=lower_bound, upper=upper_bound)
        elif method == 'remove':
            # Remove outlier rows
            df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
        elif method == 'transform':
            # Log transformation for skewed data
            if df_clean[col].min() > 0:
                df_clean[f'{col}_log'] = np.log1p(df_clean[col])
    
    return df_clean

# ==========================================
# 4. FEATURE ENGINEERING FOR SALES DATA
# ==========================================

def engineer_temporal_features(df, date_column='sale_date'):
    """
    Create time-based features for sales prediction
    """
    df['year'] = df[date_column].dt.year
    df['quarter'] = df[date_column].dt.quarter
    df['month'] = df[date_column].dt.month
    df['week'] = df[date_column].dt.isocalendar().week
    df['day_of_week'] = df[date_column].dt.dayofweek
    df['day_of_month'] = df[date_column].dt.day
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_month_start'] = df[date_column].dt.is_month_start.astype(int)
    df['is_month_end'] = df[date_column].dt.is_month_end.astype(int)
    df['is_quarter_start'] = df[date_column].dt.is_quarter_start.astype(int)
    df['is_quarter_end'] = df[date_column].dt.is_quarter_end.astype(int)
    
    # Days since last order per customer
    df = df.sort_values(['customer_id', date_column])
    df['days_since_last_order'] = df.groupby('customer_id')[date_column].diff().dt.days
    
    return df

def engineer_customer_features(df):
    """
    Create customer-based features
    """
    # Customer lifetime value components
    customer_stats = df.groupby('customer_id').agg({
        'sales_amount': ['sum', 'mean', 'std', 'count'],
        'quantity': ['sum', 'mean'],
        'sale_date': ['min', 'max']
    }).reset_index()
    
    customer_stats.columns = ['_'.join(col).strip() for col in customer_stats.columns.values]
    customer_stats.rename(columns={'customer_id_': 'customer_id'}, inplace=True)
    
    # Calculate customer tenure
    customer_stats['customer_tenure_days'] = (
        customer_stats['sale_date_max'] - customer_stats['sale_date_min']
    ).dt.days
    
    # Merge back to main dataframe
    df = df.merge(customer_stats, on='customer_id', how='left')
    
    return df

def create_lag_features(df, target_col='sales_amount', lags=[7, 14, 30]):
    """
    Create lagged features for time series
    """
    df = df.sort_values('sale_date')
    
    for lag in lags:
        df[f'{target_col}_lag_{lag}'] = df.groupby('customer_id')[target_col].shift(lag)
        
        # Rolling statistics
        df[f'{target_col}_rolling_mean_{lag}'] = df.groupby('customer_id')[target_col].rolling(
            window=lag, min_periods=1
        ).mean().reset_index(0, drop=True)
        
        df[f'{target_col}_rolling_std_{lag}'] = df.groupby('customer_id')[target_col].rolling(
            window=lag, min_periods=1
        ).std().reset_index(0, drop=True)
    
    return df

# ==========================================
# 5. DATA VALIDATION
# ==========================================

def validate_cleaned_data(df):
    """
    Final validation checks after cleaning
    """
    validation_results = {
        'no_nulls': df.isnull().sum().sum() == 0,
        'no_duplicates': df.duplicated().sum() == 0,
        'positive_sales': (df['sales_amount'] >= 0).all(),
        'valid_dates': df['sale_date'].notna().all(),
        'customer_ids_present': df['customer_id'].notna().all()
    }
    
    print("=== Data Validation Results ===")
    for check, passed in validation_results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{check}: {status}")
    
    return all(validation_results.values())

# ==========================================
# 6. MAIN CLEANING PIPELINE
# ==========================================

def main_cleaning_pipeline(file_paths):
    """
    Execute complete data cleaning pipeline
    """
    print("Starting Data Cleaning Pipeline...")
    print("=" * 50)
    
    # Step 1: Load data
    print("\n[Step 1] Loading data...")
    sales_df, customers_df, products_df = load_and_inspect_data(file_paths)
    
    # Step 2: Quality assessment
    print("\n[Step 2] Assessing data quality...")
    quality_checker = DataQualityChecker(sales_df)
    quality_report = (quality_checker
                     .check_duplicates()
                     .check_missing_values()
                     .check_outliers(['sales_amount', 'quantity', 'unit_price'])
                     .generate_report())
    
    # Step 3: Remove duplicates
    print("\n[Step 3] Removing duplicates...")
    sales_df = sales_df.drop_duplicates()
    
    # Step 4: Clean text fields
    print("\n[Step 4] Cleaning text fields...")
    sales_df = clean_hospital_names(sales_df, 'customer_name')
    sales_df = clean_product_codes(sales_df, 'product_code')
    
    # Step 5: Handle missing values
    print("\n[Step 5] Handling missing values...")
    missing_strategy = {
        'numerical_median': ['unit_price', 'discount_percentage'],
        'numerical_forward_fill': ['quantity'],
        'categorical_mode': ['payment_method', 'sales_region'],
        'categorical_unknown': ['notes']
    }
    sales_df = handle_missing_values(sales_df, missing_strategy)
    
    # Step 6: Handle outliers
    print("\n[Step 6] Handling outliers...")
    numerical_cols = ['sales_amount', 'quantity', 'unit_price']
    sales_df = handle_outliers(sales_df, numerical_cols, method='cap')
    
    # Step 7: Feature engineering
    print("\n[Step 7] Engineering features...")
    sales_df = engineer_temporal_features(sales_df)
    sales_df = engineer_customer_features(sales_df)
    sales_df = create_lag_features(sales_df)
    
    # Step 8: Merge with dimension tables
    print("\n[Step 8] Merging with dimension tables...")
    sales_df = sales_df.merge(customers_df, on='customer_id', how='left')
    sales_df = sales_df.merge(products_df, on='product_code', how='left')
    
    # Step 9: Final validation
    print("\n[Step 9] Validating cleaned data...")
    is_valid = validate_cleaned_data(sales_df)
    
    # Step 10: Save cleaned data
    print("\n[Step 10] Saving cleaned dataset...")
    sales_df.to_csv('cleaned_sales_data.csv', index=False)
    sales_df.to_parquet('cleaned_sales_data.parquet', index=False)
    
    print(f"\n✓ Pipeline complete! Final shape: {sales_df.shape}")
    print(f"✓ Features created: {len(sales_df.columns)} columns")
    
    return sales_df

# ==========================================
# 7. USAGE EXAMPLE
# ==========================================

if __name__ == "__main__":
    # Define file paths
    file_paths = {
        'sales': 'raw_sales_data.csv',
        'customers': 'hospital_master.csv',
        'products': 'product_catalog.csv'
    }
    
    # Run the pipeline
    cleaned_df = main_cleaning_pipeline(file_paths)
    
    # Display sample of cleaned data
    print("\n=== Sample of Cleaned Data ===")
    print(cleaned_df.head())
    
    # Display feature importance (basic correlation with target)
    if 'sales_amount' in cleaned_df.columns:
        numerical_features = cleaned_df.select_dtypes(include=[np.number]).columns
        correlations = cleaned_df[numerical_features].corr()['sales_amount'].sort_values(ascending=False)
        print("\n=== Top Features Correlated with Sales ===")
        print(correlations.head(10))