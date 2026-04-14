# Sales Data Visualization Guide
# Healthcare Medical Device Sales Analysis

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configure visualization settings
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4B51']

# ==========================================
# 1. TIME SERIES VISUALIZATIONS
# ==========================================

def plot_sales_trend(df):
    """
    Visualize sales trends over time with multiple perspectives
    """
    # Convert dates
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Daily Sales Revenue', 'Monthly Sales Trend', 
                       'Quarterly Performance', 'YoY Growth Rate'),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Daily sales
    daily_sales = df.groupby('Order Date')['Total Revenue'].sum().reset_index()
    fig.add_trace(
        go.Scatter(x=daily_sales['Order Date'], y=daily_sales['Total Revenue'],
                  mode='lines', name='Daily Revenue', line=dict(color=colors[0], width=1)),
        row=1, col=1
    )
    
    # Monthly aggregation with trend
    df['Month'] = df['Order Date'].dt.to_period('M')
    monthly_sales = df.groupby('Month')['Total Revenue'].sum().reset_index()
    monthly_sales['Month'] = monthly_sales['Month'].astype(str)
    
    fig.add_trace(
        go.Bar(x=monthly_sales['Month'], y=monthly_sales['Total Revenue'],
               name='Monthly Revenue', marker_color=colors[1]),
        row=1, col=2
    )
    
    # Add trend line
    z = np.polyfit(range(len(monthly_sales)), monthly_sales['Total Revenue'], 1)
    p = np.poly1d(z)
    fig.add_trace(
        go.Scatter(x=monthly_sales['Month'], y=p(range(len(monthly_sales))),
                  mode='lines', name='Trend', line=dict(color='red', dash='dash')),
        row=1, col=2
    )
    
    # Quarterly performance
    df['Quarter'] = df['Order Date'].dt.year.astype(str) + '-Q' + df['Order Date'].dt.quarter.astype(str)
    quarterly_sales = df.groupby('Quarter')['Total Revenue'].sum().reset_index()
    
    fig.add_trace(
        go.Bar(x=quarterly_sales['Quarter'], y=quarterly_sales['Total Revenue'],
               name='Quarterly Revenue', marker_color=colors[2]),
        row=2, col=1
    )
    
    # Year-over-Year growth
    df['Year'] = df['Order Date'].dt.year
    yearly_sales = df.groupby('Year')['Total Revenue'].sum().reset_index()
    yearly_sales['YoY_Growth'] = yearly_sales['Total Revenue'].pct_change() * 100
    
    fig.add_trace(
        go.Scatter(x=yearly_sales['Year'], y=yearly_sales['YoY_Growth'],
                  mode='lines+markers', name='YoY Growth %',
                  line=dict(color=colors[3], width=2),
                  marker=dict(size=10)),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, title_text="Sales Trend Analysis")
    return fig

def plot_seasonality_patterns(df):
    """
    Identify seasonal patterns in sales
    """
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Month'] = df['Order Date'].dt.month
    df['Day_of_Week'] = df['Order Date'].dt.dayofweek
    df['Week_of_Year'] = df['Order Date'].dt.isocalendar().week
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Monthly seasonality
    monthly_pattern = df.groupby('Month')['Total Revenue'].mean().reset_index()
    axes[0, 0].bar(monthly_pattern['Month'], monthly_pattern['Total Revenue'], color=colors[0])
    axes[0, 0].set_title('Average Revenue by Month')
    axes[0, 0].set_xlabel('Month')
    axes[0, 0].set_ylabel('Average Revenue')
    
    # Day of week pattern
    dow_pattern = df.groupby('Day_of_Week')['Total Revenue'].mean().reset_index()
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    axes[0, 1].bar(dow_pattern['Day_of_Week'], dow_pattern['Total Revenue'], color=colors[1])
    axes[0, 1].set_title('Average Revenue by Day of Week')
    axes[0, 1].set_xticklabels(days)
    axes[0, 1].set_xlabel('Day of Week')
    
    # Heatmap of sales by month and day
    pivot_table = df.pivot_table(values='Total Revenue', 
                                 index=df['Order Date'].dt.day,
                                 columns=df['Order Date'].dt.month,
                                 aggfunc='mean')
    
    sns.heatmap(pivot_table, cmap='YlOrRd', ax=axes[1, 0], cbar_kws={'label': 'Revenue'})
    axes[1, 0].set_title('Revenue Heatmap (Day vs Month)')
    axes[1, 0].set_xlabel('Month')
    axes[1, 0].set_ylabel('Day of Month')
    
    # Weekly pattern across the year
    weekly_pattern = df.groupby('Week_of_Year')['Total Revenue'].mean().reset_index()
    axes[1, 1].plot(weekly_pattern['Week_of_Year'], weekly_pattern['Total Revenue'], 
                    color=colors[2], linewidth=2)
    axes[1, 1].fill_between(weekly_pattern['Week_of_Year'], weekly_pattern['Total Revenue'], 
                            alpha=0.3, color=colors[2])
    axes[1, 1].set_title('Average Revenue by Week of Year')
    axes[1, 1].set_xlabel('Week of Year')
    
    plt.tight_layout()
    return fig

