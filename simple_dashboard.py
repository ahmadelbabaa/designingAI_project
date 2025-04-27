#!/usr/bin/env python3
"""
Simple HPC Dashboard for Local Testing
Provides a simplified version of the HPC dashboard for local development and testing
"""

import os
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import folium
from folium import plugins
import json
import webbrowser
import time_series_forecasting as tsf

print("===== HPC Simplified Dashboard =====")

# Create necessary folders
folders = ['data', 'config', 'output']
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Created folder: {folder}")

# Station features for synthetic data
LOCATION_FEATURES = {
    'population_density': {'min': 500, 'max': 10000},
    'avg_income': {'min': 30000, 'max': 150000},
    'traffic_volume': {'min': 1000, 'max': 50000},
    'commercial_properties': {'min': 5, 'max': 100},
    'ev_ownership': {'min': 0.01, 'max': 0.25}
}

# EV adoption projection (synthetic)
EV_ADOPTION_PROJECTIONS = {
    '2023': 0.05,
    '2024': 0.08,
    '2025': 0.12,
    '2026': 0.18,
    '2027': 0.25,
    '2028': 0.35,
    '2029': 0.45,
    '2030': 0.55
}

# Weights for viability calculation
VIABILITY_WEIGHTS = {
    'population_density': 0.2,
    'avg_income': 0.15,
    'traffic_volume': 0.25,
    'commercial_properties': 0.15,
    'ev_ownership': 0.25
}

def generate_gas_stations(num_stations=50, save=True):
    """
    Generate synthetic gas station data for analysis
    
    Args:
        num_stations (int): Number of gas stations to generate
        save (bool): Whether to save the generated data
        
    Returns:
        pd.DataFrame: DataFrame with generated gas station data
    """
    # Generate gas stations in Continental US (roughly)
    stations = []
    for i in range(num_stations):
        station_id = f"GS-{i+1:04d}"
        
        # Generate random location (Continental US)
        lat = random.uniform(30, 48)
        lon = random.uniform(-122, -71)
        
        # Generate random features
        features = {}
        for feature, limits in LOCATION_FEATURES.items():
            features[feature] = random.uniform(limits['min'], limits['max'])
        
        # Calculate viability score (0-100)
        viability_score = 0
        for feature, weight in VIABILITY_WEIGHTS.items():
            # Normalize feature value (0-1)
            min_val = LOCATION_FEATURES[feature]['min']
            max_val = LOCATION_FEATURES[feature]['max']
            normalized_value = (features[feature] - min_val) / (max_val - min_val)
            viability_score += normalized_value * weight * 100
        
        # Add some random variation to viability
        viability_score = min(100, max(0, viability_score + random.uniform(-10, 10)))
        
        # Calculate ROI based on viability (with some random variation)
        roi = viability_score / 5 + random.uniform(-3, 3)
        
        # Create station data
        station = {
            'station_id': station_id,
            'latitude': lat,
            'longitude': lon,
            'viability_score': round(viability_score, 1),
            'roi_percent': round(roi, 1),
            'population_density': round(features['population_density']),
            'avg_income': round(features['avg_income']),
            'traffic_volume': round(features['traffic_volume']),
            'commercial_properties': round(features['commercial_properties']),
            'ev_ownership': round(features['ev_ownership'], 3),
        }
        
        stations.append(station)
    
    # Create DataFrame
    df = pd.DataFrame(stations)
    
    # Save to CSV and JSON if requested
    if save:
        df.to_csv('data/synthetic_gas_stations.csv', index=False)
        df.to_json('data/synthetic_gas_stations.json', orient='records')
    
    return df

