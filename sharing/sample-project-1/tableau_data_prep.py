#!/usr/bin/env python3
"""
Tableau Data Preparation Script
Prepares cleaned sales data for optimal use in Tableau Public
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def prepare_tableau_data():
    """
    Prepare data specifically optimized for Tableau visualization
    """
    
    print("="*60)
    print("TABLEAU DATA PREPARATION")
    print("="*60)
    
    # Load cleaned data
    print("\n[1] Loading cleaned data...")
    df = pd.read_csv('cleaned_sales_data.csv')
    print(f"Loaded {len(df)} records with {len(df.columns)} features")
    
    # Convert date columns to proper format for Tableau
    print("\n[2] Formatting date columns...")
    date_columns = ['Order Date', 'Ship Date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    # Create additional calculated fields for Tableau
    print("\n[3] Creating Tableau-optimized fields...")
    
    # Date hierarchies
    df['Order_Year'] = df['Order Date'].dt.year
    df['Order_Quarter'] = 'Q' + df['Order Date'].dt.quarter.astype(str)
    df['Order_Month'] = df['Order Date'].dt.strftime('%B')
    df['Order_Month_Num'] = df['Order Date'].dt.month
    df['Order_Week'] = df['Order Date'].dt.isocalendar().week
    df['Order_Day'] = df['Order Date'].dt.day
    df['Order_Weekday'] = df['Order Date'].dt.strftime('%A')
    
    # Performance categories
    df['Revenue_Category'] = pd.cut(df['Total Revenue'], 
                                    bins=[0, 500000, 1000000, 2000000, float('inf')],
                                    labels=['Low', 'Medium', 'High', 'Very High'])
    
    df['Profit_Category'] = pd.cut(df['Profit_Margin'], 
                                   bins=[0, 20, 35, 50, 100],
                                   labels=['Low Margin', 'Medium Margin', 'Good Margin', 'Excellent Margin'])
    
    # Shipping performance
    df['Shipping_Performance'] = pd.cut(df['Shipping_Days'],
                                        bins=[0, 15, 25, 35, float('inf')],
                                        labels=['Fast', 'Normal', 'Slow', 'Very Slow'])
    
    # Regional groupings
    df['Continental_Region'] = df['Region'].map({
        'Sub-Saharan Africa': 'Africa',
        'Middle East and North Africa': 'Africa',
        'Europe': 'Europe',
        'Asia': 'Asia',
        'Australia and Oceania': 'Oceania',
        'North America': 'Americas',
        'Central America and the Caribbean': 'Americas'
    })
    
    # Customer segment (based on order patterns)
    customer_stats = df.groupby('Country').agg({
        'Total Revenue': 'sum',
        'Order ID': 'count',
        'Profit_Margin': 'mean'
    }).reset_index()
    customer_stats.columns = ['Country', 'Country_Total_Revenue', 'Country_Order_Count', 'Country_Avg_Margin']
    
    # Merge back
    df = df.merge(customer_stats, on='Country', how='left')
    
    # Customer value segment
    df['Customer_Segment'] = pd.cut(df['Country_Total_Revenue'],
                                    bins=[0, 1000000, 5000000, 10000000, float('inf')],
                                    labels=['Bronze', 'Silver', 'Gold', 'Platinum'])
    
    print(f"Added {15} Tableau-specific fields")
    
    # Create aggregated tables for better Tableau performance
    print("\n[4] Creating aggregated tables...")
    
    # Daily aggregation
    daily_agg = df.groupby('Order Date').agg({
        'Total Revenue': 'sum',
        'Total Profit': 'sum',
        'Total Cost': 'sum',
        'Units Sold': 'sum',
        'Order ID': 'count',
        'Profit_Margin': 'mean',
        'Shipping_Days': 'mean'
    }).reset_index()
    daily_agg.columns = ['Date', 'Daily_Revenue', 'Daily_Profit', 'Daily_Cost', 
                         'Daily_Units', 'Daily_Orders', 'Daily_Margin', 'Avg_Shipping']
    
    # Monthly aggregation
    df['Year_Month'] = df['Order Date'].dt.to_period('M')
    monthly_agg = df.groupby(['Year_Month', 'Region', 'Sales Channel']).agg({
        'Total Revenue': 'sum',
        'Total Profit': 'sum',
        'Units Sold': 'sum',
        'Order ID': 'count'
    }).reset_index()
    monthly_agg['Year_Month'] = monthly_agg['Year_Month'].astype(str)
    
    # Product performance
    product_agg = df.groupby(['Item Type', 'Sales Channel']).agg({
        'Total Revenue': ['sum', 'mean'],
        'Total Profit': ['sum', 'mean'],
        'Units Sold': ['sum', 'mean'],
        'Profit_Margin': 'mean',
        'Order ID': 'count'
    }).reset_index()
    product_agg.columns = ['_'.join(col).strip() for col in product_agg.columns.values]
    product_agg.rename(columns={'Item Type_': 'Item Type', 'Sales Channel_': 'Sales Channel'}, inplace=True)
    
    # Geographic performance
    geo_agg = df.groupby(['Country', 'Region']).agg({
        'Total Revenue': 'sum',
        'Total Profit': 'sum',
        'Units Sold': 'sum',
        'Order ID': 'count',
        'Profit_Margin': 'mean',
        'Shipping_Days': 'mean'
    }).reset_index()
    
    print("Created 4 aggregated tables for optimal performance")
    
    # Save all files
    print("\n[5] Saving Tableau-ready files...")
    
    # Main detailed data
    df.to_csv('tableau_sales_detailed.csv', index=False)
    print(f"Saved: tableau_sales_detailed.csv ({len(df)} rows)")
    
    # Aggregated tables
    daily_agg.to_csv('tableau_daily_metrics.csv', index=False)
    print(f"Saved: tableau_daily_metrics.csv ({len(daily_agg)} rows)")
    
    monthly_agg.to_csv('tableau_monthly_metrics.csv', index=False)
    print(f"Saved: tableau_monthly_metrics.csv ({len(monthly_agg)} rows)")
    
    product_agg.to_csv('tableau_product_metrics.csv', index=False)
    print(f"Saved: tableau_product_metrics.csv ({len(product_agg)} rows)")
    
    geo_agg.to_csv('tableau_geographic_metrics.csv', index=False)
    print(f"Saved: tableau_geographic_metrics.csv ({len(geo_agg)} rows)")
    
    # Create Tableau instructions file
    create_tableau_instructions()
    
    print("\n" + "="*60)
    print("TABLEAU PREPARATION COMPLETE!")
    print("="*60)
    
    return df

def create_tableau_instructions():
    """
    Create instructions for Tableau Public upload
    """
    
    instructions = """
    TABLEAU PUBLIC UPLOAD INSTRUCTIONS
    ===================================
    
    1. PREPARE TABLEAU PUBLIC ACCOUNT
       - Go to https://public.tableau.com
       - Sign up for free account if needed
       - Download Tableau Public Desktop
    
    2. CONNECT TO DATA
       - Open Tableau Public Desktop
       - Click "Connect" > "Text file"
       - Select: tableau_sales_detailed.csv
       - Add connections for aggregated tables:
         * tableau_daily_metrics.csv
         * tableau_monthly_metrics.csv
         * tableau_product_metrics.csv
         * tableau_geographic_metrics.csv
    
    3. CREATE RELATIONSHIPS
       - Link tables on common fields:
         * Date fields for time-based joins
         * Region/Country for geographic joins
         * Item Type for product joins
    
    4. BUILD DASHBOARDS
       
       Dashboard 1: Executive Overview
       - KPI cards: Total Revenue, Profit Margin, Orders
       - Line chart: Revenue trend over time
       - Bar chart: Top 10 products
       - Map: Revenue by country
       
       Dashboard 2: Sales Analysis
       - Time series with forecast
       - Seasonality patterns
       - Channel comparison
       - Priority distribution
       
       Dashboard 3: Product Performance
       - Product matrix (revenue vs margin)
       - Category breakdown
       - Trend by product type
       - Channel effectiveness
       
       Dashboard 4: Geographic Insights
       - World map with revenue bubbles
       - Regional comparison
       - Country rankings
       - Shipping performance by location
       
       Dashboard 5: Predictive Analytics
       - Forecast visualization
       - Trend indicators
       - Performance vs target
       - Alert indicators
    
    5. APPLY FORMATTING
       - Use consistent color scheme:
         * Primary: #2E86AB
         * Secondary: #A23B72
         * Accent: #F18F01
         * Alert: #C73E1D
         * Success: #6A994E
       - Add filters for interactivity
       - Include tooltips with details
       - Add dashboard actions for drill-down
    
    6. PUBLISH TO TABLEAU PUBLIC
       - Click "Server" > "Tableau Public" > "Save to Tableau Public"
       - Enter workbook name: "Healthcare Sales Analytics"
       - Add description and tags
       - Set visibility to Public
       - Copy the share URL
    
    7. SHARE THE DASHBOARD
       - Get the public URL from Tableau Public
       - Test embedding code for websites
       - Share link with stakeholders
    
    CALCULATED FIELDS TO CREATE IN TABLEAU:
    
    1. YoY Growth:
       (SUM([Total Revenue]) - LOOKUP(SUM([Total Revenue]), -12)) / 
       ABS(LOOKUP(SUM([Total Revenue]), -12)) * 100
    
    2. Profit Margin %:
       SUM([Total Profit]) / SUM([Total Revenue]) * 100
    
    3. Revenue per Order:
       SUM([Total Revenue]) / COUNTD([Order ID])
    
    4. Shipping Efficiency:
       IF [Shipping_Days] <= 15 THEN 'Excellent'
       ELSEIF [Shipping_Days] <= 25 THEN 'Good'
       ELSEIF [Shipping_Days] <= 35 THEN 'Fair'
       ELSE 'Poor' END
    
    5. Customer Lifetime Value:
       {FIXED [Country]: SUM([Total Revenue])}
    
    FILTERS TO ADD:
    - Date Range
    - Region
    - Country
    - Product Type
    - Sales Channel
    - Order Priority
    
    PARAMETERS TO CREATE:
    - Revenue Target (for comparison)
    - Forecast Period (months ahead)
    - Top N Products (dynamic ranking)
    """
    
    with open('tableau_instructions.txt', 'w') as f:
        f.write(instructions)
    
    print("Created: tableau_instructions.txt")

def main():
    """
    Main execution
    """
    try:
        # Check if cleaned data exists
        if not os.path.exists('cleaned_sales_data.csv'):
            print("ERROR: cleaned_sales_data.csv not found!")
            print("Please run 01_data_cleaning_pipeline.py first")
            return
        
        # Prepare Tableau data
        df = prepare_tableau_data()
        
        # Print summary statistics
        print("\n" + "="*60)
        print("SUMMARY STATISTICS")
        print("="*60)
        print(f"Total Revenue: ${df['Total Revenue'].sum():,.2f}")
        print(f"Total Profit: ${df['Total Profit'].sum():,.2f}")
        print(f"Average Profit Margin: {df['Profit_Margin'].mean():.2f}%")
        print(f"Total Orders: {df['Order ID'].nunique():,}")
        print(f"Date Range: {df['Order Date'].min()} to {df['Order Date'].max()}")
        print(f"Countries: {df['Country'].nunique()}")
        print(f"Product Types: {df['Item Type'].nunique()}")
        
        print("\n✅ All Tableau files ready for upload!")
        print("📊 Follow instructions in tableau_instructions.txt")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()