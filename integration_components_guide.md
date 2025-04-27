# HPC Prediction Analysis - Integration Components Guide

This document outlines the four main integration components of the HPC Prediction Analysis project and identifies the existing files related to each component.

## 1. EV Charging Pattern Analysis

**Purpose:** Analyze charging behavior patterns from historical data to identify usage trends, peak times, and user behaviors.

**Core Files:**
- `ev_charging_patterns.csv` - Primary dataset containing charging session data
- `ev_charging_analysis.py` - New file to be implemented that will perform the analysis
- `output/charging_patterns/` - Directory where analysis visualizations will be stored
- `templates/charging_patterns.html` - Template file for displaying analysis in the dashboard

**Integration Points:**
- The analysis output from `ev_charging_analysis.py` should be integrated into the dashboard via a new route in `enhanced_dashboard.py`
- Visualization files will be served from the `output/charging_patterns/` directory

## 2. Station Conversion Analysis

**Purpose:** Evaluate the feasibility and ROI of converting gas stations to EV charging stations.

**Core Files:**
- `conversion_advisor.py` - Contains the existing logic for conversion analysis
- `gas_stations.csv` and `gas_stations.json` - Datasets with gas station information
- `output/conversion_advisor/` - Directory containing conversion visualization outputs
- `templates/conversion_advisor.html` - Dashboard template for conversion analysis

**Integration Points:**
- Already integrated into the dashboard via routes in `enhanced_dashboard.py`
- Data flow: Gas station data → Conversion analysis → Visualization → Dashboard display

## 3. Time Series Forecasting

**Purpose:** Predict future charging demand and usage patterns for planning capacity.

**Core Files:**
- `time_series_forecasting.py` - Contains forecasting models and visualization generation
- Various `GS-XXXX_forecast_data.csv` files in the `data/` directory - Individual station forecast data
- `forecast_summary.json` and `forecast_trends.json` - Aggregated forecast results
- `output/forecasts/` - Directory containing forecast visualization outputs

**Integration Points:**
- Forecast visualizations are integrated into the dashboard
- Station-specific forecasts can be accessed via the dashboard interface

## 4. HPC Integration Pipeline

**Purpose:** Process, combine, and prepare data from multiple sources for cohesive analysis.

**Core Files:**
- `HPC_integration_part1.py` - Initial data setup and Kaggle data downloading
- `HPC_integration_part2.py` - Data processing and transformation
- `HPC_integration_part3.py` - Final data integration and preparation
- `hpc_usage_master.csv` - The integrated dataset resulting from the pipeline
- `config/hpc_cost_params.yaml` - Configuration parameters for cost calculations

**Integration Points:**
- This pipeline creates the integrated datasets used by all other analysis components
- Changes to the integration pipeline would need to be reflected in the analysis components

## Dashboard Integration

**Main Files:**
- `enhanced_dashboard.py` - Flask application implementing the web dashboard
- `templates/dashboard.html` - Main dashboard template
- `static/` directory - CSS, JavaScript, and other static assets
- `output/enhanced_dashboard.html` - Generated dashboard output

**Key Integration Requirements:**
1. Each component should produce visualizations in its designated output directory
2. New routes should be added to `enhanced_dashboard.py` for any new component
3. Templates should follow the existing structure in the `templates/` directory
4. Component outputs should be in formats (HTML, PNG, JSON) that can be integrated into the dashboard

## Development Process

When implementing the new EV charging pattern analysis component:

1. First review existing components to understand the code style and patterns
2. Create the analysis script following similar patterns to existing scripts
3. Generate visualizations in the specified output directory
4. Add new route(s) to the dashboard application
5. Create dashboard template(s) following existing patterns
6. Test the integration to ensure data flows correctly

This modular approach ensures that each component can both function independently and integrate seamlessly into the overall dashboard. 