import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import json
import os
from IPython.display import display, HTML, IFrame
import ipywidgets as widgets
from datetime import datetime, timedelta
import random
import warnings
warnings.filterwarnings('ignore')

# Set the style for plots
plt.style.use('ggplot')
sns.set_style("whitegrid")
sns.set_palette("viridis")

# Define color scheme for green energy theme
GREEN_ENERGY_COLORS = {
    'primary': '#00a67d',      # Green energy primary
    'secondary': '#0cc0df',    # Electric blue
    'accent': '#f7b733',       # Energy yellow
    'dark_bg': '#0a2e36',      # Dark background
    'light_bg': '#f0f7f4',     # Light background
    'text_light': '#ffffff',   # Light text
    'text_dark': '#0a2e36',    # Dark text
    'success': '#4caf50',      # Success green
    'warning': '#ff9800',      # Warning orange
    'danger': '#f44336'        # Danger red
}

# Function to generate synthetic gas station data
def generate_gas_station_data(n_stations=100):
    """Generate synthetic gas station data with viability scores."""
    # Define major cities with coordinates
    cities = [
        {"name": "New York", "lat": 40.7128, "lng": -74.0060},
        {"name": "Los Angeles", "lat": 34.0522, "lng": -118.2437},
        {"name": "Chicago", "lat": 41.8781, "lng": -87.6298},
        {"name": "Houston", "lat": 29.7604, "lng": -95.3698},
        {"name": "Phoenix", "lat": 33.4484, "lng": -112.0740},
        {"name": "Philadelphia", "lat": 39.9526, "lng": -75.1652},
        {"name": "San Antonio", "lat": 29.4241, "lng": -98.4936},
        {"name": "San Diego", "lat": 32.7157, "lng": -117.1611},
        {"name": "Dallas", "lat": 32.7767, "lng": -96.7970},
        {"name": "San Francisco", "lat": 37.7749, "lng": -122.4194}
    ]

    # Station names and types
    station_names = ["Shell", "Exxon", "BP", "Chevron", "Mobil", "Texaco", "Sunoco", "Valero", "Marathon", "Phillips 66"]
    station_types = ["Highway", "Urban", "Suburban", "Rural"]

    # Lists to store data
    data = []

    for i in range(n_stations):
        # Select a random city
        city = random.choice(cities)

        # Create a small random offset to distribute stations around the city
        lat_offset = (random.random() - 0.5) * 0.2
        lng_offset = (random.random() - 0.5) * 0.2

        # Generate random metrics for viability calculation
        traffic_volume = random.randint(1000, 11000)  # 1000-11000 vehicles per day
        ev_adoption_rate = random.uniform(0.05, 0.25)  # 5-25% EV adoption in area
        competitor_distance = random.uniform(1, 16)  # 1-16 km to nearest competitor
        land_size = random.uniform(500, 2500)  # 500-2500 sq meters
        power_availability = random.uniform(0.2, 1.0)  # 20-100% power grid capacity

        # Calculate viability score (0-100)
        viability_score = (
            (traffic_volume / 11000) * 30 +  # 30% weight to traffic
            (ev_adoption_rate / 0.25) * 25 +  # 25% weight to EV adoption
            (min(competitor_distance, 10) / 10) * 15 +  # 15% weight to competitor distance (capped at 10km)
            (land_size / 2500) * 15 +  # 15% weight to land size
            (power_availability) * 15  # 15% weight to power availability
        )

        viability_score = min(round(viability_score), 100)

        # Determine station type based on location and traffic
        station_type = random.choice(station_types)

        # Calculate financial metrics
        conversion_cost = round((1000000 - 200000 * (power_availability)) * (1 - land_size/5000) + 500000)
        annual_revenue = round(traffic_volume * ev_adoption_rate * 5 * 365)  # Assuming $5 average per charging session
        annual_operating_cost = round(annual_revenue * (0.4 + random.uniform(0, 0.2)))  # 40-60% of revenue
        annual_profit = annual_revenue - annual_operating_cost
        roi = round((annual_profit / conversion_cost) * 100 * 10) / 10
        payback_period = round(conversion_cost / annual_profit * 10) / 10 if annual_profit > 0 else float('inf')

        # Calculate solar potential
        solar_potential = round(land_size * 0.1 * (0.7 + random.uniform(0, 0.3)))  # kWh per day
        solar_installation_cost = round(solar_potential * 1000)  # $1000 per kWh capacity
        solar_annual_savings = round(solar_potential * 365 * 0.15)  # 15 cents per kWh
        solar_roi = round(solar_annual_savings / solar_installation_cost * 100 * 10) / 10
        solar_payback = round(solar_installation_cost / solar_annual_savings * 10) / 10 if solar_annual_savings > 0 else float('inf')

        # Store the data
        data.append({
            "id": f"station-{i+1}",
            "name": f"{random.choice(station_names)} {city['name']} {i+1}",
            "lat": city["lat"] + lat_offset,
            "lng": city["lng"] + lng_offset,
            "city": city["name"],
            "type": station_type,
            "traffic_volume": traffic_volume,
            "ev_adoption_rate": round(ev_adoption_rate * 100),
            "competitor_distance": round(competitor_distance * 10) / 10,
            "land_size": round(land_size),
            "power_availability": round(power_availability * 100),
            "viability_score": viability_score,
            "conversion_cost": conversion_cost,
            "annual_revenue": annual_revenue,
            "annual_operating_cost": annual_operating_cost,
            "annual_profit": annual_profit,
            "roi": roi,
            "payback_period": payback_period,
            "solar_potential": solar_potential,
            "solar_installation_cost": solar_installation_cost,
            "solar_annual_savings": solar_annual_savings,
            "solar_roi": solar_roi,
            "solar_payback": solar_payback,
            "base_price": 0.40,  # $ per kWh
            "peak_price": 0.55,  # $ per kWh during peak hours
            "off_peak_price": 0.30,  # $ per kWh during off-peak
            "estimated_revenue_increase": random.randint(10, 30)  # 10-30% increase with dynamic pricing
        })

    return pd.DataFrame(data)

