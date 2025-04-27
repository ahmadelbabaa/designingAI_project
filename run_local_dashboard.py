#!/usr/bin/env python3
"""
Local test launcher for HPC Dashboard
Includes fallbacks for external APIs and keys
"""

import os
import sys
import json
import yaml
import pandas as pd
import numpy as np
import random
from datetime import datetime
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, HTML

# Suppress warnings
warnings.filterwarnings('ignore')

print("===== HPC Dashboard Local Test =====")

# Create necessary folders
folders = ['data', 'config', 'notebooks', 'scripts']
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Created folder: {folder}")

# ===== STEP 1: Create fallback data =====
print("\n===== Creating fallback data =====")

# Define HPC cost tiers
cost_yaml = """
hpc_tiers:
 - name: HPC_350KW
   capex: 300000
   cable_cooling: 25000
 - name: HPC_1000KW
   capex: 500000
   cable_cooling: 40000

electricity_rate: 0.15
staff_cost_monthly: 1200
maintenance_percent: 0.05
hpc_fee_per_kwh: 0.40
"""

with open("config/hpc_cost_params.yaml", "w") as f:
    f.write(cost_yaml)

with open("config/hpc_cost_params.yaml", "r") as f:
    cost_data = yaml.safe_load(f)
print("Loaded HPC cost config:\n", cost_data)

