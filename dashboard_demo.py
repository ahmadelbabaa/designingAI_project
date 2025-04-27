#!/usr/bin/env python
"""
Dashboard Demo
---------------
Demonstrates Phase 1 capabilities by loading EV charging data, 
validating it, and generating an interactive dashboard.
"""

import os
import pandas as pd
import json
from datetime import datetime

from utils.data_loader import DataLoader
from utils.data_validator import DataValidator
from utils.data_visualizer import DataVisualizer
from utils.unified_data_repository import UnifiedDataRepository

def run_dashboard_demo():
    """Run the dashboard demo to showcase Phase 1 capabilities"""
    print("\n=== EV Charging Data Analysis Dashboard Demo ===")
    print("Loading and processing data...")
    
    # Step 1: Load Data
    loader = DataLoader(data_dir="data")
    loader.load_all_data()
    
    # Get data from repository
    repo = UnifiedDataRepository()
    stations = repo.get_dataset("stations")
    sessions = repo.get_dataset("sessions")
    forecasts = repo.get_dataset("forecasts")
    
    # Print data summary
    print("\nData Summary:")
    print(f"  Stations: {len(stations) if stations is not None else 0}")
    print(f"  Sessions: {len(sessions) if sessions is not None else 0}")
    print(f"  Forecasts: {len(forecasts) if forecasts is not None else 0}")
    
    # Step 2: Validate Data
    print("\nValidating data...")
    validator = DataValidator()
    
    if stations is not None:
        is_valid, report = validator.validate_stations(stations)
        print("\nStation Data Validation:")
        validator.print_validation_report(report)
    
    if sessions is not None:
        is_valid, report = validator.validate_sessions(sessions)
        print("\nSession Data Validation:")
        validator.print_validation_report(report)
    
    if forecasts is not None:
        is_valid, report = validator.validate_forecasts(forecasts)
        print("\nForecast Data Validation:")
        validator.print_validation_report(report)
    
    # Step 3: Create Dashboard
    print("\nGenerating dashboard...")
    visualizer = DataVisualizer(output_dir="output")
    dashboard_path = os.path.join("output", "ev_charging_dashboard.html")
    
    # Generate the dashboard
    visualizer.create_dashboard(
        stations=stations,
        sessions=sessions,
        forecasts=forecasts,
        save_path=dashboard_path
    )
    
    print(f"\nDashboard generated successfully at: {dashboard_path}")
    print("\nDashboard includes:")
    print("  - Summary statistics for stations, sessions, and energy delivery")
    print("  - Interactive map of charging stations")
    print("  - Charging session patterns analysis")
    print("  - Energy demand forecasts with prediction intervals")
    print("  - Cross-station comparison visualizations")
    
    print("\nOpen the dashboard in your web browser to explore the visualizations.")
    
    # Attempt to open the dashboard in the default browser
    try:
        import webbrowser
        webbrowser.open('file://' + os.path.abspath(dashboard_path))
        print("Dashboard opened in your default web browser.")
    except:
        print("Please open the dashboard file manually in your web browser.")

if __name__ == "__main__":
    run_dashboard_demo() 