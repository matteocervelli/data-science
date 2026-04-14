#!/usr/bin/env python3
import json
import requests

# Grafana credentials
GRAFANA_URL = "http://localhost:3000"
USERNAME = "admin"
PASSWORD = "Password123!"

def import_dashboard(dashboard_file, title):
    """Import a dashboard to Grafana"""
    
    # Read the dashboard JSON
    with open(dashboard_file, 'r') as f:
        dashboard_json = json.load(f)
    
    # Update datasource references
    for panel in dashboard_json['dashboard'].get('panels', []):
        for target in panel.get('targets', []):
            target['datasource'] = {
                "type": "frser-sqlite-datasource",
                "uid": "bev5d9szs78qod"
            }
            target['refId'] = 'A'
    
    # Add required fields
    dashboard_json['dashboard']['id'] = None
    dashboard_json['dashboard']['uid'] = None
    dashboard_json['overwrite'] = True
    dashboard_json['folderId'] = 0
    
    # Import the dashboard
    response = requests.post(
        f"{GRAFANA_URL}/api/dashboards/db",
        auth=(USERNAME, PASSWORD),
        headers={"Content-Type": "application/json"},
        json=dashboard_json
    )
    
    if response.status_code == 200:
        print(f"✅ Successfully imported: {title}")
        result = response.json()
        print(f"   URL: {GRAFANA_URL}/d/{result['uid']}")
    else:
        print(f"❌ Failed to import {title}: {response.text}")

# Import both dashboards
print("Importing Grafana dashboards...")
import_dashboard('grafana/dashboards/sales_overview.json', 'Healthcare Sales Overview')
import_dashboard('grafana/dashboards/ml_predictions.json', 'ML Predictions & Analytics')

print("\n📊 Access your dashboards at: http://localhost:3000")
print("   Username: admin")
print("   Password: Password123!")