// Conversion Advisor JavaScript
// Handles interaction with the conversion advisor API and provides fallback functionality

const FALLBACK_RECOMMENDATION = `
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
`;

// Cache for storing recommendations by station ID
const recommendationCache = {};

// Initialize the map when the page loads
let stationMap = null;
let stationMarkers = {};
let selectedStation = null;
let allStations = []; // Store all stations for reference

document.addEventListener('DOMContentLoaded', () => {
    // Initialize map if container exists
    const mapContainer = document.getElementById('station-map');
    if (mapContainer) {
        // Wait for page to fully load before initializing map
        window.addEventListener('load', () => {
            // Small additional delay to ensure all resources are loaded
            setTimeout(() => {
                try {
                    initializeMap();
                } catch (error) {
                    console.error('Error initializing map:', error);
                    document.getElementById('map-error').textContent = 'Error initializing map. Please refresh the page.';
                    document.getElementById('map-error').style.display = 'block';
                    document.querySelector('.map-loading').style.display = 'none';
                }
            }, 300);
        });
    }
    
    // Set up form submission handler if form exists
    const form = document.getElementById('conversionForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
    
    // Set up station selection handler if select exists
    const stationSelect = document.getElementById('station-select');
    if (stationSelect) {
        stationSelect.addEventListener('change', handleStationSelection);
    }
    
    // Explicitly set up the recommendation button
    const recommendButton = document.getElementById('generate-recommendation');
    if (recommendButton) {
        recommendButton.addEventListener('click', function() {
            generateRecommendation();
        });
    }
});

// Initialize the map with station markers
function initializeMap() {
    console.log("Initializing map");
    
    try {
        // Hide the loading indicator when map is initialized
        const mapLoading = document.querySelector('.map-loading');
        
        // Create a map centered on the San Francisco Bay Area (where our sample data is)
        stationMap = L.map('station-map', {
            center: [37.7749, -122.4194],
            zoom: 9,
            minZoom: 3,
            maxZoom: 18
        });
        
        // Add multiple tile layer options for redundancy
        const openStreetMapLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        });
        
        const cartoDBLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd'
        });
        
        // Try to add OpenStreetMap first
        openStreetMapLayer.addTo(stationMap)
            .on('tileerror', function() {
                console.warn('OpenStreetMap tiles failed to load, switching to CartoDB');
                openStreetMapLayer.remove();
                cartoDBLayer.addTo(stationMap);
            });
            
        // Add a fallback handler if both tile layers fail
        cartoDBLayer.on('tileerror', function() {
            console.error('Both tile layers failed to load');
            document.getElementById('map-error').textContent = 'Map tiles failed to load. Please check your internet connection.';
            document.getElementById('map-error').style.display = 'block';
        });
        
        // Listen for map load event
        stationMap.on('load', function() {
            console.log("Map loaded successfully");
            if (mapLoading) mapLoading.style.display = 'none';
        });
        
        // Set a timeout to ensure map loading indicator is hidden
        setTimeout(() => {
            if (mapLoading) mapLoading.style.display = 'none';
        }, 3000);
        
        console.log("Fetching gas stations data");
        
        // Fetch gas stations data
        fetch('/api/gas_stations')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error fetching gas stations');
                }
                return response.json();
            })
            .then(stations => {
                console.log(`Loaded ${stations.length} stations`);
                allStations = stations; // Store all stations
                addStationsToMap(stations);
                
                // Select the first station by default
                if (stations.length > 0) {
                    console.log(`Selecting first station: ${stations[0].station_id}`);
                    selectStation(stations[0]);
                    
                    // Update dropdown to show first station
                    const stationSelect = document.getElementById('station-select');
                    if (stationSelect && stationSelect.options.length > 0) {
                        stationSelect.selectedIndex = 0;
                    }
                }
            })
            .catch(error => {
                console.error('Error loading stations:', error);
                document.getElementById('map-error').textContent = 'Error loading stations. Please refresh the page.';
                document.getElementById('map-error').style.display = 'block';
                if (mapLoading) mapLoading.style.display = 'none';
            });
    } catch (error) {
        console.error('Error in map initialization:', error);
        document.getElementById('map-error').textContent = 'Error initializing map. Please refresh the page.';
        document.getElementById('map-error').style.display = 'block';
        const mapLoading = document.querySelector('.map-loading');
        if (mapLoading) mapLoading.style.display = 'none';
    }
}

