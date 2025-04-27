# EV Charging Pattern Analysis - Detailed Implementation Plan

## Introduction

This document provides an **extremely detailed, step-by-step implementation plan** for the EV Charging Pattern Analysis component. Follow this plan **exactly** to ensure proper integration with the existing system.

## Directory Structure Reference

```
/Users/skarnz/hpc_prediction_analysis/          # Project root
├── data/                                       # Data directory
│   ├── ev_charging_patterns.csv                # Primary dataset for analysis
│   ├── station_data_dataverse.csv              # Station metadata
│   ├── hpc_usage_master.csv                    # Combined dataset
│   └── ...
├── output/                                     # Visualization outputs
│   ├── charging_patterns/                      # Create this directory
│   │   ├── hourly_patterns.png                 # Standard time pattern visual
│   │   ├── daily_patterns.png                  # Daily usage patterns
│   │   ├── station_comparison.html             # Interactive station comparison
│   │   └── ...
│   └── ...
├── templates/                                  # Flask templates
│   ├── base.html                               # Base template (DO NOT MODIFY)
│   ├── dashboard.html                          # Main dashboard (ONLY modify designated sections)
│   ├── charging_patterns.html                  # Create this file
│   └── ...
├── static/                                     # Static assets
│   ├── js/
│   │   ├── dashboard_controller.js             # Main controller (DO NOT MODIFY)
│   │   ├── charging_patterns.js                # Create this file
│   │   └── ...
│   ├── css/
│   │   ├── dashboard_styles.css                # Main styles (ONLY append to)
│   │   └── ...
│   └── ...
├── config/                                     # Configuration files
│   ├── dashboard_components.json               # Component registry (ONLY append to)
│   └── ...
├── enhanced_dashboard.py                       # Flask application (ONLY add routes)
├── conversion_advisor.py                       # Existing component (DO NOT MODIFY)
├── time_series_forecasting.py                  # Existing component (DO NOT MODIFY)
├── ev_charging_analysis.py                     # Create this file
└── ...
```

## Dataset Structure Reference

**ev_charging_patterns.csv structure:**
- `session_id`: Unique identifier for charging session (string)
- `station_id`: Station identifier (string)
- `start_time`: Session start time in ISO format (YYYY-MM-DD HH:MM:SS)
- `end_time`: Session end time in ISO format (YYYY-MM-DD HH:MM:SS)
- `energy_delivered`: Energy in kWh (float)
- `user_id`: User identifier (string)
- `cost`: Cost in USD (float)
- `vehicle_type`: Type of vehicle (string)

## Implementation Steps

### PHASE 1: Environment Setup and Exploration (Days 1-2)

#### Step 1.1: Create Output Directory
```bash
mkdir -p output/charging_patterns
```

#### Step 1.2: Explore Data Structure
```python
# Create a minimal script to analyze data structure
import pandas as pd

def explore_dataset():
    # Load the dataset
    data_path = 'data/ev_charging_patterns.csv'
    df = pd.read_csv(data_path)
    
    # Examine structure
    print("Dataset shape:", df.shape)
    print("\nColumn names:", df.columns.tolist())
    print("\nData types:\n", df.dtypes)
    print("\nSample data (5 rows):\n", df.head(5))
    print("\nMissing values:\n", df.isnull().sum())
    
    # Date/time range
    if 'start_time' in df.columns:
        df['start_time'] = pd.to_datetime(df['start_time'])
        print("\nDate range:", df['start_time'].min(), "to", df['start_time'].max())
    
    # Summary statistics
    print("\nSummary statistics:\n", df.describe())

if __name__ == "__main__":
    explore_dataset()
```

**Validation point:** 
- Verify dataset has expected columns
- Check for missing values
- Note data ranges and distributions

### PHASE 2: Core Analysis Functions Development (Days 3-7)

#### Step 2.1: Create Initial File Structure
Create `ev_charging_analysis.py` with this skeleton:

```python
"""
EV Charging Pattern Analysis
----------------------------
This module analyzes EV charging patterns based on historical data.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Tuple
import json
import datetime

# Configure plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("viridis")

# Constants
DATA_PATH = 'data/ev_charging_patterns.csv'
STATION_DATA_PATH = 'data/station_data_dataverse.csv'
OUTPUT_DIR = 'output/charging_patterns'


def load_data() -> pd.DataFrame:
    """
    Load and preprocess the charging patterns dataset.
    
    Returns:
        pd.DataFrame: Preprocessed charging data
    """
    # Load data
    df = pd.read_csv(DATA_PATH)
    
    # Convert timestamps to datetime
    for col in ['start_time', 'end_time']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    # Calculate session duration in hours
    if 'start_time' in df.columns and 'end_time' in df.columns:
        df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600
    
    return df


def analyze_time_patterns(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze temporal patterns in charging data.
    
    Args:
        data (pd.DataFrame): Charging session data with timestamps
        
    Returns:
        Dict[str, Any]: Dictionary containing temporal pattern analysis results
    """
    # TODO: Implement time pattern analysis
    return {}


def analyze_station_utilization(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze station utilization patterns.
    
    Args:
        data (pd.DataFrame): Charging session data
        
    Returns:
        Dict[str, Any]: Dictionary containing station utilization analysis results
    """
    # TODO: Implement station utilization analysis
    return {}


def analyze_energy_delivery(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze energy delivery patterns.
    
    Args:
        data (pd.DataFrame): Charging session data
        
    Returns:
        Dict[str, Any]: Dictionary containing energy delivery analysis results
    """
    # TODO: Implement energy delivery analysis
    return {}


def analyze_session_duration(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze session duration patterns.
    
    Args:
        data (pd.DataFrame): Charging session data
        
    Returns:
        Dict[str, Any]: Dictionary containing session duration analysis results
    """
    # TODO: Implement session duration analysis
    return {}


def analyze_user_behavior(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze user behavior patterns.
    
    Args:
        data (pd.DataFrame): Charging session data
        
    Returns:
        Dict[str, Any]: Dictionary containing user behavior analysis results
    """
    # TODO: Implement user behavior analysis
    return {}


def generate_visualizations(results: Dict[str, Dict[str, Any]], output_dir: str) -> List[str]:
    """
    Generate visualizations based on analysis results.
    
    Args:
        results (Dict[str, Dict[str, Any]]): Analysis results
        output_dir (str): Directory to save visualizations
        
    Returns:
        List[str]: List of paths to generated visualizations
    """
    # TODO: Implement visualization generation
    return []


def run_analysis() -> Dict[str, Dict[str, Any]]:
    """
    Run the complete analysis pipeline.
    
    Returns:
        Dict[str, Dict[str, Any]]: Complete analysis results
    """
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load and preprocess data
    data = load_data()
    
    # Run analysis functions
    results = {
        'time_patterns': analyze_time_patterns(data),
        'station_utilization': analyze_station_utilization(data),
        'energy_delivery': analyze_energy_delivery(data),
        'session_duration': analyze_session_duration(data),
        'user_behavior': analyze_user_behavior(data)
    }
    
    # Generate visualizations
    visualization_paths = generate_visualizations(results, OUTPUT_DIR)
    results['visualization_paths'] = visualization_paths
    
    return results


if __name__ == "__main__":
    results = run_analysis()
    print(f"Analysis complete. Results available in {OUTPUT_DIR}")
```

**Validation point:**
- Verify the script runs without errors
- Verify the functions are properly defined
- Verify the imports are working

#### Step 2.2: Implement Time Pattern Analysis

Update the `analyze_time_patterns` function:

```python
def analyze_time_patterns(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze temporal patterns in charging data.
    
    Args:
        data (pd.DataFrame): Charging session data with timestamps
        
    Returns:
        Dict[str, Any]: Dictionary containing temporal pattern analysis results
    """
    results = {}
    
    # Ensure datetime columns are properly formatted
    if 'start_time' not in data.columns:
        return {'error': 'start_time column not found in dataset'}
    
    # Extract time components
    data['hour'] = data['start_time'].dt.hour
    data['day_of_week'] = data['start_time'].dt.dayofweek
    data['day_name'] = data['start_time'].dt.day_name()
    data['month'] = data['start_time'].dt.month
    data['year'] = data['start_time'].dt.year
    data['date'] = data['start_time'].dt.date
    
    # Hourly distribution
    hourly_counts = data.groupby('hour').size()
    hourly_energy = data.groupby('hour')['energy_delivered'].sum()
    
    results['hourly_distribution'] = {
        'counts': hourly_counts.to_dict(),
        'energy': hourly_energy.to_dict()
    }
    
    # Daily distribution
    daily_counts = data.groupby('day_of_week').size()
    daily_energy = data.groupby('day_of_week')['energy_delivered'].sum()
    
    results['daily_distribution'] = {
        'counts': daily_counts.to_dict(),
        'energy': daily_energy.to_dict(),
        'day_names': {i: day for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])}
    }
    
    # Monthly distribution
    monthly_counts = data.groupby('month').size()
    monthly_energy = data.groupby('month')['energy_delivered'].sum()
    
    results['monthly_distribution'] = {
        'counts': monthly_counts.to_dict(),
        'energy': monthly_energy.to_dict()
    }
    
    # Time series trend (daily)
    daily_time_series = data.groupby('date').agg({
        'energy_delivered': 'sum',
        'session_id': 'count'
    })
    daily_time_series.columns = ['total_energy', 'session_count']
    
    # Convert to serializable format
    results['daily_time_series'] = {
        'dates': [str(date) for date in daily_time_series.index],
        'energy': daily_time_series['total_energy'].tolist(),
        'counts': daily_time_series['session_count'].tolist()
    }
    
    # Peak usage times
    hourly_avg = data.groupby('hour')['energy_delivered'].mean()
    peak_hour = hourly_avg.idxmax()
    
    results['peak_usage'] = {
        'peak_hour': int(peak_hour),
        'peak_hour_avg_energy': float(hourly_avg[peak_hour]),
        'hourly_avg_energy': hourly_avg.to_dict()
    }
    
    return results
```

**Validation point:**
- Run the function on sample data
- Verify all expected results are produced
- Check calculation correctness

#### Step 2.3: Implement Station Utilization Analysis

Update the `analyze_station_utilization` function:

```python
def analyze_station_utilization(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze station utilization patterns.
    
    Args:
        data (pd.DataFrame): Charging session data
        
    Returns:
        Dict[str, Any]: Dictionary containing station utilization analysis results
    """
    results = {}
    
    # Station usage counts
    station_counts = data.groupby('station_id').size().sort_values(ascending=False)
    station_energy = data.groupby('station_id')['energy_delivered'].sum().sort_values(ascending=False)
    station_duration = data.groupby('station_id')['duration'].sum().sort_values(ascending=False)
    
    # Top 10 most used stations
    top_stations = station_counts.head(10)
    top_energy_stations = station_energy.head(10)
    
    results['top_stations'] = {
        'by_usage': {
            'station_ids': top_stations.index.tolist(),
            'session_counts': top_stations.tolist()
        },
        'by_energy': {
            'station_ids': top_energy_stations.index.tolist(),
            'energy_delivered': top_energy_stations.tolist()
        }
    }
    
    # Calculate utilization rate (assuming 24hr availability)
    # This is simplified and would need actual station operational hours for precision
    station_time_coverage = data.groupby('station_id').apply(
        lambda x: (x['duration'].sum() / (24 * len(x['start_time'].dt.date.unique()))) * 100
    ).sort_values(ascending=False)
    
    results['utilization_rate'] = {
        'station_ids': station_time_coverage.index.tolist(),
        'utilization_percentage': station_time_coverage.tolist()
    }
    
    # Average session metrics by station
    station_avg_metrics = data.groupby('station_id').agg({
        'duration': 'mean',
        'energy_delivered': 'mean'
    }).sort_values(by='energy_delivered', ascending=False)
    
    results['station_averages'] = {
        'station_ids': station_avg_metrics.index.tolist(),
        'avg_duration': station_avg_metrics['duration'].tolist(),
        'avg_energy': station_avg_metrics['energy_delivered'].tolist()
    }
    
    # Station usage patterns over time of day
    # Create a pivot table of hour vs station
    station_hour_usage = pd.pivot_table(
        data, 
        values='energy_delivered',
        index='hour',
        columns='station_id',
        aggfunc='sum',
        fill_value=0
    )
    
    # Convert to serializable format
    results['hourly_station_usage'] = {
        'hours': station_hour_usage.index.tolist(),
        'stations': station_hour_usage.columns.tolist(),
        'energy_matrix': station_hour_usage.values.tolist()
    }
    
    return results
```

