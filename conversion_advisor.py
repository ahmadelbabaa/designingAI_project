#!/usr/bin/env python3
"""
Gas Station Conversion Advisor
Leverages existing models and GPT-4 to generate personalized conversion recommendations
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from time_series_forecasting import generate_usage_data, forecast_station_usage
from hpc_pricing_rl import HPCPricingEnv, evaluate_pricing_model

# Constants
API_KEY = os.environ.get("OPENAI_API_KEY", "")  # Get from environment or configure manually
GAS_STATIONS_FILE = "data/gas_stations.csv"
DEFAULT_NUM_SCENARIOS = 3
OUTPUT_DIR = "output/conversion_advisor"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_gas_stations():
    """Load gas station data"""
    try:
        return pd.read_csv(GAS_STATIONS_FILE)
    except:
        # Create a synthetic dataset if file doesn't exist
        return generate_synthetic_gas_stations()

def generate_synthetic_gas_stations(num_stations=50):
    """Generate synthetic gas station data for demo purposes"""
    # Generate random US locations with realistic distribution
    stations = []
    for i in range(num_stations):
        station_id = f"GS-{i:04d}"
        lat = np.random.uniform(24.0, 49.0)  # Continental US latitudes
        lon = np.random.uniform(-125.0, -66.0)  # Continental US longitudes
        
        # Generate some business metrics
        daily_customers = np.random.randint(200, 1000)
        monthly_revenue = daily_customers * np.random.uniform(15, 40) * 30
        
        stations.append({
            'station_id': station_id,
            'latitude': lat,
            'longitude': lon,
            'daily_customers': daily_customers,
            'monthly_revenue': monthly_revenue,
            'has_convenience_store': np.random.choice([True, False], p=[0.8, 0.2]),
            'property_size_sqft': np.random.randint(5000, 30000)
        })
    
    df = pd.DataFrame(stations)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(GAS_STATIONS_FILE), exist_ok=True)
    
    # Save as CSV
    df.to_csv(GAS_STATIONS_FILE, index=False)
    
    # Also save as JSON for easy loading in dashboard
    with open(GAS_STATIONS_FILE.replace('.csv', '.json'), 'w') as f:
        json.dump(stations, f)
    
    return df

def generate_demand_scenarios(station_data, num_scenarios=3):
    """Generate multiple charging demand scenarios for a gas station location"""
    # Create base parameters for each scenario
    scenario_params = {
        'optimistic': {
            'growth_rate': 0.04,  # 4% monthly growth
            'base_sessions_factor': 1.2,
            'base_energy_factor': 1.1
        },
        'realistic': {
            'growth_rate': 0.02,  # 2% monthly growth
            'base_sessions_factor': 1.0,
            'base_energy_factor': 1.0
        },
        'conservative': {
            'growth_rate': 0.01,  # 1% monthly growth
            'base_sessions_factor': 0.8,
            'base_energy_factor': 0.9
        }
    }
    
    # Base parameters derived from station's current business
    base_sessions = station_data['daily_customers'] * 0.05  # Assume 5% of customers would use EV charging
    base_energy = 50  # average kWh per session
    
    scenarios = {}
    for name, params in scenario_params.items():
        # Generate historical and forecast data
        historical_df = generate_usage_data(
            station_data['station_id'],
            days=180,
            base_sessions=base_sessions * params['base_sessions_factor'],
            base_energy=base_energy * params['base_energy_factor'],
            growth_rate=params['growth_rate']
        )
        
        forecast_df, plot_path = forecast_station_usage(
            historical_df,
            forecast_days=365,  # 1 year forecast
            plot=True,
            output_dir=OUTPUT_DIR
        )
        
        # Store scenario data
        scenarios[name] = {
            'historical': historical_df,
            'forecast': forecast_df,
            'plot_path': plot_path,
            'params': params
        }
    
    return scenarios

def calculate_roi_metrics(scenarios, investment_tiers):
    """Calculate ROI metrics for each scenario and investment tier"""
    roi_results = {}
    
    for scenario_name, scenario_data in scenarios.items():
        forecast = scenario_data['forecast']
        roi_results[scenario_name] = {}
        
        for tier_name, tier_data in investment_tiers.items():
            # Calculate key financial metrics
            capex = tier_data['capex']
            
            # Annual metrics
            annual_energy = forecast['energy_delivered_kwh'].sum()
            annual_revenue = forecast['revenue_usd'].sum()
            annual_opex = annual_energy * 0.15 + 12 * 1200  # electricity cost + monthly staff
            annual_profit = annual_revenue - annual_opex
            
            # ROI calculations
            payback_years = capex / annual_profit if annual_profit > 0 else float('inf')
            roi_5yr = (5 * annual_profit - capex) / capex if capex > 0 else 0
            
            roi_results[scenario_name][tier_name] = {
                'capex': capex,
                'annual_energy_kwh': annual_energy,
                'annual_revenue': annual_revenue,
                'annual_opex': annual_opex,
                'annual_profit': annual_profit,
                'payback_years': payback_years,
                'roi_5yr': roi_5yr
            }
    
    return roi_results

def query_gpt4(prompt, api_key=API_KEY, max_tokens=1000):
    """Call GPT-4 API to generate recommendations"""
    # If no API key, return a placeholder response
    if not api_key:
        print("Warning: No OpenAI API key provided. Using placeholder recommendation.")
        return generate_placeholder_recommendation()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error calling GPT-4 API: {e}")
        return generate_placeholder_recommendation()

def generate_placeholder_recommendation():
    """Generate a placeholder recommendation when GPT-4 API is not available"""
    return """