// Add station markers to the map
function addStationsToMap(stations) {
    console.log(`Adding ${stations.length} stations to map`);
    
    // Define marker icons for different viability scores
    const greenIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
    
    const orangeIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
    
    const redIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
    
    const blueIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });
    
    stations.forEach(station => {
        // Only add markers for stations with coordinates
        if (station.latitude && station.longitude) {
            // Determine marker color based on viability score
            let markerIcon = blueIcon;
            if (station.viability_score >= 70) {
                markerIcon = greenIcon;
            } else if (station.viability_score >= 50) {
                markerIcon = orangeIcon;
            } else {
                markerIcon = redIcon;
            }
            
            // Create popup content
            const popupContent = `
                <div class="station-popup">
                    <h3>${station.name}</h3>
                    <p><strong>ID:</strong> ${station.station_id}</p>
                    <p><strong>Viability Score:</strong> ${station.viability_score || 'N/A'}</p>
                    <p><strong>Estimated ROI:</strong> ${station.estimated_roi ? station.estimated_roi + '%' : 'N/A'}</p>
                    <p><strong>Daily Customers:</strong> ${station.daily_customers || 'N/A'}</p>
                    <p><strong>Recommendation:</strong> ${station.recommendation || 'N/A'}</p>
                    <button onclick="selectAndShowStation('${station.station_id}')" class="popup-button">Select Station</button>
                </div>
            `;
            
            // Create marker
            const marker = L.marker([station.latitude, station.longitude], {
                icon: markerIcon
            })
            .bindPopup(popupContent)
            .addTo(stationMap)
            .on('click', () => {
                selectStation(station);
                
                // Update dropdown to match selected station
                const stationSelect = document.getElementById('station-select');
                if (stationSelect) {
                    stationSelect.value = station.station_id;
                }
            });
            
            stationMarkers[station.station_id] = marker;
        }
    });
    
    // Add custom CSS for popups
    const style = document.createElement('style');
    style.innerHTML = `
        .station-popup { min-width: 200px; }
        .station-popup h3 { margin-top: 0; color: #00a67d; }
        .popup-button {
            background-color: #00a67d;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            margin-top: 10px;
            cursor: pointer;
        }
        .popup-button:hover {
            background-color: #008f6c;
        }
    `;
    document.head.appendChild(style);
    
    console.log("Map markers added");
}

// Global function to select and show station from popup button
window.selectAndShowStation = function(stationId) {
    const station = allStations.find(s => s.station_id === stationId);
    if (station) {
        selectStation(station);
        
        // Update dropdown to match selected station
        const stationSelect = document.getElementById('station-select');
        if (stationSelect) {
            stationSelect.value = stationId;
        }
        
        // Close the popup
        stationMarkers[stationId].closePopup();
    }
};

