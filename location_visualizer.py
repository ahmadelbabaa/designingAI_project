#!/usr/bin/env python3
"""
Location-Based EV Charging Visualizations Generator
A simplified script to generate visualizations for EV charging data filtered by location.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
import seaborn as sns
import json

# Use non-interactive matplotlib backend
import matplotlib
matplotlib.use('Agg')

# Set plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("viridis")

# Constants
OUTPUT_DIR = 'output/charging_patterns'
DATA_PATH = 'data/ev_charging_patterns.csv'
SAMPLE_PATH = 'data/ev_charging_patterns_sample.csv'

# Custom JSON encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


def ensure_output_dir():
    """Create the output directory if it doesn't exist"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_data(location=None):
    """Load and filter the charging data by location
    
    Args:
        location (str, optional): Location to filter data by
        
    Returns:
        pd.DataFrame: Filtered charging data
    """
    # Load the data file
    data_file = DATA_PATH if os.path.exists(DATA_PATH) else SAMPLE_PATH
    
    try:
        print(f"Loading data from {data_file}...")
        df = pd.read_csv(data_file)
        print(f"Loaded {len(df)} rows of data")
    except Exception as e:
        print(f"Error loading data: {e}")
        return create_synthetic_data()
    
    # Process data
    # Convert timestamps if they exist
    if 'Charging Start Time' in df.columns:
        df['Charging Start Time'] = pd.to_datetime(df['Charging Start Time'])
        df['Charging End Time'] = pd.to_datetime(df['Charging End Time'])
        
        # Extract time features
        df['Hour of Day'] = df['Charging Start Time'].dt.hour
        df['Day of Week'] = df['Charging Start Time'].dt.dayofweek
        df['Month'] = df['Charging Start Time'].dt.month
        df['Is Weekend'] = df['Day of Week'].isin([5, 6])
        
        # Categorize time of day
        df['Time of Day'] = df['Hour of Day'].apply(categorize_time)
    
    # Filter by location if specified
    if location:
        print(f"Filtering data for location: {location}")
        original_count = len(df)
        
        # Try different location fields that might exist in the data
        if 'Location' in df.columns:
            df = df[df['Location'].str.contains(location, case=False, na=False)]
        elif 'City' in df.columns:
            df = df[df['City'].str.contains(location, case=False, na=False)]
        elif 'Charging Station Location' in df.columns:
            df = df[df['Charging Station Location'].str.contains(location, case=False, na=False)]
        elif 'Charging Station ID' in df.columns and location.startswith('Station_'):
            df = df[df['Charging Station ID'] == location]
        
        print(f"After filtering: {len(df)} rows (filtered from {original_count})")
        
        # If no data after filtering, create synthetic data
        if len(df) == 0:
            print("No data found for the specified location. Using synthetic data.")
            df = create_synthetic_data(location)
    
    return df


def categorize_time(hour):
    """Categorize hour into time of day
    
    Args:
        hour (int): Hour of day (0-23)
        
    Returns:
        str: Time of day category
    """
    if 5 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 21:
        return 'Evening'
    else:
        return 'Night'


