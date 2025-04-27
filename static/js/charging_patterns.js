// EV Charging Patterns - JavaScript
// 
// This file contains client-side code for interactive visualizations on the
// charging patterns dashboard view.

const ChargingPatterns = {
    // Cache for data
    data: null,
    
    // Initialize the dashboard component
    init: function() {
        console.log("Initializing EV Charging Patterns component...");
        
        // Fetch data for interactive charts
        this.fetchData();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Subscribe to data update events
        if (typeof EventBus !== 'undefined') {
            EventBus.subscribe('ev_charging_data_updated', this.onDataUpdated.bind(this));
        }
    },
    
    // Fetch data from the API
    fetchData: function() {
        fetch('/api/v1/charging-patterns/summary')
            .then(response => response.json())
            .then(data => {
                this.data = data;
                this.renderCharts();
            })
            .catch(error => {
                console.error('Error fetching charging pattern data:', error);
                // Display fallback or error message
                if (document.getElementById('top-stations-chart')) {
                    document.getElementById('top-stations-chart').innerHTML = 
                        '<div class="alert alert-danger">Error loading chart data. Please try again later.</div>';
                }
                if (document.getElementById('utilization-chart')) {
                    document.getElementById('utilization-chart').innerHTML = 
                        '<div class="alert alert-danger">Error loading chart data. Please try again later.</div>';
                }
            });
    },
    
    // Render interactive charts using Plotly
    renderCharts: function() {
        if (!this.data) return;
        
        // Check if the necessary elements and Plotly library exist
        if (!window.Plotly) {
            console.warn('Plotly library not loaded. Skipping interactive charts.');
            return;
        }
        
        // Render top stations chart
        const topStationsElement = document.getElementById('top-stations-chart');
        if (topStationsElement && this.data.station_utilization && this.data.station_utilization.top_stations) {
            const stationData = this.data.station_utilization.top_stations.by_usage;
            const trace = {
                x: stationData.station_ids,
                y: stationData.session_counts,
                type: 'bar',
                marker: {
                    color: 'rgba(50, 171, 96, 0.7)',
                    line: {
                        color: 'rgba(50, 171, 96, 1.0)',
                        width: 2
                    }
                }
            };
            
            const layout = {
                title: 'Top Stations by Usage',
                xaxis: {
                    title: 'Station ID',
                    tickangle: -45
                },
                yaxis: {
                    title: 'Number of Sessions'
                },
                margin: {
                    l: 50,
                    r: 50,
                    b: 100,
                    t: 50,
                    pad: 4
                }
            };
            
            Plotly.newPlot('top-stations-chart', [trace], layout);
        }
        
        // Render utilization chart
        const utilizationElement = document.getElementById('utilization-chart');
        if (utilizationElement && this.data.station_utilization && this.data.station_utilization.utilization_rate) {
            const utilizationData = this.data.station_utilization.utilization_rate;
            
            // Limit to top 10 stations for clarity
            const stationIds = utilizationData.station_ids.slice(0, 10);
            const utilizationRates = utilizationData.utilization_percentage.slice(0, 10);
            
            const trace = {
                x: stationIds,
                y: utilizationRates,
                type: 'bar',
                marker: {
                    color: 'rgba(55, 128, 191, 0.7)',
                    line: {
                        color: 'rgba(55, 128, 191, 1.0)',
                        width: 2
                    }
                }
            };
            
            const layout = {
                title: 'Station Utilization Rates (Top 10)',
                xaxis: {
                    title: 'Station ID',
                    tickangle: -45
                },
                yaxis: {
                    title: 'Utilization Rate (%)',
                    range: [0, 100]
                },
                margin: {
                    l: 50,
                    r: 50,
                    b: 100,
                    t: 50,
                    pad: 4
                }
            };
            
            Plotly.newPlot('utilization-chart', [trace], layout);
        }
        
        // Render energy consumption by hour chart
        const hourlyEnergyElement = document.getElementById('hourly-energy-chart');
        if (hourlyEnergyElement && this.data.energy_delivery && this.data.energy_delivery.time_based_energy) {
            const hourlyEnergy = this.data.energy_delivery.time_based_energy.hourly_energy_kwh;
            const hours = Array.from({length: 24}, (_, i) => i);
            const energy = hours.map(hour => hourlyEnergy[hour] || 0);
            
            const trace = {
                x: hours,
                y: energy,
                type: 'scatter',
                mode: 'lines+markers',
                line: {
                    color: 'rgba(34, 139, 34, 1.0)',
                    width: 3
                },
                marker: {
                    color: 'rgba(34, 139, 34, 0.8)',
                    size: 8
                },
                fill: 'tozeroy',
                fillcolor: 'rgba(34, 139, 34, 0.2)'
            };
            
            const layout = {
                title: 'Energy Consumption by Hour of Day',
                xaxis: {
                    title: 'Hour of Day',
                    dtick: 2
                },
                yaxis: {
                    title: 'Energy Consumed (kWh)'
                },
                margin: {
                    l: 50,
                    r: 20,
                    b: 50,
                    t: 50,
                    pad: 4
                }
            };
            
            Plotly.newPlot('hourly-energy-chart', [trace], layout);
        }
    },
    
    // Set up event listeners for interactive elements
    setupEventListeners: function() {
        // Example: Add dropdown change handler if we add filter dropdowns later
        const filterDropdown = document.getElementById('station-filter');
        if (filterDropdown) {
            filterDropdown.addEventListener('change', function(event) {
                const stationId = event.target.value;
                // Filter data by station ID
                // Then update charts
            });
        }
        
        // Example: Add time period selector if needed
        const timePeriodButtons = document.querySelectorAll('.time-period-button');
        if (timePeriodButtons.length > 0) {
            timePeriodButtons.forEach(button => {
                button.addEventListener('click', function(event) {
                    const period = event.target.dataset.period;
                    // Update visualizations based on selected time period
                });
            });
        }
    },
    
    // Handle data updates from the event bus
    onDataUpdated: function(newData) {
        console.log("Received updated charging pattern data");
        this.data = newData;
        this.renderCharts();
    }
};

// Initialize the component when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    ChargingPatterns.init();
}); 