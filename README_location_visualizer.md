# Location-Based EV Charging Visualizer

A simple, standalone tool to generate visualizations for EV charging data filtered by location.

## Overview

This tool allows you to:

1. Generate visualizations for specific locations (cities, regions, or stations)
2. Analyze EV charging patterns geographically
3. Save visualizations and analysis results for later use
4. Compare charging behavior across different locations

## Usage

```bash
# Basic usage
python3 location_visualizer.py "Berlin"

# With detailed output
python3 location_visualizer.py "Berlin" --verbose
```

## Output

The script will generate several visualization files in the `output/charging_patterns/` directory:

- `[location]_hourly_patterns.png`: Charging sessions by hour of day
- `[location]_daily_patterns.png`: Charging sessions by day of week
- `[location]_time_of_day_patterns.png`: Charging sessions by time of day (morning/afternoon/evening/night)
- `[location]_top_stations.png`: Top charging stations by usage
- `[location]_charger_type_distribution.png`: Distribution of charger types
- `[location]_energy_distribution.png`: Distribution of energy consumption
- `[location]_hourly_energy.png`: Average energy consumption by hour of day
- `[location]_user_segments.png`: Distribution of user types
- `[location]_analysis_results.json`: Complete analysis results in JSON format

## Analysis Types

The tool performs the following types of analysis:

1. **Time Pattern Analysis**: When are charging sessions most frequent
2. **Station Utilization**: Which stations are most used
3. **Energy Delivery**: Energy consumption patterns
4. **Session Duration**: How long charging sessions typically last
5. **User Behavior**: Types of users and their charging habits

## Data Source

The tool uses the EV charging data from:
- `data/ev_charging_patterns.csv`

If data for the specified location is not found, the tool will generate synthetic data for demonstration purposes.

## Requirements

- Python 3.6+
- pandas
- numpy
- matplotlib
- seaborn

## Example

```bash
# Generate analysis for Berlin
python3 location_visualizer.py "Berlin" --verbose

# Generate analysis for New York
python3 location_visualizer.py "New York" --verbose

# Generate analysis for a specific station
python3 location_visualizer.py "Station_42" --verbose
``` 