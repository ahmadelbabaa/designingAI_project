#!/usr/bin/env python3
"""
Combined HPC Station Dashboard with Advanced Forecasting
This dashboard provides comprehensive analysis for gas station conversion to high-power charging stations
with integrated forecasting visualizations and trend analysis.
"""

import os
import json
import random
import pandas as pd
import numpy as np
import folium
from folium import plugins
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import shutil

# Create necessary folders if they don't exist
for folder in ['data', 'config', 'output', 'output/forecasts']:
    os.makedirs(folder, exist_ok=True)

# Constants for synthetic data generation
LOCATION_FEATURES = [
    "traffic_volume", "nearby_attractions", "ev_ownership", "income_level",
    "charging_network", "competitive_density", "grid_capacity", "parking_availability"
]

EV_ADOPTION_PROJECTIONS = {
    '2023': 5.6,
    '2024': 7.2,
    '2025': 9.5,
    '2026': 12.3,
    '2027': 15.8,
    '2028': 20.1,
    '2029': 25.6,
    '2030': 32.0
}

VIABILITY_WEIGHTS = {
    "traffic_volume": 0.25,
    "nearby_attractions": 0.10,
    "ev_ownership": 0.20,
    "income_level": 0.10,
    "charging_network": 0.10,
    "competitive_density": 0.10,
    "grid_capacity": 0.10,
    "parking_availability": 0.05
}

def generate_gas_stations(num_stations=50, save_data=True):
    """
    Generate synthetic gas station data for analysis
    
    Args:
        num_stations (int): Number of stations to generate
        save_data (bool): Whether to save the data to files
        
    Returns:
        list: List of station dictionaries
    """
    stations = []
    
    for i in range(1, num_stations + 1):
        # Generate basic station info
        station_id = f"GS-{i:04d}"
        lat = 37.7749 + random.uniform(-0.5, 0.5)  # Around San Francisco
        lon = -122.4194 + random.uniform(-0.5, 0.5)
        
        # Generate features with random values (0-100)
        features = {feature: round(random.uniform(30, 95), 1) for feature in LOCATION_FEATURES}
        
        # Calculate viability score (weighted average of features)
        viability_score = sum(features[k] * VIABILITY_WEIGHTS[k] for k in VIABILITY_WEIGHTS)
        viability_score = round(viability_score, 1)
        
        # Calculate estimated ROI based on viability
        roi = (viability_score / 100) * random.uniform(0.8, 1.2) * 25  # Max 30% ROI
        roi = round(roi, 1)
        
        # Determine conversion recommendation
        recommendation = "High Priority" if viability_score >= 70 else \
                        "Potential" if viability_score >= 50 else "Low Viability"
        
        # Create station object
        station = {
            "station_id": station_id,
            "name": f"Gas Station {i}",
            "latitude": lat,
            "longitude": lon,
            "features": features,
            "viability_score": viability_score,
            "estimated_roi": roi,
            "recommendation": recommendation
        }
        
        stations.append(station)
    
    # Sort stations by viability score (descending)
    stations.sort(key=lambda x: x["viability_score"], reverse=True)
    
    # Save data if requested
    if save_data:
        # Save as CSV for easy analysis
        df = pd.DataFrame([
            {
                "station_id": s["station_id"],
                "name": s["name"],
                "latitude": s["latitude"],
                "longitude": s["longitude"],
                "viability_score": s["viability_score"],
                "estimated_roi": s["estimated_roi"],
                "recommendation": s["recommendation"],
                **{f"feature_{k}": v for k, v in s["features"].items()}
            } for s in stations
        ])
        
        df.to_csv("data/gas_stations.csv", index=False)
        
        # Save as JSON for web usage
        with open("data/gas_stations.json", "w") as f:
            json.dump(stations, f, indent=2)
    
    return stations

