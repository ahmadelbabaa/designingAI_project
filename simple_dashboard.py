#!/usr/bin/env python3
"""
Simplified HPC Dashboard for local testing
"""

import os
import pandas as pd
import numpy as np
import random
from datetime import datetime
import matplotlib.pyplot as plt
import folium
import json
import webbrowser
import yaml

print("===== HPC Simplified Dashboard =====")

# Create necessary folders
folders = ['data', 'config', 'output']
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Created folder: {folder}")

# Generate synthetic gas station data
def generate_gas_stations(n_stations=150):
    """Generate synthetic gas station data."""
    
    # Define major cities with coordinates across the world
    cities = [
        # North America
        {"name": "New York", "lat": 40.7128, "lng": -74.0060, "region": "North America", "ev_adoption_factor": 1.1},
        {"name": "Los Angeles", "lat": 34.0522, "lng": -118.2437, "region": "North America", "ev_adoption_factor": 1.3},
        {"name": "Chicago", "lat": 41.8781, "lng": -87.6298, "region": "North America", "ev_adoption_factor": 0.9},
        {"name": "Houston", "lat": 29.7604, "lng": -95.3698, "region": "North America", "ev_adoption_factor": 0.8},
        {"name": "Phoenix", "lat": 33.4484, "lng": -112.0740, "region": "North America", "ev_adoption_factor": 0.9},
        {"name": "Philadelphia", "lat": 39.9526, "lng": -75.1652, "region": "North America", "ev_adoption_factor": 1.0},
        {"name": "San Antonio", "lat": 29.4241, "lng": -98.4936, "region": "North America", "ev_adoption_factor": 0.8},
        {"name": "San Diego", "lat": 32.7157, "lng": -117.1611, "region": "North America", "ev_adoption_factor": 1.2},
        {"name": "Dallas", "lat": 32.7767, "lng": -96.7970, "region": "North America", "ev_adoption_factor": 0.85},
        {"name": "San Francisco", "lat": 37.7749, "lng": -122.4194, "region": "North America", "ev_adoption_factor": 1.5},
        {"name": "Austin", "lat": 30.2672, "lng": -97.7431, "region": "North America", "ev_adoption_factor": 1.2},
        {"name": "Seattle", "lat": 47.6062, "lng": -122.3321, "region": "North America", "ev_adoption_factor": 1.4},
        {"name": "Denver", "lat": 39.7392, "lng": -104.9903, "region": "North America", "ev_adoption_factor": 1.1},
        {"name": "Portland", "lat": 45.5051, "lng": -122.6750, "region": "North America", "ev_adoption_factor": 1.3},
        {"name": "Miami", "lat": 25.7617, "lng": -80.1918, "region": "North America", "ev_adoption_factor": 0.9},
        
        # Canada
        {"name": "Vancouver", "lat": 49.2827, "lng": -123.1207, "region": "North America", "ev_adoption_factor": 1.4},
        {"name": "Toronto", "lat": 43.6532, "lng": -79.3832, "region": "North America", "ev_adoption_factor": 1.2},
        {"name": "Montreal", "lat": 45.5017, "lng": -73.5673, "region": "North America", "ev_adoption_factor": 1.1},
        {"name": "Calgary", "lat": 51.0447, "lng": -114.0719, "region": "North America", "ev_adoption_factor": 0.9},
        
        # Europe
        {"name": "London", "lat": 51.5074, "lng": -0.1278, "region": "Europe", "ev_adoption_factor": 1.3},
        {"name": "Paris", "lat": 48.8566, "lng": 2.3522, "region": "Europe", "ev_adoption_factor": 1.4},
        {"name": "Berlin", "lat": 52.5200, "lng": 13.4050, "region": "Europe", "ev_adoption_factor": 1.5},
        {"name": "Madrid", "lat": 40.4168, "lng": -3.7038, "region": "Europe", "ev_adoption_factor": 1.1},
        {"name": "Rome", "lat": 41.9028, "lng": 12.4964, "region": "Europe", "ev_adoption_factor": 0.9},
        {"name": "Amsterdam", "lat": 52.3676, "lng": 4.9041, "region": "Europe", "ev_adoption_factor": 1.7},
        {"name": "Oslo", "lat": 59.9139, "lng": 10.7522, "region": "Europe", "ev_adoption_factor": 2.0},
        {"name": "Stockholm", "lat": 59.3293, "lng": 18.0686, "region": "Europe", "ev_adoption_factor": 1.8},
        {"name": "Copenhagen", "lat": 55.6761, "lng": 12.5683, "region": "Europe", "ev_adoption_factor": 1.7},
        {"name": "Zurich", "lat": 47.3769, "lng": 8.5417, "region": "Europe", "ev_adoption_factor": 1.6},
        
        # Asia
        {"name": "Tokyo", "lat": 35.6762, "lng": 139.6503, "region": "Asia", "ev_adoption_factor": 1.2},
        {"name": "Shanghai", "lat": 31.2304, "lng": 121.4737, "region": "Asia", "ev_adoption_factor": 1.1},
        {"name": "Beijing", "lat": 39.9042, "lng": 116.4074, "region": "Asia", "ev_adoption_factor": 1.3},
        {"name": "Seoul", "lat": 37.5665, "lng": 126.9780, "region": "Asia", "ev_adoption_factor": 1.4},
        {"name": "Singapore", "lat": 1.3521, "lng": 103.8198, "region": "Asia", "ev_adoption_factor": 1.3},
        {"name": "Hong Kong", "lat": 22.3193, "lng": 114.1694, "region": "Asia", "ev_adoption_factor": 1.0},
        
        # Australia/Oceania
        {"name": "Sydney", "lat": -33.8688, "lng": 151.2093, "region": "Oceania", "ev_adoption_factor": 1.1},
        {"name": "Melbourne", "lat": -37.8136, "lng": 144.9631, "region": "Oceania", "ev_adoption_factor": 1.0},
        {"name": "Auckland", "lat": -36.8509, "lng": 174.7645, "region": "Oceania", "ev_adoption_factor": 1.2},
        
        # South America
        {"name": "Sao Paulo", "lat": -23.5505, "lng": -46.6333, "region": "South America", "ev_adoption_factor": 0.7},
        {"name": "Rio de Janeiro", "lat": -22.9068, "lng": -43.1729, "region": "South America", "ev_adoption_factor": 0.6},
        {"name": "Buenos Aires", "lat": -34.6037, "lng": -58.3816, "region": "South America", "ev_adoption_factor": 0.5},
        {"name": "Santiago", "lat": -33.4489, "lng": -70.6693, "region": "South America", "ev_adoption_factor": 0.8},
        {"name": "Bogota", "lat": 4.7110, "lng": -74.0721, "region": "South America", "ev_adoption_factor": 0.6},
        {"name": "Lima", "lat": -12.0464, "lng": -77.0428, "region": "South America", "ev_adoption_factor": 0.5},
        
        # Africa
        {"name": "Cairo", "lat": 30.0444, "lng": 31.2357, "region": "Africa", "ev_adoption_factor": 0.4},
        {"name": "Lagos", "lat": 6.5244, "lng": 3.3792, "region": "Africa", "ev_adoption_factor": 0.3},
        {"name": "Nairobi", "lat": -1.2921, "lng": 36.8219, "region": "Africa", "ev_adoption_factor": 0.4},
        {"name": "Cape Town", "lat": -33.9249, "lng": 18.4241, "region": "Africa", "ev_adoption_factor": 0.6},
        {"name": "Johannesburg", "lat": -26.2041, "lng": 28.0473, "region": "Africa", "ev_adoption_factor": 0.5}
    ]
    
    # Station names and types
    station_names = ["Shell", "Exxon", "BP", "Chevron", "Mobil", "Texaco", "Total", "Eni", "Petrobras", "Sinopec", "Petrochina"]
    station_types = ["Highway", "Urban", "Suburban", "Rural"]
    
    # Simple check for water coordinates - these are very approximate
    def is_likely_water(lat, lng):
        # San Francisco Bay Area
        if (37.5 < lat < 38.0) and (-122.5 < lng < -122.0):
            # Rough bounds of SF Bay
            if ((lng < -122.3 and lat < 37.8) or  # Main Bay
                (lng < -122.2 and lat > 37.8) or  # North Bay
                (lng > -122.2 and lat < 37.7)):  # South Bay
                return True
        
        # New York Harbor / Atlantic
        if (40.5 < lat < 40.9) and (-74.2 < lng < -73.7):
            if lng < -74.0 and lat < 40.7:  # NY Harbor
                return True
            if lng > -73.9 and lat < 40.65:  # Atlantic near Brooklyn
                return True
        
        # Great Lakes
        if (41.5 < lat < 44.0) and (-88.0 < lng < -85.0):  # Lake Michigan near Chicago
            if lat > 41.9 and lng < -87.5:
                return True

        # Pacific Ocean (West Coast)
        if lng < -124.0:  # Pacific Coast
            return True
            
        # Atlantic Ocean (East Coast)
        if (25.0 < lat < 45.0) and lng > -71.0:  # Atlantic Coast
            return True
            
        # Simple check for coastal cities
        coastal_cities = ["San Francisco", "Los Angeles", "Seattle", "New York", "Miami", "Vancouver", 
                          "Sydney", "Singapore", "Hong Kong", "Tokyo", "Rio de Janeiro"]
        
        # For known coastal cities, avoid placing too far in likely ocean directions
        for city in cities:
            if city["name"] in coastal_cities:
                city_lat, city_lng = city["lat"], city["lng"]
                # If we're near a coastal city
                if abs(lat - city_lat) < 0.15 and abs(lng - city_lng) < 0.15:
                    # West Coast US cities
                    if city["name"] in ["San Francisco", "Los Angeles", "Seattle", "Vancouver"] and lng < city_lng - 0.03:
                        return True
                    # East Coast US cities
                    if city["name"] in ["New York", "Miami"] and lng > city_lng + 0.03:
                        return True
                    # Other coastal checks can be added
            
        return False
    
    data = []
    station_id = 1
    
    # Ensure a balanced distribution by allocating stations per city
    # Calculate minimum number of stations per city to ensure coverage
    min_stations_per_city = max(2, n_stations // len(cities))  # At least 2 stations per city
    
    # First pass: create minimum stations for each city
    for city in cities:
        # For each city, create min_stations_per_city stations
        for i in range(min_stations_per_city):
            # Create a smaller random offset to distribute stations around the city
            lat_offset = (random.random() - 0.5) * 0.08
            lng_offset = (random.random() - 0.5) * 0.08
            
            # Calculate new coordinates
            new_lat = city["lat"] + lat_offset
            new_lng = city["lng"] + lng_offset
            
            # Check if this location is likely in water, if so adjust
            attempts = 0
            while is_likely_water(new_lat, new_lng) and attempts < 5:
                # Try a smaller offset in a different direction
                lat_offset = (random.random() - 0.5) * 0.04 * (0.8 ** attempts)
                lng_offset = (random.random() - 0.5) * 0.04 * (0.8 ** attempts)
                new_lat = city["lat"] + lat_offset
                new_lng = city["lng"] + lng_offset
                attempts += 1
            
            # Apply regional factors to metrics
            regional_ev_factor = city.get("ev_adoption_factor", 1.0)
            
            # Generate random metrics for viability calculation
            traffic_volume = random.randint(1000, 11000)
            ev_adoption_rate = random.uniform(0.05, 0.25) * regional_ev_factor
            competitor_distance = random.uniform(1, 16)
            land_size = random.uniform(500, 2500)
            power_availability = random.uniform(0.2, 1.0)
            
            # Calculate viability score (0-100)
            viability_score = (
                (traffic_volume / 11000) * 30 +  # 30% weight to traffic
                (ev_adoption_rate / (0.25 * 2.0)) * 25 +  # 25% weight to EV adoption, normalized for regional factors
                (min(competitor_distance, 10) / 10) * 15 +  # 15% weight to competitor distance
                (land_size / 2500) * 15 +  # 15% weight to land size
                (power_availability) * 15  # 15% weight to power availability
            )
            
            viability_score = min(round(viability_score), 100)
            
            # Calculate financial metrics
            conversion_cost = round((1000000 - 200000 * (power_availability)) * (1 - land_size/5000) + 500000)
            annual_revenue = round(traffic_volume * ev_adoption_rate * 5 * 365)
            annual_operating_cost = round(annual_revenue * (0.4 + random.uniform(0, 0.2)))
            annual_profit = annual_revenue - annual_operating_cost
            roi = round((annual_profit / conversion_cost) * 100 * 10) / 10
            payback_period = round(conversion_cost / annual_profit * 10) / 10 if annual_profit > 0 else float('inf')
            
            data.append({
                "id": f"station-{station_id}",
                "name": f"{random.choice(station_names)} {city['name']} {station_id}",
                "lat": new_lat,
                "lng": new_lng,
                "city": city["name"],
                "region": city["region"],
                "type": random.choice(station_types),
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
                "payback_period": payback_period
            })
            station_id += 1
    
    # Second pass: add remaining stations randomly to reach n_stations
    remaining_stations = max(0, n_stations - (min_stations_per_city * len(cities)))
    
    for i in range(remaining_stations):
        # Select a random city with weighting towards major/important cities
        city = random.choice(cities)
        
        # Create a smaller random offset to distribute stations around the city
        lat_offset = (random.random() - 0.5) * 0.08
        lng_offset = (random.random() - 0.5) * 0.08
        
        # Calculate new coordinates
        new_lat = city["lat"] + lat_offset
        new_lng = city["lng"] + lng_offset
        
        # Check if this location is likely in water, if so adjust
        attempts = 0
        while is_likely_water(new_lat, new_lng) and attempts < 5:
            # Try a smaller offset in a different direction
            lat_offset = (random.random() - 0.5) * 0.04 * (0.8 ** attempts)
            lng_offset = (random.random() - 0.5) * 0.04 * (0.8 ** attempts)
            new_lat = city["lat"] + lat_offset
            new_lng = city["lng"] + lng_offset
            attempts += 1
        
        # Apply regional factors to metrics
        regional_ev_factor = city.get("ev_adoption_factor", 1.0)
        
        # Generate random metrics for viability calculation
        traffic_volume = random.randint(1000, 11000)
        ev_adoption_rate = random.uniform(0.05, 0.25) * regional_ev_factor
        competitor_distance = random.uniform(1, 16)
        land_size = random.uniform(500, 2500)
        power_availability = random.uniform(0.2, 1.0)
        
        # Calculate viability score (0-100)
        viability_score = (
            (traffic_volume / 11000) * 30 +  # 30% weight to traffic
            (ev_adoption_rate / (0.25 * 2.0)) * 25 +  # 25% weight to EV adoption, normalized for regional factors
            (min(competitor_distance, 10) / 10) * 15 +  # 15% weight to competitor distance
            (land_size / 2500) * 15 +  # 15% weight to land size
            (power_availability) * 15  # 15% weight to power availability
        )
        
        viability_score = min(round(viability_score), 100)
        
        # Calculate financial metrics
        conversion_cost = round((1000000 - 200000 * (power_availability)) * (1 - land_size/5000) + 500000)
        annual_revenue = round(traffic_volume * ev_adoption_rate * 5 * 365)
        annual_operating_cost = round(annual_revenue * (0.4 + random.uniform(0, 0.2)))
        annual_profit = annual_revenue - annual_operating_cost
        roi = round((annual_profit / conversion_cost) * 100 * 10) / 10
        payback_period = round(conversion_cost / annual_profit * 10) / 10 if annual_profit > 0 else float('inf')
        
        data.append({
            "id": f"station-{station_id}",
            "name": f"{random.choice(station_names)} {city['name']} {station_id}",
            "lat": new_lat,
            "lng": new_lng,
            "city": city["name"],
            "region": city["region"],
            "type": random.choice(station_types),
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
            "payback_period": payback_period
        })
        station_id += 1
    
    return pd.DataFrame(data)

# Create a map with station markers
def create_map(df, output_file="output/station_map.html"):
    """Create a map with station markers colored by viability score."""
    
    # Create a map centered on the world
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    # Define a color function based on viability score
    def get_color(score):
        if score >= 80:
            return 'green'
        elif score >= 60:
            return 'orange'
        elif score >= 40:
            return 'blue'
        else:
            return 'red'
    
    # Create a legend for viability scores
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color: white; padding: 10px;
                border-radius: 5px;">
    <div style="font-weight: bold; margin-bottom: 10px;">Viability Score</div>
    <div><i class="fa fa-circle" style="color:green"></i> 80-100 - High Viability</div>
    <div><i class="fa fa-circle" style="color:orange"></i> 60-79 - Good Viability</div>
    <div><i class="fa fa-circle" style="color:blue"></i> 40-59 - Medium Viability</div>
    <div><i class="fa fa-circle" style="color:red"></i> <40 - Low Viability</div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Create regional marker clusters
    regions = df['region'].unique()
    region_clusters = {}
    
    for region in regions:
        region_clusters[region] = folium.FeatureGroup(name=f"{region}")
        m.add_child(region_clusters[region])
    
    # Add markers for each gas station
    for _, row in df.iterrows():
        popup_text = (
            f"<b>{row['name']}</b><br>"
            f"Region: {row['region']}<br>"
            f"Type: {row['type']}<br>"
            f"Viability Score: {row['viability_score']}/100<br>"
            f"ROI: {row['roi']}%<br>"
            f"Payback Period: {row['payback_period']} years<br>"
            f"EV Adoption Rate: {row['ev_adoption_rate']}%<br>"
            f"Traffic Volume: {row['traffic_volume']} vehicles/day"
        )
        
        marker = folium.Marker(
            location=[row['lat'], row['lng']],
            popup=popup_text,
            tooltip=f"{row['name']} (Score: {row['viability_score']})",
            icon=folium.Icon(color=get_color(row['viability_score']))
        )
        
        # Add the marker to the corresponding regional cluster
        region_clusters[row['region']].add_child(marker)
    
    # Add layer control to toggle regions
    folium.LayerControl().add_to(m)
    
    # Save the map
    m.save(output_file)
    return output_file

# Create traffic visualization using circle markers
def create_traffic_map(df, output_file="output/traffic_map.html"):
    """Create a traffic visualization map with circle markers."""
    
    # Create a map centered on the world
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    # Create regional feature groups
    regions = df['region'].unique()
    region_groups = {}
    
    for region in regions:
        region_groups[region] = folium.FeatureGroup(name=f"{region}")
        m.add_child(region_groups[region])
    
    # Add circle markers for each gas station, sized by traffic volume
    for _, row in df.iterrows():
        # Scale traffic volume to get circle radius (between 5 and 30)
        radius = 5 + (row['traffic_volume'] / 11000) * 25
        
        # Create color based on traffic volume
        traffic_pct = row['traffic_volume'] / 11000
        if traffic_pct > 0.8:
            color = 'red'
        elif traffic_pct > 0.5:
            color = 'orange'
        elif traffic_pct > 0.3:
            color = 'blue'
        else:
            color = 'green'
        
        popup_text = (
            f"<b>{row['name']}</b><br>"
            f"Region: {row['region']}<br>"
            f"City: {row['city']}<br>"
            f"Traffic Volume: {row['traffic_volume']} vehicles/day<br>"
            f"EV Adoption Rate: {row['ev_adoption_rate']}%"
        )
        
        circle = folium.CircleMarker(
            location=[row['lat'], row['lng']],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=popup_text,
            tooltip=f"{row['name']}: {row['traffic_volume']} vehicles/day"
        )
        
        # Add the circle to the corresponding regional group
        region_groups[row['region']].add_child(circle)
    
    # Create a legend for traffic volume
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 250px; height: 120px; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color: white; padding: 10px;
                border-radius: 5px;">
    <div style="font-weight: bold; margin-bottom: 10px;">Traffic Volume (vehicles/day)</div>
    <div><i class="fa fa-circle" style="color:red"></i> 8,000+ - Very High Traffic</div>
    <div><i class="fa fa-circle" style="color:orange"></i> 5,000-8,000 - High Traffic</div>
    <div><i class="fa fa-circle" style="color:blue"></i> 3,000-5,000 - Medium Traffic</div>
    <div><i class="fa fa-circle" style="color:green"></i> <3,000 - Low Traffic</div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control to toggle regions
    folium.LayerControl().add_to(m)
    
    # Save the map
    m.save(output_file)
    return output_file

# Create simple dashboard HTML
def create_dashboard_html(df, map_file, traffic_map_file, output_file="output/dashboard.html"):
    """Create a simple dashboard HTML file."""
    
    # Extract just the filenames without paths for iframe src
    map_filename = os.path.basename(map_file)
    traffic_map_filename = os.path.basename(traffic_map_file)
    
    # Calculate summary statistics
    avg_viability = df['viability_score'].mean()
    avg_roi = df['roi'].mean()
    avg_payback = df[df['payback_period'] < 100]['payback_period'].mean()
    high_viability_count = sum(df['viability_score'] >= 70)
    
    # Regional statistics
    regions = df['region'].unique()
    region_stats = {}
    
    for region in regions:
        region_df = df[df['region'] == region]
        region_stats[region] = {
            'count': len(region_df),
            'avg_viability': region_df['viability_score'].mean(),
            'avg_roi': region_df['roi'].mean(),
            'high_viability': sum(region_df['viability_score'] >= 70),
            'avg_ev_adoption': region_df['ev_adoption_rate'].mean()
        }
    
    # Sort regions by average viability score
    sorted_regions = sorted(region_stats.keys(), key=lambda x: region_stats[x]['avg_viability'], reverse=True)
    
    # Create region cards HTML
    region_cards_html = ""
    for region in sorted_regions:
        stats = region_stats[region]
        region_cards_html += f"""
        <div class="region-card" data-region="{region}">
            <div class="region-header">
                <div class="region-name">{region}</div>
                <div>{stats['count']} Stations</div>
            </div>
            <div class="region-metrics">
                <div class="region-metric">
                    <h4>Avg. Viability Score</h4>
                    <div class="region-metric-value">{stats['avg_viability']:.1f}</div>
                    <div class="progress-bar">
                        <div class="progress-value" style="width: {min(stats['avg_viability'], 100)}%;"></div>
                    </div>
                </div>
                <div class="region-metric">
                    <h4>Avg. ROI</h4>
                    <div class="region-metric-value">{stats['avg_roi']:.1f}%</div>
                </div>
                <div class="region-metric">
                    <h4>High Viability Stations</h4>
                    <div class="region-metric-value">{stats['high_viability']}</div>
                    <div>({(stats['high_viability'] / stats['count'] * 100):.1f}%)</div>
                </div>
                <div class="region-metric">
                    <h4>Avg. EV Adoption</h4>
                    <div class="region-metric-value">{stats['avg_ev_adoption']:.1f}%</div>
                </div>
            </div>
        </div>
        """
    
    # Create region filter buttons
    region_buttons_html = '<button class="filter-button active" data-region="all">All Regions</button>'
    for region in sorted_regions:
        region_buttons_html += f'<button class="filter-button" data-region="{region}">{region}</button>'
    
    # Create station table rows
    table_rows_html = ""
    for _, row in df.head(20).iterrows():
        table_rows_html += f'<tr data-region="{row["region"]}"><td>{row["name"]}</td><td>{row["region"]}</td><td>{row["city"]}</td><td>{row["type"]}</td><td>{row["viability_score"]}</td><td>{row["roi"]}</td><td>{row["payback_period"]}</td><td>{row["ev_adoption_rate"]}</td></tr>'
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HPC Station Conversion Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f0f7f4;
                color: #0a2e36;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                background-color: #00a67d;
                color: white;
                padding: 20px;
                border-radius: 10px;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .metric-card {{
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                padding: 20px;
                text-align: center;
            }}
            .metric-value {{
                font-size: 2.2rem;
                font-weight: bold;
                color: #00a67d;
                margin: 10px 0;
            }}
            .map-container {{
                height: 600px;
                margin-bottom: 25px;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            }}
            .tabs {{
                display: flex;
                border-bottom: 1px solid #ccc;
                margin-bottom: 20px;
            }}
            .tab {{
                padding: 10px 20px;
                cursor: pointer;
                border-bottom: 3px solid transparent;
            }}
            .tab.active {{
                border-bottom: 3px solid #00a67d;
                font-weight: bold;
            }}
            .tab-content {{
                display: none;
            }}
            .tab-content.active {{
                display: block;
            }}
            h2 {{
                color: #00a67d;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 10px;
                margin-top: 40px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .filters {{
                background-color: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }}
            .filter-group {{
                margin-bottom: 10px;
            }}
            .filter-label {{
                font-weight: bold;
                margin-right: 10px;
            }}
            .filter-buttons {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }}
            .filter-button {{
                padding: 5px 10px;
                background-color: #f0f0f0;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            .filter-button.active {{
                background-color: #00a67d;
                color: white;
            }}
            .region-card {{
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                padding: 20px;
                margin-bottom: 20px;
            }}
            .region-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }}
            .region-name {{
                font-size: 1.5rem;
                font-weight: bold;
                color: #00a67d;
            }}
            .region-metrics {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 15px;
            }}
            .region-metric {{
                text-align: center;
            }}
            .region-metric-value {{
                font-size: 1.8rem;
                font-weight: bold;
                margin: 5px 0;
            }}
            .progress-bar {{
                width: 100%;
                background-color: #e0e0e0;
                height: 8px;
                border-radius: 4px;
                margin-top: 5px;
            }}
            .progress-value {{
                height: 100%;
                border-radius: 4px;
                background-color: #00a67d;
            }}
            .chart-container {{
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                padding: 20px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>HPC Station Conversion Dashboard</h1>
            <p>Analysis of gas station viability for conversion to High-Power Charging stations</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Total Stations Analyzed</h3>
                <div class="metric-value">{len(df)}</div>
            </div>
            <div class="metric-card">
                <h3>Average Viability Score</h3>
                <div class="metric-value">{avg_viability:.1f}</div>
                <div class="metric-unit">out of 100</div>
            </div>
            <div class="metric-card">
                <h3>Average ROI</h3>
                <div class="metric-value">{avg_roi:.1f}%</div>
            </div>
            <div class="metric-card">
                <h3>High Viability Stations</h3>
                <div class="metric-value">{high_viability_count}</div>
                <div class="metric-unit">score >= 70</div>
            </div>
        </div>
        
        <h2>Interactive Maps</h2>
        <div class="tabs">
            <div class="tab active" onclick="showTab('station-map')">Station Viability Map</div>
            <div class="tab" onclick="showTab('traffic-map')">Traffic Volume Map</div>
        </div>
        
        <div id="station-map" class="tab-content active">
            <div class="map-container">
                <iframe src="{map_filename}" width="100%" height="100%" frameborder="0"></iframe>
            </div>
        </div>
        
        <div id="traffic-map" class="tab-content">
            <div class="map-container">
                <iframe src="{traffic_map_filename}" width="100%" height="100%" frameborder="0"></iframe>
            </div>
        </div>
        
        <h2>Regional Analysis</h2>
        <div class="filters">
            <div class="filter-group">
                <span class="filter-label">Region:</span>
                <div class="filter-buttons" id="region-filters">
                    {region_buttons_html}
                </div>
            </div>
        </div>
        
        <div id="region-stats-container">
            {region_cards_html}
        </div>
        
        <h2>Station Data</h2>
        <div class="filters">
            <div class="filter-group">
                <span class="filter-label">Filter by:</span>
                <div class="filter-buttons">
                    <button class="filter-button active" onclick="sortTable('viability')">Viability Score</button>
                    <button class="filter-button" onclick="sortTable('roi')">ROI</button>
                    <button class="filter-button" onclick="sortTable('ev')">EV Adoption</button>
                    <button class="filter-button" onclick="sortTable('traffic')">Traffic Volume</button>
                </div>
            </div>
        </div>
        
        <table id="station-table">
            <tr>
                <th>Station Name</th>
                <th>Region</th>
                <th>City</th>
                <th>Type</th>
                <th>Viability Score</th>
                <th>ROI (%)</th>
                <th>Payback (years)</th>
                <th>EV Adoption (%)</th>
            </tr>
            {table_rows_html}
        </table>
        <p>Showing top 20 stations</p>
        
        <script>
            // Tab switching
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
            
            // Region filtering
            var regionButtons = document.querySelectorAll('#region-filters .filter-button');
            for (var i = 0; i < regionButtons.length; i++) {{
                regionButtons[i].addEventListener('click', function() {{
                    // Remove active class from all buttons
                    for (var j = 0; j < regionButtons.length; j++) {{
                        regionButtons[j].classList.remove('active');
                    }}
                    
                    // Add active class to clicked button
                    this.classList.add('active');
                    
                    // Get selected region
                    var selectedRegion = this.getAttribute('data-region');
                    
                    // Filter region cards
                    var regionCards = document.querySelectorAll('.region-card');
                    for (var j = 0; j < regionCards.length; j++) {{
                        if (selectedRegion === 'all' || regionCards[j].getAttribute('data-region') === selectedRegion) {{
                            regionCards[j].style.display = 'block';
                        }} else {{
                            regionCards[j].style.display = 'none';
                        }}
                    }}
                    
                    // Filter table rows
                    var tableRows = document.querySelectorAll('#station-table tr[data-region]');
                    for (var j = 0; j < tableRows.length; j++) {{
                        if (selectedRegion === 'all' || tableRows[j].getAttribute('data-region') === selectedRegion) {{
                            tableRows[j].style.display = '';
                        }} else {{
                            tableRows[j].style.display = 'none';
                        }}
                    }}
                }});
            }}
            
            // Table sorting
            function sortTable(criteria) {{
                var table = document.getElementById('station-table');
                var rows = Array.from(table.querySelectorAll('tr[data-region]'));
                
                // Define sort index based on criteria
                var sortIndex;
                switch(criteria) {{
                    case 'viability':
                        sortIndex = 4;
                        break;
                    case 'roi':
                        sortIndex = 5;
                        break;
                    case 'ev':
                        sortIndex = 7;
                        break;
                    case 'traffic':
                        // Not directly shown, but could be added
                        sortIndex = 4; // Default to viability
                        break;
                    default:
                        sortIndex = 4;
                }}
                
                // Sort rows
                rows.sort(function(a, b) {{
                    var aValue = parseFloat(a.cells[sortIndex].innerText);
                    var bValue = parseFloat(b.cells[sortIndex].innerText);
                    return bValue - aValue; // Descending order
                }});
                
                // Reorder rows in the table
                for (var i = 0; i < rows.length; i++) {{
                    table.appendChild(rows[i]);
                }}
                
                // Update button styles
                var buttons = document.querySelectorAll('.filter-buttons .filter-button');
                for (var i = 0; i < buttons.length; i++) {{
                    buttons[i].classList.remove('active');
                    if (buttons[i].getAttribute('onclick').includes(criteria)) {{
                        buttons[i].classList.add('active');
                    }}
                }}
            }}
        </script>
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(output_file, "w") as f:
        f.write(html_content)
    
    return output_file

# Main function
def main():
    """Main function to generate the dashboard."""
    
    print("\n===== Generating Gas Station Data =====")
    df = generate_gas_stations(n_stations=150)
    print(f"Generated {len(df)} gas stations for analysis")
    
    print("\n===== Creating Maps =====")
    map_file = create_map(df)
    print(f"Created station map: {map_file}")
    
    traffic_map_file = create_traffic_map(df)
    print(f"Created traffic map: {traffic_map_file}")
    
    print("\n===== Creating Dashboard =====")
    dashboard_file = create_dashboard_html(df, map_file, traffic_map_file)
    print(f"Created dashboard: {dashboard_file}")
    
    # Try to open the dashboard in a web browser
    try:
        print("\n===== Opening Dashboard in Browser =====")
        webbrowser.open('file://' + os.path.abspath(dashboard_file))
        print("Dashboard opened in browser")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print(f"Please open {dashboard_file} manually in your browser")
    
    return dashboard_file

if __name__ == "__main__":
    main() 