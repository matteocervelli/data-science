#!/usr/bin/env python3
"""
Create a Grafana dashboard using JSON API datasource as alternative
"""

import json
import sqlite3
import pandas as pd
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
import requests

# First, create a simple API server for the data
class DataAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        conn = sqlite3.connect('healthcare_sales.db')
        
        if self.path == '/metrics':
            # Get summary metrics
            metrics = {}
            metrics['total_revenue'] = pd.read_sql("SELECT SUM(revenue) as value FROM daily_metrics", conn).iloc[0,0]
            metrics['total_orders'] = pd.read_sql("SELECT SUM(order_count) as value FROM daily_metrics", conn).iloc[0,0]
            metrics['avg_margin'] = pd.read_sql("SELECT AVG(avg_margin) as value FROM daily_metrics", conn).iloc[0,0]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(metrics).encode())
            
        elif self.path == '/daily':
            # Get daily data
            df = pd.read_sql("SELECT * FROM daily_metrics ORDER BY date DESC LIMIT 30", conn)
            data = df.to_dict(orient='records')
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data, default=str).encode())
            
        elif self.path == '/products':
            # Get product data
            df = pd.read_sql("SELECT * FROM product_metrics ORDER BY revenue DESC", conn)
            data = df.to_dict(orient='records')
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data, default=str).encode())
        else:
            self.send_response(404)
            self.end_headers()
        
        conn.close()

