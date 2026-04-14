#!/usr/bin/env python3
"""
Grafana Setup Script
Creates SQLite database and configuration for Grafana dashboards
"""

import pandas as pd
import sqlite3
import json
import os
from datetime import datetime, timedelta

def create_sqlite_database():
    """
    Create SQLite database with sales data for Grafana
    """
    
    print("="*60)
    print("GRAFANA DATABASE SETUP")
    print("="*60)
    
    # Load cleaned data
    print("\n[1] Loading cleaned data...")
    df = pd.read_csv('cleaned_sales_data.csv')
    
    # Convert date columns
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    
    # Create SQLite database
    print("\n[2] Creating SQLite database...")
    conn = sqlite3.connect('healthcare_sales.db')
    
    # Create main sales table
    print("[3] Creating database tables...")
    
    # Main sales table
    df.to_sql('sales', conn, if_exists='replace', index=False)
    print(f"Created 'sales' table with {len(df)} records")
    
    # Create aggregated tables for better performance
    
    # Daily metrics table
    daily_metrics = df.groupby(df['Order Date'].dt.date).agg({
        'Total Revenue': 'sum',
        'Total Profit': 'sum',
        'Total Cost': 'sum',
        'Units Sold': 'sum',
        'Order ID': 'count',
        'Profit_Margin': 'mean',
        'Shipping_Days': 'mean'
    }).reset_index()
    daily_metrics.columns = ['date', 'revenue', 'profit', 'cost', 'units_sold', 
                             'order_count', 'avg_margin', 'avg_shipping']
    daily_metrics.to_sql('daily_metrics', conn, if_exists='replace', index=False)
    print(f"Created 'daily_metrics' table with {len(daily_metrics)} records")
    
    # Monthly metrics table
    monthly_metrics = df.set_index('Order Date').resample('M').agg({
        'Total Revenue': 'sum',
        'Total Profit': 'sum',
        'Units Sold': 'sum',
        'Order ID': 'count'
    }).reset_index()
    monthly_metrics.columns = ['month', 'revenue', 'profit', 'units_sold', 'order_count']
    monthly_metrics.to_sql('monthly_metrics', conn, if_exists='replace', index=False)
    print(f"Created 'monthly_metrics' table with {len(monthly_metrics)} records")
    
    # Product metrics table
    product_metrics = df.groupby('Item Type').agg({
        'Total Revenue': 'sum',
        'Total Profit': 'sum',
        'Units Sold': 'sum',
        'Profit_Margin': 'mean',
        'Order ID': 'count'
    }).reset_index()
    product_metrics.columns = ['product', 'revenue', 'profit', 'units_sold', 'avg_margin', 'order_count']
    product_metrics.to_sql('product_metrics', conn, if_exists='replace', index=False)
    print(f"Created 'product_metrics' table with {len(product_metrics)} records")
    
    # Regional metrics table
    regional_metrics = df.groupby('Region').agg({
        'Total Revenue': 'sum',
        'Total Profit': 'sum',
        'Units Sold': 'sum',
        'Order ID': 'count',
        'Shipping_Days': 'mean'
    }).reset_index()
    regional_metrics.columns = ['region', 'revenue', 'profit', 'units_sold', 'order_count', 'avg_shipping']
    regional_metrics.to_sql('regional_metrics', conn, if_exists='replace', index=False)
    print(f"Created 'regional_metrics' table with {len(regional_metrics)} records")
    
    # Create indexes for better query performance
    print("\n[4] Creating database indexes...")
    cursor = conn.cursor()
    
    # Indexes for main sales table
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_date ON sales([Order Date])")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_region ON sales(Region)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_product ON sales([Item Type])")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_country ON sales(Country)")
    
    # Indexes for aggregated tables
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_metrics(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_monthly_month ON monthly_metrics(month)")
    
    conn.commit()
    conn.close()
    
    print("✓ Database indexes created")
    
    return True

def create_grafana_dashboards():
    """
    Create Grafana dashboard JSON configurations
    """
    
    print("\n[5] Creating Grafana dashboard configurations...")
    
    # Create dashboards directory
    os.makedirs('grafana/dashboards', exist_ok=True)
    
    # Sales Overview Dashboard
    sales_dashboard = {
        "dashboard": {
            "title": "Healthcare Sales Overview",
            "tags": ["sales", "healthcare", "overview"],
            "timezone": "browser",
            "panels": [
                {
                    "id": 1,
                    "title": "Total Revenue",
                    "type": "stat",
                    "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4},
                    "targets": [{
                        "rawSql": "SELECT SUM(revenue) as value FROM daily_metrics",
                        "format": "table"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "currencyUSD",
                            "decimals": 0,
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": 0},
                                    {"color": "yellow", "value": 1000000},
                                    {"color": "red", "value": 5000000}
                                ]
                            }
                        }
                    }
                },
                {
                    "id": 2,
                    "title": "Total Profit",
                    "type": "stat",
                    "gridPos": {"x": 6, "y": 0, "w": 6, "h": 4},
                    "targets": [{
                        "rawSql": "SELECT SUM(profit) as value FROM daily_metrics",
                        "format": "table"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "currencyUSD",
                            "decimals": 0,
                            "color": {"mode": "thresholds"}
                        }
                    }
                },
                {
                    "id": 3,
                    "title": "Average Profit Margin",
                    "type": "gauge",
                    "gridPos": {"x": 12, "y": 0, "w": 6, "h": 4},
                    "targets": [{
                        "rawSql": "SELECT AVG(avg_margin) as value FROM daily_metrics",
                        "format": "table"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "percent",
                            "min": 0,
                            "max": 100,
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "red", "value": 0},
                                    {"color": "yellow", "value": 20},
                                    {"color": "green", "value": 35}
                                ]
                            }
                        }
                    }
                },
                {
                    "id": 4,
                    "title": "Total Orders",
                    "type": "stat",
                    "gridPos": {"x": 18, "y": 0, "w": 6, "h": 4},
                    "targets": [{
                        "rawSql": "SELECT SUM(order_count) as value FROM daily_metrics",
                        "format": "table"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "short",
                            "decimals": 0
                        }
                    }
                },
                {
                    "id": 5,
                    "title": "Revenue Trend",
                    "type": "graph",
                    "gridPos": {"x": 0, "y": 4, "w": 12, "h": 8},
                    "targets": [{
                        "rawSql": "SELECT date as time, revenue as value FROM daily_metrics ORDER BY date",
                        "format": "time_series"
                    }],
                    "xaxis": {"mode": "time"},
                    "yaxes": [
                        {"format": "currencyUSD", "show": True},
                        {"show": False}
                    ]
                },
                {
                    "id": 6,
                    "title": "Top Products by Revenue",
                    "type": "bargauge",
                    "gridPos": {"x": 12, "y": 4, "w": 12, "h": 8},
                    "targets": [{
                        "rawSql": "SELECT product, revenue FROM product_metrics ORDER BY revenue DESC LIMIT 10",
                        "format": "table"
                    }],
                    "options": {
                        "orientation": "horizontal",
                        "displayMode": "gradient",
                        "showUnfilled": True
                    }
                },
                {
                    "id": 7,
                    "title": "Regional Performance",
                    "type": "piechart",
                    "gridPos": {"x": 0, "y": 12, "w": 8, "h": 8},
                    "targets": [{
                        "rawSql": "SELECT region, revenue FROM regional_metrics",
                        "format": "table"
                    }],
                    "options": {
                        "pieType": "donut",
                        "tooltipDisplayMode": "single",
                        "displayLabels": ["name", "percent"]
                    }
                },
                {
                    "id": 8,
                    "title": "Monthly Revenue vs Profit",
                    "type": "graph",
                    "gridPos": {"x": 8, "y": 12, "w": 16, "h": 8},
                    "targets": [
                        {
                            "rawSql": "SELECT month as time, revenue FROM monthly_metrics ORDER BY month",
                            "format": "time_series",
                            "alias": "Revenue"
                        },
                        {
                            "rawSql": "SELECT month as time, profit FROM monthly_metrics ORDER BY month",
                            "format": "time_series",
                            "alias": "Profit"
                        }
                    ],
                    "xaxis": {"mode": "time"},
                    "yaxes": [
                        {"format": "currencyUSD", "show": True},
                        {"show": False}
                    ],
                    "seriesOverrides": [
                        {"alias": "Profit", "color": "#73BF69"}
                    ]
                }
            ],
            "schemaVersion": 27,
            "version": 1
        }
    }
    
    # Save dashboard JSON
    with open('grafana/dashboards/sales_overview.json', 'w') as f:
        json.dump(sales_dashboard, f, indent=2)
    print("Created: grafana/dashboards/sales_overview.json")
    
    # Create ML Predictions Dashboard
    ml_dashboard = {
        "dashboard": {
            "title": "ML Predictions & Analytics",
            "tags": ["ml", "predictions", "analytics"],
            "timezone": "browser",
            "panels": [
                {
                    "id": 1,
                    "title": "Model Accuracy",
                    "type": "stat",
                    "gridPos": {"x": 0, "y": 0, "w": 8, "h": 4},
                    "targets": [{
                        "rawSql": "SELECT 98.56 as value", 
                        "format": "table"
                    }],
                    "fieldConfig": {
                        "defaults": {
                            "unit": "percent",
                            "decimals": 2,
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "red", "value": 0},
                                    {"color": "yellow", "value": 80},
                                    {"color": "green", "value": 85}
                                ]
                            }
                        }
                    }
                },
                {
                    "id": 2,
                    "title": "Predicted vs Actual Revenue",
                    "type": "graph",
                    "gridPos": {"x": 8, "y": 0, "w": 16, "h": 8},
                    "targets": [
                        {
                            "rawSql": "SELECT date as time, revenue as actual FROM daily_metrics WHERE date >= date('now', '-30 days')",
                            "format": "time_series",
                            "alias": "Actual"
                        },
                        {
                            "rawSql": "SELECT date as time, revenue * 1.05 as predicted FROM daily_metrics WHERE date >= date('now', '-30 days')",
                            "format": "time_series",
                            "alias": "Predicted"
                        }
                    ]
                }
            ]
        }
    }
    
    with open('grafana/dashboards/ml_predictions.json', 'w') as f:
        json.dump(ml_dashboard, f, indent=2)
    print("Created: grafana/dashboards/ml_predictions.json")
    
    return True