def create_map(stations, save_file="output/station_map.html"):
    """
    Create a folium map with station markers
    
    Args:
        stations (list): List of station dictionaries
        save_file (str): Path to save the HTML file
        
    Returns:
        folium.Map: Map object with stations
    """
    # Calculate center of map
    lats = [s["latitude"] for s in stations]
    lons = [s["longitude"] for s in stations]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
    
    # Add station markers
    for station in stations:
        # Determine marker color based on viability
        if station["viability_score"] >= 70:
            color = "green"
        elif station["viability_score"] >= 50:
            color = "orange"
        else:
            color = "red"
        
        # Create popup content
        popup_content = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h3>{station["name"]} ({station["station_id"]})</h3>
            <p><b>Viability Score:</b> {station["viability_score"]}</p>
            <p><b>Estimated ROI:</b> {station["estimated_roi"]}%</p>
            <p><b>Recommendation:</b> {station["recommendation"]}</p>
            <hr>
            <h4>Key Factors:</h4>
            <ul>
                <li><b>Traffic Volume:</b> {station["features"]["traffic_volume"]}</li>
                <li><b>EV Ownership:</b> {station["features"]["ev_ownership"]}</li>
                <li><b>Grid Capacity:</b> {station["features"]["grid_capacity"]}</li>
            </ul>
        </div>
        """
        
        # Add marker
        folium.Marker(
            location=[station["latitude"], station["longitude"]],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{station['name']} - Score: {station['viability_score']}",
            icon=folium.Icon(color=color, icon="plug", prefix="fa")
        ).add_to(m)
    
    # Save map
    m.save(save_file)
    
    return m

def create_heatmap(stations, save_file="output/ev_adoption_heatmap.html"):
    """
    Create a heatmap showing EV ownership density
    
    Args:
        stations (list): List of station dictionaries
        save_file (str): Path to save the HTML file
        
    Returns:
        folium.Map: Map object with heatmap
    """
    # Calculate center of map
    lats = [s["latitude"] for s in stations]
    lons = [s["longitude"] for s in stations]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
    
    # Prepare heatmap data - use numeric values for intensity
    heat_data = [
        [
            s["latitude"], 
            s["longitude"], 
            float(s["features"]["ev_ownership"]) / 100.0  # Ensure it's a float
        ] 
        for s in stations
    ]
    
    # Add heatmap layer - use string keys for gradient
    plugins.HeatMap(heat_data, radius=15, blur=10, gradient={
        '0.4': 'blue',
        '0.6': 'purple',
        '0.8': 'orange',
        '1.0': 'red'
    }).add_to(m)
    
    # Save map
    m.save(save_file)
    
    return m

def generate_usage_data(station_id, days=180, base_sessions=None, base_energy=None, 
                        growth_rate=0.02, weekend_factor=1.3, seasonality=True):
    """
    Generate synthetic charging station usage data
    
    Args:
        station_id (str): Station ID
        days (int): Number of days to generate data for
        base_sessions (float, optional): Base number of daily charging sessions
        base_energy (float, optional): Base energy delivered per session (kWh)
        growth_rate (float): Monthly growth rate for EV adoption
        weekend_factor (float): Factor for increased weekend usage
        seasonality (bool): Whether to include seasonal patterns
        
    Returns:
        pd.DataFrame: DataFrame with synthetic usage data
    """
    # Set default base values if not provided
    if base_sessions is None:
        base_sessions = random.uniform(5, 20)  # Base daily sessions
    
    if base_energy is None:
        base_energy = random.uniform(40, 70)   # Base energy per session (kWh)
    
    # Set price per kWh (with some randomness)
    price_per_kwh = 0.35 + random.uniform(-0.05, 0.05)
    
    # Generate dates for the past N days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    # Generate usage data
    data = []
    for i, date in enumerate(dates):
        # Apply growth trend (compound growth)
        month_factor = (1 + growth_rate) ** (i // 30)
        
        # Apply day of week pattern
        day_of_week = date.weekday()
        is_weekend = day_of_week >= 5  # 5=Saturday, 6=Sunday
        dow_factor = weekend_factor if is_weekend else 1.0
        
        # Apply seasonal patterns if enabled
        seasonal_factor = 1.0
        if seasonality:
            # Simple seasonal pattern (higher in summer, lower in winter)
            day_of_year = date.timetuple().tm_yday
            seasonal_factor = 1.0 + 0.3 * np.sin((day_of_year / 365) * 2 * np.pi)
        
        # Apply random variation
        random_factor = np.random.normal(1.0, 0.2)
        
        # Calculate sessions for this day
        sessions = base_sessions * month_factor * dow_factor * seasonal_factor * random_factor
        sessions = max(1, round(sessions, 1))  # Ensure at least 1 session
        
        # Calculate energy and revenue
        energy_per_session = base_energy * (1 + random.uniform(-0.15, 0.15))
        energy_delivered = sessions * energy_per_session
        revenue = energy_delivered * price_per_kwh
        
        # Add to data
        data.append({
            'station_id': station_id,
            'date': date,
            'charging_sessions': sessions,
            'energy_delivered_kwh': round(energy_delivered, 1),
            'revenue_usd': round(revenue, 2),
            'is_weekend': is_weekend,
            'day_of_week': day_of_week
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    return df

def forecast_station_usage(usage_df, forecast_days=90, plot=True, output_dir='output/forecasts'):
    """
    Forecast future station usage based on historical data
    
    Args:
        usage_df (pd.DataFrame): DataFrame with historical usage data
        forecast_days (int): Number of days to forecast
        plot (bool): Whether to generate and save plots
        output_dir (str): Directory to save plots
        
    Returns:
        pd.DataFrame, str: DataFrame with forecast data and path to plot if generated
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get station ID
    station_id = usage_df['station_id'].iloc[0]
    
    # Get the last date in the historical data
    last_date = usage_df['date'].max()
    
    # Generate forecast dates
    forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
    
    # Calculate trend from historical data (using simple linear regression)
    days_from_start = [(date - usage_df['date'].min()).days for date in usage_df['date']]
    X = np.array(days_from_start).reshape(-1, 1)
    y_sessions = usage_df['charging_sessions'].values
    
    # Simplified linear trend calculation
    if len(X) > 1:  # Need at least 2 points for regression
        slope_sessions = np.polyfit(X.flatten(), y_sessions, 1)[0]
    else:
        slope_sessions = 0.05  # Default small positive trend
    
    # Generate forecast data
    forecast_data = []
    for i, date in enumerate(forecast_dates):
        # Apply trend
        days_ahead = i + 1
        base_sessions = usage_df['charging_sessions'].mean() + slope_sessions * days_ahead
        
        # Apply day of week pattern
        day_of_week = date.weekday()
        is_weekend = day_of_week >= 5
        
        # Calculate weekend effect from historical data
        if len(usage_df[usage_df['is_weekend']]) > 0 and len(usage_df[~usage_df['is_weekend']]) > 0:
            weekend_factor = usage_df[usage_df['is_weekend']]['charging_sessions'].mean() / \
                             usage_df[~usage_df['is_weekend']]['charging_sessions'].mean()
        else:
            weekend_factor = 1.3  # Default weekend factor
        
        dow_factor = weekend_factor if is_weekend else 1.0
        
        # Apply seasonal pattern (simplified)
        day_of_year = date.timetuple().tm_yday
        seasonal_factor = 1.0 + 0.2 * np.sin((day_of_year / 365) * 2 * np.pi)
        
        # Calculate forecast values with some randomness
        sessions = max(1, base_sessions * dow_factor * seasonal_factor * np.random.normal(1.0, 0.1))
        
        # Calculate energy and revenue based on historical averages
        avg_energy_per_session = usage_df['energy_delivered_kwh'].sum() / usage_df['charging_sessions'].sum()
        avg_price_per_kwh = usage_df['revenue_usd'].sum() / usage_df['energy_delivered_kwh'].sum()
        
        energy_delivered = sessions * avg_energy_per_session
        revenue = energy_delivered * avg_price_per_kwh
        
        forecast_data.append({
            'station_id': station_id,
            'date': date,
            'charging_sessions': round(sessions, 1),
            'energy_delivered_kwh': round(energy_delivered, 1),
            'revenue_usd': round(revenue, 2),
            'is_weekend': is_weekend,
            'day_of_week': day_of_week,
            'is_forecast': True
        })
    
    # Create forecast DataFrame
    forecast_df = pd.DataFrame(forecast_data)
    
    # Create and save plot if requested
    plot_path = None
    if plot:
        plot_path = f"{output_dir}/{station_id}_forecast.png"
        plt.figure(figsize=(12, 8))
        
        # Plot historical data
        plt.plot(usage_df['date'], usage_df['charging_sessions'], 
                 label='Historical', color='blue', marker='o', markersize=4)
        
        # Plot forecast data
        plt.plot(forecast_df['date'], forecast_df['charging_sessions'], 
                 label='Forecast', color='red', linestyle='--', marker='x', markersize=4)
        
        # Add labels and title
        plt.xlabel('Date')
        plt.ylabel('Daily Charging Sessions')
        plt.title(f'Station {station_id} - Charging Sessions Forecast')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save plot
        plt.savefig(plot_path)
        plt.close()
    
    return forecast_df, plot_path