// Handle station selection on map
function selectStation(station) {
    console.log(`Selecting station: ${station.station_id}`);
    
    // Update selected station
    selectedStation = station;
    
    // Update UI to show selected station
    const stationDetails = document.getElementById('station-details');
    if (stationDetails) {
        let featuresHtml = '';
        if (station.features) {
            featuresHtml = '<h4>Key Factors:</h4><ul>';
            for (const [key, value] of Object.entries(station.features)) {
                const readableKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                featuresHtml += `<li><strong>${readableKey}:</strong> ${value}</li>`;
            }
            featuresHtml += '</ul>';
        }
        
        stationDetails.innerHTML = `
            <h3>${station.name} (${station.station_id})</h3>
            <p><strong>Location:</strong> ${station.latitude.toFixed(4)}, ${station.longitude.toFixed(4)}</p>
            <p><strong>Viability Score:</strong> ${station.viability_score || 'N/A'}</p>
            <p><strong>Estimated ROI:</strong> ${station.estimated_roi ? station.estimated_roi + '%' : 'N/A'}</p>
            <p><strong>Daily Customers:</strong> ${station.daily_customers || 'N/A'}</p>
            <p><strong>Monthly Revenue:</strong> $${station.monthly_revenue?.toFixed(2) || 'N/A'}</p>
            <p><strong>Recommendation:</strong> ${station.recommendation || 'N/A'}</p>
            ${featuresHtml}
        `;
        stationDetails.style.display = 'block';
    }
    
    // Highlight the selected marker
    for (const [id, marker] of Object.entries(stationMarkers)) {
        // Reset all markers to their original icons
        const s = allStations.find(s => s.station_id === id);
        if (s) {
            let iconUrl = 'blue';
            if (s.viability_score >= 70) {
                iconUrl = 'green';
            } else if (s.viability_score >= 50) {
                iconUrl = 'orange';
            } else {
                iconUrl = 'red';
            }
            
            // Use standard icon for non-selected markers
            if (id !== station.station_id) {
                marker.setIcon(new L.Icon({
                    iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${iconUrl}.png`,
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                }));
            } else {
                // Use a larger icon for the selected marker
                marker.setIcon(new L.Icon({
                    iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${iconUrl}.png`,
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [35, 57], // Larger size
                    iconAnchor: [17, 57],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                }));
            }
        }
    }
    
    // Center map on selected station
    if (stationMap) {
        stationMap.setView([station.latitude, station.longitude], 12);
    }
    
    // Open the popup for this station
    if (stationMarkers[station.station_id]) {
        stationMarkers[station.station_id].openPopup();
    }
    
    // Enable chat if it was disabled
    document.getElementById('chat-input').disabled = false;
    document.getElementById('chat-button').disabled = false;
    
    // Add AI message in chat about the selected station
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.innerHTML = `
            <div class="message message-ai">
                Hello! I can help you understand ${station.name}'s potential for EV charging conversion. This station has a viability score of ${station.viability_score || 'N/A'} and is located in the San Francisco Bay Area. What would you like to know about converting this station?
            </div>
        `;
    }
    
    // Store station data as current recommendation context
    currentRecommendation = `
Station: ${station.name} (${station.station_id})
Location: ${station.latitude.toFixed(4)}, ${station.longitude.toFixed(4)}
Viability Score: ${station.viability_score || 'N/A'}
Estimated ROI: ${station.estimated_roi ? station.estimated_roi + '%' : 'N/A'}
Daily Customers: ${station.daily_customers || 'N/A'}
Monthly Revenue: $${station.monthly_revenue?.toFixed(2) || 'N/A'}
Recommendation: ${station.recommendation || 'N/A'}
    `;
    
    if (station.features) {
        currentRecommendation += '\nKey Factors:\n';
        for (const [key, value] of Object.entries(station.features)) {
            const readableKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            currentRecommendation += `- ${readableKey}: ${value}\n`;
        }
    }
    
    // Update forecast charts with station data
    if (window.updateForecastCharts) {
        window.updateForecastCharts(station);
        
        // Update forecast statistics based on station data
        updateForecastStatistics(station);
    }
}