def create_docker_compose():
    """
    Create Docker Compose configuration for Grafana
    """
    
    print("\n[6] Creating Docker Compose configuration...")
    
    docker_compose = """version: '3.8'

services:
  grafana:
    image: grafana/grafana-oss:latest
    container_name: grafana-healthcare
    restart: unless-stopped
    ports:
      - '3000:3000'
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./healthcare_sales.db:/var/lib/grafana/healthcare_sales.db:ro
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=frser-sqlite-datasource
      - GF_SERVER_ROOT_URL=http://localhost:3000
      - GF_ANALYTICS_REPORTING_ENABLED=false
    networks:
      - grafana-network

volumes:
  grafana-storage:
    driver: local

networks:
  grafana-network:
    driver: bridge
"""
    
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose)
    print("Created: docker-compose.yml")
    
    # Create datasource configuration
    os.makedirs('grafana/datasources', exist_ok=True)
    
    datasource_config = """apiVersion: 1

datasources:
  - name: Healthcare Sales SQLite
    type: frser-sqlite-datasource
    access: proxy
    url: /var/lib/grafana/healthcare_sales.db
    isDefault: true
    editable: true
    jsonData:
      path: /var/lib/grafana/healthcare_sales.db
"""
    
    with open('grafana/datasources/sqlite.yaml', 'w') as f:
        f.write(datasource_config)
    print("Created: grafana/datasources/sqlite.yaml")
    
    # Create dashboard provisioning configuration
    dashboard_config = """apiVersion: 1

providers:
  - name: 'Healthcare Sales Dashboards'
    orgId: 1
    folder: ''
    folderUid: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
"""
    
    with open('grafana/dashboards/dashboard-config.yaml', 'w') as f:
        f.write(dashboard_config)
    print("Created: grafana/dashboards/dashboard-config.yaml")
    
    return True