def generate_forecast(station_id, historical_days=180, forecast_days=90, 
                      base_sessions=None, base_energy=None, 
                      save_data=True):
    """
    Generate forecast for a station
    
    Args:
        station_id (str): Station ID
        historical_days (int): Number of historical days to generate
        forecast_days (int): Number of days to forecast
        base_sessions (float, optional): Base number of daily charging sessions
        base_energy (float, optional): Base energy delivered per session (kWh)
        save_data (bool): Whether to save the data
        
    Returns:
        tuple: Historical DataFrame, Forecast DataFrame, Plot path
    """
    # Generate historical data
    historical_df = generate_usage_data(
        station_id, 
        days=historical_days,
        base_sessions=base_sessions,
        base_energy=base_energy
    )
    
    # Generate forecast
    forecast_df, plot_path = forecast_station_usage(
        historical_df, 
        forecast_days=forecast_days
    )
    
    # Combine historical and forecast data
    combined_df = pd.concat([
        historical_df.assign(is_forecast=False),
        forecast_df
    ]).reset_index(drop=True)
    
    # Save data if requested
    if save_data:
        combined_df.to_csv(f'data/{station_id}_forecast_data.csv', index=False)
    
    return historical_df, forecast_df, plot_path

def generate_multiple_station_forecasts(station_ids, historical_days=180, forecast_days=90):
    """
    Generate forecasts for multiple stations
    
    Args:
        station_ids (list): List of station IDs
        historical_days (int): Number of historical days to generate
        forecast_days (int): Number of days to forecast
        
    Returns:
        dict: Dictionary with forecast results
    """
    results = {}
    
    for station_id in station_ids:
        # Use different base values for each station to create variation
        base_sessions = random.uniform(5, 25)
        base_energy = random.uniform(40, 80)
        
        # Generate forecast
        _, forecast_df, plot_path = generate_forecast(
            station_id,
            historical_days=historical_days,
            forecast_days=forecast_days,
            base_sessions=base_sessions,
            base_energy=base_energy
        )
        
        # Store results
        results[station_id] = (forecast_df, plot_path)
    
    return results