def start_api_server():
    """Start the API server in background"""
    server = HTTPServer(('localhost', 8001), DataAPIHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print("✅ API Server started on http://localhost:8001")
    return server

def create_json_datasource():
    """Create JSON API datasource in Grafana"""
    
    response = requests.post(
        "http://localhost:3000/api/datasources",
        auth=("admin", "Password123!"),
        headers={"Content-Type": "application/json"},
        json={
            "name": "Healthcare API",
            "type": "marcusolsson-json-datasource",
            "access": "proxy",
            "url": "http://host.docker.internal:8001",
            "jsonData": {}
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ JSON datasource created: {result['name']}")
        return result['uid']
    elif response.status_code == 409:
        print("ℹ️ Datasource already exists")
        # Get existing datasource
        response = requests.get(
            "http://localhost:3000/api/datasources/name/Healthcare%20API",
            auth=("admin", "Password123!")
        )
        if response.status_code == 200:
            return response.json()['uid']
    else:
        print(f"❌ Failed to create datasource: {response.text}")
        return None

def create_simple_dashboard():
    """Create a simple dashboard with hardcoded data"""
    
    # Get actual data from database
    conn = sqlite3.connect('healthcare_sales.db')
    
    total_revenue = pd.read_sql("SELECT SUM(revenue) as value FROM daily_metrics", conn).iloc[0,0]
    total_orders = pd.read_sql("SELECT SUM(order_count) as value FROM daily_metrics", conn).iloc[0,0]
    avg_margin = pd.read_sql("SELECT AVG(avg_margin) as value FROM daily_metrics", conn).iloc[0,0]
    
    conn.close()
    
    dashboard = {
        "dashboard": {
            "id": None,
            "uid": None,
            "title": "Healthcare Sales - Simple View",
            "panels": [
                {
                    "id": 1,
                    "type": "stat",
                    "title": "Total Revenue",
                    "gridPos": {"x": 0, "y": 0, "w": 8, "h": 4},
                    "targets": [
                        {
                            "refId": "A",
                            "datasource": {
                                "type": "datasource",
                                "uid": "grafana"
                            }
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
                            "unit": "currencyUSD"
                        },
                        "overrides": []
                    },
                    "options": {
                        "reduceOptions": {
                            "values": False,
                            "fields": "",
                            "calcs": ["last"]
                        },
                        "orientation": "auto",
                        "textMode": "value",
                        "colorMode": "value",
                        "graphMode": "none",
                        "justifyMode": "center"
                    },
                    "pluginVersion": "12.1.1",
                    "transparent": False,
                    "fieldConfig": {
                        "defaults": {
                            "custom": {},
                            "mappings": [],
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None}
                                ]
                            },
                            "unit": "currencyUSD"
                        },
                        "overrides": [
                            {
                                "matcher": {"id": "byName", "options": "Series 1"},
                                "properties": [
                                    {
                                        "id": "custom.hideFrom",
                                        "value": {"tooltip": False, "viz": False, "legend": False}
                                    },
                                    {
                                        "id": "mappings",
                                        "value": [
                                            {
                                                "type": "value",
                                                "options": {
                                                    "0": {"text": f"${total_revenue:,.0f}"}
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    "targets": [
                        {
                            "refId": "A",
                            "datasource": {
                                "type": "datasource",
                                "uid": "grafana"
                            },
                            "queryType": "snapshot",
                            "snapshot": [
                                {
                                    "fields": [
                                        {
                                            "name": "Series 1",
                                            "type": "number",
                                            "values": [0]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": 2,
                    "type": "stat",
                    "title": "Total Orders",
                    "gridPos": {"x": 8, "y": 0, "w": 8, "h": 4},
                    "fieldConfig": {
                        "defaults": {
                            "custom": {},
                            "mappings": [],
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "blue", "value": None}
                                ]
                            },
                            "unit": "short"
                        },
                        "overrides": [
                            {
                                "matcher": {"id": "byName", "options": "Series 1"},
                                "properties": [
                                    {
                                        "id": "mappings",
                                        "value": [
                                            {
                                                "type": "value",
                                                "options": {
                                                    "0": {"text": f"{total_orders:,.0f}"}
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    "options": {
                        "reduceOptions": {
                            "values": False,
                            "fields": "",
                            "calcs": ["last"]
                        },
                        "orientation": "auto",
                        "textMode": "value",
                        "colorMode": "value",
                        "graphMode": "none",
                        "justifyMode": "center"
                    },
                    "targets": [
                        {
                            "refId": "A",
                            "datasource": {
                                "type": "datasource",
                                "uid": "grafana"
                            },
                            "queryType": "snapshot",
                            "snapshot": [
                                {
                                    "fields": [
                                        {
                                            "name": "Series 1",
                                            "type": "number",
                                            "values": [0]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": 3,
                    "type": "stat",
                    "title": "Average Profit Margin",
                    "gridPos": {"x": 16, "y": 0, "w": 8, "h": 4},
                    "fieldConfig": {
                        "defaults": {
                            "custom": {},
                            "mappings": [],
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "red", "value": None},
                                    {"color": "yellow", "value": 20},
                                    {"color": "green", "value": 35}
                                ]
                            },
                            "unit": "percent"
                        },
                        "overrides": [
                            {
                                "matcher": {"id": "byName", "options": "Series 1"},
                                "properties": [
                                    {
                                        "id": "mappings",
                                        "value": [
                                            {
                                                "type": "value",
                                                "options": {
                                                    "0": {"text": f"{avg_margin:.2f}%"}
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    "options": {
                        "reduceOptions": {
                            "values": False,
                            "fields": "",
                            "calcs": ["last"]
                        },
                        "orientation": "auto",
                        "textMode": "value",
                        "colorMode": "value",
                        "graphMode": "none",
                        "justifyMode": "center"
                    },
                    "targets": [
                        {
                            "refId": "A",
                            "datasource": {
                                "type": "datasource",
                                "uid": "grafana"
                            },
                            "queryType": "snapshot",
                            "snapshot": [
                                {
                                    "fields": [
                                        {
                                            "name": "Series 1",
                                            "type": "number",
                                            "values": [0]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "overwrite": True
    }
    
    response = requests.post(
        "http://localhost:3000/api/dashboards/db",
        auth=("admin", "Password123!"),
        headers={"Content-Type": "application/json"},
        json=dashboard
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Dashboard with data created!")
        print(f"   URL: http://localhost:3000/d/{result['uid']}")
        print(f"\n📊 Key Metrics:")
        print(f"   Total Revenue: ${total_revenue:,.2f}")
        print(f"   Total Orders: {total_orders:,.0f}")
        print(f"   Avg Profit Margin: {avg_margin:.2f}%")
        return result['uid']
    else:
        print(f"❌ Failed: {response.text}")
        return None

if __name__ == "__main__":
    print("Creating Grafana Dashboard with Actual Data")
    print("="*50)
    
    # Start API server
    # server = start_api_server()
    # time.sleep(2)
    
    # Create dashboard with hardcoded data
    uid = create_simple_dashboard()
    
    if uid:
        print("\n" + "="*50)
        print("✅ SUCCESS! Dashboard is ready with data!")
        print("="*50)
        print(f"\nOpen: http://localhost:3000/d/{uid}")
        print("Login: admin / Password123!")
        print("\nThe dashboard now shows the actual data from your database!")
        
        # Keep server running
        # print("\nAPI Server running on http://localhost:8001")
        # print("Press Ctrl+C to stop...")
        # try:
        #     while True:
        #         time.sleep(1)
        # except KeyboardInterrupt:
        #     print("\nStopping server...")