def create_synthetic_data(location=None):
    """Create synthetic data when real data is unavailable
    
    Args:
        location (str, optional): Location to include in the synthetic data
        
    Returns:
        pd.DataFrame: Synthetic charging data
    """
    print("Creating synthetic charging data...")
    np.random.seed(42)
    
    # Number of data points
    n_points = 1000
    
    # Create timestamps spanning 3 months
    start_date = pd.Timestamp('2023-01-01')
    end_date = pd.Timestamp('2023-03-31')
    charging_start = pd.date_range(start=start_date, end=end_date, periods=n_points)
    
    # Create random durations between 0.5 and 6 hours
    durations = np.random.uniform(0.5, 6, n_points)
    charging_end = charging_start + pd.to_timedelta(durations, unit='h')
    
    # Create energy consumption (kWh) based on duration with some randomness
    energy = durations * np.random.uniform(5, 15, n_points)
    
    # Create charging rate with some randomness
    charging_rate = energy / durations
    
    # Create station IDs
    station_ids = [f"Station_{i}" for i in np.random.randint(1, 50, n_points)]
    
    # Create vehicle models
    models = np.random.choice(
        ['Tesla Model 3', 'Tesla Model Y', 'Nissan Leaf', 'Chevy Bolt', 'BMW i3', 
         'Hyundai Kona', 'Kia Niro', 'Ford Mustang Mach-E'], 
        n_points
    )
    
    # Create charger types
    charger_types = np.random.choice(
        ['Level 1', 'Level 2', 'DC Fast'], 
        n_points, 
        p=[0.1, 0.6, 0.3]
    )
    
    # Create user types
    user_types = np.random.choice(
        ['Commuter', 'Casual', 'Commercial', 'Fleet'], 
        n_points, 
        p=[0.4, 0.3, 0.2, 0.1]
    )
    
    # Create user IDs
    user_ids = [f"User_{i}" for i in np.random.randint(1, 200, n_points)]
    
    # Create DataFrame
    df = pd.DataFrame({
        'Charging Start Time': charging_start,
        'Charging End Time': charging_end,
        'Charging Duration (hours)': durations,
        'Energy Consumed (kWh)': energy,
        'Charging Rate (kW)': charging_rate,
        'Charging Station ID': station_ids,
        'Vehicle Model': models,
        'Charger Type': charger_types,
        'User Type': user_types,
        'User ID': user_ids,
        'Location': location if location else 'Unknown'
    })
    
    # Extract time features
    df['Hour of Day'] = df['Charging Start Time'].dt.hour
    df['Day of Week'] = df['Charging Start Time'].dt.dayofweek
    df['Month'] = df['Charging Start Time'].dt.month
    df['Is Weekend'] = df['Day of Week'].isin([5, 6])
    df['Time of Day'] = df['Hour of Day'].apply(categorize_time)
    
    return df