**Continue implementing the remaining analysis functions following the same pattern.**

### PHASE 3: Visualization Generation (Days 8-12)

#### Step 3.1: Implement Time Pattern Visualizations

Update the `generate_visualizations` function with time pattern visualizations:

```python
def generate_time_pattern_visualizations(time_results: Dict[str, Any], output_dir: str) -> List[str]:
    """
    Generate visualizations for time pattern analysis.
    
    Args:
        time_results (Dict[str, Any]): Time pattern analysis results
        output_dir (str): Output directory for visualizations
        
    Returns:
        List[str]: Paths to generated visualizations
    """
    visualization_paths = []
    
    # Hourly distribution visualization
    plt.figure(figsize=(12, 6))
    hours = list(time_results['hourly_distribution']['counts'].keys())
    counts = list(time_results['hourly_distribution']['counts'].values())
    energy = list(time_results['hourly_distribution']['energy'].values())
    
    ax1 = plt.subplot(111)
    ax1.bar(hours, counts, alpha=0.7, label='Session Count')
    ax1.set_xlabel('Hour of Day')
    ax1.set_ylabel('Number of Sessions')
    ax1.set_title('Charging Sessions by Hour of Day')
    ax1.set_xticks(range(0, 24))
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    ax2 = ax1.twinx()
    ax2.plot(hours, energy, color='red', marker='o', label='Energy Delivered (kWh)')
    ax2.set_ylabel('Total Energy Delivered (kWh)')
    
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper center')
    
    plt.tight_layout()
    hourly_path = os.path.join(output_dir, 'hourly_patterns.png')
    plt.savefig(hourly_path, dpi=300)
    plt.close()
    visualization_paths.append(hourly_path)
    
    # Daily distribution visualization
    plt.figure(figsize=(12, 6))
    days = list(range(7))
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    counts = [time_results['daily_distribution']['counts'].get(day, 0) for day in days]
    energy = [time_results['daily_distribution']['energy'].get(day, 0) for day in days]
    
    ax1 = plt.subplot(111)
    ax1.bar(day_names, counts, alpha=0.7, label='Session Count')
    ax1.set_xlabel('Day of Week')
    ax1.set_ylabel('Number of Sessions')
    ax1.set_title('Charging Sessions by Day of Week')
    plt.xticks(rotation=45)
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    ax2 = ax1.twinx()
    ax2.plot(day_names, energy, color='red', marker='o', label='Energy Delivered (kWh)')
    ax2.set_ylabel('Total Energy Delivered (kWh)')
    
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper center')
    
    plt.tight_layout()
    daily_path = os.path.join(output_dir, 'daily_patterns.png')
    plt.savefig(daily_path, dpi=300)
    plt.close()
    visualization_paths.append(daily_path)
    
    # Time series visualization
    plt.figure(figsize=(15, 7))
    dates = [datetime.datetime.strptime(date, '%Y-%m-%d').date() for date in time_results['daily_time_series']['dates']]
    energy = time_results['daily_time_series']['energy']
    counts = time_results['daily_time_series']['counts']
    
    ax1 = plt.subplot(111)
    ax1.plot(dates, counts, label='Session Count')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Number of Sessions')
    ax1.set_title('Daily Charging Sessions and Energy Delivery Over Time')
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    ax2 = ax1.twinx()
    ax2.plot(dates, energy, color='red', label='Energy Delivered (kWh)')
    ax2.set_ylabel('Total Energy Delivered (kWh)')
    
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left')
    
    plt.tight_layout()
    time_series_path = os.path.join(output_dir, 'time_series.png')
    plt.savefig(time_series_path, dpi=300)
    plt.close()
    visualization_paths.append(time_series_path)
    
    # Interactive visualization using Plotly (if installed)
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # Create hourly heatmap by day of week
        hour_day_pivot = pd.DataFrame({
            'hour': np.repeat(range(24), 7),
            'day': np.tile(range(7), 24),
            'count': np.random.rand(24*7) * 100  # Replace with actual data
        })
        
        fig = px.density_heatmap(
            hour_day_pivot, 
            x='hour', 
            y='day',
            z='count', 
            labels={'hour': 'Hour of Day', 'day': 'Day of Week', 'count': 'Session Count'},
            title='Charging Session Density by Hour and Day',
            color_continuous_scale='viridis'
        )
        
        # Update y-axis to show day names
        fig.update_yaxes(
            tickmode='array',
            tickvals=list(range(7)),
            ticktext=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        )
        
        # Update layout
        fig.update_layout(
            xaxis=dict(tickmode='linear', tick0=0, dtick=1),
            width=1000,
            height=600
        )
        
        # Save as interactive HTML
        heatmap_path = os.path.join(output_dir, 'hourly_heatmap.html')
        fig.write_html(heatmap_path)
        visualization_paths.append(heatmap_path)
    except ImportError:
        print("Plotly not installed. Skipping interactive visualizations.")
    
    return visualization_paths
```