def create_map(stations_df):
    """
    Create a folium map with station markers
    
    Args:
        stations_df (pd.DataFrame): DataFrame with station data
        
    Returns:
        folium.Map: Map with station markers
    """
    # Calculate center of map
    center_lat = stations_df['latitude'].mean()
    center_lon = stations_df['longitude'].mean()
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
    # Add station markers
    for _, station in stations_df.iterrows():
        # Determine color based on viability score
        if station['viability_score'] >= 75:
            color = 'green'
        elif station['viability_score'] >= 50:
            color = 'blue'
        elif station['viability_score'] >= 25:
            color = 'orange'
        else:
            color = 'red'
        
        # Create popup content
        popup_content = f"""
        <h4>Station {station['station_id']}</h4>
        <b>Viability Score:</b> {station['viability_score']}<br>
        <b>ROI:</b> {station['roi_percent']}%<br>
        <b>Population Density:</b> {station['population_density']}<br>
        <b>Avg Income:</b> ${station['avg_income']:,.0f}<br>
        <b>Traffic Volume:</b> {station['traffic_volume']}<br>
        <b>Commercial Properties:</b> {station['commercial_properties']}<br>
        <b>EV Ownership:</b> {station['ev_ownership'] * 100:.1f}%
        """
        
        # Add marker
        folium.Marker(
            location=[station['latitude'], station['longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color=color, icon='gas-pump', prefix='fa'),
            tooltip=f"Station {station['station_id']} (Score: {station['viability_score']})"
        ).add_to(m)
    
    # Save map
    m.save('output/station_map.html')
    
    return m

def create_heatmap(stations_df):
    """
    Create a heatmap of EV ownership
    
    Args:
        stations_df (pd.DataFrame): DataFrame with station data
        
    Returns:
        folium.Map: Map with heatmap
    """
    # Calculate center of map
    center_lat = stations_df['latitude'].mean()
    center_lon = stations_df['longitude'].mean()
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
    # Prepare heatmap data (lat, lon, weight)
    heatmap_data = []
    for _, station in stations_df.iterrows():
        heatmap_data.append([
            station['latitude'], 
            station['longitude'], 
            station['ev_ownership']  # Use EV ownership as weight
        ])
    
    # Add heatmap layer
    plugins.HeatMap(heatmap_data).add_to(m)
    
    # Save map
    m.save('output/ev_adoption_heatmap.html')
    
    return m

def calculate_dashboard_stats(stations_df):
    """
    Calculate summary statistics for dashboard
    
    Args:
        stations_df (pd.DataFrame): DataFrame with station data
        
    Returns:
        dict: Dictionary with calculated statistics
    """
    stats = {
        'total_stations': len(stations_df),
        'avg_viability': round(stations_df['viability_score'].mean(), 1),
        'avg_roi': round(stations_df['roi_percent'].mean(), 1),
        'high_viability_count': len(stations_df[stations_df['viability_score'] >= 70]),
        'low_viability_count': len(stations_df[stations_df['viability_score'] < 30])
    }
    
    return stats

def generate_forecasts(stations_df, top_n=5, forecast_days=90):
    """
    Generate time series forecasts for top stations
    
    Args:
        stations_df (pd.DataFrame): DataFrame with station data
        top_n (int): Number of top stations to forecast
        forecast_days (int): Number of days to forecast
        
    Returns:
        dict: Dictionary with forecast results
    """
    # Get top stations by viability score
    top_stations = stations_df.sort_values('viability_score', ascending=False).head(top_n)
    
    # Generate forecasts
    station_ids = top_stations['station_id'].tolist()
    forecast_results = tsf.generate_multiple_station_forecasts(
        station_ids, 
        forecast_days=forecast_days
    )
    
    # Save forecast data
    forecast_data = {}
    for station_id, (forecast_df, plot_path) in forecast_results.items():
        forecast_data[station_id] = {
            'avg_sessions': round(forecast_df['charging_sessions'].mean(), 1),
            'total_energy': round(forecast_df['energy_delivered_kwh'].sum(), 1),
            'total_revenue': round(forecast_df['revenue_usd'].sum(), 2),
            'plot_path': plot_path
        }
    
    # Save forecast data as JSON
    with open('data/forecast_summary.json', 'w') as f:
        json.dump(
            {
                station_id: {
                    k: v for k, v in data.items() if k != 'plot_path'
                } 
                for station_id, data in forecast_data.items()
            }, 
            f, 
            indent=2
        )
    
    return forecast_results

def create_dashboard_html(stats, forecast_results=None):
    """
    Create dashboard HTML file
    
    Args:
        stats (dict): Dictionary with dashboard statistics
        forecast_results (dict, optional): Dictionary with forecast results
        
    Returns:
        str: Path to saved HTML file
    """
    # HTML template
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HPC Station Conversion Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f5f7fa;
                color: #333;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            header {{
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            h1, h2, h3 {{
                margin-top: 0;
            }}
            .stats-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                flex: 1;
                min-width: 200px;
                text-align: center;
            }}
            .stat-value {{
                font-size: 2rem;
                font-weight: bold;
                margin: 10px 0;
                color: #2980b9;
            }}
            .map-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 30px;
            }}
            .map-card {{
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                flex: 1;
                min-width: 45%;
            }}
            .map-frame {{
                width: 100%;
                height: 500px;
                border: none;
            }}
            .projections-card {{
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
            .projections-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }}
            .projection-item {{
                text-align: center;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }}
            .projection-year {{
                font-weight: bold;
                color: #2c3e50;
            }}
            .projection-value {{
                font-size: 1.2rem;
                color: #2980b9;
                margin-top: 5px;
            }}
            .forecasts-container {{
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>HPC Station Conversion Dashboard</h1>
                <p>Analysis of gas station viability for conversion to High-Power Charging stations</p>
            </header>
            
            <div class="stats-container">
                <div class="stat-card">
                    <h3>Stations Analyzed</h3>
                    <div class="stat-value">{stats['total_stations']}</div>
                </div>
                <div class="stat-card">
                    <h3>Average Viability Score</h3>
                    <div class="stat-value">{stats['avg_viability']}</div>
                </div>
                <div class="stat-card">
                    <h3>Average ROI</h3>
                    <div class="stat-value">{stats['avg_roi']}%</div>
                </div>
                <div class="stat-card">
                    <h3>High Viability Stations</h3>
                    <div class="stat-value">{stats['high_viability_count']}</div>
                </div>
            </div>
            
            <div class="map-container">
                <div class="map-card">
                    <h2>Station Viability Map</h2>
                    <iframe class="map-frame" src="station_map.html"></iframe>
                </div>
                <div class="map-card">
                    <h2>EV Adoption Heatmap</h2>
                    <iframe class="map-frame" src="ev_adoption_heatmap.html"></iframe>
                </div>
            </div>
            
            <div class="projections-card">
                <h2>EV Adoption Projections</h2>
                <p>Projected electric vehicle adoption rates from 2023 to 2030</p>
                <div class="projections-grid">
    """
    
    # Add EV projections
    for year, rate in EV_ADOPTION_PROJECTIONS.items():
        html += f"""
                    <div class="projection-item">
                        <div class="projection-year">{year}</div>
                        <div class="projection-value">{rate * 100:.0f}%</div>
                    </div>
        """
    
    html += """
                </div>
            </div>
    """
    
    # Add forecasts if available
    if forecast_results:
        html += """
            <h2>Station Usage Forecasts</h2>
            <p>Forecasted usage for top stations based on viability scores</p>
            <div class="forecasts-container">
        """
        
        # Add forecast HTML content
        forecast_html = tsf.create_forecast_visualization_html(forecast_results)
        html += forecast_html
        
        html += """
            </div>
        """
    
    # Close HTML
    html += """
        </div>
    </body>
    </html>
    """
    
    # Save HTML to file
    output_path = 'output/dashboard.html'
    with open(output_path, 'w') as f:
        f.write(html)
    
    return output_path

def main():
    """Main function to run the dashboard"""
    print("Starting HPC Station Conversion Dashboard generation...")
    
    # Create necessary folders
    print("Creating necessary folders...")
    os.makedirs('data', exist_ok=True)
    os.makedirs('config', exist_ok=True) 
    os.makedirs('output', exist_ok=True)
    os.makedirs('output/forecasts', exist_ok=True)
    
    # Generate synthetic gas station data
    print("Generating synthetic gas station data...")
    stations_df = generate_gas_stations(num_stations=50)
    print(f"Generated {len(stations_df)} gas stations for analysis")
    
    # Create map with station markers
    print("Creating station map...")
    create_map(stations_df)
    print("Station map created and saved to output/station_map.html")
    
    # Create EV adoption heatmap
    print("Creating EV adoption heatmap...")
    create_heatmap(stations_df)
    print("EV adoption heatmap created and saved to output/ev_adoption_heatmap.html")
    
    # Calculate dashboard statistics
    print("Calculating dashboard statistics...")
    stats = calculate_dashboard_stats(stations_df)
    
    # Generate forecasts for top stations
    print("Generating forecasts for top stations...")
    forecast_results = generate_forecasts(stations_df, top_n=5)
    print(f"Forecasts generated for {len(forecast_results)} stations")
    
    # Create dashboard HTML
    print("Creating dashboard HTML...")
    dashboard_path = create_dashboard_html(stats, forecast_results)
    print(f"Dashboard created and saved to {dashboard_path}")
    
    print("Dashboard generation complete!")
    print(f"Open {dashboard_path} in a web browser to view the dashboard")

if __name__ == "__main__":
    main() 