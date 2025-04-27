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

document.addEventListener('DOMContentLoaded', () => {
    // Initialize map if container exists
    const mapContainer = document.getElementById('station-map');
    if (mapContainer) {
        initializeMap();
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
        
        // Trigger recommendation generation if recommend button exists
        const recommendButton = document.getElementById('generate-recommendation');
        if (recommendButton) {
            recommendButton.addEventListener('click', generateRecommendation);
        }
    }
});

// Initialize the map with station markers
function initializeMap() {
    // Create a map centered on the US
    stationMap = L.map('station-map').setView([39.8283, -98.5795], 4);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(stationMap);
    
    // Fetch gas stations data
    fetch('/api/gas_stations')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error fetching gas stations');
            }
            return response.json();
        })
        .then(stations => {
            addStationsToMap(stations);
        })
        .catch(error => {
            console.error('Error loading stations:', error);
            document.getElementById('map-error').textContent = 'Error loading stations. Please try again later.';
        });
}

// Add station markers to the map
function addStationsToMap(stations) {
    stations.forEach(station => {
        // Only add markers for stations with coordinates
        if (station.latitude && station.longitude) {
            const marker = L.marker([station.latitude, station.longitude])
                .addTo(stationMap)
                .bindTooltip(station.station_id)
                .on('click', () => selectStation(station));
            
            stationMarkers[station.station_id] = marker;
        }
    });
}

// Handle station selection on map
function selectStation(station) {
    // Update selected station
    selectedStation = station;
    
    // Update UI to show selected station
    const stationSelect = document.getElementById('station-select');
    if (stationSelect) {
        stationSelect.value = station.station_id;
    }
    
    // Show station details
    const stationDetails = document.getElementById('station-details');
    if (stationDetails) {
        stationDetails.innerHTML = `
            <h3>${station.station_id}</h3>
            <p><strong>Location:</strong> ${station.latitude.toFixed(4)}, ${station.longitude.toFixed(4)}</p>
            <p><strong>Daily Customers:</strong> ${station.daily_customers}</p>
            <p><strong>Monthly Revenue:</strong> $${station.monthly_revenue.toFixed(2)}</p>
        `;
        stationDetails.style.display = 'block';
    }
    
    // Update marker styles to highlight selected station
    Object.values(stationMarkers).forEach(m => {
        m.setIcon(L.icon({
            iconUrl: '/static/images/marker-icon.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34]
        }));
    });
    
    if (stationMarkers[station.station_id]) {
        stationMarkers[station.station_id].setIcon(L.icon({
            iconUrl: '/static/images/marker-icon-selected.png',
            iconSize: [30, 46],
            iconAnchor: [15, 46],
            popupAnchor: [1, -34]
        }));
    }
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
    
    // Find station data and update the map selection
    fetch(`/api/gas_stations/${stationId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error fetching station details');
            }
            return response.json();
        })
        .then(station => {
            selectStation(station);
            
            // Center map on selected station
            if (stationMap && station.latitude && station.longitude) {
                stationMap.setView([station.latitude, station.longitude], 10);
            }
        })
        .catch(error => {
            console.error('Error fetching station details:', error);
        });
} 