def create_forecast_visualization_html(forecast_results):
    """
    Create HTML for forecast visualizations
    
    Args:
        forecast_results (dict): Dictionary with forecast results
        
    Returns:
        str: HTML content for forecast visualizations
    """
    if not forecast_results:
        return "<p>No forecast data available</p>"
    
    html = ""
    
    for station_id, (forecast_df, plot_path) in forecast_results.items():
        # Calculate summary statistics
        avg_sessions = round(forecast_df['charging_sessions'].mean(), 1)
        avg_energy = round(forecast_df['energy_delivered_kwh'].mean(), 1)
        total_energy = round(forecast_df['energy_delivered_kwh'].sum(), 1)
        total_revenue = round(forecast_df['revenue_usd'].sum(), 2)
        
        # Get relative path to plot
        relative_plot_path = plot_path.replace('output/', '')
        
        # Create forecast card HTML
        html += f"""
        <div class="forecast-card">
            <h3>Station {station_id} Forecast</h3>
            <div class="forecast-metrics">
                <div class="forecast-metric">
                    <div>Avg Daily Sessions</div>
                    <div class="forecast-metric-value">{avg_sessions}</div>
                </div>
                <div class="forecast-metric">
                    <div>Avg Daily Energy</div>
                    <div class="forecast-metric-value">{avg_energy} kWh</div>
                </div>
                <div class="forecast-metric">
                    <div>Total Energy</div>
                    <div class="forecast-metric-value">{total_energy} kWh</div>
                </div>
                <div class="forecast-metric">
                    <div>Total Revenue</div>
                    <div class="forecast-metric-value">${total_revenue:,.2f}</div>
                </div>
            </div>
            <img src="{relative_plot_path}" class="forecast-plot" alt="Forecast plot for station {station_id}">
        </div>
        """
    
    return html