# ==========================================
# 2. PRODUCT & CATEGORY ANALYSIS
# ==========================================

def plot_product_performance(df):
    """
    Analyze product performance metrics
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Top 10 Products by Revenue', 'Product Type Distribution',
                       'Sales Channel Performance', 'Priority Orders Impact'),
        specs=[[{'type': 'bar'}, {'type': 'pie'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    # Top products
    top_products = df.groupby('Item Type')['Total Revenue'].sum().nlargest(10).reset_index()
    fig.add_trace(
        go.Bar(x=top_products['Total Revenue'], y=top_products['Item Type'],
               orientation='h', marker_color=colors[0]),
        row=1, col=1
    )
    
    # Product type distribution
    product_dist = df.groupby('Item Type')['Total Revenue'].sum().reset_index()
    fig.add_trace(
        go.Pie(labels=product_dist['Item Type'], values=product_dist['Total Revenue'],
               hole=0.3),
        row=1, col=2
    )
    
    # Sales channel comparison
    channel_perf = df.groupby('Sales Channel').agg({
        'Total Revenue': 'sum',
        'Total Profit': 'sum',
        'Units Sold': 'sum'
    }).reset_index()
    
    fig.add_trace(
        go.Bar(x=channel_perf['Sales Channel'], y=channel_perf['Total Revenue'],
               name='Revenue', marker_color=colors[2]),
        row=2, col=1
    )
    
    # Order priority impact
    priority_impact = df.groupby('Order Priority')['Total Revenue'].mean().reset_index()
    priority_order = ['L', 'M', 'H', 'C']  # Low, Medium, High, Critical
    priority_impact['Order Priority'] = pd.Categorical(priority_impact['Order Priority'], 
                                                       categories=priority_order, ordered=True)
    priority_impact = priority_impact.sort_values('Order Priority')
    
    fig.add_trace(
        go.Bar(x=priority_impact['Order Priority'], y=priority_impact['Total Revenue'],
               marker_color=colors[3]),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, title_text="Product Performance Analysis")
    return fig

# ==========================================
# 3. GEOGRAPHIC ANALYSIS
# ==========================================

def plot_geographic_distribution(df):
    """
    Visualize sales by region and country
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # Regional performance
    regional_sales = df.groupby('Region').agg({
        'Total Revenue': 'sum',
        'Total Profit': 'sum',
        'Units Sold': 'sum'
    }).reset_index()
    
    x = np.arange(len(regional_sales))
    width = 0.35
    
    axes[0, 0].bar(x - width/2, regional_sales['Total Revenue']/1e6, width, 
                   label='Revenue (M)', color=colors[0])
    axes[0, 0].bar(x + width/2, regional_sales['Total Profit']/1e6, width,
                   label='Profit (M)', color=colors[1])
    axes[0, 0].set_xlabel('Region')
    axes[0, 0].set_ylabel('Amount (Millions)')
    axes[0, 0].set_title('Revenue vs Profit by Region')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(regional_sales['Region'], rotation=45)
    axes[0, 0].legend()
    
    # Top 15 countries
    top_countries = df.groupby('Country')['Total Revenue'].sum().nlargest(15).reset_index()
    axes[0, 1].barh(top_countries['Country'], top_countries['Total Revenue']/1e6, 
                    color=colors[2])
    axes[0, 1].set_xlabel('Revenue (Millions)')
    axes[0, 1].set_title('Top 15 Countries by Revenue')
    
    # Profit margin by region
    regional_sales['Profit_Margin'] = (regional_sales['Total Profit'] / 
                                       regional_sales['Total Revenue'] * 100)
    axes[1, 0].bar(regional_sales['Region'], regional_sales['Profit_Margin'], 
                   color=colors[3])
    axes[1, 0].set_xlabel('Region')
    axes[1, 0].set_ylabel('Profit Margin (%)')
    axes[1, 0].set_title('Profit Margin by Region')
    axes[1, 0].axhline(y=regional_sales['Profit_Margin'].mean(), 
                       color='red', linestyle='--', label='Average')
    axes[1, 0].legend()
    
    # Regional growth over time
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Year_Month'] = df['Order Date'].dt.to_period('M')
    regional_trend = df.groupby(['Year_Month', 'Region'])['Total Revenue'].sum().reset_index()
    regional_trend['Year_Month'] = regional_trend['Year_Month'].astype(str)
    
    for region in regional_trend['Region'].unique():
        region_data = regional_trend[regional_trend['Region'] == region]
        axes[1, 1].plot(region_data['Year_Month'], region_data['Total Revenue']/1e6,
                       label=region, linewidth=2)
    
    axes[1, 1].set_xlabel('Month')
    axes[1, 1].set_ylabel('Revenue (Millions)')
    axes[1, 1].set_title('Regional Revenue Trends')
    axes[1, 1].legend(loc='upper left')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    return fig

