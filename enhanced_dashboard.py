#!/usr/bin/env python3
"""
Enhanced HPC Station Dashboard with Advanced Forecasting
This dashboard provides analysis for gas station conversion to high-power charging stations
with integrated forecasting visualizations.
"""

# Force matplotlib to use non-interactive backend to prevent GUI thread issues
import matplotlib
matplotlib.use('Agg')

import os
import json
import random
import pandas as pd
import numpy as np
import folium
from folium import plugins
import time_series_forecasting as tsf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import shutil
import time
from flask import Flask, render_template, request, jsonify
from conversion_advisor import generate_conversion_recommendation, create_dashboard_html, load_gas_stations
from ev_charging_analysis import run_analysis

# Create Flask app with standard static folder configuration
app = Flask(__name__, 
            static_folder='static',  # Use the standard static folder
            template_folder='templates')

# Create necessary folders if they don't exist
for folder in ['data', 'config', 'output', 'output/forecasts', 'output/conversion_advisor', 'templates']:
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

# Add code near the beginning of the file to ensure static directory exists
def ensure_static_dir():
    """Ensure static directory exists"""
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/forecasts', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)

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
            "recommendation": recommendation,
            "daily_customers": random.randint(200, 1000),
            "monthly_revenue": random.randint(50000, 200000),
            "property_size_sqft": random.randint(5000, 30000),
            "has_convenience_store": random.choice([True, False])
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
                "daily_customers": s["daily_customers"],
                "monthly_revenue": s["monthly_revenue"],
                "property_size_sqft": s["property_size_sqft"],
                "has_convenience_store": s["has_convenience_store"],
                **{f"feature_{k}": v for k, v in s["features"].items()}
            } for s in stations
        ])
        
        df.to_csv("data/gas_stations.csv", index=False)
        
        # Save as JSON for web usage
        with open("data/gas_stations.json", "w") as f:
            json.dump(stations, f, indent=2)
    
    return stations

def create_map(stations, save_file="static/station_map.html"):
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

def create_heatmap(stations, save_file="static/ev_adoption_heatmap.html"):
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
    
    # Prepare heatmap data
    heat_data = [
        [
            s["latitude"], 
            s["longitude"], 
            s["features"]["ev_ownership"] / 100.0  # Normalize to 0-1 range
        ] 
        for s in stations
    ]
    
    # Add heatmap layer
    plugins.HeatMap(heat_data, radius=15, blur=10, gradient={
        '0.4': 'blue',
        '0.6': 'purple',
        '0.8': 'orange',
        '1.0': 'red'
    }).add_to(m)
    
    # Save map
    m.save(save_file)
    
    return m

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
        historical_df, forecast_df, plot_path = tsf.generate_forecast(
            station_id,
            historical_days=historical_days,
            forecast_days=forecast_days,
            base_sessions=base_sessions,
            save_data=True
        )
        
        # Store forecast results
        forecast_results[station_id] = (forecast_df, plot_path)
    
    # Analyze trends across stations
    trends = tsf.analyze_forecast_trends(forecast_results)
    
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

def create_comparative_performance_chart(stations, forecast_results, save_file="static/forecasts/comparative_chart.png"):
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

def create_dashboard_html(stations, stats, forecast_results, save_file="static/enhanced_dashboard.html"):
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
    relative_chart_path = comparative_chart_path.replace("static/", "") if comparative_chart_path else ""
    
    # Get forecast visualizations
    forecast_html = tsf.create_forecast_visualization_html(forecast_results)
    
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

# Add routes for the web interface
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/conversion_advisor')
def conversion_advisor_page():
    """Conversion advisor page"""
    stations_df = load_gas_stations()
    stations = [row.to_dict() for _, row in stations_df.iterrows()]
    return render_template('conversion_advisor.html', stations=stations)

@app.route('/charging_patterns')
def charging_patterns():
    """EV Charging Patterns Analysis page"""
    return render_template('charging_patterns.html')

