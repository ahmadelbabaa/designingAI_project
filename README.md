# HPC Station Conversion Analysis Dashboard

## Overview

This project implements a comprehensive MLOps pipeline for analyzing gas station viability for conversion to High-Power Charging (HPC) stations. The dashboard provides:

- **Interactive Map**: Explore gas stations with color-coded viability scores
- **Financial Analysis**: ROI and payback period calculations for each location
- **Traffic Analysis**: Heatmap visualization of traffic patterns
- **EV Adoption Forecasting**: Project future EV adoption rates
- **Scenario Comparison**: Compare different investment strategies
- **Dynamic Pricing Simulation**: Optimize charging prices

## Project Components

1. **HPC_integration_part1.py**: Sets up environment, data collection and preprocessing
2. **HPC_integration_part2.py**: Data integration and ROI analysis
3. **HPC_integration_part3.py**: Advanced analytics including geospatial analysis
4. **hpc_dashboard.py**: Dashboard visualization and interactive elements

## Setup Instructions

1. Clone this repository
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the Jupyter notebook to execute the dashboard:
   ```
   jupyter notebook "HPC Dashboard Collab (1).ipynb"
   ```

## Features

- Modern UI with green energy theme
- Interactive geospatial analysis
- Financial modeling with scenario comparison
- EV adoption forecasting
- Dynamic pricing optimization

## Data Sources

The dashboard can utilize data from the following sources for real-world analysis:

### EV Charging Data Resources

1. **[Open Charge Map](https://openchargemap.org/site)** - The global public registry of electric vehicle charging locations. Provides comprehensive data on charging station locations, availability, and specifications worldwide.

### Kaggle Datasets

2. **[Electric Vehicle Charging Patterns](https://www.kaggle.com/datasets/valakhorasani/electric-vehicle-charging-patterns)** - Contains data on EV charging session start/end times, duration, energy consumed, and user behavior patterns. Useful for understanding usage patterns and demand forecasting.

3. **[Electric Vehicle Charging Dataset](https://www.kaggle.com/datasets/michaelbryantds/electric-vehicle-charging-dataset)** - Comprehensive dataset with charging station metrics, including location data, power ratings, connector types, and usage statistics.

4. **[Residential EV Charging from Apartment Buildings](https://www.kaggle.com/datasets/anshtanwar/residential-ev-chargingfrom-apartment-buildings)** - Dataset focusing on residential charging patterns in multi-unit dwellings, providing insights into urban residential charging needs.

5. **[EV Charging Station Usage of California City](https://www.kaggle.com/datasets/venkatsairo4899/ev-charging-station-usage-of-california-city)** - Detailed usage statistics of charging stations in California cities, including time-of-day patterns, session duration, and energy consumption.

### Additional Research Data

6. **[One Year Half-Hourly Profiles of Demand, PV Generation and EV Charging](https://ieee-dataport.org/documents/one-year-half-hourly-profiles-demand-pv-generation-and-ev-charging-household-london-uk)** - IEEE DataPort dataset containing detailed half-hourly profiles of residential electricity demand, PV generation, and EV charging for households in London, UK. Provides valuable insights into integrated energy system patterns.

### Kaggle Search

For additional relevant datasets, explore [Kaggle's EV charging session collections](https://www.kaggle.com/datasets?search=ev+charging+session).

## Requirements

- Python 3.7+
- Required Python packages are listed in requirements.txt