// Function to update forecast statistics based on station data
function updateForecastStatistics(station) {
    if (!station) return;
    
    // Calculate forecast values based on station properties
    const viabilityFactor = station.viability_score / 100 || 0.5;
    const dailyCustomersFactor = Math.min(station.daily_customers / 500, 2) || 1;
    
    // Update demand stats
    const currentDemand = Math.round(5 * dailyCustomersFactor);
    const futureDemand = Math.round(40 * viabilityFactor * dailyCustomersFactor);
    const demandGrowth = Math.round(52 * viabilityFactor);
    
    document.getElementById('current-demand').textContent = currentDemand;
    document.getElementById('future-demand').textContent = futureDemand;
    document.getElementById('demand-growth').textContent = demandGrowth + '%';
    
    // Update ROI stats
    const initialRoi = (8.2 * viabilityFactor).toFixed(1);
    const futureRoi = (22.6 * viabilityFactor).toFixed(1);
    const paybackPeriod = (3.5 / viabilityFactor).toFixed(1);
    
    document.getElementById('initial-roi').textContent = initialRoi + '%';
    document.getElementById('future-roi').textContent = futureRoi + '%';
    document.getElementById('payback-period').textContent = paybackPeriod;
    
    // Update adoption stats
    const currentAdoption = (7.8 * viabilityFactor).toFixed(1);
    const futureAdoption = (32.5 * viabilityFactor).toFixed(1);
    const adoptionCagr = (33.1 * viabilityFactor).toFixed(1);
    
    document.getElementById('current-adoption').textContent = currentAdoption + '%';
    document.getElementById('future-adoption').textContent = futureAdoption + '%';
    document.getElementById('adoption-cagr').textContent = adoptionCagr + '%';
}

// Generate recommendation for the selected station
function generateRecommendation() {
    const stationId = document.getElementById('station-select').value;
    if (!stationId) {
        alert('Please select a station first');
        return;
    }
    
    const resultsDiv = document.getElementById('recommendation-results');
    const loader = document.getElementById('recommendation-loader');
    const frame = document.getElementById('recommendation-frame');
    const textOutput = document.getElementById('recommendation-text');
    
    // Show loading state
    resultsDiv.style.display = 'block';
    if (loader) loader.style.display = 'block';
    if (frame) frame.style.display = 'none';
    if (textOutput) textOutput.style.display = 'none';
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
    
    // Check if we have a cached result
    if (recommendationCache[stationId]) {
        displayRecommendation(recommendationCache[stationId], loader, frame, textOutput);
        return;
    }
    
    // Set timeout for request
    const timeoutId = setTimeout(() => {
        if (loader) loader.innerHTML = 'Request is taking longer than expected. Using cached data...';
        // After timeout, use fallback
        const fallbackResult = {
            recommendation: FALLBACK_RECOMMENDATION,
            source: 'fallback'
        };
        recommendationCache[stationId] = fallbackResult;
        displayRecommendation(fallbackResult, loader, frame, textOutput);
    }, 10000); // 10 second timeout
    
    // Make API request
    fetch(`/generate_recommendation?station_id=${stationId}`)
        .then(response => {
            clearTimeout(timeoutId);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Cache successful response
            const result = {
                dashboard_url: data.dashboard_url,
                recommendation: data.recommendation || FALLBACK_RECOMMENDATION,
                source: 'api'
            };
            recommendationCache[stationId] = result;
            displayRecommendation(result, loader, frame, textOutput);
            
            // Update current recommendation for chat context
            currentRecommendation = data.recommendation || FALLBACK_RECOMMENDATION;
            
            // Enable chat
            document.getElementById('chat-input').disabled = false;
            document.getElementById('chat-button').disabled = false;
            
            // Add AI message in chat
            addChatMessage("I've analyzed this station's data and generated a detailed recommendation. You can now ask me specific questions about this recommendation or the station's conversion potential.", false);
        })
        .catch(error => {
            clearTimeout(timeoutId);
            console.error('Error:', error);
            
            // Use fallback on error
            const fallbackResult = {
                recommendation: FALLBACK_RECOMMENDATION,
                source: 'fallback-error'
            };
            recommendationCache[stationId] = fallbackResult;
            displayRecommendation(fallbackResult, loader, frame, textOutput);
            
            // Still update current recommendation for chat context
            currentRecommendation = FALLBACK_RECOMMENDATION;
            
            // Enable chat
            document.getElementById('chat-input').disabled = false;
            document.getElementById('chat-button').disabled = false;
        });
}

