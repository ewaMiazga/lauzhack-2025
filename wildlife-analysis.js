// Wildlife Analysis JavaScript

let uploadedVideo = null;
let videoFile = null;

// DOM Elements
const uploadArea = document.getElementById('upload-area');
const videoInput = document.getElementById('video-input');
const browseBtn = document.getElementById('browse-btn');
const videoPreviewSection = document.getElementById('video-preview-section');
const videoPreview = document.getElementById('video-preview');
const analyzeBtn = document.getElementById('analyze-video-btn');
const resultsSection = document.getElementById('results-section');
const loadingState = document.getElementById('loading-state');
const resultsDisplay = document.getElementById('results-display');
const promptInput = document.getElementById('wildlife-prompt-input');

// Upload Area - Click to browse
uploadArea.addEventListener('click', () => {
    videoInput.click();
});

browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    videoInput.click();
});

// Drag and Drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type.startsWith('video/')) {
        handleVideoUpload(files[0]);
    } else {
        alert('Please drop a valid video file');
    }
});

// File Input Change
videoInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleVideoUpload(e.target.files[0]);
    }
});

// Handle Video Upload
function handleVideoUpload(file) {
    // Check file size (500MB max)
    const maxSize = 500 * 1024 * 1024; // 500MB in bytes
    if (file.size > maxSize) {
        alert('File size exceeds 500MB. Please upload a smaller video.');
        return;
    }

    videoFile = file;
    const url = URL.createObjectURL(file);
    
    videoPreview.src = url;
    document.getElementById('video-filename').textContent = file.name;
    document.getElementById('video-size').textContent = formatFileSize(file.size);
    
    // Get video duration when metadata loads
    videoPreview.addEventListener('loadedmetadata', () => {
        const duration = formatDuration(videoPreview.duration);
        document.getElementById('video-duration').textContent = duration;
    });
    
    videoPreviewSection.style.display = 'block';
    uploadArea.style.display = 'none';
    
    // Enable analyze button
    analyzeBtn.disabled = false;
}

// Format File Size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Format Duration
function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Analyze Video Button
analyzeBtn.addEventListener('click', async () => {
    if (!videoFile) {
        alert('Please upload a video first');
        return;
    }
    
    // Get custom prompt if provided
    const customPrompt = promptInput.value.trim();
    
    // Show results section and loading state
    resultsSection.style.display = 'block';
    loadingState.style.display = 'block';
    resultsDisplay.style.display = 'none';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    try {
        // TODO: Send video and prompt to backend for analysis
        // For now, simulate with mock data
        await simulateAnalysis(customPrompt);
    } catch (error) {
        console.error('Analysis error:', error);
        alert('An error occurred during analysis. Please try again.');
        resultsSection.style.display = 'none';
    }
});

// Simulate Analysis (Replace with actual API call)
async function simulateAnalysis(customPrompt = '') {
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Log the custom prompt for future backend integration
    if (customPrompt) {
        console.log('Custom analysis prompt:', customPrompt);
    }
    
    // Mock data
    const mockResults = {
        speciesDetected: [
            {
                name: 'White-tailed Deer',
                icon: '🦌',
                count: 5,
                confidence: '94%',
                firstSeen: '00:23'
            },
            {
                name: 'Red Fox',
                icon: '🦊',
                count: 2,
                confidence: '89%',
                firstSeen: '01:45'
            },
            {
                name: 'Wild Turkey',
                icon: '🦃',
                count: 3,
                confidence: '92%',
                firstSeen: '02:10'
            }
        ],
        timeline: [
            { time: '00:23', species: 'White-tailed Deer', description: 'Adult deer crossing from left to right' },
            { time: '00:45', species: 'White-tailed Deer', description: 'Two deer grazing near the tree line' },
            { time: '01:45', species: 'Red Fox', description: 'Fox moving through the underbrush' },
            { time: '02:10', species: 'Wild Turkey', description: 'Three turkeys foraging on the ground' },
            { time: '03:30', species: 'White-tailed Deer', description: 'Deer herd of 3 animals passing through' }
        ],
        aiSummary: 'The video shows diverse wildlife activity over a 4-minute period. White-tailed deer were the most frequently observed species with 5 individual sightings, suggesting this is an active deer corridor. A red fox was observed mid-afternoon, likely hunting. Three wild turkeys were spotted foraging, indicating a healthy ecosystem. All detections show high confidence levels (89-94%), confirming reliable identification. The area appears to be a thriving wildlife habitat with minimal human disturbance.'
    };
    
    displayResults(mockResults);
}

// Display Results
function displayResults(results) {
    loadingState.style.display = 'none';
    resultsDisplay.style.display = 'block';
    
    // Update summary cards
    document.getElementById('species-count').textContent = results.speciesDetected.length;
    document.getElementById('sightings-count').textContent = results.timeline.length;
    document.getElementById('analysis-duration').textContent = document.getElementById('video-duration').textContent;
    
    // Update AI summary
    document.getElementById('ai-summary-content').innerHTML = `<p>${results.aiSummary}</p>`;
    
    // Display species cards
    const speciesGrid = document.getElementById('species-grid');
    speciesGrid.innerHTML = '';
    results.speciesDetected.forEach(species => {
        const card = document.createElement('div');
        card.className = 'species-card';
        card.innerHTML = `
            <div class="species-header">
                <span class="species-icon">${species.icon}</span>
                <span class="species-name">${species.name}</span>
            </div>
            <div class="species-stats">
                <p><strong>Sightings:</strong> ${species.count}</p>
                <p><strong>Confidence:</strong> ${species.confidence}</p>
                <p><strong>First seen:</strong> ${species.firstSeen}</p>
            </div>
        `;
        speciesGrid.appendChild(card);
    });
    
    // Display timeline
    const timelineContainer = document.getElementById('timeline-container');
    timelineContainer.innerHTML = '';
    results.timeline.forEach(item => {
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item';
        timelineItem.innerHTML = `
            <div class="timeline-time">${item.time}</div>
            <div class="timeline-species">${item.species}</div>
            <div class="timeline-description">${item.description}</div>
        `;
        timelineContainer.appendChild(timelineItem);
    });
}
