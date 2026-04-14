#!/usr/bin/env python3
"""
Data Cleaning Pipeline for 10000 Sales Records
Adapted for healthcare sales prediction project
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 1. DATA LOADING & INSPECTION
# ==========================================

def load_and_inspect_sales_data(file_path):
    """Load sales data and perform initial inspection"""
    
    # Load data with proper date parsing
    df = pd.read_csv(file_path)
    
    # Convert date columns to datetime
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%m/%d/%Y')
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {', '.join(df.columns)}")
    
    # Initial inspection
    print("\n=== Data Types ===")
    print(df.dtypes)
    
    print("\n=== Missing Values Summary ===")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("No missing values found")
    
    print("\n=== Basic Statistics ===")
    print(df[['Units Sold', 'Unit Price', 'Unit Cost', 'Total Revenue', 'Total Cost', 'Total Profit']].describe())
    
    return df

# ==========================================
# 2. DATA QUALITY ASSESSMENT
# ==========================================

class DataQualityChecker:
    """Comprehensive data quality assessment for sales data"""
    
    def __init__(self, df):
        self.df = df
        self.quality_report = {}
    
    def check_duplicates(self):
        """Identify duplicate records"""
        # Check for duplicate Order IDs
        duplicate_orders = self.df['Order ID'].duplicated().sum()
        
        # Check for completely duplicate rows
        duplicate_rows = self.df.duplicated().sum()
        
        self.quality_report['duplicates'] = {
            'duplicate_order_ids': duplicate_orders,
            'duplicate_rows': duplicate_rows,
            'duplicate_percentage': (duplicate_rows / len(self.df)) * 100
        }
        
        print(f"Found {duplicate_orders} duplicate Order IDs")
        print(f"Found {duplicate_rows} completely duplicate rows")
        return self
    
    def check_missing_values(self):
        """Analyze missing value patterns"""
        missing_counts = self.df.isnull().sum()
        missing_percentages = (missing_counts / len(self.df)) * 100
        
        missing_summary = pd.DataFrame({
            'column': missing_counts.index,
            'missing_count': missing_counts.values,
            'missing_percentage': missing_percentages.values
        })
        
        self.quality_report['missing_values'] = missing_summary[missing_summary['missing_count'] > 0]
        
        if len(self.quality_report['missing_values']) > 0:
            print("\nColumns with missing values:")
            print(self.quality_report['missing_values'])
        else:
            print("No missing values detected")
        return self
    
    def check_outliers(self, numerical_cols=None):
        """Detect outliers using IQR method"""
        if numerical_cols is None:
            numerical_cols = ['Units Sold', 'Unit Price', 'Unit Cost', 
                            'Total Revenue', 'Total Cost', 'Total Profit']
        
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
        
        print("\nOutlier Analysis:")
        for col, stats in outliers.items():
            if stats['count'] > 0:
                print(f"  {col}: {stats['count']} outliers ({stats['percentage']:.2f}%)")
        return self
    
    def check_data_consistency(self):
        """Check for data consistency issues"""
        issues = []
        
        # Check if Total Revenue = Units Sold * Unit Price
        revenue_check = np.abs(self.df['Total Revenue'] - 
                              (self.df['Units Sold'] * self.df['Unit Price'])) > 0.01
        if revenue_check.any():
            issues.append(f"Revenue calculation mismatch: {revenue_check.sum()} rows")
        
        # Check if Total Cost = Units Sold * Unit Cost
        cost_check = np.abs(self.df['Total Cost'] - 
                           (self.df['Units Sold'] * self.df['Unit Cost'])) > 0.01
        if cost_check.any():
            issues.append(f"Cost calculation mismatch: {cost_check.sum()} rows")
        
        # Check if Total Profit = Total Revenue - Total Cost
        profit_check = np.abs(self.df['Total Profit'] - 
                             (self.df['Total Revenue'] - self.df['Total Cost'])) > 0.01
        if profit_check.any():
            issues.append(f"Profit calculation mismatch: {profit_check.sum()} rows")
        
        # Check if Ship Date >= Order Date
        date_check = self.df['Ship Date'] < self.df['Order Date']
        if date_check.any():
            issues.append(f"Ship date before order date: {date_check.sum()} rows")
        
        self.quality_report['consistency_issues'] = issues
        
        if issues:
            print("\nData Consistency Issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("No data consistency issues found")
        return self
    
    def generate_report(self):
        """Generate comprehensive quality report"""
        return self.quality_report

# ==========================================
# 3. DATA CLEANING FUNCTIONS
# ==========================================

def handle_duplicates(df):
    """Remove duplicate records"""
    print(f"Records before removing duplicates: {len(df)}")
    
    # Remove duplicate Order IDs, keeping the first occurrence
    df = df.drop_duplicates(subset=['Order ID'], keep='first')
    
    print(f"Records after removing duplicates: {len(df)}")
    return df

def fix_calculation_errors(df):
    """Fix any calculation errors in financial columns"""
    # Recalculate Total Revenue
    df['Total Revenue'] = df['Units Sold'] * df['Unit Price']
    
    # Recalculate Total Cost
    df['Total Cost'] = df['Units Sold'] * df['Unit Cost']
    
    # Recalculate Total Profit
    df['Total Profit'] = df['Total Revenue'] - df['Total Cost']
    
    print("Financial calculations verified and corrected")
    return df

def handle_outliers(df, method='cap'):
    """Handle outliers in numerical columns"""
    numerical_cols = ['Units Sold', 'Unit Price', 'Unit Cost', 
                     'Total Revenue', 'Total Cost', 'Total Profit']
    
    for col in numerical_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        if method == 'cap':
            # Cap outliers at boundaries
            original_outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            if original_outliers > 0:
                df[col] = df[col].clip(lower=max(0, lower_bound), upper=upper_bound)
                print(f"Capped {original_outliers} outliers in {col}")
    
    return df

# ==========================================
# 4. FEATURE ENGINEERING
# ==========================================

def engineer_temporal_features(df):
    """Create time-based features for sales prediction"""
    
    # Basic temporal features
    df['Year'] = df['Order Date'].dt.year
    df['Quarter'] = df['Order Date'].dt.quarter
    df['Month'] = df['Order Date'].dt.month
    df['Week'] = df['Order Date'].dt.isocalendar().week
    df['Day_of_Week'] = df['Order Date'].dt.dayofweek
    df['Day_of_Month'] = df['Order Date'].dt.day
    df['Is_Weekend'] = df['Day_of_Week'].isin([5, 6]).astype(int)
    df['Is_Month_Start'] = df['Order Date'].dt.is_month_start.astype(int)
    df['Is_Month_End'] = df['Order Date'].dt.is_month_end.astype(int)
    df['Is_Quarter_Start'] = df['Order Date'].dt.is_quarter_start.astype(int)
    df['Is_Quarter_End'] = df['Order Date'].dt.is_quarter_end.astype(int)
    
    # Shipping time features
    df['Shipping_Days'] = (df['Ship Date'] - df['Order Date']).dt.days
    
    # Season feature
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'
    
    df['Season'] = df['Month'].apply(get_season)
    
    print(f"Added {13} temporal features")
    return df

def engineer_product_features(df):
    """Create product-based features"""
    
    # Profit margin
    df['Profit_Margin'] = (df['Total Profit'] / df['Total Revenue']) * 100
    df['Profit_Margin'] = df['Profit_Margin'].fillna(0)
    
    # Unit profit
    df['Unit_Profit'] = df['Unit Price'] - df['Unit Cost']
    
    # Price to cost ratio
    df['Price_Cost_Ratio'] = df['Unit Price'] / df['Unit Cost']
    
    # Order value categories
    revenue_quartiles = df['Total Revenue'].quantile([0.25, 0.5, 0.75])
    df['Order_Size'] = pd.cut(df['Total Revenue'], 
                              bins=[0, revenue_quartiles[0.25], revenue_quartiles[0.5], 
                                   revenue_quartiles[0.75], float('inf')],
                              labels=['Small', 'Medium', 'Large', 'Very Large'])
    
    print(f"Added {4} product features")
    return df

def engineer_geographic_features(df):
    """Create geographic and market features"""
    
    # Region-Country combination
    df['Region_Country'] = df['Region'] + '_' + df['Country']
    
    # Market segment (combination of Region and Sales Channel)
    df['Market_Segment'] = df['Region'] + '_' + df['Sales Channel']
    
    # Priority level encoding
    priority_map = {'L': 1, 'M': 2, 'H': 3, 'C': 4}
    df['Priority_Level'] = df['Order Priority'].map(priority_map)
    
    print(f"Added {3} geographic features")
    return df

def create_aggregated_features(df):
    """Create aggregated features based on historical patterns"""
    
    # Sort by date for proper aggregation
    df = df.sort_values('Order Date')
    
    # Country-level averages
    country_stats = df.groupby('Country').agg({
        'Total Revenue': ['mean', 'std'],
        'Units Sold': ['mean', 'std'],
        'Profit_Margin': 'mean'
    }).reset_index()
    country_stats.columns = ['Country', 'Country_Avg_Revenue', 'Country_Std_Revenue',
                             'Country_Avg_Units', 'Country_Std_Units', 'Country_Avg_Margin']
    df = df.merge(country_stats, on='Country', how='left')
    
    # Item type performance
    item_stats = df.groupby('Item Type').agg({
        'Total Revenue': 'mean',
        'Units Sold': 'mean',
        'Profit_Margin': 'mean'
    }).reset_index()
    item_stats.columns = ['Item Type', 'Item_Avg_Revenue', 'Item_Avg_Units', 'Item_Avg_Margin']
    df = df.merge(item_stats, on='Item Type', how='left')
    
    # Sales channel performance
    channel_stats = df.groupby('Sales Channel').agg({
        'Total Revenue': 'mean',
        'Shipping_Days': 'mean'
    }).reset_index()
    channel_stats.columns = ['Sales Channel', 'Channel_Avg_Revenue', 'Channel_Avg_Shipping']
    df = df.merge(channel_stats, on='Sales Channel', how='left')
    
    print(f"Added {11} aggregated features")
    return df

# ==========================================
# 5. DATA VALIDATION
# ==========================================

def validate_cleaned_data(df):
    """Final validation checks after cleaning"""
    validation_results = {
        'no_nulls_in_critical': df[['Order ID', 'Order Date', 'Total Revenue']].isnull().sum().sum() == 0,
        'no_duplicate_orders': df['Order ID'].duplicated().sum() == 0,
        'positive_revenues': (df['Total Revenue'] >= 0).all(),
        'valid_dates': df['Order Date'].notna().all(),
        'valid_shipping': (df['Shipping_Days'] >= 0).all() if 'Shipping_Days' in df.columns else True,
        'consistent_calculations': np.allclose(df['Total Profit'], 
                                              df['Total Revenue'] - df['Total Cost'], 
                                              rtol=0.01)
    }
    
    print("\n=== Data Validation Results ===")
    for check, passed in validation_results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{check}: {status}")
    
    return all(validation_results.values())

# ==========================================
# 6. MAIN CLEANING PIPELINE
# ==========================================

def main_cleaning_pipeline(input_file='10000 Sales Records.csv'):
    """Execute complete data cleaning pipeline"""
    
    print("=" * 60)
    print("STARTING DATA CLEANING PIPELINE")
    print("=" * 60)
    
    # Step 1: Load data
    print("\n[Step 1] Loading data...")
    df = load_and_inspect_sales_data(input_file)
    
    # Step 2: Quality assessment
    print("\n[Step 2] Assessing data quality...")
    quality_checker = DataQualityChecker(df)
    quality_report = (quality_checker
                     .check_duplicates()
                     .check_missing_values()
                     .check_outliers()
                     .check_data_consistency()
                     .generate_report())
    
    # Step 3: Remove duplicates
    print("\n[Step 3] Handling duplicates...")
    df = handle_duplicates(df)
    
    # Step 4: Fix calculation errors
    print("\n[Step 4] Fixing calculation errors...")
    df = fix_calculation_errors(df)
    
    # Step 5: Handle outliers
    print("\n[Step 5] Handling outliers...")
    df = handle_outliers(df, method='cap')
    
    # Step 6: Feature engineering - Temporal
    print("\n[Step 6] Engineering temporal features...")
    df = engineer_temporal_features(df)
    
    # Step 7: Feature engineering - Product
    print("\n[Step 7] Engineering product features...")
    df = engineer_product_features(df)
    
    # Step 8: Feature engineering - Geographic
    print("\n[Step 8] Engineering geographic features...")
    df = engineer_geographic_features(df)
    
    # Step 9: Create aggregated features
    print("\n[Step 9] Creating aggregated features...")
    df = create_aggregated_features(df)
    
    # Step 10: Final validation
    print("\n[Step 10] Validating cleaned data...")
    is_valid = validate_cleaned_data(df)
    
    # Step 11: Save cleaned data
    print("\n[Step 11] Saving cleaned dataset...")
    df.to_csv('cleaned_sales_data.csv', index=False)
    print(f"Saved to: cleaned_sales_data.csv")
    
    # Also save as parquet for better performance
    df.to_parquet('cleaned_sales_data.parquet', index=False)
    print(f"Saved to: cleaned_sales_data.parquet")
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE!")
    print("=" * 60)
    print(f"✓ Final shape: {df.shape}")
    print(f"✓ Features created: {len(df.columns)} columns")
    print(f"✓ Date range: {df['Order Date'].min()} to {df['Order Date'].max()}")
    
    return df

# ==========================================
# 7. EXECUTION
# ==========================================

if __name__ == "__main__":
    # Run the pipeline
    cleaned_df = main_cleaning_pipeline('10000 Sales Records.csv')
    
    # Display sample of cleaned data
    print("\n=== Sample of Cleaned Data ===")
    print(cleaned_df.head())
    
    # Display new features
    print("\n=== New Features Created ===")
    original_cols = ['Region', 'Country', 'Item Type', 'Sales Channel', 'Order Priority',
                    'Order Date', 'Order ID', 'Ship Date', 'Units Sold', 'Unit Price',
                    'Unit Cost', 'Total Revenue', 'Total Cost', 'Total Profit']
    new_features = [col for col in cleaned_df.columns if col not in original_cols]
    print(f"Added {len(new_features)} new features:")
    for i in range(0, len(new_features), 4):
        print("  " + ", ".join(new_features[i:i+4]))
    
    # Display feature correlations with Total Revenue
    print("\n=== Top Features Correlated with Total Revenue ===")
    numerical_features = cleaned_df.select_dtypes(include=[np.number]).columns
    correlations = cleaned_df[numerical_features].corr()['Total Revenue'].sort_values(ascending=False)
    print(correlations.head(15))
    
    # Summary statistics of key metrics
    print("\n=== Summary Statistics After Cleaning ===")
    key_metrics = ['Total Revenue', 'Total Profit', 'Profit_Margin', 'Units Sold']
    print(cleaned_df[key_metrics].describe())