# Gas Station Conversion Recommendation

## Executive Summary
Based on the data analysis, this gas station shows strong potential for EV charging conversion. The Standard (2 chargers) investment tier offers the best balance of investment and returns.

## Detailed Recommendation

### Conversion Decision
**Recommendation: Convert to include EV charging stations**

The station's location and customer traffic make it well-suited for EV charging infrastructure. Our analysis shows positive ROI under most scenarios.

### Investment Tier
**Recommended Tier: Standard (2 chargers)**

* One Level 2 charger for longer stays
* One DC Fast charger for quick charging
* Total investment: $150,000

### Timing
**Optimal timing: Within 6-12 months**

The market is showing steady growth, but not yet saturated. Early movers will establish customer loyalty.

### Key Risks and Mitigations
1. **Risk**: Lower than projected utilization
   **Mitigation**: Start with Standard tier rather than Premium; focus on marketing to early adopters

2. **Risk**: Faster technological obsolescence
   **Mitigation**: Choose equipment with upgrade paths; negotiate maintenance contracts

3. **Risk**: Grid capacity limitations
   **Mitigation**: Conduct utility assessment before installation; consider on-site battery storage

### Additional Revenue Opportunities
1. Add premium snacks and convenience items targeting EV users
2. Partner with nearby businesses for cross-promotions
3. Implement a loyalty program across both fuel and EV customers