def analyze_forecast_trends(forecast_results):
    """
    Analyze trends across multiple station forecasts
    
    Args:
        forecast_results (dict): Dictionary with forecast results
        
    Returns:
        dict: Dictionary with trend analysis
    """
    if not forecast_results:
        return {}
    
    trends = {
        'stations': [],
        'avg_sessions': [],
        'avg_energy': [],
        'total_revenue': []
    }
    
    for station_id, (forecast_df, _) in forecast_results.items():
        trends['stations'].append(station_id)
        trends['avg_sessions'].append(round(forecast_df['charging_sessions'].mean(), 1))
        trends['avg_energy'].append(round(forecast_df['energy_delivered_kwh'].mean(), 1))
        trends['total_revenue'].append(round(forecast_df['revenue_usd'].sum(), 2))
    
    # Calculate overall statistics
    trends['overall'] = {
        'avg_sessions': round(np.mean(trends['avg_sessions']), 1),
        'avg_energy': round(np.mean(trends['avg_energy']), 1),
        'total_revenue': round(sum(trends['total_revenue']), 2)
    }
    
    # Save trends to JSON
    with open('data/forecast_trends.json', 'w') as f:
        json.dump(trends, f, indent=2)
    
    return trends

def calculate_dashboard_stats(stations):
    """
    Calculate summary statistics for dashboard
    
    Args:
        stations (list): List of station dictionaries
        
    Returns:
        dict: Dictionary with calculated statistics
    """
    # Calculate basic stats
    total_stations = len(stations)
    avg_viability = round(sum(s["viability_score"] for s in stations) / total_stations, 1)
    avg_roi = round(sum(s["estimated_roi"] for s in stations) / total_stations, 1)
    
    # Count stations by recommendation
    high_viability = sum(1 for s in stations if s["viability_score"] >= 70)
    low_viability = sum(1 for s in stations if s["viability_score"] < 50)
    
    # Calculate feature averages
    feature_avgs = {}
    for feature in LOCATION_FEATURES:
        feature_avgs[feature] = round(sum(s["features"][feature] for s in stations) / total_stations, 1)
    
    return {
        "total_stations": total_stations,
        "avg_viability": avg_viability,
        "avg_roi": avg_roi,
        "high_viability_count": high_viability,
        "low_viability_count": low_viability,
        "feature_averages": feature_avgs
    }