# Function to create synthetic EV charging data
def create_synthetic_ev_data(prefix, n_rows=1000):
    """
    Create synthetic EV charging data
    """
    # Define possible values
    station_ids = [f"station_{i}" for i in range(1, 51)]
    vehicle_types = ['Tesla Model 3', 'Tesla Model Y', 'Nissan Leaf', 'Chevy Bolt', 'Ford Mustang Mach-E', 
                    'Hyundai Kona Electric', 'Kia EV6', 'Volkswagen ID.4', 'Audi e-tron', 'Rivian R1T']
    connector_types = ['CCS', 'CHAdeMO', 'Tesla Supercharger', 'Type 2']
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 
              'San Antonio', 'San Diego', 'Dallas', 'San Francisco']
    
    # Generate random data
    data = {
        'session_id': [f"session_{i}" for i in range(1, n_rows+1)],
        'station_id': [random.choice(station_ids) for _ in range(n_rows)],
        'vehicle_type': [random.choice(vehicle_types) for _ in range(n_rows)],
        'connector_type': [random.choice(connector_types) for _ in range(n_rows)],
        'start_time': [datetime.now().strftime('%Y-%m-%d %H:%M:%S') for _ in range(n_rows)],
        'duration_minutes': [random.randint(15, 120) for _ in range(n_rows)],
        'energy_kwh': [random.uniform(10, 80) for _ in range(n_rows)],
        'city': [random.choice(cities) for _ in range(n_rows)],
        'latitude': [random.uniform(25, 48) for _ in range(n_rows)],
        'longitude': [random.uniform(-125, -70) for _ in range(n_rows)],
        'temperature_c': [random.uniform(-10, 35) for _ in range(n_rows)],
        'is_weekday': [random.choice([True, False]) for _ in range(n_rows)],
        'hour_of_day': [random.randint(0, 23) for _ in range(n_rows)]
    }
    
    # Add dataset-specific columns
    if prefix == "patterns":
        data['Time of Day'] = [random.choice(['Morning', 'Afternoon', 'Evening', 'Night']) for _ in range(n_rows)]
        data['Day of Week'] = [random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']) for _ in range(n_rows)]
        data['Charging Rate (kW)'] = [random.choice([50, 150, 350]) for _ in range(n_rows)]
        data['Energy Consumed (kWh)'] = data['energy_kwh']  # Duplicate for consistent naming
        data['Charging Duration (hours)'] = [duration/60 for duration in data['duration_minutes']]
    
    return pd.DataFrame(data)

# Create synthetic datasets to replace Kaggle downloads
print("Creating synthetic datasets for EV charging data...")
datasets = [
    ("ev_charging_patterns.csv", "patterns", 1000),
    ("station_data_dataverse.csv", "stations", 800),
    ("EVChargingStationUsage.csv", "usage", 1200)
]

for filename, prefix, rows in datasets:
    filepath = f"data/{filename}"
    df = create_synthetic_ev_data(prefix, rows)
    df.to_csv(filepath, index=False)
    
    # Create sample file
    sample_filepath = filepath.replace(".csv", "_sample.csv")
    sample_size = min(500, rows)
    df_sample = df.sample(n=sample_size, random_state=42)
    df_sample.to_csv(sample_filepath, index=False)
    print(f"Created {filepath} and {sample_filepath}")

# Create dummy TomTom O/D file
tomtom_od = {
    "version": "1.0",
    "timestamp": datetime.now().isoformat(),
    "status": "OK",
    "results": [
        {
            "origin": {"latitude": 40.7128, "longitude": -74.0060},
            "destination": {"latitude": 42.3601, "longitude": -71.0589},
            "flowCount": 12500,
            "averageTravelTime": 14400  # 4 hours in seconds
        },
        {
            "origin": {"latitude": 34.0522, "longitude": -118.2437},
            "destination": {"latitude": 37.7749, "longitude": -122.4194},
            "flowCount": 9800,
            "averageTravelTime": 21600  # 6 hours in seconds
        }
    ]
}

with open("data/tomtom_od.json", "w") as f:
    json.dump(tomtom_od, f)
print("Created dummy TomTom O/D data")

# ===== STEP 2: Create master dataset for analysis =====
print("\n===== Creating master dataset for analysis =====")

# Load the synthetic datasets
df_1 = pd.read_csv("data/ev_charging_patterns_sample.csv")
df_2 = pd.read_csv("data/station_data_dataverse_sample.csv")
df_3 = pd.read_csv("data/EVChargingStationUsage_sample.csv")

# Extract common fields to create a standardized dataset
df_1_std = pd.DataFrame()
df_1_std['energy_kwh'] = df_1['energy_kwh']
if 'Charging Duration (hours)' in df_1.columns:
    df_1_std['duration_hours'] = df_1['Charging Duration (hours)']
if 'Charging Rate (kW)' in df_1.columns:
    df_1_std['charging_rate_kw'] = df_1['Charging Rate (kW)']
if 'Time of Day' in df_1.columns:
    df_1_std['time_of_day'] = df_1['Time of Day']
if 'Day of Week' in df_1.columns:
    df_1_std['day_of_week'] = df_1['Day of Week']
df_1_std['source'] = 'dataset_1'

# Create similar standardized datasets for df_2 and df_3
df_2_std = pd.DataFrame()
df_2_std['energy_kwh'] = df_2['energy_kwh']
df_2_std['source'] = 'dataset_2'

df_3_std = pd.DataFrame()
df_3_std['energy_kwh'] = df_3['energy_kwh']
df_3_std['source'] = 'dataset_3'

# Concatenate the standardized datasets
df_hpc_master = pd.concat([df_1_std, df_2_std, df_3_std], ignore_index=True)
print(f"Master HPC usage shape: {df_hpc_master.shape}")

# Save the master dataset
df_hpc_master.to_csv("data/hpc_usage_master.csv", index=False)
print("Saved merged HPC usage data to data/hpc_usage_master.csv")

# Create a forecast using a simple formula
df_hpc_master['daily_kwh_forecast'] = df_hpc_master['energy_kwh'] * 1.2  # Simple factor
df_hpc_master.to_csv("data/hpc_usage_with_forecast.csv", index=False)
print("Added forecast data and saved to data/hpc_usage_with_forecast.csv")

# ===== STEP 3: Run HPC dashboard =====
print("\n===== Running HPC Dashboard =====")
print("Importing hpc_dashboard module...")

try:
    # Try to import the dashboard module
    import hpc_dashboard
    
    # Run the dashboard
    df = hpc_dashboard.generate_gas_station_data(n_stations=50)
    print(f"Generated {len(df)} gas stations for analysis")
    
    # Create visualizations
    print("Creating dashboard visualizations...")
    hpc_dashboard.create_dashboard_visualizations(df)
    
    # Create maps
    print("Creating interactive maps...")
    station_map = hpc_dashboard.create_interactive_map(df)
    traffic_map = hpc_dashboard.create_traffic_heatmap(df)
    
    # Save maps as HTML
    station_map.save('station_map.html')
    traffic_map.save('traffic_map.html')
    print("Saved interactive maps as HTML files")
    
    # Create the dashboard HTML
    print("Creating dashboard HTML...")
    html_content = hpc_dashboard.create_dashboard_html(df)
    
    print("\n===== Dashboard Ready =====")
    print("You can view the dashboard by opening 'hpc_dashboard.html'")
    
    # Try to open the dashboard in a web browser
    import webbrowser
    webbrowser.open('hpc_dashboard.html')
    
except Exception as e:
    print(f"Error running dashboard: {e}")
    print("Check that all dependencies are installed and the hpc_dashboard.py file is accessible") 