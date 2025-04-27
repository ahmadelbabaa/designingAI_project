"""
Data Visualizer
--------------
Utilities for visualizing charging station, session, and forecast data.
Provides functions for generating interactive maps, charts, and dashboards.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Optional, Union, Tuple
import folium
from folium.plugins import MarkerCluster
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

class DataVisualizer:
    """
    Visualizer for creating charts, maps, and visualizations of charging data.
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize the visualizer
        
        Args:
            output_dir: Directory to save visualization outputs
        """
        self.output_dir = output_dir
        self._ensure_output_dirs()
    
    def _ensure_output_dirs(self) -> None:
        """Ensure output directories exist"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'stations'), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'sessions'), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'forecasts'), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'dashboards'), exist_ok=True)
    
    def create_station_map(self, 
                          stations: pd.DataFrame, 
                          save_path: Optional[str] = None,
                          cluster: bool = True,
                          include_charger_info: bool = True) -> folium.Map:
        """
        Create an interactive map of charging stations
        
        Args:
            stations: DataFrame of stations with location data
            save_path: Path to save the HTML map (optional)
            cluster: Whether to cluster markers for better performance with many stations
            include_charger_info: Whether to include charger information in popups
            
        Returns:
            Folium map object
        """
        # Check if we have the required location data
        if 'location' not in stations.columns and ('latitude' not in stations.columns or 'longitude' not in stations.columns):
            raise ValueError("Station data must contain 'location' column or 'latitude'/'longitude' columns")
        
        # Extract latitude and longitude from location if needed
        if 'location' in stations.columns and 'latitude' not in stations.columns:
            # Assuming location is a dictionary with lat/lng keys
            stations['latitude'] = stations['location'].apply(lambda x: x.get('latitude') if isinstance(x, dict) else None)
            stations['longitude'] = stations['location'].apply(lambda x: x.get('longitude') if isinstance(x, dict) else None)
        
        # Calculate map center (average of all coordinates)
        valid_coords = stations.dropna(subset=['latitude', 'longitude'])
        if len(valid_coords) == 0:
            # Default to a reasonable center if no valid coordinates
            center = [39.8283, -98.5795]  # Center of the United States
            zoom_start = 4
        else:
            center = [valid_coords['latitude'].mean(), valid_coords['longitude'].mean()]
            zoom_start = 10 if len(valid_coords) < 100 else 6
        
        # Create the map
        m = folium.Map(location=center, zoom_start=zoom_start, tiles='OpenStreetMap')
        
        # Add stations to the map
        if cluster:
            marker_cluster = MarkerCluster().add_to(m)
        
        for _, station in valid_coords.iterrows():
            # Create popup content
            popup_content = f"""
            <b>{station.get('name', 'Station')}</b><br>
            ID: {station.get('station_id', 'Unknown')}<br>
            Operator: {station.get('operator', 'Unknown')}<br>
            """
            
            # Add charger information if available and requested
            if include_charger_info and 'chargers' in station and isinstance(station['chargers'], list):
                popup_content += "<b>Chargers:</b><br>"
                for charger in station['chargers']:
                    charger_type = charger.get('power_type', '')
                    power = charger.get('max_power_kw', '')
                    charger_id = charger.get('charger_id', '')
                    
                    popup_content += f"- {charger_id}: {charger_type} {power} kW<br>"
            
            # Create marker
            popup = folium.Popup(popup_content, max_width=300)
            marker = folium.Marker(
                location=[station['latitude'], station['longitude']],
                popup=popup,
                tooltip=station.get('name', f"Station {station.get('station_id', '')}")
            )
            
            # Add marker to the map (either to the cluster or directly to the map)
            if cluster:
                marker.add_to(marker_cluster)
            else:
                marker.add_to(m)
        
        # Save the map if a path is provided
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            m.save(save_path)
            print(f"Map saved to {save_path}")
        
        return m
    
    def create_session_summary(self, 
                              sessions: pd.DataFrame, 
                              save_dir: Optional[str] = None) -> Dict[str, plt.Figure]:
        """
        Create summary visualizations for charging session data
        
        Args:
            sessions: DataFrame of charging sessions
            save_dir: Directory to save the generated charts
            
        Returns:
            Dictionary of generated matplotlib figures
        """
        # Ensure we have the necessary columns
        required_cols = ['start_time', 'end_time', 'energy_delivered_kwh']
        missing_cols = [col for col in required_cols if col not in sessions.columns]
        if missing_cols:
            raise ValueError(f"Sessions data missing required columns: {missing_cols}")
        
        # Convert time columns to datetime if they aren't already
        for col in ['start_time', 'end_time']:
            if not pd.api.types.is_datetime64_dtype(sessions[col]):
                sessions[col] = pd.to_datetime(sessions[col])
        
        # Calculate session duration if not present
        if 'duration_minutes' not in sessions.columns:
            sessions['duration_minutes'] = (sessions['end_time'] - sessions['start_time']).dt.total_seconds() / 60
        
        # Create directory for saving if provided
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        
        # Initialize dictionary to store figures
        figures = {}
        
        # 1. Sessions by hour of day
        plt.figure(figsize=(12, 6))
        sessions['hour_of_day'] = sessions['start_time'].dt.hour
        hourly_counts = sessions['hour_of_day'].value_counts().sort_index()
        
        ax = hourly_counts.plot(kind='bar', color='skyblue')
        ax.set_title('Number of Charging Sessions by Hour of Day')
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Number of Sessions')
        ax.set_xticks(range(24))
        ax.set_xticklabels([f"{h:02d}:00" for h in range(24)])
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        figures['sessions_by_hour'] = plt.gcf()
        if save_dir:
            plt.savefig(os.path.join(save_dir, 'sessions_by_hour.png'), dpi=300)
        
        # 2. Session duration distribution
        plt.figure(figsize=(12, 6))
        
        # Filter out extreme outliers for better visualization
        duration_data = sessions['duration_minutes']
        duration_data = duration_data[duration_data < duration_data.quantile(0.99)]
        
        ax = sns.histplot(duration_data, bins=30, kde=True)
        ax.set_title('Distribution of Charging Session Durations')
        ax.set_xlabel('Duration (minutes)')
        ax.set_ylabel('Frequency')
        plt.tight_layout()
        
        figures['duration_distribution'] = plt.gcf()
        if save_dir:
            plt.savefig(os.path.join(save_dir, 'duration_distribution.png'), dpi=300)
        
        # 3. Energy delivered distribution
        plt.figure(figsize=(12, 6))
        
        # Filter out extreme outliers for better visualization
        energy_data = sessions['energy_delivered_kwh']
        energy_data = energy_data[energy_data < energy_data.quantile(0.99)]
        
        ax = sns.histplot(energy_data, bins=30, kde=True)
        ax.set_title('Distribution of Energy Delivered per Session')
        ax.set_xlabel('Energy Delivered (kWh)')
        ax.set_ylabel('Frequency')
        plt.tight_layout()
        
        figures['energy_distribution'] = plt.gcf()
        if save_dir:
            plt.savefig(os.path.join(save_dir, 'energy_distribution.png'), dpi=300)
        
        # 4. Sessions by day of week
        plt.figure(figsize=(12, 6))
        sessions['day_of_week'] = sessions['start_time'].dt.day_name()
        # Ensure days are in order
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = sessions['day_of_week'].value_counts().reindex(day_order)
        
        ax = day_counts.plot(kind='bar', color='lightgreen')
        ax.set_title('Number of Charging Sessions by Day of Week')
        ax.set_xlabel('Day of Week')
        ax.set_ylabel('Number of Sessions')
        plt.tight_layout()
        
        figures['sessions_by_day'] = plt.gcf()
        if save_dir:
            plt.savefig(os.path.join(save_dir, 'sessions_by_day.png'), dpi=300)
        
        # 5. Energy vs Duration scatter plot
        plt.figure(figsize=(10, 8))
        
        # Filter out extreme outliers for better visualization
        filtered_data = sessions[
            (sessions['duration_minutes'] < sessions['duration_minutes'].quantile(0.99)) & 
            (sessions['energy_delivered_kwh'] < sessions['energy_delivered_kwh'].quantile(0.99))
        ]
        
        ax = sns.scatterplot(
            data=filtered_data, 
            x='duration_minutes', 
            y='energy_delivered_kwh',
            alpha=0.6
        )
        ax.set_title('Energy Delivered vs. Session Duration')
        ax.set_xlabel('Duration (minutes)')
        ax.set_ylabel('Energy Delivered (kWh)')
        
        # Add a trend line
        sns.regplot(
            data=filtered_data, 
            x='duration_minutes', 
            y='energy_delivered_kwh',
            scatter=False,
            ax=ax
        )
        
        plt.tight_layout()
        
        figures['energy_vs_duration'] = plt.gcf()
        if save_dir:
            plt.savefig(os.path.join(save_dir, 'energy_vs_duration.png'), dpi=300)
        
        return figures
    
    def create_forecast_visualizations(self, 
                                      forecasts: List[Dict[str, Any]], 
                                      save_dir: Optional[str] = None,
                                      include_ci: bool = True) -> Dict[str, Union[plt.Figure, go.Figure]]:
        """
        Create visualizations for forecast data
        
        Args:
            forecasts: List of forecast objects
            save_dir: Directory to save the generated charts
            include_ci: Whether to include confidence intervals
            
        Returns:
            Dictionary of generated figures
        """
        # Create directory for saving if provided
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
        
        # Initialize dictionary to store figures
        figures = {}
        
        # Process each forecast
        for forecast in forecasts:
            # Skip if we don't have the required data
            if 'forecasted_values' not in forecast or not forecast['forecasted_values']:
                continue
            
            station_id = forecast.get('station_id', 'unknown')
            forecast_id = forecast.get('forecast_id', f"forecast-{station_id}")
            
            # Convert forecasted values to a DataFrame for easier plotting
            forecast_points = []
            for point in forecast['forecasted_values']:
                point_data = {
                    'timestamp': pd.to_datetime(point['timestamp']),
                    'predicted_demand_kwh': point.get('predicted_demand_kwh', 0)
                }
                
                # Add confidence interval data if available
                if include_ci and 'prediction_interval' in point:
                    point_data['lower_bound'] = point['prediction_interval'].get('lower_bound', None)
                    point_data['upper_bound'] = point['prediction_interval'].get('upper_bound', None)
                
                forecast_points.append(point_data)
            
            if not forecast_points:
                continue
                
            df = pd.DataFrame(forecast_points)
            
            # Create interactive plotly figure
            fig = go.Figure()
            
            # Add the main forecast line
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['predicted_demand_kwh'],
                mode='lines+markers',
                name='Predicted Demand (kWh)',
                line=dict(color='blue', width=2)
            ))
            
            # Add confidence intervals if available
            if include_ci and 'lower_bound' in df.columns and 'upper_bound' in df.columns:
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['upper_bound'],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False
                ))
                
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['lower_bound'],
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',
                    fillcolor='rgba(0, 0, 255, 0.2)',
                    name='95% Confidence Interval'
                ))
            
            # Set the title and labels
            fig.update_layout(
                title=f"Energy Demand Forecast for Station {station_id}",
                xaxis_title="Date & Time",
                yaxis_title="Predicted Energy Demand (kWh)",
                hovermode="x unified"
            )
            
            # Save the figure if a directory is provided
            figures[f"forecast_{station_id}"] = fig
            if save_dir:
                fig.write_html(os.path.join(save_dir, f"forecast_{station_id}.html"))
                fig.write_image(os.path.join(save_dir, f"forecast_{station_id}.png"), width=1200, height=800)
        
        # Create a comparative chart if we have multiple forecasts
        if len(forecasts) > 1:
            # Create a comparison figure with total daily demand for each station
            daily_demand = {}
            
            for forecast in forecasts:
                station_id = forecast.get('station_id', 'unknown')
                if 'forecasted_values' not in forecast or not forecast['forecasted_values']:
                    continue
                
                # Convert to DataFrame
                df = pd.DataFrame([{
                    'timestamp': pd.to_datetime(point['timestamp']),
                    'predicted_demand_kwh': point.get('predicted_demand_kwh', 0)
                } for point in forecast['forecasted_values']])
                
                # Group by day and sum up the demand
                df['date'] = df['timestamp'].dt.date
                daily = df.groupby('date')['predicted_demand_kwh'].sum().reset_index()
                
                daily_demand[station_id] = daily
            
            # Create the comparison chart
            if daily_demand:
                fig = go.Figure()
                
                for station_id, data in daily_demand.items():
                    fig.add_trace(go.Bar(
                        x=data['date'],
                        y=data['predicted_demand_kwh'],
                        name=f"Station {station_id}"
                    ))
                
                fig.update_layout(
                    title="Daily Energy Demand Comparison Across Stations",
                    xaxis_title="Date",
                    yaxis_title="Predicted Daily Energy Demand (kWh)",
                    barmode='group'
                )
                
                figures["station_comparison"] = fig
                if save_dir:
                    fig.write_html(os.path.join(save_dir, "station_comparison.html"))
                    fig.write_image(os.path.join(save_dir, "station_comparison.png"), width=1200, height=800)
        
        return figures
    
    def create_dashboard(self, 
                         stations: Optional[pd.DataFrame] = None, 
                         sessions: Optional[pd.DataFrame] = None,
                         forecasts: Optional[List[Dict[str, Any]]] = None,
                         save_path: Optional[str] = None) -> str:
        """
        Create an HTML dashboard combining visualizations from multiple data sources
        
        Args:
            stations: DataFrame of stations
            sessions: DataFrame of sessions
            forecasts: List of forecast objects
            save_path: Path to save the HTML dashboard
            
        Returns:
            HTML string of the dashboard
        """
        dashboard_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EV Charging Data Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }
                .dashboard {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    background-color: #2c3e50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    margin-bottom: 20px;
                    border-radius: 5px;
                }
                .card {
                    background-color: white;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                    padding: 20px;
                }
                .chart-container {
                    width: 100%;
                    height: 400px;
                    margin-bottom: 20px;
                }
                .map-container {
                    width: 100%;
                    height: 500px;
                    margin-bottom: 20px;
                }
                .row {
                    display: flex;
                    flex-wrap: wrap;
                    margin-right: -10px;
                    margin-left: -10px;
                }
                .col {
                    flex: 1;
                    padding: 0 10px;
                    min-width: 300px;
                }
                @media (max-width: 768px) {
                    .col {
                        flex: 0 0 100%;
                    }
                }
                h1, h2, h3 {
                    color: #2c3e50;
                }
                .summary-stats {
                    display: flex;
                    justify-content: space-between;
                    flex-wrap: wrap;
                }
                .stat-card {
                    background-color: #f9f9f9;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin-bottom: 15px;
                    flex: 1;
                    min-width: 200px;
                    margin-right: 10px;
                }
                .stat-card h3 {
                    margin-top: 0;
                    font-size: 16px;
                    color: #7f8c8d;
                }
                .stat-card p {
                    font-size: 24px;
                    font-weight: bold;
                    margin: 5px 0 0 0;
                    color: #2c3e50;
                }
            </style>
        </head>
        <body>
            <div class="dashboard">
                <div class="header">
                    <h1>EV Charging Data Dashboard</h1>
                    <p>Real-time visualizations and analytics for EV charging infrastructure</p>
                </div>
        """
        
        # Add summary statistics section
        dashboard_html += """
                <div class="card">
                    <h2>Summary Statistics</h2>
                    <div class="summary-stats">
        """
        
        # Station stats
        if stations is not None:
            total_stations = len(stations)
            total_chargers = 0
            for _, station in stations.iterrows():
                if 'chargers' in station and isinstance(station['chargers'], list):
                    total_chargers += len(station['chargers'])
                elif 'charger_count' in station:
                    total_chargers += station['charger_count']
            
            dashboard_html += f"""
                        <div class="stat-card">
                            <h3>Total Stations</h3>
                            <p>{total_stations}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Total Chargers</h3>
                            <p>{total_chargers}</p>
                        </div>
            """
        
        # Session stats
        if sessions is not None:
            total_sessions = len(sessions)
            
            # Convert to datetime if needed
            for col in ['start_time', 'end_time']:
                if col in sessions.columns and not pd.api.types.is_datetime64_dtype(sessions[col]):
                    sessions[col] = pd.to_datetime(sessions[col])
            
            total_energy = sessions['energy_delivered_kwh'].sum() if 'energy_delivered_kwh' in sessions.columns else 0
            avg_duration = sessions['duration_minutes'].mean() if 'duration_minutes' in sessions.columns else 0
            
            dashboard_html += f"""
                        <div class="stat-card">
                            <h3>Total Sessions</h3>
                            <p>{total_sessions}</p>
                        </div>
                        <div class="stat-card">
                            <h3>Total Energy Delivered</h3>
                            <p>{total_energy:.2f} kWh</p>
                        </div>
                        <div class="stat-card">
                            <h3>Avg Session Duration</h3>
                            <p>{avg_duration:.1f} min</p>
                        </div>
            """
        
        dashboard_html += """
                    </div>
                </div>
        """
        
        # Add station map if we have station data
        if stations is not None:
            try:
                # Create the map
                map_path = os.path.join(self.output_dir, 'dashboards', 'station_map.html')
                self.create_station_map(stations, save_path=map_path)
                
                dashboard_html += """
                <div class="card">
                    <h2>Charging Station Map</h2>
                    <div class="map-container">
                        <iframe src="station_map.html" width="100%" height="100%" frameborder="0"></iframe>
                    </div>
                </div>
                """
            except Exception as e:
                print(f"Error creating station map: {e}")
        
        # Add session visualizations if we have session data
        if sessions is not None:
            try:
                # Create the session visualizations
                session_dir = os.path.join(self.output_dir, 'dashboards', 'sessions')
                os.makedirs(session_dir, exist_ok=True)
                session_figures = self.create_session_summary(sessions, save_dir=session_dir)
                
                dashboard_html += """
                <div class="card">
                    <h2>Charging Session Analysis</h2>
                    <div class="row">
                        <div class="col">
                            <div class="chart-container">
                                <img src="sessions/sessions_by_hour.png" width="100%" />
                            </div>
                        </div>
                        <div class="col">
                            <div class="chart-container">
                                <img src="sessions/sessions_by_day.png" width="100%" />
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col">
                            <div class="chart-container">
                                <img src="sessions/duration_distribution.png" width="100%" />
                            </div>
                        </div>
                        <div class="col">
                            <div class="chart-container">
                                <img src="sessions/energy_distribution.png" width="100%" />
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col">
                            <div class="chart-container">
                                <img src="sessions/energy_vs_duration.png" width="100%" />
                            </div>
                        </div>
                    </div>
                </div>
                """
            except Exception as e:
                print(f"Error creating session visualizations: {e}")
        
        # Add forecast visualizations if we have forecast data
        if forecasts is not None and len(forecasts) > 0:
            try:
                # Create the forecast visualizations
                forecast_dir = os.path.join(self.output_dir, 'dashboards', 'forecasts')
                os.makedirs(forecast_dir, exist_ok=True)
                forecast_figures = self.create_forecast_visualizations(forecasts, save_dir=forecast_dir)
                
                dashboard_html += """
                <div class="card">
                    <h2>Energy Demand Forecasts</h2>
                """
                
                # Add each forecast plot
                for station_id, _ in forecast_figures.items():
                    if station_id == "station_comparison":
                        continue
                    
                    dashboard_html += f"""
                    <div class="chart-container">
                        <iframe src="forecasts/{station_id}.html" width="100%" height="100%" frameborder="0"></iframe>
                    </div>
                    """
                
                # Add station comparison if available
                if "station_comparison" in forecast_figures:
                    dashboard_html += """
                    <div class="chart-container">
                        <iframe src="forecasts/station_comparison.html" width="100%" height="100%" frameborder="0"></iframe>
                    </div>
                    """
                
                dashboard_html += """
                </div>
                """
            except Exception as e:
                print(f"Error creating forecast visualizations: {e}")
        
        # Close the HTML
        dashboard_html += """
            </div>
        </body>
        </html>
        """
        
        # Save the dashboard if a path is provided
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w') as f:
                f.write(dashboard_html)
            print(f"Dashboard saved to {save_path}")
        
        return dashboard_html

# Command line interface
if __name__ == "__main__":
    import argparse
    from utils.unified_data_repository import UnifiedDataRepository
    
    parser = argparse.ArgumentParser(description="Create visualizations from charging data")
    parser.add_argument("--output-dir", type=str, default="output",
                       help="Directory to save visualization outputs")
    parser.add_argument("--station-map", action="store_true",
                       help="Create a map of charging stations")
    parser.add_argument("--session-summary", action="store_true",
                       help="Create summary visualizations for charging sessions")
    parser.add_argument("--forecast-viz", action="store_true",
                       help="Create visualizations for forecasts")
    parser.add_argument("--dashboard", action="store_true",
                       help="Create a comprehensive dashboard")
    
    args = parser.parse_args()
    
    # Initialize visualizer and repository
    visualizer = DataVisualizer(output_dir=args.output_dir)
    repository = UnifiedDataRepository()
    
    # Check what visualizations to create
    if args.station_map:
        stations = repository.get_dataset("stations")
        if stations is not None:
            save_path = os.path.join(args.output_dir, "stations", "station_map.html")
            visualizer.create_station_map(stations, save_path=save_path)
            print(f"Station map saved to {save_path}")
    
    if args.session_summary:
        sessions = repository.get_dataset("sessions")
        if sessions is not None:
            save_dir = os.path.join(args.output_dir, "sessions")
            visualizer.create_session_summary(sessions, save_dir=save_dir)
            print(f"Session visualizations saved to {save_dir}")
    
    if args.forecast_viz:
        forecasts = repository.get_dataset("forecasts")
        if forecasts is not None:
            save_dir = os.path.join(args.output_dir, "forecasts")
            visualizer.create_forecast_visualizations(forecasts, save_dir=save_dir)
            print(f"Forecast visualizations saved to {save_dir}")
    
    if args.dashboard:
        # Get all data types for the dashboard
        stations = repository.get_dataset("stations")
        sessions = repository.get_dataset("sessions")
        forecasts = repository.get_dataset("forecasts")
        
        save_path = os.path.join(args.output_dir, "dashboards", "dashboard.html")
        visualizer.create_dashboard(stations, sessions, forecasts, save_path=save_path)
        print(f"Dashboard saved to {save_path}") 