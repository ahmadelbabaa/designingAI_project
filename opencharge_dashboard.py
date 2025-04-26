#!/usr/bin/env python3
"""
OpenChargeMap Dashboard Visualization

This script creates interactive visualizations for charging station data from OpenChargeMap.
"""

import os
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster, HeatMap
import matplotlib.pyplot as plt
import seaborn as sns
import webbrowser

from opencharge_integration import load_multiple_regions, fetch_charging_stations_batch

def create_station_map(df, output_file="output/charging_stations_map.html"):
    """
    Create an interactive map of charging stations.
    
    Args:
        df (pandas.DataFrame): DataFrame with charging station data
        output_file (str): Output HTML file path
        
    Returns:
        str: Path to output file
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Determine map center
    center_lat = df['latitude'].mean()
    center_lng = df['longitude'].mean()
    
    # Create map
    m = folium.Map(location=[center_lat, center_lng], zoom_start=5)
    
    # Create marker clusters
    marker_cluster = MarkerCluster().add_to(m)
    
    # Define power level colors
    def get_power_color(power_kw):
        if power_kw >= 150:
            return 'red'       # Ultra-fast charging
        elif power_kw >= 50:
            return 'orange'    # Fast charging
        elif power_kw >= 22:
            return 'blue'      # Standard charging
        else:
            return 'green'     # Slow charging
    
    # Add markers for each station
    for _, row in df.iterrows():
        popup_text = f"""
        <b>{row['name']}</b><br>
        Power: {row['power_kw']} kW<br>
        Connectors: {row['connector_types']}<br>
        Operator: {row['operator']}<br>
        Access: {row['access_type']}<br>
        Status: {row['status']}<br>
        Address: {row['address']}, {row['city']}, {row['state']} {row['postcode']}<br>
        """
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_text,
            tooltip=f"{row['name']} ({row['power_kw']} kW)",
            icon=folium.Icon(color=get_power_color(row['power_kw']))
        ).add_to(marker_cluster)
    
    # Add legend
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; width: 200px; z-index: 1000; font-size: 14px; background-color: white; padding: 10px; border: 1px solid grey;">
    <p><b>Power Levels</b></p>
    <p><i class="fa fa-circle" style="color:red"></i> Ultra-fast (150+ kW)</p>
    <p><i class="fa fa-circle" style="color:orange"></i> Fast (50-149 kW)</p>
    <p><i class="fa fa-circle" style="color:blue"></i> Standard (22-49 kW)</p>
    <p><i class="fa fa-circle" style="color:green"></i> Slow (< 22 kW)</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save map
    m.save(output_file)
    
    return output_file

def create_heatmap(df, output_file="output/charging_stations_heatmap.html"):
    """
    Create a heatmap visualization of charging station density.
    
    Args:
        df (pandas.DataFrame): DataFrame with charging station data
        output_file (str): Output HTML file path
        
    Returns:
        str: Path to output file
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Determine map center
    center_lat = df['latitude'].mean()
    center_lng = df['longitude'].mean()
    
    # Create map
    m = folium.Map(location=[center_lat, center_lng], zoom_start=5)
    
    # Prepare heatmap data
    heat_data = [[row['latitude'], row['longitude']] for _, row in df.iterrows()]
    
    # Add heatmap layer
    HeatMap(heat_data, radius=15, blur=10).add_to(m)
    
    # Save map
    m.save(output_file)
    
    return output_file

