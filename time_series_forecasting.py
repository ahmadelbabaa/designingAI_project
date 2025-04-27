#!/usr/bin/env python3
"""
Time Series Forecasting Module for HPC Station Analysis
Provides functions for generating, forecasting, and visualizing charging station data
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
import json

# Ensure forecast output directory exists
os.makedirs('output/forecasts', exist_ok=True)

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

if __name__ == "__main__":
    # Test the module
    print("Generating forecasts for test stations...")
    
    # Generate forecasts for 3 test stations
    test_station_ids = ["GS-0001", "GS-0002", "GS-0003"]
    forecast_results = generate_multiple_station_forecasts(test_station_ids, 
                                                          historical_days=180, 
                                                          forecast_days=90)
    
    # Analyze trends
    trends = analyze_forecast_trends(forecast_results)
    
    print(f"Generated forecasts for {len(forecast_results)} stations")
    print(f"Overall average daily sessions: {trends['overall']['avg_sessions']}")
    print(f"Overall average daily energy: {trends['overall']['avg_energy']} kWh")
    print(f"Overall total revenue: ${trends['overall']['total_revenue']:,.2f}")
    print("Forecast plots saved to output/forecasts/") 