// Display recommendation result
function displayRecommendation(result, loader, frame, textOutput) {
    if (loader) loader.style.display = 'none';
    
    // If we have an iframe and URL, use it
    if (frame && result.dashboard_url) {
        frame.style.display = 'block';
        frame.src = result.dashboard_url;
    } 
    // Otherwise use text output
    else if (textOutput) {
        textOutput.style.display = 'block';
        textOutput.innerHTML = formatMarkdown(result.recommendation);
        
        // If this is a fallback, show a note
        if (result.source.includes('fallback')) {
            const fallbackNote = document.createElement('div');
            fallbackNote.className = 'fallback-note';
            fallbackNote.textContent = 'Note: This is an AI-generated recommendation based on the station profile. Real-time data analysis was not available.';
            textOutput.prepend(fallbackNote);
        }
    }
}

// Format markdown text to HTML
function formatMarkdown(markdown) {
    if (!markdown) return '';
    
    // Simple markdown formatting (headers, lists, bold)
    return markdown
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/^\* (.*$)/gm, '<li>$1</li>')
        .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
        .replace(/<\/li>\n<li>/g, '</li><li>')
        .replace(/^\n<li>/gm, '<ul><li>')
        .replace(/<\/li>\n\n/gm, '</li></ul>\n\n')
        .replace(/\n\n/g, '<br><br>');
}

// Handle form submission for manual station details
function handleFormSubmit(e) {
    e.preventDefault();
    
    // Show loading indicator
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultCard = document.getElementById('resultCard');
    
    if (loadingIndicator) loadingIndicator.style.display = 'block';
    if (resultCard) resultCard.style.display = 'none';
    
    // Get form data
    const formData = new FormData(e.target);
    const formDataObj = {};
    
    formData.forEach((value, key) => {
        formDataObj[key] = value;
    });
    
    // Timeout for fallback
    const timeoutId = setTimeout(() => {
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (resultCard) {
            resultCard.style.display = 'block';
            const output = document.getElementById('recommendationOutput');
            if (output) {
                output.innerHTML = `<div class="fallback-note">Using AI-generated recommendation as real-time analysis is unavailable.</div>` + 
                                   formatMarkdown(FALLBACK_RECOMMENDATION);
            }
        }
    }, 8000); // 8 second timeout
    
    // Send data to API
    fetch('/api/generate_recommendation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formDataObj)
    })
    .then(response => {
        clearTimeout(timeoutId);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Hide loading indicator
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        
        // Show result and populate with recommendation
        if (resultCard) {
            resultCard.style.display = 'block';
            const output = document.getElementById('recommendationOutput');
            if (output) {
                output.innerHTML = formatMarkdown(data.recommendation || FALLBACK_RECOMMENDATION);
            }
            
            // Scroll to result
            resultCard.scrollIntoView({ behavior: 'smooth' });
        }
    })
    .catch(error => {
        clearTimeout(timeoutId);
        console.error('Error:', error);
        
        // Show fallback on error
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (resultCard) {
            resultCard.style.display = 'block';
            const output = document.getElementById('recommendationOutput');
            if (output) {
                output.innerHTML = `<div class="fallback-note">Error connecting to analysis service. Using AI-generated recommendation instead.</div>` + 
                                   formatMarkdown(FALLBACK_RECOMMENDATION);
            }
            
            // Scroll to result
            resultCard.scrollIntoView({ behavior: 'smooth' });
        }
    });
}

// Handle station selection dropdown change
function handleStationSelection(e) {
    const stationId = e.target.value;
    
    // Find station data in our local cache first
    let station = allStations.find(s => s.station_id === stationId);
    
    if (station) {
        selectStation(station);
    } else {
        // If not in cache, fetch from API
        fetch(`/api/gas_stations/${stationId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error fetching station details');
                }
                return response.json();
            })
            .then(station => {
                selectStation(station);
            })
            .catch(error => {
                console.error('Error fetching station details:', error);
            });
    }
} 