@app.route('/api/v1/charging-patterns/summary', methods=['GET'])
def charging_patterns_api():
    """API endpoint to serve data for interactive visualizations"""
    try:
        # Check if cached results exist
        cache_file = 'output/charging_patterns/analysis_results.json'
        if os.path.exists(cache_file):
            # Load cached results if they exist and are less than 1 day old
            file_mod_time = os.path.getmtime(cache_file)
            if (time.time() - file_mod_time) < 86400:  # 24 hours in seconds
                with open(cache_file, 'r') as f:
                    results = json.load(f)
                return jsonify(results)
        
        # Run analysis if no cache or cache is old
        results = run_analysis()
        
        # Cache results for future requests
        os.makedirs('output/charging_patterns', exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(results, f)
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gas_stations')
def gas_stations_api():
    """API endpoint for gas station data"""
    try:
        stations_df = load_gas_stations()
        stations = [row.to_dict() for _, row in stations_df.iterrows()]
        return jsonify(stations)
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/gas_stations/<station_id>')
def gas_station_detail_api(station_id):
    """API endpoint for individual gas station data"""
    try:
        stations_df = load_gas_stations()
        if station_id not in stations_df['station_id'].values:
            return jsonify({'error': f'Station ID {station_id} not found'}), 404
            
        station = stations_df[stations_df['station_id'] == station_id].iloc[0].to_dict()
        return jsonify(station)
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/generate_recommendation', methods=['POST'])
def generate_recommendation_post_api():
    """API endpoint for generating recommendations via POST"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract information from the form
        station_name = data.get('stationName', 'Custom Station')
        location = data.get('location', 'Unknown')
        station_type = data.get('stationType', 'Urban')
        daily_traffic = int(data.get('dailyTraffic', 500))
        
        # Create a synthetic station
        station_data = {
            'station_id': f"CUSTOM-{int(time.time())}",
            'name': station_name,
            'location': location,
            'station_type': station_type,
            'daily_customers': daily_traffic,
            'monthly_revenue': daily_traffic * 30 * 5.5,  # Estimate monthly revenue
            'property_size_sqft': 15000,
            'has_convenience_store': True,
            'latitude': 39.8283,  # Default location (will be replaced if we geocode)
            'longitude': -98.5795
        }
        
        # Try to make a recommendation
        try:
            from conversion_advisor import create_conversion_prompt, query_gpt4
            from openai_config import get_openai_api_key
            
            # Create simple scenarios
            scenarios = {
                'realistic': {
                    'forecast': pd.DataFrame({
                        'charging_sessions': [daily_traffic * 0.05] * 30,
                        'energy_delivered_kwh': [daily_traffic * 0.05 * 30] * 30,
                        'revenue_usd': [daily_traffic * 0.05 * 30 * 0.35] * 30
                    })
                }
            }
            
            # Simple ROI data
            roi_results = {
                'realistic': {
                    'Basic (1 charger)': {
                        'capex': 50000,
                        'annual_profit': daily_traffic * 0.05 * 30 * 0.35 * 12 * 0.5,
                        'payback_years': 50000 / (daily_traffic * 0.05 * 30 * 0.35 * 12 * 0.5),
                        'roi_5yr': (daily_traffic * 0.05 * 30 * 0.35 * 12 * 0.5 * 5 - 50000) / 50000
                    },
                    'Standard (2 chargers)': {
                        'capex': 150000,
                        'annual_profit': daily_traffic * 0.05 * 30 * 0.35 * 12 * 0.7,
                        'payback_years': 150000 / (daily_traffic * 0.05 * 30 * 0.35 * 12 * 0.7),
                        'roi_5yr': (daily_traffic * 0.05 * 30 * 0.35 * 12 * 0.7 * 5 - 150000) / 150000
                    }
                }
            }
            
            # Create prompt for GPT-4
            prompt = create_conversion_prompt(station_data, scenarios, roi_results)
            
            # Get recommendation from GPT-4
            recommendation = query_gpt4(prompt)
            
            return jsonify({
                'success': True,
                'station_data': station_data,
                'recommendation': recommendation
            })
            
        except Exception as inner_e:
            # Log the error but continue to return a placeholder
            print(f"Error generating recommendation: {str(inner_e)}")
            import traceback
            print(traceback.format_exc())
            
            # Return a placeholder recommendation
            from conversion_advisor import generate_placeholder_recommendation
            return jsonify({
                'success': True,
                'station_data': station_data,
                'recommendation': generate_placeholder_recommendation(),
                'error': str(inner_e)
            })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# Update the existing route to improve error handling
@app.route('/generate_recommendation')
def generate_recommendation_api():
    """API endpoint for generating recommendations"""
    try:
        station_id = request.args.get('station_id')
        if not station_id:
            return jsonify({'error': 'No station ID provided'}), 400
        
        print(f"Generating recommendation for station: {station_id}")
        
        try:
            # Try to generate the actual recommendation
            result = generate_conversion_recommendation(station_id)
            dashboard_path = create_dashboard_html(result)
            
            # Extract the recommendation text
            recommendation = result.get('recommendation', generate_placeholder_recommendation())
            
            # Get the filename part of the dashboard path
            dashboard_filename = os.path.basename(dashboard_path)
            
            return jsonify({
                'success': True,
                'dashboard_url': dashboard_filename,
                'recommendation': recommendation
            })
        except Exception as inner_e:
            # If there's an error, generate a fallback
            print(f"Error generating recommendation: {str(inner_e)}")
            import traceback
            print(traceback.format_exc())
            
            # Use placeholder recommendation
            from conversion_advisor import generate_placeholder_recommendation
            
            return jsonify({
                'success': True,
                'recommendation': generate_placeholder_recommendation(),
                'error': str(inner_e)
            })
            
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error in endpoint: {str(e)}")
        print(f"Traceback: {error_traceback}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_traceback
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """API endpoint for GPT chat interactions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_message = data.get('message', '')
        context = data.get('context', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Create a system message that includes context
        system_message = f"""
You are an AI advisor specializing in helping gas station owners convert to EV charging stations.
Your responses should be helpful, concise, and business-focused.

Here is the current recommendation context that the user is asking about:

{context}

When answering, focus on practical advice related to EV charging conversion decisions.
If the context above doesn't contain information needed to answer a question, be honest 
about limitations while still providing the most helpful response possible.
"""
        
        # Prepare messages for the chat API
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        try:
            from openai_config import OPENAI_API_KEY, OPENAI_API_ENDPOINT
            import requests
            
            # Call Azure OpenAI API
            headers = {
                "Content-Type": "application/json",
                "api-key": OPENAI_API_KEY,
            }
            
            payload = {
                "messages": messages,
                "max_tokens": 800,
                "temperature": 0.7
            }
            
            # Make the API call with a timeout
            response = requests.post(
                OPENAI_API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=15  # 15 second timeout
            )
            
            if response.status_code != 200:
                print(f"Error calling Azure OpenAI API: {response.status_code}")
                print(f"Response: {response.text}")
                raise Exception(f"API Error: {response.status_code}")
                
            # Extract and return the response
            ai_response = response.json()["choices"][0]["message"]["content"]
            
            return jsonify({
                'success': True,
                'response': ai_response
            })
            
        except Exception as api_error:
            # Log the error but provide a fallback response
            print(f"Error calling Azure OpenAI API: {str(api_error)}")
            import traceback
            print(traceback.format_exc())
            
            # Generate a basic response based on the question
            fallback_response = generate_fallback_chat_response(user_message)
            
            return jsonify({
                'success': True,
                'response': fallback_response,
                'used_fallback': True,
                'error': str(api_error)
            })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

def generate_fallback_chat_response(user_message):
    """Generate a reasonable fallback response based on the user's question"""
    user_message = user_message.lower()
    
    # Check for common question patterns
    if any(word in user_message for word in ['roi', 'return', 'investment', 'payback', 'profitable']):
        return """The ROI for EV charging stations typically ranges from 3-7 years depending on several factors:
        
1. Location and traffic volume
2. Charging speed (Level 2 vs. DC Fast)
3. Utilization rates
4. Electricity costs and pricing model
5. Available incentives and tax credits

For most gas stations, a phased approach starting with 1-2 chargers allows testing demand before larger investments."""

    elif any(word in user_message for word in ['cost', 'price', 'expensive', 'investment', 'budget']):
        return """The costs for installing EV charging stations vary widely:

• Level 2 charger: $2,000-$5,000 per port plus installation ($1,000-$5,000)
• DC Fast Charger: $25,000-$150,000 per unit plus installation ($10,000-$50,000)
• Additional costs may include utility upgrades, permits, and site preparation

Many utilities, states, and the federal government offer incentives that can offset 30-80% of these costs."""

    elif any(word in user_message for word in ['customer', 'attract', 'retention', 'spend']):
        return """EV drivers typically spend 15-45 minutes at charging stations, creating additional retail opportunities:

• EV owners have 30-40% higher average household incomes than ICE vehicle owners
• Food and beverage sales can increase 20-35% with proper amenities
• Additional services like WiFi, premium snacks, and comfortable seating can further increase spending
• Partner with nearby businesses for cross-promotion opportunities"""

    elif any(word in user_message for word in ['when', 'timing', 'right time', 'too early', 'too late']):
        return """Timing for EV charging conversion depends on your location and customer base:

• Urban/suburban areas with higher EV adoption rates offer immediate opportunities
• Highway locations are seeing growing demand from long-distance travelers
• Early movers can establish customer loyalty and capture government incentives
• Start small with 1-2 chargers to test demand before larger investments
• Many experts suggest acting within the next 12-24 months to stay competitive"""

    elif any(word in user_message for word in ['type', 'charger', 'level 2', 'fast', 'dc']):
        return """The optimal charger types depend on your location and customer patterns:

• Level 2 (7-22 kW): Good for locations where customers stay 1-4 hours
• DC Fast (50-350 kW): Ideal for highway locations or quick turnover
• Most successful sites offer a mix of both types to serve different needs

Consider future-proofing with higher power options or at least conduit installation for future expansion."""

    else:
        return """Based on industry standards, successful EV charging station conversions typically follow these guidelines:

1. Start with 1-2 chargers to test demand before larger investments
2. Choose locations near amenities where customers can spend time
3. Take advantage of available government incentives and utility programs
4. Consider a mix of charging speeds to accommodate different customer needs
5. Create a comfortable waiting environment with strong WiFi and amenities
6. Develop additional revenue streams beyond charging fees

I'd be happy to provide more specific guidance on any particular aspect of your conversion plan."""

def main():
    """Main function to run the dashboard"""
    # Ensure the output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Generate synthetic gas stations
    stations = generate_gas_stations(num_stations=50)
    
    # Calculate dashboard statistics
    stats = calculate_dashboard_stats(stations)
    
    # Create interactive map
    create_map(stations, save_file="static/station_map.html")
    print("Created station map at static/station_map.html")
    
    # Create EV adoption heatmap
    create_heatmap(stations, save_file="static/ev_adoption_heatmap.html")
    print("Created EV adoption heatmap at static/ev_adoption_heatmap.html")
    
    # Generate forecasts for top stations
    forecast_results = generate_forecasts(stations, top_n=5)
    print(f"Generated forecasts for {len(forecast_results)} stations")
    
    # Create dashboard HTML
    dashboard_path = create_dashboard_html(stations, stats, forecast_results)
    print(f"Dashboard generated at {dashboard_path}")
    
    print("\nStarting Flask app on port 8081...")
    print("Dashboard is self-contained, no additional server needed.")
    print("Visit http://localhost:8081/ to access the dashboard")
    
    # Start the Flask app
    app.run(debug=True, port=8081)

if __name__ == "__main__":
    # At the beginning of the main function or where processing starts, add:
    ensure_static_dir()
    main()