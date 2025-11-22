// Global State
const appState = {
    selectedRegion: null,
    selectedLayers: ['layer-truecolor'],
    startDate: null,
    endDate: null,
    conversationHistory: []
};

// Initialize Map
let map;
let drawnItems;
let drawControl;

function initMap() {
    // Create map centered on a default location
    map = L.map('map').setView([46.5197, 6.6323], 8); // Centered on Switzerland

    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Initialize FeatureGroup to store drawn items
    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // Initialize draw control
    drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems,
            edit: true,
            remove: true
        },
        draw: {
            polygon: false,
            polyline: false,
            circle: false,
            circlemarker: false,
            marker: false,
            rectangle: {
                shapeOptions: {
                    color: '#ff6b35',
                    weight: 3,
                    fillOpacity: 0.2
                }
            }
        }
    });
    map.addControl(drawControl);

    // Handle draw events
    map.on(L.Draw.Event.CREATED, function (event) {
        const layer = event.layer;
        
        // Remove previous drawings
        drawnItems.clearLayers();
        
        // Add new drawing
        drawnItems.addLayer(layer);
        
        // Get bounds
        const bounds = layer.getBounds();
        const north = bounds.getNorth().toFixed(4);
        const south = bounds.getSouth().toFixed(4);
        const east = bounds.getEast().toFixed(4);
        const west = bounds.getWest().toFixed(4);
        
        // Update state
        appState.selectedRegion = {
            north: parseFloat(north),
            south: parseFloat(south),
            east: parseFloat(east),
            west: parseFloat(west),
            bounds: bounds
        };
        
        // Update UI
        updateRegionInfo();
        updateFetchButton();
    });

    map.on(L.Draw.Event.DELETED, function () {
        appState.selectedRegion = null;
        updateRegionInfo();
        updateFetchButton();
    });

    map.on(L.Draw.Event.EDITED, function (event) {
        const layers = event.layers;
        layers.eachLayer(function (layer) {
            const bounds = layer.getBounds();
            const north = bounds.getNorth().toFixed(4);
            const south = bounds.getSouth().toFixed(4);
            const east = bounds.getEast().toFixed(4);
            const west = bounds.getWest().toFixed(4);
            
            appState.selectedRegion = {
                north: parseFloat(north),
                south: parseFloat(south),
                east: parseFloat(east),
                west: parseFloat(west),
                bounds: bounds
            };
            
            updateRegionInfo();
            updateFetchButton();
        });
    });
}

// Update Region Info Display
function updateRegionInfo() {
    const regionInfoDiv = document.getElementById('region-info');
    
    if (appState.selectedRegion) {
        const { north, south, east, west } = appState.selectedRegion;
        const area = calculateArea(north, south, east, west);
        
        regionInfoDiv.innerHTML = `
            <div class="region-details">
                <p><strong>Coordinates:</strong></p>
                <p>North: ${north}°</p>
                <p>South: ${south}°</p>
                <p>East: ${east}°</p>
                <p>West: ${west}°</p>
                <p><strong>Approx. Area:</strong> ${area} km²</p>
            </div>
        `;
    } else {
        regionInfoDiv.innerHTML = '<p class="no-selection">No region selected yet</p>';
    }
}

// Calculate approximate area in km²
function calculateArea(north, south, east, west) {
    const R = 6371; // Earth's radius in km
    const latDiff = (north - south) * Math.PI / 180;
    const lonDiff = (east - west) * Math.PI / 180;
    const avgLat = ((north + south) / 2) * Math.PI / 180;
    
    const height = latDiff * R;
    const width = lonDiff * R * Math.cos(avgLat);
    const area = Math.abs(height * width);
    
    return area.toFixed(2);
}

// Initialize Date Inputs
function initDateInputs() {
    const today = new Date();
    const endDateInput = document.getElementById('end-date');
    const startDateInput = document.getElementById('start-date');
    
    // Set end date to today
    endDateInput.value = today.toISOString().split('T')[0];
    appState.endDate = endDateInput.value;
    
    // Set start date to 30 days ago
    const thirtyDaysAgo = new Date(today);
    thirtyDaysAgo.setDate(today.getDate() - 30);
    startDateInput.value = thirtyDaysAgo.toISOString().split('T')[0];
    appState.startDate = startDateInput.value;
    
    // Add event listeners
    startDateInput.addEventListener('change', (e) => {
        appState.startDate = e.target.value;
        updateFetchButton();
    });
    
    endDateInput.addEventListener('change', (e) => {
        appState.endDate = e.target.value;
        updateFetchButton();
    });
}

// Initialize Layer Toggles
function initLayerToggles() {
    const toggles = document.querySelectorAll('.toggle-item input[type="checkbox"]');
    
    toggles.forEach(toggle => {
        toggle.addEventListener('change', (e) => {
            const layerId = e.target.id;
            
            if (e.target.checked) {
                if (!appState.selectedLayers.includes(layerId)) {
                    appState.selectedLayers.push(layerId);
                }
            } else {
                appState.selectedLayers = appState.selectedLayers.filter(id => id !== layerId);
            }
            
            updateFetchButton();
        });
    });
}

// Update Fetch Button State
function updateFetchButton() {
    const fetchBtn = document.getElementById('fetch-data-btn');
    const submitBtn = document.getElementById('submit-prompt-btn');
    
    const hasRegion = appState.selectedRegion !== null;
    const hasDateRange = appState.startDate && appState.endDate;
    const hasLayers = appState.selectedLayers.length > 0;
    
    fetchBtn.disabled = !(hasRegion && hasDateRange && hasLayers);
}