# ==========================================
# 4. CORRELATION & RELATIONSHIPS
# ==========================================

def plot_correlation_analysis(df):
    """
    Analyze correlations between key metrics
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Correlation heatmap
    numerical_cols = ['Units Sold', 'Unit Price', 'Unit Cost', 
                     'Total Revenue', 'Total Cost', 'Total Profit']
    correlation_matrix = df[numerical_cols].corr()
    
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, ax=axes[0, 0], cbar_kws={'label': 'Correlation'})
    axes[0, 0].set_title('Feature Correlation Matrix')
    
    # Price vs Volume relationship
    axes[0, 1].scatter(df['Unit Price'], df['Units Sold'], 
                      alpha=0.5, color=colors[0], s=20)
    axes[0, 1].set_xlabel('Unit Price')
    axes[0, 1].set_ylabel('Units Sold')
    axes[0, 1].set_title('Price-Volume Relationship')
    
    # Add trend line
    z = np.polyfit(df['Unit Price'], df['Units Sold'], 1)
    p = np.poly1d(z)
    axes[0, 1].plot(df['Unit Price'].sort_values(), 
                   p(df['Unit Price'].sort_values()),
                   "r--", alpha=0.8, label='Trend')
    axes[0, 1].legend()
    
    # Profit margin distribution
    df['Profit_Margin'] = (df['Total Profit'] / df['Total Revenue']) * 100
    axes[1, 0].hist(df['Profit_Margin'], bins=50, color=colors[1], edgecolor='black')
    axes[1, 0].axvline(df['Profit_Margin'].mean(), color='red', 
                       linestyle='--', label=f'Mean: {df["Profit_Margin"].mean():.1f}%')
    axes[1, 0].set_xlabel('Profit Margin (%)')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_title('Profit Margin Distribution')
    axes[1, 0].legend()
    
    # Revenue vs Cost with profit bands
    scatter = axes[1, 1].scatter(df['Total Cost'], df['Total Revenue'], 
                                 c=df['Total Profit'], cmap='RdYlGn', 
                                 alpha=0.6, s=20)
    axes[1, 1].set_xlabel('Total Cost')
    axes[1, 1].set_ylabel('Total Revenue')
    axes[1, 1].set_title('Revenue vs Cost (colored by Profit)')
    
    # Add break-even line
    max_val = max(df['Total Cost'].max(), df['Total Revenue'].max())
    axes[1, 1].plot([0, max_val], [0, max_val], 'k--', alpha=0.5, label='Break-even')
    axes[1, 1].legend()
    
    plt.colorbar(scatter, ax=axes[1, 1], label='Profit')
    plt.tight_layout()
    return fig

# ==========================================
# 5. FORECASTING PREP VISUALIZATIONS
# ==========================================

def plot_forecasting_features(df):
    """
    Visualizations specifically for ML model preparation
    """
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    
    # Create lag features for visualization
    df = df.sort_values('Order Date')
    daily_revenue = df.groupby('Order Date')['Total Revenue'].sum().reset_index()
    daily_revenue['Revenue_Lag7'] = daily_revenue['Total Revenue'].shift(7)
    daily_revenue['Revenue_MA7'] = daily_revenue['Total Revenue'].rolling(7).mean()
    daily_revenue['Revenue_MA30'] = daily_revenue['Total Revenue'].rolling(30).mean()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Autocorrelation Analysis', 'Moving Averages',
                       'Volatility Analysis', 'Decomposition Components')
    )
    
    # Autocorrelation
    from pandas.plotting import autocorrelation_plot
    ax1 = plt.subplot(2, 2, 1)
    autocorrelation_plot(daily_revenue['Total Revenue'].dropna(), ax=ax1)
    ax1.set_title('Revenue Autocorrelation')
    
    # Moving averages
    fig.add_trace(
        go.Scatter(x=daily_revenue['Order Date'], y=daily_revenue['Total Revenue'],
                  mode='lines', name='Actual', line=dict(color=colors[0], width=1)),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=daily_revenue['Order Date'], y=daily_revenue['Revenue_MA7'],
                  mode='lines', name='7-day MA', line=dict(color=colors[1], width=2)),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(x=daily_revenue['Order Date'], y=daily_revenue['Revenue_MA30'],
                  mode='lines', name='30-day MA', line=dict(color=colors[2], width=2)),
        row=1, col=2
    )
    
    # Volatility
    daily_revenue['Returns'] = daily_revenue['Total Revenue'].pct_change()
    daily_revenue['Volatility'] = daily_revenue['Returns'].rolling(30).std()
    
    fig.add_trace(
        go.Scatter(x=daily_revenue['Order Date'], y=daily_revenue['Volatility'],
                  mode='lines', fill='tozeroy', line=dict(color=colors[3])),
        row=2, col=1
    )
    
    # Trend strength indicator
    daily_revenue['Trend_Strength'] = (daily_revenue['Revenue_MA7'] - 
                                       daily_revenue['Revenue_MA30']).abs()
    fig.add_trace(
        go.Bar(x=daily_revenue['Order Date'], y=daily_revenue['Trend_Strength'],
               marker_color=colors[4]),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=True, title_text="ML Feature Analysis")
    return fig

# ==========================================
# 6. EXECUTIVE DASHBOARD
# ==========================================

def create_executive_dashboard(df):
    """
    High-level dashboard for stakeholders
    """
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    
    # Calculate KPIs
    total_revenue = df['Total Revenue'].sum()
    total_profit = df['Total Profit'].sum()
    profit_margin = (total_profit / total_revenue) * 100
    avg_order_value = df['Total Revenue'].mean()
    total_orders = len(df)
    
    # Create dashboard
    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=('Total Revenue', 'Profit Margin', 'Order Volume',
                       'Revenue Trend', 'Top Products', 'Regional Split',
                       'Channel Performance', 'Order Priority', 'Profit Trend'),
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}],
               [{'type': 'scatter'}, {'type': 'bar'}, {'type': 'pie'}],
               [{'type': 'bar'}, {'type': 'pie'}, {'type': 'scatter'}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )
    
    # KPI Cards
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=total_revenue/1e6,
            number={'suffix': "M", 'font': {'size': 30}},
            delta={'reference': total_revenue/1e6 * 0.9, 'relative': True},
            title={'text': "Total Revenue"}),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=profit_margin,
            number={'suffix': "%", 'font': {'size': 30}},
            gauge={'axis': {'range': [None, 50]}, 'bar': {'color': colors[1]}},
            title={'text': "Profit Margin"}),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=total_orders,
            number={'font': {'size': 30}},
            delta={'reference': total_orders * 0.95},
            title={'text': "Total Orders"}),
        row=1, col=3
    )
    
    # Revenue trend
    monthly_revenue = df.groupby(df['Order Date'].dt.to_period('M'))['Total Revenue'].sum()
    fig.add_trace(
        go.Scatter(x=monthly_revenue.index.astype(str), y=monthly_revenue.values/1e6,
                  mode='lines+markers', line=dict(color=colors[0], width=2)),
        row=2, col=1
    )
    
    # Top 5 products
    top5_products = df.groupby('Item Type')['Total Revenue'].sum().nlargest(5)
    fig.add_trace(
        go.Bar(x=top5_products.index, y=top5_products.values/1e6,
               marker_color=colors[2]),
        row=2, col=2
    )
    
    # Regional split
    regional_split = df.groupby('Region')['Total Revenue'].sum()
    fig.add_trace(
        go.Pie(labels=regional_split.index, values=regional_split.values,
               hole=0.3),
        row=2, col=3
    )
    
    # Channel performance
    channel_perf = df.groupby('Sales Channel')['Total Revenue'].sum()
    fig.add_trace(
        go.Bar(x=channel_perf.index, y=channel_perf.values/1e6,
               marker_color=colors[3]),
        row=3, col=1
    )
    
    # Order priority distribution
    priority_dist = df.groupby('Order Priority')['Total Revenue'].sum()
    fig.add_trace(
        go.Pie(labels=priority_dist.index, values=priority_dist.values),
        row=3, col=2
    )
    
    # Profit trend
    monthly_profit = df.groupby(df['Order Date'].dt.to_period('M'))['Total Profit'].sum()
    fig.add_trace(
        go.Scatter(x=monthly_profit.index.astype(str), y=monthly_profit.values/1e6,
                  mode='lines+markers', fill='tozeroy',
                  line=dict(color=colors[4], width=2)),
        row=3, col=3
    )
    
    fig.update_layout(height=900, showlegend=False, 
                     title_text="Executive Sales Dashboard")
    return fig

# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    """
    Execute all visualizations
    """
    # Load data
    df = pd.read_csv('10000 Sales Records.csv')
    
    print("Generating Sales Visualizations...")
    print("=" * 50)
    
    # 1. Time Series Analysis
    print("\n[1/6] Creating time series visualizations...")
    fig1 = plot_sales_trend(df)
    fig1.show()
    
    fig2 = plot_seasonality_patterns(df)
    plt.show()
    
    # 2. Product Analysis
    print("[2/6] Creating product performance visualizations...")
    fig3 = plot_product_performance(df)
    fig3.show()
    
    # 3. Geographic Analysis
    print("[3/6] Creating geographic visualizations...")
    fig4 = plot_geographic_distribution(df)
    plt.show()
    
    # 4. Correlation Analysis
    print("[4/6] Creating correlation visualizations...")
    fig5 = plot_correlation_analysis(df)
    plt.show()
    
    # 5. ML Prep Visualizations
    print("[5/6] Creating ML feature visualizations...")
    fig6 = plot_forecasting_features(df)
    fig6.show()
    
    # 6. Executive Dashboard
    print("[6/6] Creating executive dashboard...")
    fig7 = create_executive_dashboard(df)
    fig7.show()
    
    print("\n✓ All visualizations complete!")
    print("Key insights generated for ML model development")

if __name__ == "__main__":
    main()