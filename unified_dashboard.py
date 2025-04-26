#!/usr/bin/env python3
"""
Unified HPC Dashboard for HPC Station Conversion Analysis

This script creates a unified dashboard that combines OpenChargeMap data with 
simulated gas station data to provide a comprehensive analysis platform.
"""

import os
import pandas as pd
import numpy as np
import random
from datetime import datetime
import matplotlib.pyplot as plt
import folium
from folium import plugins
from folium.plugins import MarkerCluster, HeatMap
import json
import webbrowser
import seaborn as sns
import time

# Import from existing modules
from opencharge_integration import load_multiple_regions, fetch_charging_stations_batch

# Create necessary folders
folders = ['data', 'config', 'output']
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Created folder: {folder}")

# Function to fetch OpenChargeMap data
def fetch_opencharge_data(force_refresh=False):
    """Fetch charging station data from OpenChargeMap API"""
    print("\n===== Loading OpenChargeMap Data =====")
    
    # Define cities for data collection
    cities = [
        {"name": "New York", "latitude": 40.7128, "longitude": -74.0060, "country_code": "US"},
        {"name": "Los Angeles", "latitude": 34.0522, "longitude": -118.2437, "country_code": "US"},
        {"name": "Chicago", "latitude": 41.8781, "longitude": -87.6298, "country_code": "US"},
        {"name": "London", "latitude": 51.5074, "longitude": -0.1278, "country_code": "GB"},
        {"name": "Berlin", "latitude": 52.5200, "longitude": 13.4050, "country_code": "DE"},
    ]
    
    # Check if data already exists, otherwise fetch it
    data_dir = "data/charging_stations"
    city_names = [city["name"] for city in cities]
    
    all_exist = True
    for city in city_names:
        file_path = f"{data_dir}/{city.lower().replace(' ', '_')}.csv"
        if not os.path.exists(file_path) or force_refresh:
            all_exist = False
            break
    
    if not all_exist:
        print("Fetching charging station data from OpenChargeMap API...")
        fetch_charging_stations_batch(cities, output_dir=data_dir)
    else:
        print("Using cached OpenChargeMap data...")
    
    # Load data
    df = load_multiple_regions(city_names, data_dir=data_dir)
    
    if df is None or len(df) == 0:
        print("No OpenChargeMap data found. Continuing with simulated data only.")
        return None
    
    print(f"Loaded {len(df)} charging stations from {len(city_names)} cities.")
    return df

# Generate synthetic gas station data
def generate_gas_stations(n_stations=50):
    """Generate synthetic gas station data."""
    print("\n===== Generating Synthetic Gas Station Data =====")
    
    # Define major cities with coordinates across the world
    cities = [
        # North America
        {"name": "New York", "lat": 40.7128, "lng": -74.0060, "region": "North America", "ev_adoption_factor": 1.1, 
         "ev_growth_rate": 0.22, "ev_sales_share": 0.08},
        {"name": "Los Angeles", "lat": 34.0522, "lng": -118.2437, "region": "North America", "ev_adoption_factor": 1.3,
         "ev_growth_rate": 0.25, "ev_sales_share": 0.12},
        {"name": "Chicago", "lat": 41.8781, "lng": -87.6298, "region": "North America", "ev_adoption_factor": 0.9,
         "ev_growth_rate": 0.18, "ev_sales_share": 0.06},
        # Shortened city list for simplicity
        {"name": "London", "lat": 51.5074, "lng": -0.1278, "region": "Europe", "ev_adoption_factor": 1.3,
         "ev_growth_rate": 0.30, "ev_sales_share": 0.20},
        {"name": "Berlin", "lat": 52.5200, "lng": 13.4050, "region": "Europe", "ev_adoption_factor": 1.5,
         "ev_growth_rate": 0.33, "ev_sales_share": 0.25},
    ]
    
    # Station names and types
    station_names = ["Shell", "Exxon", "BP", "Chevron", "Mobil"]
    station_types = ["Highway", "Urban", "Suburban", "Rural"]
    
    data = []
    station_id = 1
    
    # Create stations around each city
    for city in cities:
        # For each city, create a few stations
        for i in range(n_stations // len(cities) + 1):
            # Create a random offset to distribute stations around the city
            lat_offset = (random.random() - 0.5) * 0.08
            lng_offset = (random.random() - 0.5) * 0.08
            
            # Calculate new coordinates
            new_lat = city["lat"] + lat_offset
            new_lng = city["lng"] + lng_offset
            
            # Generate random metrics
            traffic_volume = random.randint(1000, 10000)
            ev_adoption_rate = random.randint(5, 25)
            viability_score = random.randint(30, 95)
            roi = random.randint(5, 25)
            
            data.append({
                "id": f"station-{station_id}",
                "name": f"{random.choice(station_names)} {city['name']} {station_id}",
                "latitude": new_lat,
                "longitude": new_lng,
                "city": city["name"],
                "region": city["region"],
                "type": random.choice(station_types),
                "traffic_volume": traffic_volume,
                "ev_adoption_rate": ev_adoption_rate,
                "viability_score": viability_score,
                "roi": roi,
                "payback_period": random.randint(3, 12),
            })
            station_id += 1
    
    df = pd.DataFrame(data)
    print(f"Generated {len(df)} gas stations for analysis")
    
    # Save data to CSV for reference
    df.to_csv("data/gas_stations.csv", index=False)
    print("Saved data to data/gas_stations.csv")
    
    return df

# Create EV adoption forecast
def create_ev_forecast(base_year=2025, forecast_years=5, growth_rates=[5, 10, 15], output_file="output/ev_forecast.png"):
    """Create EV adoption forecast visualization."""
    print("\n===== Creating EV Adoption Forecast =====")
    
    years = list(range(base_year, base_year + forecast_years + 1))

    # Create a figure
    plt.figure(figsize=(12, 8))

    # Plot different growth scenarios
    for rate in growth_rates:
        # Starting from 10% adoption in base year
        adoption = [10]

        # Calculate adoption for each year
        for i in range(1, len(years)):
            adoption.append(adoption[-1] * (1 + rate/100))

        plt.plot(years, adoption, marker='o', linewidth=3, label=f"{rate}% Annual Growth")

    # Add labels and title
    plt.title('EV Adoption Rate Forecast', fontsize=18)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('EV Adoption Rate (%)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)

    # Set y-axis to percentage
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))

    # Save the figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Created EV adoption forecast: {output_file}")
    
    return output_file