# Function to create an interactive map
def create_interactive_map(df, center=[39.8283, -98.5795], zoom=4):
    """Create an interactive map with gas stations colored by viability score."""
    # Create a map centered on the US
    m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")

    # Define a color function based on viability score
    def get_color(score):
        if score >= 80:
            return '#00a67d'  # Green for high viability
        elif score >= 60:
            return '#f7b733'  # Yellow for medium-high viability
        elif score >= 40:
            return '#ff9900'  # Orange for medium viability
        else:
            return '#f44336'  # Red for low viability

    # Add markers for each gas station
    for _, row in df.iterrows():
        # Create popup content
        popup_content = f"""
        <div style="font-family: Arial, sans-serif; width: 300px;">
            <h3 style="margin-top: 0; border-bottom: 2px solid #00a67d; padding-bottom: 5px;">{row['name']}</h3>
            <p><strong>Type:</strong> {row['type']}</p>
            <p><strong>Viability Score:</strong> {row['viability_score']}/100</p>

            <div style="display: flex; border-bottom: 1px solid #ddd; margin: 15px 0 10px;">
                <button onclick="showTab('viability-{row['id']}')" style="background: none; border: none; padding: 8px 15px; cursor: pointer; border-bottom: 3px solid #00a67d; font-weight: bold;">Viability</button>
                <button onclick="showTab('financial-{row['id']}')" style="background: none; border: none; padding: 8px 15px; cursor: pointer; border-bottom: 3px solid transparent;">Financial</button>
                <button onclick="showTab('solar-{row['id']}')" style="background: none; border: none; padding: 8px 15px; cursor: pointer; border-bottom: 3px solid transparent;">Solar</button>
            </div>

            <div id="viability-{row['id']}" class="tab-content" style="display: block;">
                <h4 style="margin-top: 0;">Viability Factors</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Traffic Volume:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">{row['traffic_volume']:,} vehicles/day</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">EV Adoption Rate:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">{row['ev_adoption_rate']}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Competitor Distance:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">{row['competitor_distance']} km</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Land Size:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">{row['land_size']} m²</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Power Availability:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">{row['power_availability']}%</td>
                    </tr>
                </table>
            </div>

            <div id="financial-{row['id']}" class="tab-content" style="display: none;">
                <h4 style="margin-top: 0;">Financial Analysis</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Conversion Cost:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">${row['conversion_cost']:,}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Annual Revenue:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">${row['annual_revenue']:,}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Annual Operating Cost:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">${row['annual_operating_cost']:,}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Annual Profit:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">${row['annual_profit']:,}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">ROI:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">{row['roi']}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Payback Period:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">{row['payback_period']} years</td>
                    </tr>
                </table>
            </div>

            <div id="solar-{row['id']}" class="tab-content" style="display: none;">
                <h4 style="margin-top: 0;">Solar Integration</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Solar Potential:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">{row['solar_potential']} kWh/day</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Installation Cost:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">${row['solar_installation_cost']:,}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Annual Savings:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">${row['solar_annual_savings']:,}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Solar ROI:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">{row['solar_roi']}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border-bottom: 1px solid #eee; font-weight: bold;">Solar Payback Period:</td>
                        <td style="padding: 5px; border-bottom: 1px solid #eee;">{row['solar_payback']} years</td>
                    </tr>
                </table>
            </div>

            <script>
            function showTab(tabId) {
                // Hide all tab contents
                var tabContents = document.getElementsByClassName('tab-content');
                for (var i = 0; i < tabContents.length; i++) {
                    tabContents[i].style.display = 'none';
                }

                // Show the selected tab content
                document.getElementById(tabId).style.display = 'block';

                // Update button styles
                var buttons = document.getElementsByTagName('button');
                for (var i = 0; i < buttons.length; i++) {
                    buttons[i].style.borderBottom = '3px solid transparent';
                    buttons[i].style.fontWeight = 'normal';
                }

                // Highlight the active button
                event.target.style.borderBottom = '3px solid #00a67d';
                event.target.style.fontWeight = 'bold';
            }
            </script>
        </div>
        """

        # Create a custom icon
        icon_html = f"""
            <div style="background-color: {get_color(row['viability_score'])};
                        width: 30px;
                        height: 30px;
                        border-radius: 15px;
                        border: 2px solid white;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        font-weight: bold;
                        color: white;
                        box-shadow: 0 0 10px rgba(0,0,0,0.3);">
                {row['viability_score']}
            </div>
        """

        icon = folium.DivIcon(
            html=icon_html,
            icon_size=(30, 30),
            icon_anchor=(15, 15)
        )

        # Add the marker to the map
        folium.Marker(
            location=[row['lat'], row['lng']],
            popup=folium.Popup(popup_content, max_width=350),
            icon=icon,
            tooltip=f"{row['name']} (Score: {row['viability_score']})"
        ).add_to(m)

    # Add a legend
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; right: 50px;
                border: 2px solid grey;
                z-index: 9999;
                background-color: white;
                padding: 10px;
                border-radius: 5px;
                font-family: Arial, sans-serif;">
        <h4 style="margin-top: 0;">Viability Score Legend</h4>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="background-color: #00a67d; width: 20px; height: 20px; border-radius: 10px; margin-right: 10px;"></div>
            <span>80-100: Excellent</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="background-color: #f7b733; width: 20px; height: 20px; border-radius: 10px; margin-right: 10px;"></div>
            <span>60-79: Good</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="background-color: #ff9900; width: 20px; height: 20px; border-radius: 10px; margin-right: 10px;"></div>
            <span>40-59: Moderate</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background-color: #f44336; width: 20px; height: 20px; border-radius: 10px; margin-right: 10px;"></div>
            <span>0-39: Low</span>
        </div>
    </div>
    '''

    m.get_root().html.add_child(folium.Element(legend_html))

    return m

# Function to create a traffic heatmap
def create_traffic_heatmap(df, center=[39.8283, -98.5795], zoom=4):
    """Create a heatmap showing traffic volume at gas stations."""
    # Create a map centered on the US
    m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")

    # Prepare data for heatmap
    heat_data = [[row['lat'], row['lng'], row['traffic_volume'] / 1000] for _, row in df.iterrows()]

    # Add heatmap layer
    HeatMap(heat_data, radius=15, gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'yellow', 1: 'red'}).add_to(m)

    # Add a legend
    legend_html = '''
    <div style="position: fixed;
                bottom: 50px; right: 50px;
                border: 2px solid grey;
                z-index: 9999;
                background-color: white;
                padding: 10px;
                border-radius: 5px;
                font-family: Arial, sans-serif;">
        <h4 style="margin-top: 0;">Traffic Volume Heatmap</h4>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="background-color: red; width: 20px; height: 20px; margin-right: 10px;"></div>
            <span>High Traffic</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="background-color: yellow; width: 20px; height: 20px; margin-right: 10px;"></div>
            <span>Medium-High Traffic</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px;">
            <div style="background-color: lime; width: 20px; height: 20px; margin-right: 10px;"></div>
            <span>Medium Traffic</span>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background-color: blue; width: 20px; height: 20px; margin-right: 10px;"></div>
            <span>Low Traffic</span>
        </div>
    </div>
    '''

    m.get_root().html.add_child(folium.Element(legend_html))

    return m

# Function to create visualizations for dashboard
def create_dashboard_visualizations(df):
    """Create visualizations for the dashboard."""
    # Set the style
    plt.style.use('ggplot')
    sns.set_palette([GREEN_ENERGY_COLORS['primary'], GREEN_ENERGY_COLORS['secondary'],
                     GREEN_ENERGY_COLORS['accent'], GREEN_ENERGY_COLORS['warning']])

    # Create a figure with subplots
    fig = plt.figure(figsize=(20, 15))

    # 1. Viability Score Distribution
    ax1 = plt.subplot(2, 2, 1)
    sns.histplot(df['viability_score'], bins=10, kde=True, ax=ax1)
    ax1.set_title('Viability Score Distribution', fontsize=16)
    ax1.set_xlabel('Viability Score', fontsize=12)
    ax1.set_ylabel('Number of Stations', fontsize=12)

    # 2. ROI vs Viability Score
    ax2 = plt.subplot(2, 2, 2)
    sns.scatterplot(x='viability_score', y='roi', data=df, hue='type', size='traffic_volume',
                   sizes=(50, 300), alpha=0.7, ax=ax2)
    ax2.set_title('ROI vs Viability Score', fontsize=16)
    ax2.set_xlabel('Viability Score', fontsize=12)
    ax2.set_ylabel('ROI (%)', fontsize=12)

    # 3. Payback Period by Station Type
    ax3 = plt.subplot(2, 2, 3)
    # Filter out infinite payback periods
    df_finite = df[df['payback_period'] < 100]
    sns.boxplot(x='type', y='payback_period', data=df_finite, ax=ax3)
    ax3.set_title('Payback Period by Station Type', fontsize=16)
    ax3.set_xlabel('Station Type', fontsize=12)
    ax3.set_ylabel('Payback Period (years)', fontsize=12)

    # 4. Traffic Volume vs EV Adoption Rate
    ax4 = plt.subplot(2, 2, 4)
    scatter = sns.scatterplot(x='traffic_volume', y='ev_adoption_rate', data=df,
                             hue='viability_score', size='land_size', sizes=(50, 300),
                             palette='viridis', ax=ax4)
    ax4.set_title('Traffic Volume vs EV Adoption Rate', fontsize=16)
    ax4.set_xlabel('Traffic Volume (vehicles/day)', fontsize=12)
    ax4.set_ylabel('EV Adoption Rate (%)', fontsize=12)

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    plt.savefig('dashboard_visualizations.png', dpi=300, bbox_inches='tight')

    return fig

# Function to create EV adoption forecast
def create_ev_forecast(base_year=2025, forecast_years=5, growth_rates=[5, 10, 15]):
    """Create EV adoption forecast visualization."""
    years = list(range(base_year, base_year + forecast_years + 1))

    # Create a figure
    plt.figure(figsize=(12, 8))

    # Plot different growth scenarios
    for rate in growth_rates:
        # Starting from 10% adoption in base year
        adoption = [10]

        # Calculate adoption for each year
        for i in range(1, len(years)):
            adoption.append(adoption[-1] * (1 + rate/100))

        plt.plot(years, adoption, marker='o', linewidth=3, label=f"{rate}% Annual Growth")

    # Add labels and title
    plt.title('EV Adoption Rate Forecast', fontsize=18)
    plt.xlabel('Year', fontsize=14)
    plt.ylabel('EV Adoption Rate (%)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)

    # Set y-axis to percentage
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0f}%'))

    # Save the figure
    plt.savefig('ev_forecast.png', dpi=300, bbox_inches='tight')

    return plt.gcf()

# Function to create dynamic pricing simulator
def create_dynamic_pricing_simulator():
    """Create a dynamic pricing simulator widget."""
    # Create widgets
    base_price = widgets.FloatSlider(
        value=0.40,
        min=0.20,
        max=0.60,
        step=0.05,
        description='Base Price ($/kWh):',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
        style={'description_width': 'initial'}
    )

    peak_differential = widgets.IntSlider(
        value=30,
        min=10,
        max=50,
        step=5,
        description='Peak/Off-Peak Differential (%):',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='d',
        style={'description_width': 'initial'}
    )

    demand_elasticity = widgets.IntSlider(
        value=15,
        min=5,
        max=25,
        step=5,
        description='Demand Elasticity (%):',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='d',
        style={'description_width': 'initial'}
    )

    # Output widget for results
    output = widgets.Output()

    # Function to update results
    def update_results(base_price, peak_differential, demand_elasticity):
        peak_price = base_price * (1 + peak_differential/100)
        off_peak_price = base_price * (1 - peak_differential/100)

        # Simple model for revenue increase based on elasticity and price differential
        revenue_increase = peak_differential * 0.5 + demand_elasticity * 0.3 + random.uniform(5, 15)

        with output:
            output.clear_output()
            print(f"Base Price: ${base_price:.2f}/kWh")
            print(f"Peak Hours Price: ${peak_price:.2f}/kWh")
            print(f"Off-Peak Price: ${off_peak_price:.2f}/kWh")
            print(f"Estimated Revenue Increase: {revenue_increase:.1f}%")
            print(f"Recommended Peak Hours: 4:00 PM - 8:00 PM")
            print(f"Recommended Off-Peak Hours: 11:00 PM - 6:00 AM")

    # Create interactive widget
    interactive_widget = widgets.interactive(
        update_results,
        base_price=base_price,
        peak_differential=peak_differential,
        demand_elasticity=demand_elasticity
    )

    # Display initial results
    update_results(0.40, 30, 15)

    # Create a VBox to display everything
    simulator = widgets.VBox([
        widgets.HTML("<h3 style='color: #00a67d;'>Dynamic Pricing Simulator</h3>"),
        widgets.HTML("<p>Optimize charging prices based on time of day, demand, and grid capacity</p>"),
        interactive_widget,
        output
    ])

    return simulator

# Function to create scenario comparison
def create_scenario_comparison(df):
    """Create a scenario comparison visualization."""
    # Define scenarios
    scenarios = {
        'Base Case': {
            'ev_growth': 10,
            'incentive': 0,
            'solar': False
        },
        'High EV Growth': {
            'ev_growth': 20,
            'incentive': 0,
            'solar': False
        },
        'Government Incentives': {
            'ev_growth': 10,
            'incentive': 30,
            'solar': False
        },
        'Solar Integration': {
            'ev_growth': 10,
            'incentive': 0,
            'solar': True
        },
        'Optimistic': {
            'ev_growth': 20,
            'incentive': 30,
            'solar': True
        }
    }

    # Calculate metrics for each scenario
    results = {}

    for name, params in scenarios.items():
        # Copy the dataframe
        scenario_df = df.copy()

        # Apply EV growth
        if params['ev_growth'] > 10:  # Base case is 10%
            growth_factor = params['ev_growth'] / 10
            scenario_df['annual_revenue'] = scenario_df['annual_revenue'] * growth_factor
            scenario_df['annual_profit'] = scenario_df['annual_revenue'] - scenario_df['annual_operating_cost']

        # Apply incentives
        if params['incentive'] > 0:
            incentive_factor = 1 - (params['incentive'] / 100)
            scenario_df['conversion_cost'] = scenario_df['conversion_cost'] * incentive_factor

        # Apply solar integration
        if params['solar']:
            scenario_df['annual_profit'] = scenario_df['annual_profit'] + scenario_df['solar_annual_savings']

        # Recalculate ROI and payback period
        scenario_df['roi'] = (scenario_df['annual_profit'] / scenario_df['conversion_cost']) * 100
        scenario_df['payback_period'] = scenario_df['conversion_cost'] / scenario_df['annual_profit']

        # Calculate metrics
        results[name] = {
            'avg_roi': scenario_df['roi'].mean(),
            'avg_payback': scenario_df['payback_period'].mean(),
            'total_investment': scenario_df['conversion_cost'].sum(),
            'annual_profit': scenario_df['annual_profit'].sum(),
            'viable_stations': sum(scenario_df['roi'] > 15)  # Stations with ROI > 15%
        }

    # Create a dataframe from results
    results_df = pd.DataFrame(results).T

    # Create a figure
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # 1. Average ROI
    axes[0, 0].bar(results_df.index, results_df['avg_roi'], color=GREEN_ENERGY_COLORS['primary'])
    axes[0, 0].set_title('Average ROI (%)', fontsize=16)
    axes[0, 0].set_ylabel('ROI (%)', fontsize=12)
    axes[0, 0].tick_params(axis='x', rotation=45)

    # 2. Average Payback Period
    axes[0, 1].bar(results_df.index, results_df['avg_payback'], color=GREEN_ENERGY_COLORS['secondary'])
    axes[0, 1].set_title('Average Payback Period (years)', fontsize=16)
    axes[0, 1].set_ylabel('Years', fontsize=12)
    axes[0, 1].tick_params(axis='x', rotation=45)

    # 3. Total Investment
    axes[1, 0].bar(results_df.index, results_df['total_investment'] / 1e6, color=GREEN_ENERGY_COLORS['accent'])
    axes[1, 0].set_title('Total Investment ($ millions)', fontsize=16)
    axes[1, 0].set_ylabel('$ Millions', fontsize=12)
    axes[1, 0].tick_params(axis='x', rotation=45)

    # 4. Viable Stations
    axes[1, 1].bar(results_df.index, results_df['viable_stations'], color=GREEN_ENERGY_COLORS['success'])
    axes[1, 1].set_title('Number of Viable Stations (ROI > 15%)', fontsize=16)
    axes[1, 1].set_ylabel('Count', fontsize=12)
    axes[1, 1].tick_params(axis='x', rotation=45)

    # Adjust layout
    plt.tight_layout()

    # Save the figure
    plt.savefig('scenario_comparison.png', dpi=300, bbox_inches='tight')

    return fig, results_df

# Function to create a dashboard HTML
def create_dashboard_html(df):
    """Create an HTML dashboard with all visualizations."""
    # Create visualizations
    dashboard_viz = create_dashboard_visualizations(df)
    ev_forecast_viz = create_ev_forecast()
    scenario_fig, scenario_df = create_scenario_comparison(df)

    # Create maps
    station_map = create_interactive_map(df)
    traffic_map = create_traffic_heatmap(df)

    # Save maps as HTML
    station_map.save('station_map.html')
    traffic_map.save('traffic_map.html')

    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HPC Station Conversion Dashboard</title>
        <style>
            :root {{
                --primary-color: #00a67d;
                --secondary-color: #0cc0df;
                --accent-color: #f7b733;
                --dark-bg: #0a2e36;
                --light-bg: #f0f7f4;
                --text-light: #ffffff;
                --text-dark: #0a2e36;
                --border-color: rgba(255, 255, 255, 0.2);
                --card-bg: rgba(255, 255, 255, 0.1);
                --success-color: #4caf50;
                --warning-color: #ff9800;
                --danger-color: #f44336;
            }}

            body {{
                margin: 0;
                padding: 0;
                font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                background: var(--dark-bg);
                color: var(--text-light);
                overflow-x: hidden;
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}

            header {{
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: linear-gradient(135deg, rgba(0, 166, 125, 0.1) 0%, rgba(12, 192, 223, 0.1) 100%);
                border-radius: 10px;
                border: 1px solid var(--border-color);
            }}

            h1 {{
                font-size: 2.5rem;
                margin: 0;
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}

            h2 {{
                font-size: 1.8rem;
                margin-top: 40px;
                margin-bottom: 20px;
                color: var(--primary-color);
                border-bottom: 2px solid var(--border-color);
                padding-bottom: 10px;
            }}

            .dashboard-section {{
                background: rgba(10, 46, 54, 0.6);
                border-radius: 16px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                border: 1px solid var(--border-color);
                padding: 25px;
                margin-bottom: 30px;
                position: relative;
                overflow: hidden;
            }}

            .dashboard-section::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 4px;
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            }}

            .map-container {{
                height: 600px;
                margin-bottom: 25px;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                border: 1px solid var(--border-color);
            }}

            .tabs {{
                display: flex;
                border-bottom: 1px solid var(--border-color);
                margin-bottom: 20px;
            }}

            .tab {{
                padding: 10px 20px;
                cursor: pointer;
                border-bottom: 3px solid transparent;
                transition: all 0.3s ease;
            }}

            .tab.active {{
                border-bottom: 3px solid var(--primary-color);
                font-weight: bold;
            }}

            .tab-content {{
                display: none;
            }}

            .tab-content.active {{
                display: block;
            }}

            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}

            .metric-card {{
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                padding: 20px;
                text-align: center;
                border: 1px solid var(--border-color);
                transition: all 0.3s ease;
            }}

            .metric-card h3 {{
                margin-top: 0;
                color: var(--text-light);
                font-size: 1rem;
                font-weight: 500;
                margin-bottom: 15px;
            }}

            .metric-value {{
                font-size: 2.2rem;
                font-weight: bold;
                background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 10px 0;
                line-height: 1;
            }}

            .metric-unit {{
                font-size: 0.9rem;
                color: rgba(255, 255, 255, 0.7);
                margin-top: 5px;
            }}

            .viz-container {{
                margin-top: 30px;
                text-align: center;
            }}

            .viz-container img {{
                max-width: 100%;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            }}

            iframe {{
                width: 100%;
                height: 600px;
                border: none;
                border-radius: 10px;
            }}

            footer {{
                text-align: center;
                margin-top: 50px;
                padding: 20px;
                border-top: 1px solid var(--border-color);
                color: rgba(255, 255, 255, 0.7);
            }}

            @media (max-width: 768px) {{
                .metrics-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>HPC Station Conversion Dashboard</h1>
                <p>Interactive analysis of gas station viability for conversion to High-Power Charging stations</p>
            </header>

            <div class="dashboard-section">
                <h2>Overview</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Total Stations Analyzed</h3>
                        <div class="metric-value">{len(df)}</div>
                    </div>
                    <div class="metric-card">
                        <h3>Average Viability Score</h3>
                        <div class="metric-value">{df['viability_score'].mean():.1f}</div>
                        <div class="metric-unit">out of 100</div>
                    </div>
                    <div class="metric-card">
                        <h3>Average ROI</h3>
                        <div class="metric-value">{df['roi'].mean():.1f}%</div>
                    </div>
                    <div class="metric-card">
                        <h3>Average Payback Period</h3>
                        <div class="metric-value">{df[df['payback_period'] < 100]['payback_period'].mean():.1f}</div>
                        <div class="metric-unit">years</div>
                    </div>
                </div>
            </div>

            <div class="dashboard-section">
                <h2>Interactive Maps</h2>
                <div class="tabs">
                    <div class="tab active" onclick="showTab('station-map')">Station Viability Map</div>
                    <div class="tab" onclick="showTab('traffic-map')">Traffic Heatmap</div>
                </div>

                <div id="station-map" class="tab-content active">
                    <div class="map-container">
                        <iframe src="station_map.html"></iframe>
                    </div>
                </div>

                <div id="traffic-map" class="tab-content">
                    <div class="map-container">
                        <iframe src="traffic_map.html"></iframe>
                    </div>
                </div>
            </div>

            <div class="dashboard-section">
                <h2>Data Analysis</h2>
                <div class="viz-container">
                    <img src="dashboard_visualizations.png" alt="Dashboard Visualizations">
                </div>
            </div>

            <div class="dashboard-section">
                <h2>EV Adoption Forecast</h2>
                <div class="viz-container">
                    <img src="ev_forecast.png" alt="EV Adoption Forecast">
                </div>
            </div>

            <div class="dashboard-section">
                <h2>Scenario Comparison</h2>
                <div class="viz-container">
                    <img src="scenario_comparison.png" alt="Scenario Comparison">
                </div>

                <div class="scenario-table">
                    <h3>Scenario Details</h3>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                        <thead>
                            <tr style="background: rgba(255, 255, 255, 0.1);">
                                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border-color);">Scenario</th>
                                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border-color);">Avg ROI (%)</th>
                                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border-color);">Avg Payback (years)</th>
                                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border-color);">Total Investment ($M)</th>
                                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border-color);">Viable Stations</th>
                            </tr>
                        </thead>
                        <tbody>
                            {{
                                ''.join([
                                    f'<tr style="border-bottom: 1px solid var(--border-color);">'
                                    f'<td style="padding: 10px;">{index}</td>'
                                    f'<td style="padding: 10px; text-align: right;">{row["avg_roi"]:.1f}%</td>'
                                    f'<td style="padding: 10px; text-align: right;">{row["avg_payback"]:.1f}</td>'
                                    f'<td style="padding: 10px; text-align: right;">${row["total_investment"]/1e6:.1f}M</td>'
                                    f'<td style="padding: 10px; text-align: right;">{row["viable_stations"]}</td>'
                                    f'</tr>'
                                    for index, row in scenario_df.iterrows()
                                ])
                            }}
                        </tbody>
                    </table>
                </div>
            </div>

            <footer>
                <p>HPC Station Conversion Analysis Dashboard | Created for MLOps Project</p>
            </footer>
        </div>

        <script>
            function showTab(tabId) {{
                // Hide all tab contents
                var tabContents = document.getElementsByClassName('tab-content');
                for (var i = 0; i < tabContents.length; i++) {{
                    tabContents[i].classList.remove('active');
                }}

                // Show the selected tab content
                document.getElementById(tabId).classList.add('active');

                // Update tab styles
                var tabs = document.getElementsByClassName('tab');
                for (var i = 0; i < tabs.length; i++) {{
                    tabs[i].classList.remove('active');
                }}

                // Find the clicked tab and make it active
                var clickedTab = event.target;
                clickedTab.classList.add('active');
            }}
        </script>
    </body>
    </html>
    """

    # Save the HTML file
    with open('hpc_dashboard.html', 'w') as f:
        f.write(html_content)

    return html_content

# Main function to run in Google Colab
def run_hpc_dashboard():
    """Main function to run the HPC dashboard in Google Colab."""
    print("Generating gas station data...")
    df = generate_gas_station_data(n_stations=100)

    print("Creating visualizations...")
    create_dashboard_visualizations(df)
    create_ev_forecast()
    create_scenario_comparison(df)

    print("Creating interactive maps...")
    station_map = create_interactive_map(df)
    traffic_map = create_traffic_heatmap(df)

    # Save maps
    station_map.save('station_map.html')
    traffic_map.save('traffic_map.html')

    print("Creating dashboard HTML...")
    create_dashboard_html(df)

    print("Dashboard created successfully!")
    print("You can view the dashboard by opening 'hpc_dashboard.html'")

    # Display the dashboard in Colab
    display(HTML('<h2 style="color: #00a67d;">HPC Station Conversion Dashboard</h2>'))
    display(IFrame(src='hpc_dashboard.html', width='100%', height=600))

    return df

# If running directly
if __name__ == "__main__":
    df = run_hpc_dashboard()