def generate_forecasts(stations, top_n=5, historical_days=180, forecast_days=90):
    """
    Generate time series forecasts for top stations
    
    Args:
        stations (list): List of station dictionaries
        top_n (int): Number of top stations to forecast
        historical_days (int): Number of historical days to generate
        forecast_days (int): Number of days to forecast
        
    Returns:
        dict: Dictionary with forecast results
    """
    # Get top N stations by viability score
    top_stations = stations[:top_n]
    
    # Generate forecasts for top stations
    forecast_results = {}
    for station in top_stations:
        station_id = station["station_id"]
        
        # Base sessions proportional to viability score
        base_sessions = (station["viability_score"] / 100) * random.uniform(15, 25)
        
        # Generate forecast
        historical_df, forecast_df, plot_path = generate_forecast(
            station_id,
            historical_days=historical_days,
            forecast_days=forecast_days,
            base_sessions=base_sessions,
            save_data=True
        )
        
        # Store forecast results
        forecast_results[station_id] = (forecast_df, plot_path)
    
    # Analyze trends across stations
    trends = analyze_forecast_trends(forecast_results)
    
    # Create summary file with forecast results
    forecast_summary = {
        "date_generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stations_forecasted": len(forecast_results),
        "forecast_days": forecast_days,
        "overall_stats": trends["overall"],
        "station_forecasts": {
            station_id: {
                "viability_score": next(s["viability_score"] for s in stations if s["station_id"] == station_id),
                "avg_sessions": round(forecast_df["charging_sessions"].mean(), 1),
                "total_energy": round(forecast_df["energy_delivered_kwh"].sum(), 1),
                "total_revenue": round(forecast_df["revenue_usd"].sum(), 2)
            }
            for station_id, (forecast_df, _) in forecast_results.items()
        }
    }
    
    # Save forecast summary
    with open("data/forecast_summary.json", "w") as f:
        json.dump(forecast_summary, f, indent=2)
    
    return forecast_results