def generate_time_visualizations(df, location):
    """Generate time-based visualizations
    
    Args:
        df (pd.DataFrame): Charging data
        location (str): Location being analyzed
    
    Returns:
        list: Paths to generated visualization files
    """
    paths = []
    
    # Format location string for titles and filenames
    loc_title = f" in {location}" if location else ""
    loc_filename = f"{location.lower().replace(' ', '_')}_" if location else ""
    
    # 1. Hourly distribution
    plt.figure(figsize=(12, 6))
    hourly_counts = df.groupby('Hour of Day').size()
    hourly_energy = df.groupby('Hour of Day')['Energy Consumed (kWh)'].sum()
    
    ax1 = plt.subplot(111)
    ax1.bar(hourly_counts.index, hourly_counts.values, alpha=0.7, color='#3498db', label='Session Count')
    ax1.set_xlabel('Hour of Day', fontsize=12)
    ax1.set_ylabel('Number of Sessions', fontsize=12)
    ax1.set_title(f'EV Charging Sessions by Hour of Day{loc_title}', fontsize=14, fontweight='bold')
    ax1.set_xticks(range(0, 24, 2))
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    ax2 = ax1.twinx()
    ax2.plot(hourly_energy.index, hourly_energy.values, color='#e74c3c', marker='o', 
             markersize=4, label='Energy Consumed (kWh)')
    ax2.set_ylabel('Total Energy Consumed (kWh)', fontsize=12)
    
    # Add combined legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper center')
    
    plt.tight_layout()
    hourly_path = os.path.join(OUTPUT_DIR, f'{loc_filename}hourly_patterns.png')
    plt.savefig(hourly_path, dpi=300)
    plt.close()
    paths.append(hourly_path)
    
    # 2. Daily distribution
    plt.figure(figsize=(12, 6))
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_counts = df.groupby('Day of Week').size()
    daily_counts = daily_counts.reindex(range(7), fill_value=0)  # Ensure all days are included
    daily_energy = df.groupby('Day of Week')['Energy Consumed (kWh)'].sum()
    daily_energy = daily_energy.reindex(range(7), fill_value=0)  # Ensure all days are included
    
    ax1 = plt.subplot(111)
    ax1.bar(day_names, daily_counts.values, alpha=0.7, color='#3498db', label='Session Count')
    ax1.set_xlabel('Day of Week', fontsize=12)
    ax1.set_ylabel('Number of Sessions', fontsize=12)
    ax1.set_title(f'EV Charging Sessions by Day of Week{loc_title}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    ax2 = ax1.twinx()
    ax2.plot(day_names, daily_energy.values, color='#e74c3c', marker='o', 
             markersize=4, label='Energy Consumed (kWh)')
    ax2.set_ylabel('Total Energy Consumed (kWh)', fontsize=12)
    
    # Add combined legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper center')
    
    plt.tight_layout()
    daily_path = os.path.join(OUTPUT_DIR, f'{loc_filename}daily_patterns.png')
    plt.savefig(daily_path, dpi=300)
    plt.close()
    paths.append(daily_path)
    
    # 3. Time of day distribution
    plt.figure(figsize=(10, 6))
    time_of_day_order = ['Morning', 'Afternoon', 'Evening', 'Night']
    time_counts = df.groupby('Time of Day').size()
    time_counts = time_counts.reindex(time_of_day_order, fill_value=0)  # Ensure proper order
    time_energy = df.groupby('Time of Day')['Energy Consumed (kWh)'].sum()
    time_energy = time_energy.reindex(time_of_day_order, fill_value=0)  # Ensure proper order
    
    ax1 = plt.subplot(111)
    ax1.bar(time_counts.index, time_counts.values, alpha=0.7, color='#3498db', label='Session Count')
    ax1.set_xlabel('Time of Day', fontsize=12)
    ax1.set_ylabel('Number of Sessions', fontsize=12)
    ax1.set_title(f'EV Charging Sessions by Time of Day{loc_title}', fontsize=14, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    ax2 = ax1.twinx()
    ax2.plot(time_energy.index, time_energy.values, color='#e74c3c', marker='o', 
             markersize=4, label='Energy Consumed (kWh)')
    ax2.set_ylabel('Total Energy Consumed (kWh)', fontsize=12)
    
    # Add combined legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper center')
    
    plt.tight_layout()
    time_of_day_path = os.path.join(OUTPUT_DIR, f'{loc_filename}time_of_day_patterns.png')
    plt.savefig(time_of_day_path, dpi=300)
    plt.close()
    paths.append(time_of_day_path)
    
    return paths


def generate_station_visualizations(df, location):
    """Generate station-based visualizations
    
    Args:
        df (pd.DataFrame): Charging data
        location (str): Location being analyzed
    
    Returns:
        list: Paths to generated visualization files
    """
    paths = []
    
    # Format location string for titles and filenames
    loc_title = f" in {location}" if location else ""
    loc_filename = f"{location.lower().replace(' ', '_')}_" if location else ""
    
    # 1. Top stations by usage
    plt.figure(figsize=(12, 6))
    station_counts = df.groupby('Charging Station ID').size().sort_values(ascending=False)
    
    # Take top 10 stations
    top_stations = station_counts.head(10)
    
    # Create horizontal bar chart for better readability
    plt.barh(top_stations.index, top_stations.values, color='#2ecc71')
    
    # Add count labels to the bars
    for i, count in enumerate(top_stations.values):
        plt.text(count + 5, i, str(count), va='center')
    
    plt.xlabel('Number of Sessions', fontsize=12)
    plt.ylabel('Charging Station ID', fontsize=12)
    plt.title(f'Top 10 Charging Stations by Usage{loc_title}', fontsize=14, fontweight='bold')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    top_stations_path = os.path.join(OUTPUT_DIR, f'{loc_filename}top_stations.png')
    plt.savefig(top_stations_path, dpi=300)
    plt.close()
    paths.append(top_stations_path)
    
    # 2. Charger type distribution
    plt.figure(figsize=(10, 6))
    charger_counts = df.groupby('Charger Type').size()
    
    # Create pie chart
    plt.pie(charger_counts, labels=charger_counts.index, autopct='%1.1f%%', 
            startangle=90, colors=['#e74c3c', '#3498db', '#2ecc71'], 
            wedgeprops={'edgecolor': 'white', 'linewidth': 1})
    
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title(f'Distribution of Charging Sessions by Charger Type{loc_title}', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    charger_type_path = os.path.join(OUTPUT_DIR, f'{loc_filename}charger_type_distribution.png')
    plt.savefig(charger_type_path, dpi=300)
    plt.close()
    paths.append(charger_type_path)
    
    return paths


def generate_energy_visualizations(df, location):
    """Generate energy-based visualizations
    
    Args:
        df (pd.DataFrame): Charging data
        location (str): Location being analyzed
    
    Returns:
        list: Paths to generated visualization files
    """
    paths = []
    
    # Format location string for titles and filenames
    loc_title = f" in {location}" if location else ""
    loc_filename = f"{location.lower().replace(' ', '_')}_" if location else ""
    
    # 1. Energy distribution
    plt.figure(figsize=(10, 6))
    
    # Create energy bins
    energy_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, float('inf')]
    energy_labels = ['0-10', '10-20', '20-30', '30-40', '40-50', '50-60', 
                     '60-70', '70-80', '80-90', '90-100', '100+']
    
    # Bin the energy values
    energy_binned = pd.cut(df['Energy Consumed (kWh)'], bins=energy_bins, labels=energy_labels)
    energy_counts = energy_binned.value_counts().sort_index()
    
    # Plot the histogram
    plt.bar(energy_counts.index, energy_counts.values, color='#1abc9c')
    plt.xlabel('Energy Consumed (kWh)', fontsize=12)
    plt.ylabel('Number of Sessions', fontsize=12)
    plt.title(f'Distribution of Energy Consumption per Session{loc_title}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    energy_dist_path = os.path.join(OUTPUT_DIR, f'{loc_filename}energy_distribution.png')
    plt.savefig(energy_dist_path, dpi=300)
    plt.close()
    paths.append(energy_dist_path)
    
    # 2. Hourly energy consumption
    plt.figure(figsize=(10, 6))
    
    hourly_energy = df.groupby('Hour of Day')['Energy Consumed (kWh)'].mean()
    
    plt.plot(hourly_energy.index, hourly_energy.values, 
             marker='o', markersize=6, color='#1abc9c', linewidth=2)
    plt.fill_between(hourly_energy.index, hourly_energy.values, 
                     alpha=0.3, color='#1abc9c')
    
    plt.xlabel('Hour of Day', fontsize=12)
    plt.ylabel('Average Energy Consumed (kWh)', fontsize=12)
    plt.title(f'Average Energy Consumption by Hour of Day{loc_title}', fontsize=14, fontweight='bold')
    plt.xticks(range(0, 24, 2))
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    hourly_energy_path = os.path.join(OUTPUT_DIR, f'{loc_filename}hourly_energy.png')
    plt.savefig(hourly_energy_path, dpi=300)
    plt.close()
    paths.append(hourly_energy_path)
    
    return paths


def generate_user_visualizations(df, location):
    """Generate user behavior visualizations
    
    Args:
        df (pd.DataFrame): Charging data
        location (str): Location being analyzed
    
    Returns:
        list: Paths to generated visualization files
    """
    paths = []
    
    # Format location string for titles and filenames
    loc_title = f" in {location}" if location else ""
    loc_filename = f"{location.lower().replace(' ', '_')}_" if location else ""
    
    # 1. User segments by type
    plt.figure(figsize=(10, 6))
    
    # User type distribution
    user_counts = df.groupby('User Type').size()
    
    # Create pie chart
    plt.pie(user_counts, labels=user_counts.index, autopct='%1.1f%%', 
            startangle=90, colors=['#34495e', '#2c3e50', '#1a5276', '#2980b9'], 
            wedgeprops={'edgecolor': 'white', 'linewidth': 1})
    
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title(f'Distribution of EV Charging Users by Type{loc_title}', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    user_segments_path = os.path.join(OUTPUT_DIR, f'{loc_filename}user_segments.png')
    plt.savefig(user_segments_path, dpi=300)
    plt.close()
    paths.append(user_segments_path)
    
    return paths


def analyze_data(df, location):
    """Analyze the charging data and return summary statistics
    
    Args:
        df (pd.DataFrame): Charging data
        location (str): Location being analyzed
        
    Returns:
        dict: Analysis results
    """
    # Initialize results dictionary
    results = {}
    
    # Basic stats
    results['data_summary'] = {
        'total_sessions': len(df),
        'location': location,
        'date_range': {
            'start': df['Charging Start Time'].min().strftime('%Y-%m-%d') if len(df) > 0 else None,
            'end': df['Charging End Time'].max().strftime('%Y-%m-%d') if len(df) > 0 else None
        }
    }
    
    # Time pattern analysis
    results['time_patterns'] = {
        'hourly': {
            'peak_hour': df.groupby('Hour of Day').size().idxmax(),
            'distribution': df.groupby('Hour of Day').size().to_dict()
        },
        'day_of_week': {
            'peak_day': df.groupby('Day of Week').size().idxmax(),
            'distribution': df.groupby('Day of Week').size().to_dict()
        },
        'time_of_day': {
            'peak_period': df.groupby('Time of Day').size().idxmax(),
            'distribution': df.groupby('Time of Day').size().to_dict()
        }
    }
    
    # Station utilization analysis
    results['station_utilization'] = {
        'total_stations': df['Charging Station ID'].nunique(),
        'top_stations': df.groupby('Charging Station ID').size().sort_values(ascending=False).head(10).to_dict(),
        'charger_types': {
            'distribution': df.groupby('Charger Type').size().to_dict(),
            'most_common_type': df['Charger Type'].mode()[0] if len(df) > 0 else None
        }
    }
    
    # Energy delivery analysis
    results['energy_delivery'] = {
        'total_energy_kwh': df['Energy Consumed (kWh)'].sum(),
        'avg_energy_per_session_kwh': df['Energy Consumed (kWh)'].mean(),
        'avg_charging_rate_kw': df['Charging Rate (kW)'].mean()
    }
    
    # Session duration analysis
    results['session_duration'] = {
        'avg_duration_hours': df['Charging Duration (hours)'].mean(),
        'max_duration_hours': df['Charging Duration (hours)'].max(),
        'min_duration_hours': df['Charging Duration (hours)'].min()
    }
    
    # User behavior analysis
    results['user_behavior'] = {
        'total_users': df['User ID'].nunique(),
        'avg_sessions_per_user': len(df) / df['User ID'].nunique() if df['User ID'].nunique() > 0 else 0,
        'user_types': {
            'distribution': df.groupby('User Type').size().to_dict(),
            'most_common_type': df['User Type'].mode()[0] if len(df) > 0 else None
        }
    }
    
    return results


def main():
    """Main entry point for the script"""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Generate EV charging pattern visualizations for a specific location',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Add command line arguments
    parser.add_argument(
        'location', 
        type=str, 
        help='Location to analyze (city name, region, or station ID)'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true', 
        help='Display detailed progress information'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Ensure output directory exists
    ensure_output_dir()
    
    # Load and filter data by location
    df = load_data(args.location)
    
    # Generate visualizations
    print("Generating time pattern visualizations...")
    time_paths = generate_time_visualizations(df, args.location)
    
    print("Generating station visualizations...")
    station_paths = generate_station_visualizations(df, args.location)
    
    print("Generating energy visualizations...")
    energy_paths = generate_energy_visualizations(df, args.location)
    
    print("Generating user visualizations...")
    user_paths = generate_user_visualizations(df, args.location)
    
    # Combine all paths
    all_paths = time_paths + station_paths + energy_paths + user_paths
    
    # Analyze data
    print("Analyzing data...")
    analysis_results = analyze_data(df, args.location)
    
    # Save analysis results to JSON
    loc_filename = f"{args.location.lower().replace(' ', '_')}_" if args.location else ""
    results_file = os.path.join(OUTPUT_DIR, f'{loc_filename}analysis_results.json')
    with open(results_file, 'w') as f:
        json.dump(analysis_results, f, indent=4, cls=NumpyEncoder)
    
    # Print summary
    if args.verbose:
        print("\nAnalysis Results:")
        print(f"Location: {args.location}")
        print(f"Total Sessions: {analysis_results['data_summary']['total_sessions']}")
        print(f"Peak Hour: {analysis_results['time_patterns']['hourly']['peak_hour']}:00")
        print(f"Peak Day: {analysis_results['time_patterns']['day_of_week']['peak_day']}")
        print(f"Peak Time of Day: {analysis_results['time_patterns']['time_of_day']['peak_period']}")
        print(f"Total Energy Delivered: {analysis_results['energy_delivery']['total_energy_kwh']:.2f} kWh")
        print(f"Average Session Duration: {analysis_results['session_duration']['avg_duration_hours']:.2f} hours")
        print(f"Total Users: {analysis_results['user_behavior']['total_users']}")
        
        print("\nGenerated Visualization Files:")
        for path in all_paths:
            print(f"- {path}")
    
    print(f"\nAnalysis complete! Generated {len(all_paths)} visualization files.")
    print(f"Results saved to: {results_file}")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main()) 