**Continue implementing visualizations for other analysis components.**

### PHASE 4: Dashboard Integration (Days 13-17)

#### Step 4.1: Create Template File

Create `templates/charging_patterns.html`:

```html
{% extends "base.html" %}

{% block title %}EV Charging Patterns Analysis{% endblock %}

{% block content %}
<div class="container mt-4">
    <h1 class="dashboard-title">EV Charging Patterns Analysis</h1>
    
    <div class="row mt-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h2 class="card-title">Time-Based Patterns</h2>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h3>Hourly Distribution</h3>
                            <img src="{{ url_for('static', filename='../output/charging_patterns/hourly_patterns.png') }}" 
                                 class="img-fluid" alt="Hourly Charging Patterns">
                        </div>
                        <div class="col-md-6">
                            <h3>Daily Distribution</h3>
                            <img src="{{ url_for('static', filename='../output/charging_patterns/daily_patterns.png') }}" 
                                 class="img-fluid" alt="Daily Charging Patterns">
                        </div>
                    </div>
                    <div class="row mt-4">
                        <div class="col-md-12">
                            <h3>Charging Activity Over Time</h3>
                            <img src="{{ url_for('static', filename='../output/charging_patterns/time_series.png') }}" 
                                 class="img-fluid" alt="Time Series Analysis">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h2 class="card-title">Station Utilization</h2>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h3>Top Stations by Usage</h3>
                            <div id="top-stations-chart" style="height: 400px;"></div>
                        </div>
                        <div class="col-md-6">
                            <h3>Station Utilization Rates</h3>
                            <div id="utilization-chart" style="height: 400px;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header bg-info text-white">
                    <h2 class="card-title">Energy Delivery Analysis</h2>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h3>Energy Delivery Distribution</h3>
                            <img src="{{ url_for('static', filename='../output/charging_patterns/energy_distribution.png') }}" 
                                 class="img-fluid" alt="Energy Distribution">
                        </div>
                        <div class="col-md-6">
                            <h3>Energy by Vehicle Type</h3>
                            <img src="{{ url_for('static', filename='../output/charging_patterns/energy_by_vehicle.png') }}" 
                                 class="img-fluid" alt="Energy by Vehicle Type">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header bg-warning text-dark">
                    <h2 class="card-title">Session Duration Analysis</h2>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-12">
                            <h3>Session Duration Distribution</h3>
                            <img src="{{ url_for('static', filename='../output/charging_patterns/duration_distribution.png') }}" 
                                 class="img-fluid" alt="Duration Distribution">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4 mb-5">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header bg-dark text-white">
                    <h2 class="card-title">User Behavior Patterns</h2>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h3>User Segments</h3>
                            <img src="{{ url_for('static', filename='../output/charging_patterns/user_segments.png') }}" 
                                 class="img-fluid" alt="User Segments">
                        </div>
                        <div class="col-md-6">
                            <h3>User Frequency Distribution</h3>
                            <img src="{{ url_for('static', filename='../output/charging_patterns/user_frequency.png') }}" 
                                 class="img-fluid" alt="User Frequency">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
{{ super() }}
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script src="{{ url_for('static', filename='js/charging_patterns.js') }}"></script>
{% endblock %}
```

#### Step 4.2: Create JavaScript File

