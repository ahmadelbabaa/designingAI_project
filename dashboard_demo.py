#!/usr/bin/env python
"""
Enhanced Dashboard Demo
-----------------------
Integrates EV charging data analysis with ML forecasting and GPT-4o powered 
conversion recommendations, served through an interactive web interface.
"""

import os
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments

# Flask imports
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Utils imports
from utils.data_loader import DataLoader
from utils.data_validator import DataValidator
from utils.data_visualizer import DataVisualizer
from utils.unified_data_repository import UnifiedDataRepository

# Component imports
from time_series_forecasting import generate_forecast, analyze_forecast_trends
from conversion_advisor import (
    generate_conversion_recommendation, 
    create_dashboard_html, 
    load_gas_stations,
    generate_placeholder_recommendation,
    create_conversion_prompt,
    query_gpt4
)
from ev_charging_analysis import run_analysis

# Create Flask app
app = Flask(__name__, 
            static_folder='output',  # Serve files directly from output directory
            template_folder='templates')

# Create necessary directories
for folder in ['data', 'config', 'output', 'output/forecasts', 'output/conversion_advisor', 'templates']:
    os.makedirs(folder, exist_ok=True)

# Routes
@app.route('/')
def index():
    """Dashboard home page"""
    # Load data
    repo = UnifiedDataRepository()
    stations = repo.get_dataset("stations")
    sessions = repo.get_dataset("sessions")
    forecasts = repo.get_dataset("forecasts")
    
    # Pass data counts to template
    data_counts = {
        "stations": len(stations) if stations is not None else 0,
        "sessions": len(sessions) if sessions is not None else 0,
        "forecasts": len(forecasts) if forecasts is not None else 0
    }
    
    return render_template('dashboard.html', data_counts=data_counts)

@app.route('/conversion_advisor')
def conversion_advisor_page():
    """Conversion advisor page"""
    stations_df = load_gas_stations()
    stations = [row.to_dict() for _, row in stations_df.iterrows()]
    return render_template('conversion_advisor.html', stations=stations)

@app.route('/charging_patterns')
def charging_patterns_page():
    """Charging patterns analysis page"""
    # Get charging patterns analysis
    analysis_results = run_analysis()
    return render_template('charging_patterns.html', results=analysis_results)

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

def run_dashboard_demo():
    """Run the enhanced dashboard demo with web server"""
    print("\n=== Enhanced EV Charging Analysis & Conversion Dashboard ===")
    print("Loading and processing data...")
    
    # Load all data
    loader = DataLoader(data_dir="data")
    loader.load_all_data()
    
    print("\nStarting web server...")
    print("You can access the dashboard at http://127.0.0.1:5000/")
    
    # Start Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    run_dashboard_demo() 