By implementing these recommendations, you can position your station for the EV transition while maintaining your core business.
"""

def format_scenario_summary(scenarios, roi_results):
    """Format scenario data for GPT-4 prompt"""
    summary = []
    
    for scenario_name, scenario_data in scenarios.items():
        forecast = scenario_data['forecast']
        summary.append(f"\n## {scenario_name.upper()} SCENARIO:")
        summary.append(f"- Average daily sessions: {forecast['charging_sessions'].mean():.1f}")
        summary.append(f"- Total annual energy: {forecast['energy_delivered_kwh'].sum():.1f} kWh")
        summary.append(f"- Total annual revenue: ${forecast['revenue_usd'].sum():.2f}")
        
        # Add ROI metrics
        roi_data = roi_results[scenario_name]
        for tier_name, metrics in roi_data.items():
            summary.append(f"\n  {tier_name} INVESTMENT TIER:")
            summary.append(f"  - Capital expenditure: ${metrics['capex']:,.2f}")
            summary.append(f"  - Annual profit: ${metrics['annual_profit']:,.2f}")
            summary.append(f"  - Payback period: {metrics['payback_years']:.1f} years")
            summary.append(f"  - 5-year ROI: {metrics['roi_5yr']*100:.1f}%")
    
    return "\n".join(summary)

def create_conversion_prompt(station_data, scenarios, roi_results):
    """Create a prompt for GPT-4 to generate conversion recommendations"""
    prompt = f"""
    You are an expert advisor helping gas station owners decide if and how they should convert their stations to include EV charging infrastructure. Please analyze the following data about a gas station and various EV charging demand scenarios to provide a business recommendation.
    
    ## GAS STATION INFORMATION:
    - Station ID: {station_data['station_id']}
    - Location: Latitude {station_data['latitude']:.4f}, Longitude {station_data['longitude']:.4f}
    - Current daily customers: {station_data['daily_customers']}
    - Monthly revenue: ${station_data['monthly_revenue']:,.2f}
    - Property size: {station_data['property_size_sqft']} sq ft
    - Has convenience store: {'Yes' if station_data['has_convenience_store'] else 'No'}
    
    ## EV CHARGING FORECAST SCENARIOS:
    {format_scenario_summary(scenarios, roi_results)}
    
    ## REQUESTED RECOMMENDATION:
    Based on the data above, please provide a detailed business recommendation covering:
    
    1. Whether this gas station should convert to include EV charging stations (and why)
    2. If yes, which investment tier would be most appropriate for their situation
    3. The optimal timing for conversion (immediate, 1 year, 2+ years)
    4. Key risks they should be aware of and how to mitigate them
    5. Additional revenue opportunities related to EV charging (e.g. convenience store sales)
    
    Format your response in clear business language that a gas station owner would understand, with section headings and bullet points where appropriate.
    """
    return prompt

def generate_conversion_recommendation(station_id):
    """Generate a complete conversion recommendation for a gas station"""
    # Load station data
    stations_df = load_gas_stations()
    station_data = stations_df[stations_df['station_id'] == station_id].iloc[0].to_dict()
    
    # Define investment tiers
    investment_tiers = {
        'Basic (1 charger)': {
            'num_chargers': 1,
            'charger_type': 'Level 2',
            'capex': 50000
        },
        'Standard (2 chargers)': {
            'num_chargers': 2,
            'charger_type': 'Level 2 + DC Fast',
            'capex': 150000
        },
        'Premium (4 chargers)': {
            'num_chargers': 4,
            'charger_type': 'DC Fast + Level 2',
            'capex': 300000
        }
    }
    
    # Generate demand scenarios
    scenarios = generate_demand_scenarios(station_data)
    
    # Calculate ROI metrics
    roi_results = calculate_roi_metrics(scenarios, investment_tiers)
    
    # Create prompt for GPT-4
    prompt = create_conversion_prompt(station_data, scenarios, roi_results)
    
    # Get recommendation from GPT-4
    recommendation = query_gpt4(prompt)
    
    # Prepare result object
    result = {
        'station_data': station_data,
        'scenarios': {
            name: {
                'forecast_summary': data['forecast'].describe().to_dict(),
                'plot_path': data['plot_path']
            } for name, data in scenarios.items()
        },
        'roi_results': roi_results,
        'recommendation': recommendation
    }
    
    # Save result to file
    with open(f"{OUTPUT_DIR}/{station_id}_recommendation.json", 'w') as f:
        json.dump(result, f, default=str, indent=2)
    
    return result

def create_dashboard_html(recommendation_result):
    """Create HTML for conversion advisor dashboard"""
    station = recommendation_result['station_data']
    scenarios = recommendation_result['scenarios']
    roi_results = recommendation_result['roi_results']
    recommendation = recommendation_result['recommendation']
    
    # Create HTML components
    scenario_plots_html = ""
    for name, data in scenarios.items():
        plot_path = data['plot_path'].replace('output/', '')
        scenario_plots_html += f"""
        <div class="scenario-card">
            <h3>{name.capitalize()} Scenario</h3>
            <img src="{plot_path}" class="scenario-plot">
        </div>
        """
    
    roi_table_html = """
    <table class="roi-table">
        <thead>
            <tr>
                <th>Investment Tier</th>
                <th>Scenario</th>
                <th>Payback (years)</th>
                <th>5-yr ROI</th>
                <th>Annual Profit</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for tier_name in roi_results['realistic'].keys():
        for scenario_name in roi_results.keys():
            metrics = roi_results[scenario_name][tier_name]
            roi_table_html += f"""
            <tr>
                <td>{tier_name}</td>
                <td>{scenario_name.capitalize()}</td>
                <td>{"∞" if metrics['payback_years'] == float('inf') else f"{metrics['payback_years']:.1f}"}</td>
                <td>{metrics['roi_5yr']*100:.1f}%</td>
                <td>${metrics['annual_profit']:,.2f}</td>
            </tr>
            """
    
    roi_table_html += """
        </tbody>
    </table>
    """
    
    # Format recommendation text with proper HTML
    recommendation_html = recommendation.replace('\n\n', '</p><p>')
    recommendation_html = f"<p>{recommendation_html}</p>"
    
    # Complete HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gas Station Conversion Advisor - {station['station_id']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background-color: #2c3e50; color: white; padding: 20px; margin-bottom: 20px; }}
            .station-info {{ display: flex; flex-wrap: wrap; margin-bottom: 20px; }}
            .info-item {{ flex: 1; min-width: 200px; margin: 10px; }}
            .scenario-container {{ display: flex; flex-wrap: wrap; justify-content: space-between; margin-bottom: 20px; }}
            .scenario-card {{ flex: 1; min-width: 300px; margin: 10px; border: 1px solid #ddd; padding: 15px; }}
            .scenario-plot {{ width: 100%; max-height: 300px; object-fit: contain; }}
            .roi-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            .roi-table th, .roi-table td {{ border: 1px solid #ddd; padding: 8px; text-align: right; }}
            .roi-table th {{ background-color: #f2f2f2; }}
            .recommendation {{ background-color: #f8f9fa; padding: 20px; border-left: 4px solid #2c3e50; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Gas Station Conversion Advisor</h1>
                <h2>{station['station_id']}</h2>
            </div>
            
            <h2>Station Information</h2>
            <div class="station-info">
                <div class="info-item">
                    <strong>Location:</strong> {station['latitude']:.4f}, {station['longitude']:.4f}
                </div>
                <div class="info-item">
                    <strong>Daily Customers:</strong> {station['daily_customers']}
                </div>
                <div class="info-item">
                    <strong>Monthly Revenue:</strong> ${station['monthly_revenue']:,.2f}
                </div>
                <div class="info-item">
                    <strong>Property Size:</strong> {station['property_size_sqft']} sq ft
                </div>
                <div class="info-item">
                    <strong>Convenience Store:</strong> {'Yes' if station['has_convenience_store'] else 'No'}
                </div>
            </div>
            
            <h2>Demand Scenarios</h2>
            <div class="scenario-container">
                {scenario_plots_html}
            </div>
            
            <h2>Financial Analysis</h2>
            {roi_table_html}
            
            <h2>AI-Generated Recommendation</h2>
            <div class="recommendation">
                {recommendation_html}
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save HTML to file
    html_path = f"{OUTPUT_DIR}/{station['station_id']}_dashboard.html"
    with open(html_path, 'w') as f:
        f.write(html)
    
    return html_path

def create_dashboard_component():
    """Create HTML component that can be embedded in existing dashboard"""
    # Generate synthetic stations if needed
    stations_df = load_gas_stations()
    
    # Create selection options
    station_options = "\n".join([f'<option value="{row["station_id"]}">{row["station_id"]}</option>' 
                                for _, row in stations_df.iterrows()])
    
    html = f"""
    <div class="conversion-advisor-component">
        <h2>Gas Station Conversion Advisor</h2>
        
        <div class="input-section">
            <label for="station-select">Select Gas Station:</label>
            <select id="station-select">
                {station_options}
            </select>
            
            <button id="generate-recommendation" onclick="generateRecommendation()">
                Generate Recommendation
            </button>
        </div>
        
        <div id="recommendation-results" style="display: none;">
            <div class="loader" id="recommendation-loader">Generating recommendation...</div>
            <iframe id="recommendation-frame" style="width: 100%; height: 800px; border: none;"></iframe>
        </div>
        
        <script>
            function generateRecommendation() {{
                const stationId = document.getElementById('station-select').value;
                const resultsDiv = document.getElementById('recommendation-results');
                const loader = document.getElementById('recommendation-loader');
                const frame = document.getElementById('recommendation-frame');
                
                resultsDiv.style.display = 'block';
                loader.style.display = 'block';
                frame.style.display = 'none';
                
                // Make AJAX request to backend
                fetch(`/generate_recommendation?station_id=${{stationId}}`)
                    .then(response => response.json())
                    .then(data => {{
                        loader.style.display = 'none';
                        frame.style.display = 'block';
                        frame.src = data.dashboard_url;
                    }})
                    .catch(error => {{
                        loader.innerHTML = `Error: ${{error.message}}`;
                    }});
            }}
        </script>
    </div>
    """
    
    return html

if __name__ == "__main__":
    # Generate a sample recommendation
    stations_df = load_gas_stations()
    sample_station_id = stations_df.iloc[0]['station_id']
    
    print(f"Generating recommendation for {sample_station_id}...")
    result = generate_conversion_recommendation(sample_station_id)
    
    html_path = create_dashboard_html(result)
    print(f"Recommendation dashboard saved to {html_path}") 