Create `static/js/charging_patterns.js`:

```javascript
// EV Charging Patterns - JavaScript
// 
// This file contains client-side code for interactive visualizations on the
// charging patterns dashboard view.

const ChargingPatterns = {
    // Cache for data
    data: null,
    
    // Initialize the dashboard component
    init: function() {
        console.log("Initializing EV Charging Patterns component...");
        
        // Fetch data for interactive charts
        this.fetchData();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Subscribe to data update events
        if (typeof EventBus !== 'undefined') {
            EventBus.subscribe('ev_charging_data_updated', this.onDataUpdated.bind(this));
        }
    },
    
    // Fetch data from the API
    fetchData: function() {
        fetch('/api/v1/charging-patterns/summary')
            .then(response => response.json())
            .then(data => {
                this.data = data;
                this.renderCharts();
            })
            .catch(error => {
                console.error('Error fetching charging pattern data:', error);
                // Display fallback or error message
                document.getElementById('top-stations-chart').innerHTML = 
                    '<div class="alert alert-danger">Error loading chart data. Please try again later.</div>';
                document.getElementById('utilization-chart').innerHTML = 
                    '<div class="alert alert-danger">Error loading chart data. Please try again later.</div>';
            });
    },
    
    // Render interactive charts using Plotly
    renderCharts: function() {
        if (!this.data) return;
        
        // Render top stations chart
        if (this.data.station_utilization && this.data.station_utilization.top_stations) {
            const stationData = this.data.station_utilization.top_stations.by_usage;
            const trace = {
                x: stationData.station_ids,
                y: stationData.session_counts,
                type: 'bar',
                marker: {
                    color: 'rgba(50, 171, 96, 0.7)',
                    line: {
                        color: 'rgba(50, 171, 96, 1.0)',
                        width: 2
                    }
                }
            };
            
            const layout = {
                title: 'Top Stations by Usage',
                xaxis: {
                    title: 'Station ID',
                    tickangle: -45
                },
                yaxis: {
                    title: 'Number of Sessions'
                },
                margin: {
                    l: 50,
                    r: 50,
                    b: 100,
                    t: 50,
                    pad: 4
                }
            };
            
            Plotly.newPlot('top-stations-chart', [trace], layout);
        }
        
        // Render utilization chart
        if (this.data.station_utilization && this.data.station_utilization.utilization_rate) {
            const utilizationData = this.data.station_utilization.utilization_rate;
            
            // Limit to top 10 stations for clarity
            const stationIds = utilizationData.station_ids.slice(0, 10);
            const utilizationRates = utilizationData.utilization_percentage.slice(0, 10);
            
            const trace = {
                x: stationIds,
                y: utilizationRates,
                type: 'bar',
                marker: {
                    color: 'rgba(55, 128, 191, 0.7)',
                    line: {
                        color: 'rgba(55, 128, 191, 1.0)',
                        width: 2
                    }
                }
            };
            
            const layout = {
                title: 'Station Utilization Rates (Top 10)',
                xaxis: {
                    title: 'Station ID',
                    tickangle: -45
                },
                yaxis: {
                    title: 'Utilization Rate (%)',
                    range: [0, 100]
                },
                margin: {
                    l: 50,
                    r: 50,
                    b: 100,
                    t: 50,
                    pad: 4
                }
            };
            
            Plotly.newPlot('utilization-chart', [trace], layout);
        }
    },
    
    // Set up event listeners for interactive elements
    setupEventListeners: function() {
        // Example: Add dropdown change handler if we add filter dropdowns later
        const filterDropdown = document.getElementById('station-filter');
        if (filterDropdown) {
            filterDropdown.addEventListener('change', function(event) {
                const stationId = event.target.value;
                // Filter data by station ID
                // Then update charts
            });
        }
    },
    
    // Handle data updates from the event bus
    onDataUpdated: function(newData) {
        console.log("Received updated charging pattern data");
        this.data = newData;
        this.renderCharts();
    }
};

// Initialize the component when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    ChargingPatterns.init();
});
```

#### Step 4.3: Add Flask Route

Update `enhanced_dashboard.py` with a new route:

```python
# Add this import near the top of the file
from ev_charging_analysis import run_analysis

# Add this route to the Flask application
@app.route('/charging-patterns')
def charging_patterns():
    return render_template('charging_patterns.html')

# Add API endpoint to serve data for interactive visualizations
@app.route('/api/v1/charging-patterns/summary', methods=['GET'])
def charging_patterns_api():
    # Run analysis or load cached results
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
```

#### Step 4.4: Register Component in Dashboard

Add a new card to `templates/dashboard.html` in the designated section:

```html
<!-- BEGIN EXTENSIBLE SECTION: DASHBOARD CARDS -->
<!-- Existing cards... -->

<!-- EV Charging Patterns Analysis Card -->
<div class="col-md-6 mb-4">
    <div class="card dashboard-card h-100">
        <div class="card-body">
            <h5 class="card-title">
                <i class="fas fa-chart-line"></i> EV Charging Patterns
            </h5>
            <p class="card-text">Analyze charging behavior patterns, peak usage times, and user segments.</p>
            <a href="{{ url_for('charging_patterns') }}" class="btn btn-primary">View Analysis</a>
        </div>
    </div>
</div>

<!-- END EXTENSIBLE SECTION: DASHBOARD CARDS -->
```

Update `config/dashboard_components.json` to register the component:

```json
{
  "id": "charging_patterns",
  "name": "EV Charging Patterns",
  "route": "/charging-patterns",
  "icon": "chart-line",
  "permission": "analyst"
}
```

### PHASE 5: Testing (Days 18-20)

#### Step 5.1: Create Unit Tests

Create `tests/test_ev_charging_analysis.py`:

```python
"""
Unit tests for EV Charging Pattern Analysis
"""

import unittest
import pandas as pd
import os
import sys
import json
from datetime import datetime, timedelta

# Add the project root to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ev_charging_analysis import (
    load_data,
    analyze_time_patterns,
    analyze_station_utilization,
    analyze_energy_delivery,
    analyze_session_duration,
    analyze_user_behavior,
    generate_visualizations,
    run_analysis
)


class TestEVChargingAnalysis(unittest.TestCase):
    """Test cases for the EV Charging Pattern Analysis module"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a sample dataframe for testing
        self.sample_data = pd.DataFrame({
            'session_id': ['S1', 'S2', 'S3', 'S4', 'S5'],
            'station_id': ['ST1', 'ST2', 'ST1', 'ST3', 'ST2'],
            'start_time': [
                datetime(2023, 1, 1, 8, 0), 
                datetime(2023, 1, 1, 12, 0),
                datetime(2023, 1, 2, 9, 0),
                datetime(2023, 1, 2, 18, 0),
                datetime(2023, 1, 3, 7, 0)
            ],
            'end_time': [
                datetime(2023, 1, 1, 10, 0), 
                datetime(2023, 1, 1, 14, 0),
                datetime(2023, 1, 2, 11, 0),
                datetime(2023, 1, 2, 19, 0),
                datetime(2023, 1, 3, 8, 30)
            ],
            'energy_delivered': [10.5, 15.2, 12.3, 8.7, 9.1],
            'user_id': ['U1', 'U2', 'U1', 'U3', 'U2'],
            'cost': [5.25, 7.60, 6.15, 4.35, 4.55],
            'vehicle_type': ['Sedan', 'SUV', 'Sedan', 'Compact', 'SUV']
        })
        
        # Calculate duration
        self.sample_data['duration'] = (
            self.sample_data['end_time'] - self.sample_data['start_time']
        ).dt.total_seconds() / 3600
        
        # Create test output directory
        self.test_output_dir = 'output/test_charging_patterns'
        os.makedirs(self.test_output_dir, exist_ok=True)
    
    def test_analyze_time_patterns(self):
        """Test time patterns analysis function"""
        results = analyze_time_patterns(self.sample_data)
        
        # Check that the results have the expected structure
        self.assertIn('hourly_distribution', results)
        self.assertIn('counts', results['hourly_distribution'])
        self.assertIn('energy', results['hourly_distribution'])
        
        self.assertIn('daily_distribution', results)
        self.assertIn('counts', results['daily_distribution'])
        self.assertIn('energy', results['daily_distribution'])
        
        # Check some expected values
        self.assertIn(8, results['hourly_distribution']['counts'])
        self.assertEqual(results['hourly_distribution']['counts'][8], 1)
        
        # Check peak usage
        self.assertIn('peak_usage', results)
        self.assertIn('peak_hour', results['peak_usage'])
    
    def test_analyze_station_utilization(self):
        """Test station utilization analysis function"""
        results = analyze_station_utilization(self.sample_data)
        
        # Check that the results have the expected structure
        self.assertIn('top_stations', results)
        self.assertIn('by_usage', results['top_stations'])
        self.assertIn('station_ids', results['top_stations']['by_usage'])
        
        # Check that ST1 is the most used station (2 sessions)
        self.assertEqual(results['top_stations']['by_usage']['station_ids'][0], 'ST1')

    # Add more test methods for other functions...
    
    def test_generate_visualizations(self):
        """Test visualization generation"""
        # Run analysis
        results = {
            'time_patterns': analyze_time_patterns(self.sample_data),
            'station_utilization': analyze_station_utilization(self.sample_data),
            'energy_delivery': analyze_energy_delivery(self.sample_data),
            'session_duration': analyze_session_duration(self.sample_data),
            'user_behavior': analyze_user_behavior(self.sample_data)
        }
        
        # Generate visualizations
        vis_paths = generate_visualizations(results, self.test_output_dir)
        
        # Check that visualization files were created
        self.assertGreater(len(vis_paths), 0)
        for path in vis_paths:
            self.assertTrue(os.path.exists(path))
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up test output files
        for file in os.listdir(self.test_output_dir):
            os.remove(os.path.join(self.test_output_dir, file))
        os.rmdir(self.test_output_dir)


if __name__ == '__main__':
    unittest.main()
```