# Create a map with station markers
def create_gas_station_map(df, output_file="output/station_map.html"):
    """Create a map with gas station markers colored by viability score."""
    print("\n===== Creating Gas Station Map =====")
    
    # Create a map centered on the world
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    # Define a color function based on viability score
    def get_color(score):
        if score >= 80:
            return 'green'
        elif score >= 60:
            return 'orange'
        elif score >= 40:
            return 'blue'
        else:
            return 'red'
    
    # Create clusters
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers for each gas station
    for _, row in df.iterrows():
        popup_text = (
            f"<b>{row['name']}</b><br>"
            f"Region: {row['region']}<br>"
            f"Type: {row['type']}<br>"
            f"Viability Score: {row['viability_score']}/100<br>"
            f"ROI: {row['roi']}%<br>"
            f"Payback Period: {row['payback_period']} years<br>"
            f"EV Adoption Rate: {row['ev_adoption_rate']}%<br>"
            f"Traffic Volume: {row['traffic_volume']} vehicles/day"
        )
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_text,
            tooltip=f"{row['name']} (Score: {row['viability_score']})",
            icon=folium.Icon(color=get_color(row['viability_score']))
        ).add_to(marker_cluster)
    
    # Add legend
    legend_html = """
    <div style="position: fixed; bottom: 50px; right: 50px; width: 220px; z-index: 1000; font-size: 14px; background-color: white; padding: 10px; border: 1px solid grey; border-radius: 5px;">
    <p><b>Viability Score</b></p>
    <p><i class="fa fa-circle" style="color:green"></i> High (80+)</p>
    <p><i class="fa fa-circle" style="color:orange"></i> Medium (60-79)</p>
    <p><i class="fa fa-circle" style="color:blue"></i> Low (40-59)</p>
    <p><i class="fa fa-circle" style="color:red"></i> Poor (<40)</p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    m.save(output_file)
    print(f"Created gas station map: {output_file}")
    
    return output_file

# Create charging station map
def create_charging_station_map(df, output_file="output/charging_stations_map.html"):
    """Create an interactive map of charging stations."""
    print("\n===== Creating Charging Station Map =====")
    
    # Determine map center
    center_lat = df['latitude'].mean()
    center_lng = df['longitude'].mean()
    
    # Create map
    m = folium.Map(location=[center_lat, center_lng], zoom_start=4)
    
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
    <div style="position: fixed; bottom: 50px; right: 50px; width: 220px; z-index: 1000; font-size: 14px; background-color: white; padding: 10px; border: 1px solid grey; border-radius: 5px;">
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
    print(f"Created charging station map: {output_file}")
    
    return output_file

# Create heatmap
def create_heatmap(df, value_col='ev_adoption_rate', output_file="output/ev_adoption_heatmap.html"):
    """Create a heatmap of EV adoption rates."""
    print("\n===== Creating EV Adoption Heatmap =====")
    
    # Create a map centered on the world
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    # Prepare data points for the heatmap
    heat_data = []
    for _, row in df.iterrows():
        try:
            lat = float(row['latitude'])
            lng = float(row['longitude'])
            weight = float(row[value_col])
            heat_data.append([lat, lng, weight])
        except (ValueError, TypeError) as e:
            print(f"Error processing row: {row['name']} - {e}")
            continue
    
    # Add the heatmap layer to the map
    plugins.HeatMap(heat_data).add_to(m)
    
    # Save the map
    m.save(output_file)
    print(f"Created heatmap: {output_file}")
    
    return output_file

# Create power distribution chart for OpenChargeMap data
def create_power_distribution_chart(df, output_file="output/power_distribution.png"):
    """Create a bar chart showing the distribution of charging power levels."""
    print("\n===== Creating Power Distribution Chart =====")
    
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
    print(f"Created power distribution chart: {output_file}")
    
    return output_file

# Create viability distribution chart for gas stations
def create_viability_chart(df, output_file="output/viability_distribution.png"):
    """Create a bar chart showing the distribution of viability scores."""
    print("\n===== Creating Viability Score Distribution Chart =====")
    
    # Create viability categories
    df['viability_category'] = pd.cut(
        df['viability_score'],
        bins=[0, 40, 60, 80, 100],
        labels=['Poor (<40)', 'Low (40-59)', 'Medium (60-79)', 'High (80+)']
    )
    
    # Calculate counts
    viability_counts = df['viability_category'].value_counts().sort_index()
    
    # Set up plot
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=viability_counts.index, y=viability_counts.values)
    
    # Add percentage labels
    total = viability_counts.sum()
    for i, count in enumerate(viability_counts.values):
        percentage = count / total * 100
        ax.text(i, count + 0.5, f"{percentage:.1f}%", ha='center')
    
    # Add labels and title
    plt.title('Distribution of Gas Station Viability Scores', fontsize=16)
    plt.ylabel('Number of Stations', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Created viability distribution chart: {output_file}")
    
    return output_file

# Add regional analysis and financial calculations
def compute_roi(daily_kwh, power_tier='HPC_350KW'):
    """Compute ROI for HPC stations based on usage."""
    # Default cost parameters if config not available
    cost_params = {
        'hpc_tiers': [
            {
                'name': 'HPC_350KW',
                'capex': 500000,
                'cable_cooling': 50000
            },
            {
                'name': 'HPC_1000KW',
                'capex': 1000000,
                'cable_cooling': 100000
            }
        ],
        'electricity_rate': 0.12,  # cost to buy power
        'hpc_fee_per_kwh': 0.40,   # HPC user pays
        'staff_cost_monthly': 5000,
        'maintenance_percent': 0.05
    }
    
    # Try to load from config if available
    cost_params_path = "config/hpc_cost_params.yaml"
    if os.path.exists(cost_params_path):
        try:
            import yaml
            with open(cost_params_path, "r") as f:
                cost_params = yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading cost parameters: {e}")
    
    # Find matching tier
    tier_config = next((t for t in cost_params['hpc_tiers'] if t['name'] == power_tier), cost_params['hpc_tiers'][0])

    capex = tier_config['capex'] + tier_config['cable_cooling']
    elec_rate = cost_params['electricity_rate']  # cost to buy power
    fee_kwh = cost_params['hpc_fee_per_kwh']     # HPC user pays
    staff_monthly = cost_params['staff_cost_monthly']
    maint_percent = cost_params['maintenance_percent']

    # Daily revenue
    daily_revenue = daily_kwh * fee_kwh
    # Daily electricity cost
    daily_cost = daily_kwh * elec_rate

    # Approximate daily staff & maintenance
    daily_staff = staff_monthly / 30.0
    daily_maintenance = maint_percent * capex / 365.0

    daily_net = daily_revenue - (daily_cost + daily_staff + daily_maintenance)
    annual_net = daily_net * 365

    # ROI percentage
    roi_percent = (annual_net / capex) * 100
    
    # Payback period
    payback = capex / (annual_net if annual_net > 0 else 1e-9)

    return {
        'daily_revenue': daily_revenue,
        'daily_cost': daily_cost,
        'daily_staff': daily_staff,
        'daily_maintenance': daily_maintenance,
        'daily_net': daily_net,
        'annual_net': annual_net,
        'roi_percent': roi_percent,
        'payback_years': payback
    }

# Create regional analysis
def create_regional_analysis(df, output_file="output/regional_analysis.png"):
    """Create regional analysis visualizations."""
    print("\n===== Creating Regional Analysis =====")
    
    if 'region' not in df.columns:
        print("No region data available for analysis")
        return None
    
    # Create a figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    
    # Set the style
    plt.style.use('ggplot')
    
    # Color palette for regions
    region_colors = {
        'North America': '#00A67D',  # Primary green
        'Europe': '#0cc0df',        # Secondary blue
        'Asia': '#f7b733',          # Accent yellow
        'Other': '#e74c3c'          # Red
    }
    
    # 1. Station Distribution by Region (top left)
    region_counts = df['region'].value_counts()
    axes[0, 0].bar(region_counts.index, region_counts.values, color=[region_colors.get(r, '#888888') for r in region_counts.index])
    axes[0, 0].set_title('Station Distribution by Region', fontsize=16)
    axes[0, 0].set_ylabel('Number of Stations', fontsize=14)
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Add count labels
    for i, count in enumerate(region_counts.values):
        axes[0, 0].text(i, count + 0.5, str(count), ha='center', fontweight='bold')
    
    # 2. Average Viability Score by Region (top right)
    if 'viability_score' in df.columns:
        region_viability = df.groupby('region')['viability_score'].mean().sort_values(ascending=False)
        axes[0, 1].bar(region_viability.index, region_viability.values, color=[region_colors.get(r, '#888888') for r in region_viability.index])
        axes[0, 1].set_title('Average Viability Score by Region', fontsize=16)
        axes[0, 1].set_ylabel('Average Viability Score', fontsize=14)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Add score labels
        for i, score in enumerate(region_viability.values):
            axes[0, 1].text(i, score + 1, f"{score:.1f}", ha='center', fontweight='bold')
    
    # 3. EV Adoption Rate by Region (bottom left)
    if 'ev_adoption_rate' in df.columns:
        region_ev_adoption = df.groupby('region')['ev_adoption_rate'].mean().sort_values(ascending=False)
        axes[1, 0].bar(region_ev_adoption.index, region_ev_adoption.values, color=[region_colors.get(r, '#888888') for r in region_ev_adoption.index])
        axes[1, 0].set_title('Average EV Adoption Rate by Region', fontsize=16)
        axes[1, 0].set_ylabel('EV Adoption Rate (%)', fontsize=14)
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Add percentage labels
        for i, rate in enumerate(region_ev_adoption.values):
            axes[1, 0].text(i, rate + 0.5, f"{rate:.1f}%", ha='center', fontweight='bold')
    
    # 4. ROI by Region (bottom right)
    if 'roi' in df.columns:
        region_roi = df.groupby('region')['roi'].mean().sort_values(ascending=False)
        axes[1, 1].bar(region_roi.index, region_roi.values, color=[region_colors.get(r, '#888888') for r in region_roi.index])
        axes[1, 1].set_title('Average ROI by Region', fontsize=16)
        axes[1, 1].set_ylabel('ROI (%)', fontsize=14)
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        # Add percentage labels
        for i, roi in enumerate(region_roi.values):
            axes[1, 1].text(i, roi + 0.5, f"{roi:.1f}%", ha='center', fontweight='bold')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Created regional analysis chart: {output_file}")
    
    return output_file

# Create competitor analysis
def create_competitor_analysis(df, output_file="output/competitor_analysis.png"):
    """Create competitor analysis visualization showing the impact of nearby competitors."""
    print("\n===== Creating Competitor Analysis =====")
    
    # Simulate competitor data if not available
    if 'competitor_nearby' not in df.columns:
        df['competitor_nearby'] = np.random.choice([True, False], size=len(df))
    
    # Apply competitor usage factor
    competitor_usage_factor = 0.2  # if competitor HPC is within 3 km, reduce usage by 20%
    
    if 'ev_adoption_rate' in df.columns:
        df['adjusted_adoption'] = df.apply(
            lambda r: r['ev_adoption_rate'] * (1 - competitor_usage_factor)
            if r['competitor_nearby'] else r['ev_adoption_rate'],
            axis=1
        )

    if 'roi' in df.columns:
        df['adjusted_roi'] = df.apply(
            lambda r: r['roi'] * (1 - competitor_usage_factor)
            if r['competitor_nearby'] else r['roi'],
            axis=1
        )
    
    # Create comparison figure
    plt.figure(figsize=(14, 8))
    
    # Set up the axes
    ax1 = plt.subplot(1, 2, 1)
    ax2 = plt.subplot(1, 2, 2)
    
    # Plot the EV adoption rate comparison
    if 'adjusted_adoption' in df.columns:
        data = {
            'Original': df['ev_adoption_rate'].mean(),
            'With Competition': df['adjusted_adoption'].mean()
        }
        ax1.bar(data.keys(), data.values(), color=['#00A67D', '#5ED9B9'])
        ax1.set_title('Impact of Competition on EV Adoption', fontsize=16)
        ax1.set_ylabel('Average EV Adoption Rate (%)', fontsize=14)
        
        # Add percentage labels
        for i, (k, v) in enumerate(data.items()):
            ax1.text(i, v + 0.5, f"{v:.1f}%", ha='center', fontweight='bold')
    
    # Plot the ROI comparison
    if 'adjusted_roi' in df.columns:
        data = {
            'Original': df['roi'].mean(),
            'With Competition': df['adjusted_roi'].mean()
        }
        ax2.bar(data.keys(), data.values(), color=['#00A67D', '#5ED9B9'])
        ax2.set_title('Impact of Competition on ROI', fontsize=16)
        ax2.set_ylabel('Average ROI (%)', fontsize=14)
        
        # Add percentage labels
        for i, (k, v) in enumerate(data.items()):
            ax2.text(i, v + 0.5, f"{v:.1f}%", ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Created competitor analysis chart: {output_file}")
    
    return output_file

# Create solar potential analysis
def create_solar_analysis(df, output_file="output/solar_potential.png"):
    """Create solar potential visualization."""
    print("\n===== Creating Solar Potential Analysis =====")
    
    # Generate solar potential data if not available
    if 'solar_potential' not in df.columns:
        df['solar_potential'] = np.random.uniform(50, 200, size=len(df))
        df['solar_installation_cost'] = df['solar_potential'] * 1000
        df['solar_annual_savings'] = df['solar_potential'] * 365 * 0.15
        df['solar_roi'] = (df['solar_annual_savings'] / df['solar_installation_cost']) * 100
        df['solar_payback'] = df['solar_installation_cost'] / df['solar_annual_savings']
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Solar Potential Distribution (top left)
    if 'solar_potential' in df.columns:
        axes[0, 0].hist(df['solar_potential'], bins=10, color='#00A67D', alpha=0.7)
        axes[0, 0].set_title('Solar Potential Distribution', fontsize=16)
        axes[0, 0].set_xlabel('Daily Solar Potential (kWh)', fontsize=14)
        axes[0, 0].set_ylabel('Number of Stations', fontsize=14)
    
    # 2. Solar ROI (top right)
    if 'solar_roi' in df.columns:
        axes[0, 1].hist(df['solar_roi'], bins=10, color='#00A67D', alpha=0.7)
        axes[0, 1].set_title('Solar ROI Distribution', fontsize=16)
        axes[0, 1].set_xlabel('Solar ROI (%)', fontsize=14)
        axes[0, 1].set_ylabel('Number of Stations', fontsize=14)
    
    # 3. Solar Savings Distribution (bottom left)
    if 'solar_annual_savings' in df.columns:
        axes[1, 0].hist(df['solar_annual_savings'], bins=10, color='#00A67D', alpha=0.7)
        axes[1, 0].set_title('Annual Solar Savings Distribution', fontsize=16)
        axes[1, 0].set_xlabel('Annual Solar Savings ($)', fontsize=14)
        axes[1, 0].set_ylabel('Number of Stations', fontsize=14)
    
    # 4. Solar Payback Period (bottom right)
    if 'solar_payback' in df.columns:
        valid_payback = df['solar_payback'][df['solar_payback'] < 30]
        axes[1, 1].hist(valid_payback, bins=10, color='#00A67D', alpha=0.7)
        axes[1, 1].set_title('Solar Payback Period Distribution', fontsize=16)
        axes[1, 1].set_xlabel('Payback Period (years)', fontsize=14)
        axes[1, 1].set_ylabel('Number of Stations', fontsize=14)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Created solar potential analysis chart: {output_file}")
    
    return output_file

# Create traffic analysis
def create_traffic_analysis(df, output_file="output/traffic_analysis.png"):
    """Create traffic analysis visualization."""
    print("\n===== Creating Traffic Analysis =====")
    
    # Generate traffic data if not available
    if 'traffic_volume' not in df.columns:
        df['traffic_volume'] = np.random.randint(1000, 10000, size=len(df))
    
    # Create figure
    plt.figure(figsize=(10, 6))
    
    # Create traffic volume distribution
    plt.hist(df['traffic_volume'], bins=15, color='#00A67D', alpha=0.7)
    plt.title('Traffic Volume Distribution', fontsize=16)
    plt.xlabel('Daily Traffic Volume (vehicles)', fontsize=14)
    plt.ylabel('Number of Stations', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Created traffic analysis chart: {output_file}")
    
    return output_file

# Create unified dashboard HTML
def create_unified_dashboard(
    charging_stations_df=None,
    gas_stations_df=None,
    charging_map_file="output/charging_stations_map.html",
    station_map_file="output/station_map.html",
    heatmap_file="output/ev_adoption_heatmap.html",
    power_chart_file="output/power_distribution.png",
    viability_chart_file="output/viability_distribution.png",
    ev_forecast_file="output/ev_forecast.png",
    regional_analysis_file="output/regional_analysis.png",
    competitor_analysis_file="output/competitor_analysis.png",
    solar_analysis_file="output/solar_potential.png",
    traffic_analysis_file="output/traffic_analysis.png",
    output_file="output/unified_dashboard.html"
):
    """Create a unified dashboard HTML file integrating all visualizations."""
    print("\n===== Creating Unified Dashboard =====")
    
    # Extract just the filenames without paths for iframe src
    charging_map_filename = os.path.basename(charging_map_file)
    station_map_filename = os.path.basename(station_map_file)
    heatmap_filename = os.path.basename(heatmap_file)
    power_chart_filename = os.path.basename(power_chart_file)
    viability_chart_filename = os.path.basename(viability_chart_file)
    ev_forecast_filename = os.path.basename(ev_forecast_file)
    regional_analysis_filename = os.path.basename(regional_analysis_file) if regional_analysis_file else None
    competitor_analysis_filename = os.path.basename(competitor_analysis_file) if competitor_analysis_file else None
    solar_analysis_filename = os.path.basename(solar_analysis_file) if solar_analysis_file else None
    traffic_analysis_filename = os.path.basename(traffic_analysis_file) if traffic_analysis_file else None
    
    # Calculate summary statistics
    stats = {
        "charging_stations": 0,
        "gas_stations": 0,
        "avg_viability": 0,
        "avg_roi": 0,
        "high_viability_count": 0,
        "regions": 0
    }
    
    if gas_stations_df is not None:
        stats["gas_stations"] = len(gas_stations_df)
        stats["avg_viability"] = gas_stations_df['viability_score'].mean()
        stats["avg_roi"] = gas_stations_df['roi'].mean()
        stats["high_viability_count"] = sum(gas_stations_df['viability_score'] >= 70)
        if 'region' in gas_stations_df.columns:
            stats["regions"] = len(gas_stations_df['region'].unique())
    
    if charging_stations_df is not None:
        stats["charging_stations"] = len(charging_stations_df)
    
    # Add regional analysis sections to HTML
    regional_section = ""
    if regional_analysis_filename:
        regional_section = f"""
        <div class="section">
            <h2>Regional Analysis</h2>
            <div class="chart-row">
                <div class="chart-container">
                    <div class="chart-title">Regional Distribution & Performance</div>
                    <img class="chart-img" src="{regional_analysis_filename}" alt="Regional Analysis">
                </div>
            </div>
        </div>
        """
    
    # Add competitor and ROI analysis sections to HTML
    competitor_section = ""
    if competitor_analysis_filename:
        competitor_section = f"""
        <div class="section">
            <h2>Competition & ROI Analysis</h2>
            <div class="chart-row">
                <div class="chart-container">
                    <div class="chart-title">Impact of Competition</div>
                    <img class="chart-img" src="{competitor_analysis_filename}" alt="Competitor Analysis">
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Traffic Volume Distribution</div>
                    <img class="chart-img" src="{traffic_analysis_filename}" alt="Traffic Analysis">
                </div>
            </div>
        </div>
        """
    
    # Add sustainability/solar analysis section to HTML
    sustainability_section = ""
    if solar_analysis_filename:
        sustainability_section = f"""
        <div class="section">
            <h2>Sustainability & Solar Integration</h2>
            <div class="chart-row">
                <div class="chart-container">
                    <div class="chart-title">Solar Potential Analysis</div>
                    <img class="chart-img" src="{solar_analysis_filename}" alt="Solar Analysis">
                </div>
            </div>
        </div>
        """
    
    # Update the stats container to include region count
    stats_html = f"""
    <div class="stats-container">
        <div class="stat-card">
            <h3>Charging Stations</h3>
            <div class="stat-value">{stats['charging_stations']}</div>
            <div>existing stations</div>
        </div>
        <div class="stat-card">
            <h3>Gas Stations Analyzed</h3>
            <div class="stat-value">{stats['gas_stations']}</div>
            <div>potential HPC locations</div>
        </div>
        <div class="stat-card">
            <h3>Regions Covered</h3>
            <div class="stat-value">{stats['regions']}</div>
            <div>geographical areas</div>
        </div>
        <div class="stat-card">
            <h3>Average Viability Score</h3>
            <div class="stat-value">{stats['avg_viability']:.1f}</div>
            <div>out of 100</div>
        </div>
        <div class="stat-card">
            <h3>Average ROI</h3>
            <div class="stat-value">{stats['avg_roi']:.1f}%</div>
            <div>annual return</div>
        </div>
        <div class="stat-card">
            <h3>High Viability Stations</h3>
            <div class="stat-value">{stats['high_viability_count']}</div>
            <div>score >= 70</div>
        </div>
    </div>
    """
    
    # Create HTML content with iframe for maps and charts
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HPC Station Conversion Analysis Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary-color: #00A67D;
                --primary-light: #5ED9B9;
                --primary-dark: #007559;
                --secondary-color: #3498db;
                --accent-color: #67de91;
                --dark-bg: #0F1720;
                --dark-card: #1a2635;
                --light-bg: #f0f7f4;
                --text-light: #ffffff;
                --text-light-secondary: rgba(255, 255, 255, 0.7);
                --text-dark: #2c3e50;
                --border-color: rgba(0, 166, 125, 0.2);
                --card-bg: rgba(0, 166, 125, 0.05);
                --success-color: #00A67D;
                --warning-color: #f39c12;
                --danger-color: #e74c3c;
            }}
            
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 0;
                background-color: var(--dark-bg);
                color: var(--text-light);
                overflow-x: hidden;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1800px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .dashboard-header {{
                background: linear-gradient(135deg, var(--primary-dark), var(--primary-color));
                color: white;
                padding: 40px;
                border-radius: 16px;
                margin-bottom: 30px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0, 166, 125, 0.2);
                position: relative;
                overflow: hidden;
            }}
            
            .dashboard-header::before {{
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><path d="M0 0 L50 0 L0 50 Z" fill="rgba(255,255,255,0.05)"/><path d="M100 0 L100 50 L50 0 Z" fill="rgba(255,255,255,0.05)"/><path d="M0 100 L0 50 L50 100 Z" fill="rgba(255,255,255,0.05)"/><path d="M100 100 L50 100 L100 50 Z" fill="rgba(255,255,255,0.05)"/></svg>');
                z-index: 0;
            }}
            
            .dashboard-header::after {{
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: radial-gradient(circle at top right, rgba(103, 222, 145, 0.2), transparent 60%);
                z-index: 0;
            }}
            
            .header-content {{
                position: relative;
                z-index: 1;
            }}
            
            h1 {{
                margin: 0;
                font-size: 2.8em;
                font-weight: 700;
                letter-spacing: -0.5px;
                background: linear-gradient(to right, var(--text-light), var(--primary-light));
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            
            .dashboard-header p {{
                margin-top: 15px;
                font-size: 1.2em;
                font-weight: 300;
                opacity: 0.9;
                max-width: 800px;
                margin-left: auto;
                margin-right: auto;
            }}
            
            .stats-container {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .stat-card {{
                background: linear-gradient(135deg, var(--dark-card), rgba(26, 38, 53, 0.7));
                border-radius: 16px;
                padding: 25px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
                flex: 1;
                min-width: 200px;
                text-align: center;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 166, 125, 0.1);
            }}
            
            .stat-card::before {{
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 4px;
                background: linear-gradient(90deg, var(--primary-color), var(--primary-light));
            }}
            
            .stat-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            }}
            
            .stat-card h3 {{
                color: var(--text-light-secondary);
                font-size: 1em;
                font-weight: 500;
                margin-top: 0;
                margin-bottom: 15px;
            }}
            
            .stat-value {{
                font-size: 2.5em;
                font-weight: 700;
                color: var(--primary-light);
                margin: 10px 0;
                text-shadow: 0 2px 10px rgba(0, 166, 125, 0.2);
            }}
            
            .stat-card div:last-child {{
                font-size: 0.9em;
                color: var(--text-light-secondary);
                margin-top: 5px;
            }}
            
            .section {{
                background: linear-gradient(135deg, var(--dark-card), rgba(26, 38, 53, 0.7));
                border-radius: 16px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(0, 166, 125, 0.1);
                position: relative;
                overflow: hidden;
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
            }}
            
            .section::after {{
                content: '';
                position: absolute;
                top: 0;
                right: 0;
                width: 300px;
                height: 300px;
                background: radial-gradient(circle, rgba(0, 166, 125, 0.1), transparent 70%);
                z-index: 0;
                border-radius: 50%;
            }}
            
            .section h2 {{
                color: var(--primary-light);
                font-weight: 600;
                padding-bottom: 15px;
                margin-top: 0;
                margin-bottom: 25px;
                position: relative;
                display: inline-block;
            }}
            
            .section h2::after {{
                content: '';
                position: absolute;
                left: 0;
                bottom: 0;
                height: 3px;
                width: 100%;
                background: linear-gradient(to right, var(--primary-color), transparent);
                border-radius: 2px;
            }}
            
            .map-container {{
                height: 70vh;
                margin-bottom: 0;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
                position: relative;
                border: 1px solid rgba(0, 166, 125, 0.2);
            }}
            
            .map-iframe {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                border: none;
            }}
            
            .tabs {{
                display: flex;
                margin-bottom: 20px;
                background-color: rgba(15, 23, 32, 0.7);
                border-radius: 12px;
                overflow: hidden;
                padding: 5px;
                position: relative;
                z-index: 5;
            }}
            
            .tab {{
                padding: 12px 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 500;
                flex: 1;
                text-align: center;
                border-radius: 8px;
                position: relative;
                overflow: hidden;
            }}
            
            .tab:hover:not(.active) {{
                background-color: rgba(0, 166, 125, 0.1);
            }}
            
            .tab.active {{
                background: linear-gradient(135deg, var(--primary-dark), var(--primary-color));
                color: white;
                box-shadow: 0 4px 15px rgba(0, 166, 125, 0.3);
            }}
            
            .tab.active::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
                animation: shine 2s infinite;
            }}
            
            @keyframes shine {{
                0% {{ transform: translateX(-100%); }}
                100% {{ transform: translateX(100%); }}
            }}
            
            .tab-content {{
                display: none;
                height: 100%;
            }}
            
            .tab-content.active {{
                display: block;
                height: 100%;
            }}
            
            .chart-row {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 25px;
                margin-bottom: 30px;
            }}
            
            .chart-container {{
                flex: 1;
                min-width: 300px;
                background: linear-gradient(135deg, var(--dark-card), rgba(26, 38, 53, 0.7));
                border-radius: 16px;
                padding: 25px;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(0, 166, 125, 0.1);
                position: relative;
                overflow: hidden;
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            
            .chart-container:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            }}
            
            .chart-title {{
                font-size: 1.1em;
                font-weight: 600;
                margin-bottom: 20px;
                color: var(--primary-light);
                position: relative;
                display: inline-block;
            }}
            
            .chart-title::after {{
                content: '';
                position: absolute;
                left: 0;
                bottom: -5px;
                height: 2px;
                width: 40px;
                background: var(--primary-color);
                border-radius: 2px;
            }}
            
            .chart-img {{
                width: 100%;
                border-radius: 10px;
                transition: transform 0.3s ease;
            }}
            
            .chart-container:hover .chart-img {{
                transform: scale(1.02);
            }}
            
            footer {{
                text-align: center;
                margin-top: 50px;
                padding: 30px 20px;
                color: var(--text-light-secondary);
                font-size: 0.9em;
                position: relative;
            }}
            
            footer::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 50%;
                transform: translateX(-50%);
                width: 200px;
                height: 1px;
                background: linear-gradient(to right, transparent, var(--primary-color), transparent);
            }}
            
            .light-accent {{
                position: absolute;
                width: 150px;
                height: 150px;
                border-radius: 50%;
                background: radial-gradient(circle, var(--primary-color) 0%, transparent 70%);
                filter: blur(50px);
                opacity: 0.05;
                z-index: 0;
            }}
            
            #accent1 {{ top: 10%; left: 5%; }}
            #accent2 {{ bottom: 15%; right: 5%; }}
            
            @media (max-width: 1200px) {{
                .stats-container {{
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                }}
                .chart-row {{
                    grid-template-columns: 1fr;
                }}
                h1 {{
                    font-size: 2.2em;
                }}
            }}
            
            @media (max-width: 768px) {{
                .dashboard-header {{
                    padding: 30px 20px;
                }}
                .section {{
                    padding: 20px;
                }}
                .map-container {{
                    height: 60vh;
                }}
                .tab {{
                    padding: 10px;
                    font-size: 0.9em;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="light-accent" id="accent1"></div>
        <div class="light-accent" id="accent2"></div>
        
        <div class="container">
            <div class="dashboard-header">
                <div class="header-content">
                    <h1>HPC Station Conversion Analysis Dashboard</h1>
                    <p>Comprehensive analysis of gas station viability for conversion to High-Power Charging stations</p>
                </div>
            </div>
            
            {stats_html}
            
            <div class="section">
                <h2>Interactive Station Maps</h2>
                <div class="tabs">
                    <div class="tab active" onclick="showTab('gas-station-map')">Gas Station Viability</div>
                    <div class="tab" onclick="showTab('charging-station-map')">Existing Charging Network</div>
                    <div class="tab" onclick="showTab('heatmap')">EV Adoption Heatmap</div>
                </div>
                
                <div class="map-container">
                    <div id="gas-station-map" class="tab-content active">
                        <iframe class="map-iframe" src="{station_map_filename}"></iframe>
                    </div>
                    
                    <div id="charging-station-map" class="tab-content">
                        <iframe class="map-iframe" src="{charging_map_filename}"></iframe>
                    </div>
                    
                    <div id="heatmap" class="tab-content">
                        <iframe class="map-iframe" src="{heatmap_filename}"></iframe>
                    </div>
                </div>
            </div>
            
            {regional_section}
            
            <div class="section">
                <h2>Forecasting & Market Analysis</h2>
                
                <div class="chart-row">
                    <div class="chart-container">
                        <div class="chart-title">EV Adoption Forecast</div>
                        <img class="chart-img" src="{ev_forecast_filename}" alt="EV Adoption Forecast">
                    </div>
                    
                    <div class="chart-container">
                        <div class="chart-title">Gas Station Viability Distribution</div>
                        <img class="chart-img" src="{viability_chart_filename}" alt="Viability Distribution">
                    </div>
                </div>
                
                <div class="chart-row">
                    <div class="chart-container">
                        <div class="chart-title">Charging Power Distribution</div>
                        <img class="chart-img" src="{power_chart_filename}" alt="Power Distribution">
                    </div>
                </div>
            </div>
            
            {competitor_section}
            
            {sustainability_section}
        </div>
        
        <footer>
            <p>HPC Station Conversion Analysis Dashboard | Empowering sustainable transportation through data-driven decisions</p>
        </footer>
        
        <script>
            function showTab(tabId) {{
                // Hide all tab contents
                var tabContents = document.getElementsByClassName('tab-content');
                for (var i = 0; i < tabContents.length; i++) {{
                    tabContents[i].classList.remove('active');
                }}
                
                // Show selected tab content
                document.getElementById(tabId).classList.add('active');
                
                // Update tab styles
                var tabs = document.getElementsByClassName('tab');
                for (var i = 0; i < tabs.length; i++) {{
                    tabs[i].classList.remove('active');
                }}
                
                // Find clicked tab and make it active
                var clickedTab = event.target;
                clickedTab.classList.add('active');
            }}
        </script>
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(output_file, "w") as f:
        f.write(html_content)
    
    print(f"Created unified dashboard: {output_file}")
    return output_file

# Main function
def main():
    """Main function to generate the unified dashboard."""
    print("===== HPC Station Conversion Analysis Dashboard =====")
    
    # Step 1: Fetch OpenChargeMap data
    charging_stations_df = fetch_opencharge_data()
    
    # Step 2: Generate synthetic gas station data
    gas_stations_df = generate_gas_stations(n_stations=50)
    
    # Step 3: Create visualizations
    print("\n===== Creating Visualizations =====")
    
    # Create maps
    if charging_stations_df is not None:
        charging_map_file = create_charging_station_map(charging_stations_df)
        power_chart_file = create_power_distribution_chart(charging_stations_df)
    else:
        charging_map_file = "output/charging_stations_map.html"
        power_chart_file = "output/power_distribution.png"
        print("Warning: No charging station data available. Using placeholders for visualizations.")
    
    station_map_file = create_gas_station_map(gas_stations_df)
    heatmap_file = create_heatmap(gas_stations_df)
    viability_chart_file = create_viability_chart(gas_stations_df)
    ev_forecast_file = create_ev_forecast()
    
    # Create additional analyses
    regional_analysis_file = create_regional_analysis(gas_stations_df)
    competitor_analysis_file = create_competitor_analysis(gas_stations_df)
    solar_analysis_file = create_solar_analysis(gas_stations_df)
    traffic_analysis_file = create_traffic_analysis(gas_stations_df)
    
    # Step 4: Create unified dashboard
    dashboard_file = create_unified_dashboard(
        charging_stations_df=charging_stations_df,
        gas_stations_df=gas_stations_df,
        charging_map_file=charging_map_file,
        station_map_file=station_map_file,
        heatmap_file=heatmap_file,
        power_chart_file=power_chart_file,
        viability_chart_file=viability_chart_file,
        ev_forecast_file=ev_forecast_file,
        regional_analysis_file=regional_analysis_file,
        competitor_analysis_file=competitor_analysis_file,
        solar_analysis_file=solar_analysis_file,
        traffic_analysis_file=traffic_analysis_file
    )
    
    # Step 5: Open dashboard in browser
    try:
        print("\n===== Opening Dashboard in Browser =====")
        webbrowser.open('file://' + os.path.abspath(dashboard_file))
        print("Dashboard opened in browser")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print(f"Please open {dashboard_file} manually in your browser")
    
    print("\n===== Dashboard Generation Complete =====")
    return dashboard_file

if __name__ == "__main__":
    main() 