// Fetch Data Handler
function initFetchButton() {
    const fetchBtn = document.getElementById('fetch-data-btn');
    
    fetchBtn.addEventListener('click', async () => {
        // Prepare data payload
        const payload = {
            region: appState.selectedRegion,
            dateRange: {
                start: appState.startDate,
                end: appState.endDate
            },
            layers: appState.selectedLayers.map(id => id.replace('layer-', ''))
        };
        
        // Show loading state
        fetchBtn.disabled = true;
        fetchBtn.innerHTML = '⏳ Fetching Data...';
        
        try {
            // TODO: Replace with actual API endpoint
            const response = await fetch('/api/fetch-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Enable prompt submission
                document.getElementById('submit-prompt-btn').disabled = false;
                
                // Show success message
                addSystemMessage('✅ Satellite data fetched successfully! You can now ask questions about the burn assessment.');
                
                fetchBtn.innerHTML = '✅ Data Fetched';
                setTimeout(() => {
                    fetchBtn.innerHTML = '🚀 Fetch Satellite Data';
                    fetchBtn.disabled = false;
                }, 2000);
            } else {
                throw new Error('Failed to fetch data');
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            addSystemMessage('❌ Error fetching satellite data. Please try again.');
            
            fetchBtn.innerHTML = '❌ Failed - Try Again';
            setTimeout(() => {
                fetchBtn.innerHTML = '🚀 Fetch Satellite Data';
                fetchBtn.disabled = false;
            }, 2000);
        }
    });
}

// Initialize Prompt Handler
function initPromptHandler() {
    const submitBtn = document.getElementById('submit-prompt-btn');
    const promptInput = document.getElementById('prompt-input');
    
    submitBtn.addEventListener('click', () => {
        handlePromptSubmission();
    });
    
    // Allow Enter to submit (Shift+Enter for new line)
    promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!submitBtn.disabled) {
                handlePromptSubmission();
            }
        }
    });
}

// Handle Prompt Submission
async function handlePromptSubmission() {
    const promptInput = document.getElementById('prompt-input');
    const prompt = promptInput.value.trim();
    
    if (!prompt) return;
    
    // Add user message to UI
    addUserMessage(prompt);
    
    // Clear input
    promptInput.value = '';
    
    // Show loading
    const loadingId = addLoadingMessage();
    
    // Disable submit button
    const submitBtn = document.getElementById('submit-prompt-btn');
    submitBtn.disabled = true;
    
    try {
        // Prepare payload
        const payload = {
            prompt: prompt,
            region: appState.selectedRegion,
            dateRange: {
                start: appState.startDate,
                end: appState.endDate
            },
            layers: appState.selectedLayers.map(id => id.replace('layer-', '')),
            conversationHistory: appState.conversationHistory
        };
        
        // TODO: Replace with actual API endpoint
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        // Remove loading message
        removeLoadingMessage(loadingId);
        
        if (response.ok) {
            const data = await response.json();
            
            // Add AI response
            addAIMessage(data.response || 'Analysis complete.');
            
            // Update conversation history
            appState.conversationHistory.push({
                role: 'user',
                content: prompt
            });
            appState.conversationHistory.push({
                role: 'assistant',
                content: data.response
            });
        } else {
            throw new Error('Failed to get response');
        }
    } catch (error) {
        console.error('Error getting response:', error);
        removeLoadingMessage(loadingId);
        addAIMessage('❌ Sorry, I encountered an error processing your request. Please try again.');
    } finally {
        submitBtn.disabled = false;
    }
}

// UI Message Functions
function addUserMessage(content) {
    const responseArea = document.getElementById('response-area');
    
    // Remove placeholder if exists
    const placeholder = responseArea.querySelector('.placeholder-message');
    if (placeholder) {
        placeholder.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-header">👤 You</div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    responseArea.appendChild(messageDiv);
    responseArea.scrollTop = responseArea.scrollHeight;
}

function addAIMessage(content) {
    const responseArea = document.getElementById('response-area');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai-message';
    messageDiv.innerHTML = `
        <div class="message-header">🤖 FireDoc VLM</div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    responseArea.appendChild(messageDiv);
    responseArea.scrollTop = responseArea.scrollHeight;
}

function addSystemMessage(content) {
    const responseArea = document.getElementById('response-area');
    
    // Remove placeholder if exists
    const placeholder = responseArea.querySelector('.placeholder-message');
    if (placeholder) {
        placeholder.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    messageDiv.innerHTML = `
        <div class="message-content" style="border-left-color: #3498db;">${escapeHtml(content)}</div>
    `;
    
    responseArea.appendChild(messageDiv);
    responseArea.scrollTop = responseArea.scrollHeight;
}

function addLoadingMessage() {
    const responseArea = document.getElementById('response-area');
    const loadingId = 'loading-' + Date.now();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai-message';
    messageDiv.id = loadingId;
    messageDiv.innerHTML = `
        <div class="message-header">🤖 FireDoc VLM</div>
        <div class="message-content loading">
            Analyzing
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    responseArea.appendChild(messageDiv);
    responseArea.scrollTop = responseArea.scrollHeight;
    
    return loadingId;
}

function removeLoadingMessage(loadingId) {
    const loadingMsg = document.getElementById(loadingId);
    if (loadingMsg) {
        loadingMsg.remove();
    }
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    initDateInputs();
    initLayerToggles();
    initFetchButton();
    initPromptHandler();
    
    console.log('🔥 FireDoc VLM initialized successfully!');
});
