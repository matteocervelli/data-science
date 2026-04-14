#!/usr/bin/env python3
"""
Fix Grafana Dashboards with proper SQLite queries
"""

import json
import requests

GRAFANA_URL = "http://localhost:3000"
USERNAME = "admin"
PASSWORD = "Password123!"

def create_working_dashboard():
    """Create a simplified dashboard that works with SQLite"""
    
    dashboard = {
        "dashboard": {
            "id": None,
            "uid": None,
            "title": "Healthcare Sales Dashboard - Working",
            "timezone": "browser",
            "schemaVersion": 27,
            "version": 0,
            "panels": [
                {
                    "id": 1,
                    "type": "stat",
                    "title": "Total Revenue",
                    "gridPos": {"x": 0, "y": 0, "w": 6, "h": 4},
                    "targets": [
                        {
                            "datasource": {
                                "type": "frser-sqlite-datasource",
                                "uid": "bev5d9szs78qod"
                            },
                            "queryText": "SELECT SUM(revenue) as revenue FROM daily_metrics",
                            "queryType": "table",
                            "rawQueryText": "SELECT SUM(revenue) as revenue FROM daily_metrics",
                            "refId": "A",
                            "format": "table"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [],
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "red", "value": 80}
                                ]
                            },
                            "unit": "currencyUSD",
                            "decimals": 0
                        }
                    },
                    "options": {
                        "reduceOptions": {
                            "values": False,
                            "fields": "revenue",
                            "calcs": ["lastNotNull"]
                        },
                        "orientation": "auto",
                        "textMode": "auto",
                        "colorMode": "value",
                        "graphMode": "none",
                        "justifyMode": "auto"
                    }
                },
                {
                    "id": 2,
                    "type": "stat",
                    "title": "Total Orders",
                    "gridPos": {"x": 6, "y": 0, "w": 6, "h": 4},
                    "targets": [
                        {
                            "datasource": {
                                "type": "frser-sqlite-datasource",
                                "uid": "bev5d9szs78qod"
                            },
                            "queryText": "SELECT SUM(order_count) as orders FROM daily_metrics",
                            "queryType": "table",
                            "rawQueryText": "SELECT SUM(order_count) as orders FROM daily_metrics",
                            "refId": "A",
                            "format": "table"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [],
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None}
                                ]
                            },
                            "unit": "short",
                            "decimals": 0
                        }
                    },
                    "options": {
                        "reduceOptions": {
                            "values": False,
                            "fields": "orders",
                            "calcs": ["lastNotNull"]
                        },
                        "orientation": "auto",
                        "textMode": "auto",
                        "colorMode": "value",
                        "graphMode": "none",
                        "justifyMode": "auto"
                    }
                },
                {
                    "id": 3,
                    "type": "stat",
                    "title": "Average Profit Margin",
                    "gridPos": {"x": 12, "y": 0, "w": 6, "h": 4},
                    "targets": [
                        {
                            "datasource": {
                                "type": "frser-sqlite-datasource",
                                "uid": "bev5d9szs78qod"
                            },
                            "queryText": "SELECT AVG(avg_margin) as margin FROM daily_metrics",
                            "queryType": "table",
                            "rawQueryText": "SELECT AVG(avg_margin) as margin FROM daily_metrics",
                            "refId": "A",
                            "format": "table"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "mappings": [],
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "red", "value": None},
                                    {"color": "yellow", "value": 20},
                                    {"color": "green", "value": 35}
                                ]
                            },
                            "unit": "percent",
                            "decimals": 2
                        }
                    },
                    "options": {
                        "reduceOptions": {
                            "values": False,
                            "fields": "margin",
                            "calcs": ["lastNotNull"]
                        },
                        "orientation": "auto",
                        "textMode": "auto",
                        "colorMode": "value",
                        "graphMode": "none",
                        "justifyMode": "auto"
                    }
                },
                {
                    "id": 4,
                    "type": "table",
                    "title": "Daily Metrics Table",
                    "gridPos": {"x": 0, "y": 4, "w": 12, "h": 8},
                    "targets": [
                        {
                            "datasource": {
                                "type": "frser-sqlite-datasource",
                                "uid": "bev5d9szs78qod"
                            },
                            "queryText": "SELECT date, revenue, profit, order_count FROM daily_metrics ORDER BY date DESC LIMIT 30",
                            "queryType": "table",
                            "rawQueryText": "SELECT date, revenue, profit, order_count FROM daily_metrics ORDER BY date DESC LIMIT 30",
                            "refId": "A",
                            "format": "table"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {
                                "align": "auto",
                                "displayMode": "auto"
                            }
                        },
                        "overrides": [
                            {
                                "matcher": {"id": "byName", "options": "revenue"},
                                "properties": [
                                    {"id": "unit", "value": "currencyUSD"},
                                    {"id": "decimals", "value": 0}
                                ]
                            },
                            {
                                "matcher": {"id": "byName", "options": "profit"},
                                "properties": [
                                    {"id": "unit", "value": "currencyUSD"},
                                    {"id": "decimals", "value": 0}
                                ]
                            }
                        ]
                    },
                    "options": {
                        "showHeader": True
                    }
                },
                {
                    "id": 5,
                    "type": "table",
                    "title": "Product Performance",
                    "gridPos": {"x": 12, "y": 4, "w": 12, "h": 8},
                    "targets": [
                        {
                            "datasource": {
                                "type": "frser-sqlite-datasource",
                                "uid": "bev5d9szs78qod"
                            },
                            "queryText": "SELECT product, revenue, profit, avg_margin FROM product_metrics ORDER BY revenue DESC",
                            "queryType": "table",
                            "rawQueryText": "SELECT product, revenue, profit, avg_margin FROM product_metrics ORDER BY revenue DESC",
                            "refId": "A",
                            "format": "table"
                        }
                    ],
                    "fieldConfig": {
                        "defaults": {
                            "custom": {
                                "align": "auto",
                                "displayMode": "auto"
                            }
                        },
                        "overrides": [
                            {
                                "matcher": {"id": "byName", "options": "revenue"},
                                "properties": [
                                    {"id": "unit", "value": "currencyUSD"},
                                    {"id": "decimals", "value": 0}
                                ]
                            },
                            {
                                "matcher": {"id": "byName", "options": "profit"},
                                "properties": [
                                    {"id": "unit", "value": "currencyUSD"},
                                    {"id": "decimals", "value": 0}
                                ]
                            },
                            {
                                "matcher": {"id": "byName", "options": "avg_margin"},
                                "properties": [
                                    {"id": "unit", "value": "percent"},
                                    {"id": "decimals", "value": 2}
                                ]
                            }
                        ]
                    },
                    "options": {
                        "showHeader": True
                    }
                }
            ]
        },
        "overwrite": True,
        "folderId": 0
    }
    
    # Import the dashboard
    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        auth=(USERNAME, PASSWORD),
        headers={"Content-Type": "application/json"},
        json=dashboard
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Dashboard created successfully!")
        print(f"   URL: {GRAFANA_URL}/d/{result['uid']}")
        return result['uid']
    else:
        print(f"❌ Failed to create dashboard: {response.text}")
        return None