#### Step 5.2: Run Unit Tests

```bash
python -m unittest tests/test_ev_charging_analysis.py
```

**Validation point:**
- All tests should pass
- Test coverage should be high

#### Step 5.3: Test Dashboard Integration

1. Start the Flask application:
```bash
python enhanced_dashboard.py
```

2. Open a web browser and navigate to:
```
http://localhost:8080/
```

3. Check that the new card appears on the dashboard.

4. Click on the "View Analysis" button to navigate to the charging patterns page.

5. Verify all visualizations are displayed correctly.

**Validation point:**
- Dashboard card appears correctly
- Visualizations load properly
- No JavaScript errors in browser console

### PHASE 6: Documentation and Finalization (Days 21-22)

#### Step 6.1: Update Documentation

Add comprehensive docstrings to all functions in `ev_charging_analysis.py`.

Update the main README.md file to include information about the new component.

#### Step 6.2: Final Integration Check

1. Run the complete dashboard application
2. Verify all components work together
3. Test navigation between components
4. Check for any visual inconsistencies

#### Step 6.3: Cleanup

1. Remove any temporary or debug code
2. Ensure all files follow the style guidelines
3. Add appropriate comments to complex sections

## Testing Checklist

- [ ] Unit tests pass for all analysis functions
- [ ] Integration tests pass for dashboard components
- [ ] Visualizations render correctly in the dashboard
- [ ] API endpoints return correct data
- [ ] Error handling works properly
- [ ] No console errors or warnings
- [ ] Responsive design works on different screen sizes

## Integration Checklist

- [ ] `ev_charging_analysis.py` implements all required functions
- [ ] Visualizations are generated in `output/charging_patterns/`
- [ ] New template file `templates/charging_patterns.html` created
- [ ] New JavaScript file `static/js/charging_patterns.js` created
- [ ] New route added to `enhanced_dashboard.py`
- [ ] Component registered in dashboard configuration
- [ ] Card added to dashboard home

## Final Deliverables

1. `ev_charging_analysis.py` - Main analysis script
2. `templates/charging_patterns.html` - Dashboard template
3. `static/js/charging_patterns.js` - Frontend code
4. `tests/test_ev_charging_analysis.py` - Unit tests
5. Visualizations in `output/charging_patterns/`
6. API endpoint for data access
7. Dashboard integration

## Important Notes

- DO NOT modify any existing components
- Follow the exact implementation plan
- Maintain consistent style with existing code
- Test thoroughly before integration
- Document all functions and modules
- Follow the dashboard's visual style 