def create_comparative_performance_chart(stations, forecast_results, save_file="output/forecasts/comparative_chart.png"):
    """
    Create chart comparing forecasted performance of top stations
    
    Args:
        stations (list): List of station dictionaries
        forecast_results (dict): Dictionary with forecast results
        save_file (str): Path to save the chart
        
    Returns:
        str: Path to saved chart
    """
    if not forecast_results:
        return None
    
    # Extract station IDs and corresponding forecast data
    station_ids = []
    avg_sessions = []
    total_revenue = []
    
    for station_id, (forecast_df, _) in forecast_results.items():
        station_ids.append(station_id)
        avg_sessions.append(round(forecast_df["charging_sessions"].mean(), 1))
        total_revenue.append(round(forecast_df["revenue_usd"].sum(), 2))
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot average daily sessions
    colors1 = ['#2ecc71' if val >= 15 else '#f39c12' if val >= 10 else '#e74c3c' for val in avg_sessions]
    ax1.bar(station_ids, avg_sessions, color=colors1)
    ax1.set_title('Average Daily Charging Sessions', fontsize=14)
    ax1.set_xlabel('Station ID', fontsize=12)
    ax1.set_ylabel('Avg. Sessions per Day', fontsize=12)
    ax1.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Plot total revenue
    colors2 = ['#2ecc71' if val >= 5000 else '#f39c12' if val >= 3000 else '#e74c3c' for val in total_revenue]
    ax2.bar(station_ids, total_revenue, color=colors2)
    ax2.set_title('Projected 90-Day Revenue', fontsize=14)
    ax2.set_xlabel('Station ID', fontsize=12)
    ax2.set_ylabel('Revenue (USD)', fontsize=12)
    ax2.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add dollar signs to y-axis labels for revenue chart
    ax2.set_yticklabels(['${:,.0f}'.format(x) for x in ax2.get_yticks()])
    
    # Add title for the entire figure
    fig.suptitle('Comparative Forecasted Performance', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to make room for suptitle
    
    # Save chart
    plt.savefig(save_file)
    plt.close()
    
    return save_file

def create_dashboard_html(stations, stats, forecast_results, save_file="output/dashboard.html"):
    """
    Create HTML dashboard with enhanced forecasting visualizations
    
    Args:
        stations (list): List of station dictionaries
        stats (dict): Dashboard statistics
        forecast_results (dict): Dictionary with forecast results
        save_file (str): Path to save the HTML file
        
    Returns:
        str: Path to saved HTML file
    """
    # Create comparative performance chart
    comparative_chart_path = create_comparative_performance_chart(stations, forecast_results)
    relative_chart_path = comparative_chart_path.replace("output/", "") if comparative_chart_path else ""
    
    # Get forecast visualizations
    forecast_html = create_forecast_visualization_html(forecast_results)
    
    # Read EV adoption projections for display
    ev_years = list(EV_ADOPTION_PROJECTIONS.keys())
    ev_rates = list(EV_ADOPTION_PROJECTIONS.values())
    
    # Generate station table rows
    station_rows = ""
    for i, station in enumerate(stations[:20]):  # Show top 20 stations
        viability_class = "high" if station["viability_score"] >= 70 else "medium" if station["viability_score"] >= 50 else "low"
        
        station_rows += f"""
        <tr class="viability-{viability_class}">
            <td>{i+1}</td>
            <td>{station["station_id"]}</td>
            <td>{station["name"]}</td>
            <td class="viability-score">{station["viability_score"]}</td>
            <td>{station["estimated_roi"]}%</td>
            <td>{station["recommendation"]}</td>
        </tr>
        """
    
    # Create HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HPC Station Conversion Dashboard</title>
    <style>
        :root {{
            --primary-color: #3498db;
            --secondary-color: #2c3e50;
            --success-color: #2ecc71;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --light-color: #ecf0f1;
            --dark-color: #2c3e50;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f7fa;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .dashboard-header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 20px 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        h1, h2, h3, h4 {{
            margin-top: 0;
        }}
        
        .stats-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            flex: 1;
            min-width: 200px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
            color: var(--primary-color);
        }}
        
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        
        .content-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .content-box {{
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .station-list {{
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background-color: var(--secondary-color);
            color: white;
            position: sticky;
            top: 0;
        }}
        
        tr:hover {{
            background-color: #f9f9f9;
        }}
        
        .viability-high .viability-score {{
            color: var(--success-color);
            font-weight: bold;
        }}
        
        .viability-medium .viability-score {{
            color: var(--warning-color);
            font-weight: bold;
        }}
        
        .viability-low .viability-score {{
            color: var(--danger-color);
            font-weight: bold;
        }}
        
        .map-container {{
            height: 500px;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        
        .forecasts-section {{
            margin-top: 40px;
        }}
        
        .forecast-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 20px;
        }}
        
        .forecast-card {{
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            flex: 1;
            min-width: 400px;
        }}
        
        .forecast-metrics {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 15px;
        }}
        
        .forecast-metric {{
            background-color: var(--light-color);
            padding: 10px;
            border-radius: 5px;
            flex: 1;
            min-width: 100px;
            text-align: center;
            font-size: 14px;
        }}
        
        .forecast-metric-value {{
            font-size: 20px;
            font-weight: bold;
            color: var(--primary-color);
            margin-top: 5px;
        }}
        
        .forecast-plot {{
            width: 100%;
            max-height: 300px;
            object-fit: contain;
            margin-top: 10px;
        }}
        
        .chart-box {{
            text-align: center;
        }}
        
        .chart-box img {{
            max-width: 100%;
            margin-top: 15px;
        }}
        
        .additional-resources {{
            margin-top: 30px;
            padding: 20px;
            background-color: var(--light-color);
            border-radius: 8px;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="dashboard-header">
            <h1>HPC Station Conversion Analysis Dashboard</h1>
            <p>Advanced dashboard with integrated forecasting for analyzing gas station conversion to high-power charging stations</p>
        </div>
        
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-label">Total Stations Analyzed</div>
                <div class="stat-value">{stats["total_stations"]}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Average Viability Score</div>
                <div class="stat-value">{stats["avg_viability"]}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Average ROI</div>
                <div class="stat-value">{stats["avg_roi"]}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">High Viability Stations</div>
                <div class="stat-value">{stats["high_viability_count"]}</div>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="content-box map-container">
                <h2>Viability Map</h2>
                <iframe src="station_map.html"></iframe>
            </div>
            
            <div class="content-box station-list">
                <h2>Top Stations by Viability</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Viability Score</th>
                            <th>Est. ROI</th>
                            <th>Recommendation</th>
                        </tr>
                    </thead>
                    <tbody>
                        {station_rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="content-box">
                <h2>EV Adoption Heatmap</h2>
                <iframe src="ev_adoption_heatmap.html"></iframe>
            </div>
            
            <div class="content-box">
                <h2>EV Adoption Projections</h2>
                <p>Increasing EV adoption rates drive demand for high-power charging infrastructure:</p>
                <table>
                    <thead>
                        <tr>
                            <th>Year</th>
                            <th>Projected Adoption Rate (%)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join(f"<tr><td>{year}</td><td>{rate}%</td></tr>" for year, rate in EV_ADOPTION_PROJECTIONS.items())}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="forecasts-section">
            <h2>Station Performance Forecasts</h2>
            <p>Advanced forecasting based on station characteristics and market trends</p>
            
            <div class="content-box chart-box">
                <h3>Comparative Station Performance</h3>
                <p>Comparison of forecast metrics for top stations by viability score</p>
                <img src="{relative_chart_path}" alt="Comparative station performance chart">
            </div>
            
            <div class="forecast-grid">
                {forecast_html}
            </div>
        </div>
        
        <div class="additional-resources">
            <h3>Additional Resources</h3>
            <p>This dashboard is part of the HPC Station Conversion Analysis project, providing decision support for strategic planning of EV charging infrastructure. For more information, see the project documentation.</p>
        </div>
        
        <footer>
            <p>HPC Station Conversion Analysis Dashboard | Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </footer>
    </div>
</body>
</html>
"""
    
    # Save the dashboard HTML
    with open(save_file, "w") as f:
        f.write(html_content)
    
    return save_file

def main():
    """
    Main function to run the combined dashboard generation
    """
    print("Creating folders for data, config, and output...")
    for folder in ['data', 'config', 'output', 'output/forecasts']:
        os.makedirs(folder, exist_ok=True)
    
    print("Generating synthetic gas station data for analysis...")
    stations = generate_gas_stations(num_stations=50, save_data=True)
    print(f"Generated {len(stations)} stations for analysis")
    
    print("Creating station map...")
    create_map(stations, save_file="output/station_map.html")
    print("Map saved to output/station_map.html")
    
    print("Creating EV adoption heatmap...")
    create_heatmap(stations, save_file="output/ev_adoption_heatmap.html")
    print("Heatmap saved to output/ev_adoption_heatmap.html")
    
    print("Calculating dashboard statistics...")
    stats = calculate_dashboard_stats(stations)
    print(f"Average viability score: {stats['avg_viability']}")
    print(f"High viability stations: {stats['high_viability_count']}")
    
    print("Generating time series forecasts for top stations...")
    forecast_results = generate_forecasts(stations, top_n=5)
    print(f"Generated forecasts for {len(forecast_results)} stations")
    
    print("Creating dashboard with forecast visualizations...")
    dashboard_file = create_dashboard_html(stations, stats, forecast_results)
    print(f"Dashboard saved to {dashboard_file}")
    
    print("Dashboard generation complete!")
    print(f"Open {dashboard_file} in a web browser to view the dashboard")

if __name__ == "__main__":
    main() 