def test_datasource():
    """Test if datasource is working"""
    response = requests.post(
        f"{GRAFANA_URL}/api/datasources/proxy/2/query",
        auth=(USERNAME, PASSWORD),
        headers={"Content-Type": "application/json"},
        json={
            "queries": [{
                "datasourceId": 2,
                "rawSql": "SELECT COUNT(*) as count FROM daily_metrics",
                "format": "table"
            }]
        }
    )
    
    print("Testing datasource connection...")
    if response.status_code == 200:
        print("✅ Datasource is working!")
        data = response.json()
        print(f"   Response: {data}")
    else:
        print(f"❌ Datasource test failed: {response.status_code}")
        print(f"   Error: {response.text}")

if __name__ == "__main__":
    print("Fixing Grafana Dashboard Issues...")
    print("-" * 50)
    
    # Test datasource
    test_datasource()
    
    print("\nCreating new working dashboard...")
    uid = create_working_dashboard()
    
    if uid:
        print("\n" + "="*50)
        print("✅ SUCCESS!")
        print("="*50)
        print(f"\n📊 Open your browser and go to:")
        print(f"   {GRAFANA_URL}/d/{uid}")
        print(f"\n   Username: admin")
        print(f"   Password: Password123!")
        print("\nThe dashboard should now show data correctly!")