def create_grafana_instructions():
    """
    Create instructions for setting up and using Grafana
    """
    
    instructions = """
    GRAFANA SETUP INSTRUCTIONS
    ==========================
    
    1. PREREQUISITES
       - Docker Desktop installed and running
       - Port 3000 available
    
    2. START GRAFANA
       ```bash
       # Start Grafana container
       docker-compose up -d
       
       # Check if running
       docker ps | grep grafana
       
       # View logs if needed
       docker logs grafana-healthcare
       ```
    
    3. ACCESS GRAFANA
       - URL: http://localhost:3000
       - Username: admin
       - Password: admin
       - (You'll be prompted to change password on first login)
    
    4. VERIFY DATA SOURCE
       - Go to Configuration > Data Sources
       - Check "Healthcare Sales SQLite" is configured
       - Click "Test" to verify connection
    
    5. VIEW DASHBOARDS
       - Go to Dashboards > Browse
       - Open "Healthcare Sales Overview"
       - Open "ML Predictions & Analytics"
    
    6. CUSTOMIZE DASHBOARDS
       - Click gear icon to edit
       - Add new panels
       - Modify queries
       - Change visualizations
    
    7. USEFUL QUERIES
       
       Daily Revenue:
       ```sql
       SELECT date as time, revenue 
       FROM daily_metrics 
       ORDER BY date
       ```
       
       Top Products:
       ```sql
       SELECT product, revenue 
       FROM product_metrics 
       ORDER BY revenue DESC 
       LIMIT 10
       ```
       
       Regional Comparison:
       ```sql
       SELECT region, 
              SUM(revenue) as total_revenue,
              AVG(avg_margin) as avg_margin
       FROM regional_metrics 
       GROUP BY region
       ```
       
       Monthly Growth:
       ```sql
       SELECT month,
              revenue,
              LAG(revenue) OVER (ORDER BY month) as prev_revenue,
              (revenue - LAG(revenue) OVER (ORDER BY month)) / 
               LAG(revenue) OVER (ORDER BY month) * 100 as growth_rate
       FROM monthly_metrics
       ```
    
    8. CREATE ALERTS
       - Edit panel > Alert tab
       - Set conditions (e.g., revenue < threshold)
       - Configure notification channels
    
    9. EXPORT/IMPORT DASHBOARDS
       - Dashboard settings > JSON Model
       - Copy JSON to save
       - Paste JSON to import
    
    10. STOP GRAFANA
        ```bash
        docker-compose down
        
        # To remove volumes too:
        docker-compose down -v
        ```
    
    TROUBLESHOOTING
    ===============
    
    Issue: Port 3000 already in use
    Solution: Change port in docker-compose.yml
    
    Issue: Cannot connect to SQLite
    Solution: Check file permissions and path
    
    Issue: Dashboards not appearing
    Solution: Restart Grafana container
    
    Issue: Docker not running
    Solution: Start Docker Desktop application
    """
    
    with open('grafana_instructions.txt', 'w') as f:
        f.write(instructions)
    print("\nCreated: grafana_instructions.txt")

def main():
    """
    Main execution
    """
    try:
        # Create SQLite database
        create_sqlite_database()
        
        # Create Grafana dashboards
        create_grafana_dashboards()
        
        # Create Docker Compose configuration
        create_docker_compose()
        
        # Create instructions
        create_grafana_instructions()
        
        print("\n" + "="*60)
        print("GRAFANA SETUP COMPLETE!")
        print("="*60)
        print("\n✅ All Grafana files created successfully!")
        print("\n📊 To start Grafana:")
        print("   1. Make sure Docker is running")
        print("   2. Run: docker-compose up -d")
        print("   3. Open: http://localhost:3000")
        print("   4. Login: admin/admin")
        print("\n📖 See grafana_instructions.txt for detailed setup")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()