def create_power_distribution_chart(df, output_file="output/power_distribution.png"):
    """
    Create a bar chart showing the distribution of charging power levels.
    
    Args:
        df (pandas.DataFrame): DataFrame with charging station data
        output_file (str): Output image file path
        
    Returns:
        str: Path to output file
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Create power level categories
    df['power_category'] = pd.cut(
        df['power_kw'],
        bins=[0, 22, 50, 150, float('inf')],
        labels=['Slow (<22 kW)', 'Standard (22-49 kW)', 'Fast (50-149 kW)', 'Ultra-fast (150+ kW)']
    )
    
    # Calculate counts
    power_counts = df['power_category'].value_counts().sort_index()
    
    # Set up plot
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=power_counts.index, y=power_counts.values)
    
    # Add percentage labels
    total = power_counts.sum()
    for i, count in enumerate(power_counts.values):
        percentage = count / total * 100
        ax.text(i, count + 5, f"{percentage:.1f}%", ha='center')
    
    # Add labels and title
    plt.title('Distribution of Charging Station Power Levels', fontsize=16)
    plt.ylabel('Number of Stations', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    return output_file

def create_connector_type_chart(df, output_file="output/connector_types.png"):
    """
    Create a bar chart showing the distribution of connector types.
    
    Args:
        df (pandas.DataFrame): DataFrame with charging station data
        output_file (str): Output image file path
        
    Returns:
        str: Path to output file
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Extract all connector types
    all_connectors = []
    for connectors in df['connector_types']:
        if pd.notna(connectors):
            all_connectors.extend([c.strip() for c in connectors.split(',')])
    
    # Count connector types
    connector_counts = pd.Series(all_connectors).value_counts()
    
    # Keep only top 10 connector types
    if len(connector_counts) > 10:
        connector_counts = connector_counts.head(10)
    
    # Set up plot
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x=connector_counts.index, y=connector_counts.values)
    
    # Add labels and title
    plt.title('Most Common Connector Types', fontsize=16)
    plt.ylabel('Number of Connectors', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    
    return output_file

def create_dashboard(output_dir="output"):
    """
    Create a dashboard HTML file with all visualizations.
    
    Args:
        output_dir (str): Output directory
        
    Returns:
        str: Path to output HTML file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define path to dashboard HTML file
    dashboard_file = f"{output_dir}/opencharge_dashboard.html"
    
    # Create dashboard HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenChargeMap Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f7f7f7;
            }
            .header {
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .container {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: center;
            }
            .chart {
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }
            .chart-title {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #2c3e50;
            }
            .map-container {
                height: 600px;
                width: 100%;
                border: none;
                border-radius: 5px;
            }
            .full-width {
                width: 100%;
            }
            .half-width {
                width: calc(50% - 20px);
            }
            @media screen and (max-width: 768px) {
                .half-width {
                    width: 100%;
                }
            }
            img {
                max-width: 100%;
                height: auto;
                display: block;
                margin: 0 auto;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>OpenChargeMap Dashboard</h1>
            <p>Interactive visualization of charging station data</p>
        </div>
        
        <div class="container">
            <div class="chart full-width">
                <div class="chart-title">Charging Station Map</div>
                <iframe class="map-container" src="charging_stations_map.html"></iframe>
            </div>
            
            <div class="chart full-width">
                <div class="chart-title">Charging Station Density Heatmap</div>
                <iframe class="map-container" src="charging_stations_heatmap.html"></iframe>
            </div>
            
            <div class="chart half-width">
                <div class="chart-title">Power Level Distribution</div>
                <img src="power_distribution.png" alt="Power Level Distribution">
            </div>
            
            <div class="chart half-width">
                <div class="chart-title">Connector Types</div>
                <img src="connector_types.png" alt="Connector Types">
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(dashboard_file, 'w') as f:
        f.write(html_content)
    
    return dashboard_file

def main():
    """
    Main function to generate the OpenChargeMap dashboard.
    """
    print("=== OpenChargeMap Dashboard Generator ===")
    
    # Define cities for data collection
    cities = [
        {"name": "New York", "latitude": 40.7128, "longitude": -74.0060, "country_code": "US"},
        {"name": "Los Angeles", "latitude": 34.0522, "longitude": -118.2437, "country_code": "US"},
        {"name": "Chicago", "latitude": 41.8781, "longitude": -87.6298, "country_code": "US"},
        {"name": "London", "latitude": 51.5074, "longitude": -0.1278, "country_code": "GB"},
        {"name": "Paris", "latitude": 48.8566, "longitude": 2.3522, "country_code": "FR"},
    ]
    
    # Check if data already exists, otherwise fetch it
    data_dir = "data/charging_stations"
    city_names = [city["name"] for city in cities]
    
    all_exist = True
    for city in city_names:
        file_path = f"{data_dir}/{city.lower().replace(' ', '_')}.csv"
        if not os.path.exists(file_path):
            all_exist = False
            break
    
    if not all_exist:
        print("Fetching charging station data...")
        fetch_charging_stations_batch(cities, output_dir=data_dir)
    
    # Load data
    print("Loading charging station data...")
    df = load_multiple_regions(city_names, data_dir=data_dir)
    
    if df is None or len(df) == 0:
        print("No data found. Please run the script again with data collection enabled.")
        return
    
    print(f"Loaded {len(df)} charging stations from {len(city_names)} cities.")
    
    # Create visualizations
    print("Creating visualizations...")
    
    create_station_map(df)
    print("Created station map.")
    
    create_heatmap(df)
    print("Created heatmap.")
    
    create_power_distribution_chart(df)
    print("Created power distribution chart.")
    
    create_connector_type_chart(df)
    print("Created connector type chart.")
    
    # Create dashboard
    print("Generating dashboard...")
    dashboard_file = create_dashboard()
    print(f"Dashboard generated at {dashboard_file}")
    
    # Open dashboard in browser
    print("Opening dashboard in browser...")
    webbrowser.open(f"file://{os.path.abspath(dashboard_file)}")

if __name__ == "__main__":
    main() 