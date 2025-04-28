# Location-Based EV Charging Pattern Analysis

This system allows you to generate visualizations and analysis for EV charging patterns filtered by location.

## Overview

The location-based visualization system allows you to:

1. Filter EV charging data by location (city, region, or specific station)
2. Generate visualizations specific to that location
3. Analyze patterns and trends in the filtered data
4. Save location-specific visualization files and analysis results

## Available Scripts

### 1. Generate Location Visualizations

This is the primary script for generating location-based visualizations:

```bash
./generate_location_visualizations.py [LOCATION] [--verbose]
```

Example usage:
```bash
# Generate visualizations for Berlin
./generate_location_visualizations.py Berlin

# Generate visualizations for a specific station with verbose output
./generate_location_visualizations.py "Station_123" --verbose
```

### 2. Test Charging Patterns

This script runs the analysis and prints a detailed summary of the results:

```bash
./test_charging_patterns.py [--location LOCATION]
```

Example usage:
```bash
# Run analysis for all data
./test_charging_patterns.py

# Run analysis for Berlin
./test_charging_patterns.py --location Berlin
```

## Output Files

All generated files will be saved in the `output/charging_patterns/` directory with the location name prefixed to the filename. For example:

- `berlin_hourly_patterns.png`
- `berlin_daily_patterns.png`
- `berlin_energy_distribution.png`
- `berlin_analysis_results.json` (contains all numerical analysis results)

## Analysis Types

The system provides the following types of analysis for each location:

1. **Time Patterns**: Shows charging session distribution by hour of day, day of week, month, and time of day
2. **Station Utilization**: Identifies top stations by usage and energy delivery, and charger type distribution
3. **Energy Delivery**: Analyzes energy consumption patterns, rates, and distribution by vehicle type
4. **Session Duration**: Shows the distribution of charging session durations and correlations with other factors
5. **User Behavior**: Analyzes user types, frequency, and profiles if user data is available

## Requirements

- Python 3.6+
- pandas
- matplotlib
- seaborn

## Data Sources

The system uses available EV charging data from the following sources:
- `data/ev_charging_patterns.csv` (or sample data if not available)
- `data/EVChargingStationUsage.csv` (or sample data if not available)

If the data files are not found, the system will generate synthetic data for demonstration purposes. 