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
        console.log('[FRONTEND] Starting video upload...');
        console.log('[FRONTEND] Video file:', videoFile.name, videoFile.size, 'bytes');
        console.log('[FRONTEND] Custom prompt:', customPrompt || '(none)');
        
        // Upload video to backend
        const formData = new FormData();
        formData.append('video', videoFile);
        formData.append('prompt', customPrompt);
        
        console.log('[FRONTEND] Uploading to http://localhost:5001/api/upload-video');
        const uploadResponse = await fetch('http://localhost:5001/api/upload-video', {
            method: 'POST',
            body: formData
        });
        
        console.log('[FRONTEND] Upload response status:', uploadResponse.status);
        
        if (!uploadResponse.ok) {
            const errorData = await uploadResponse.json();
            console.error('[FRONTEND] Upload error:', errorData);
            throw new Error(errorData.error || 'Failed to upload video');
        }
        
        const uploadData = await uploadResponse.json();
        console.log('[FRONTEND] Video uploaded successfully:', uploadData);
        
        // Analyze video
        console.log('[FRONTEND] Starting video analysis...');
        const analyzeResponse = await fetch('http://localhost:5001/api/analyze-video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_id: uploadData.video_id,
                prompt: customPrompt,
                sample_rate: 5
            })
        });
        
        console.log('[FRONTEND] Analysis response status:', analyzeResponse.status);
        
        if (!analyzeResponse.ok) {
            const errorData = await analyzeResponse.json();
            console.error('[FRONTEND] Analysis error:', errorData);
            throw new Error(errorData.error || 'Failed to analyze video');
        }
        
        const analysisData = await analyzeResponse.json();
        console.log('[FRONTEND] Analysis complete:', analysisData);
        
        // Display results from VLM
        displayVLMResults(analysisData);
        
    } catch (error) {
        console.error('[FRONTEND] Error:', error);
        alert(`An error occurred: ${error.message}\n\nCheck the browser console for details.`);
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

// Display VLM Results
function displayVLMResults(analysisData) {
    loadingState.style.display = 'none';
    resultsDisplay.style.display = 'block';
    
    // Show video at the top of results
    const resultsVideoPreview = document.getElementById('results-video-preview');
    const resultsVideo = document.getElementById('results-video');
    resultsVideo.src = videoPreview.src; // Copy the video source
    resultsVideoPreview.style.display = 'block';
    
    const analysis = analysisData.analysis;
    const metadata = analysisData.video_metadata;
    
    // Parse the VLM response to extract species list
    const speciesList = parseSpeciesFromAnalysis(analysis);
    
    // Update summary cards
    document.getElementById('species-count').textContent = speciesList.length || '—';
    document.getElementById('sightings-count').textContent = analysisData.frames_analyzed || '—';
    const duration = Math.floor(metadata.duration);
    document.getElementById('analysis-duration').textContent = `${Math.floor(duration / 60)}:${(duration % 60).toString().padStart(2, '0')}`;
    
    // Render the VLM analysis as Markdown
    const summaryContent = document.getElementById('ai-summary-content');
    if (typeof marked !== 'undefined') {
        summaryContent.innerHTML = marked.parse(analysis);
    } else {
        summaryContent.innerHTML = `<p style="white-space: pre-wrap;">${analysis}</p>`;
    }
    
    // Display detected species
    const speciesGrid = document.getElementById('species-grid');
    if (speciesList.length > 0) {
        speciesGrid.innerHTML = '';
        speciesList.forEach(species => {
            const card = document.createElement('div');
            card.className = 'species-card';
            card.innerHTML = `
                <div class="species-header">
                    <span class="species-icon">${getAnimalIcon(species)}</span>
                    <span class="species-name">${species}</span>
                </div>
                <div class="species-stats">
                    <p><strong>Status:</strong> Detected in footage</p>
                </div>
            `;
            speciesGrid.appendChild(card);
        });
    } else {
        speciesGrid.innerHTML = '<p class="placeholder-text">No species explicitly listed. See detailed analysis above.</p>';
    }
    
    const timelineContainer = document.getElementById('timeline-container');
    timelineContainer.innerHTML = '<p class="placeholder-text">Timeline information is included in the detailed analysis above.</p>';
}

// Parse species from VLM analysis
function parseSpeciesFromAnalysis(analysis) {
    const speciesList = [];
    
    // Look for "SPECIES DETECTED:" section
    const speciesMatch = analysis.match(/SPECIES DETECTED:(.*?)(?=\n\n|DETAILED ANALYSIS:|$)/is);
    
    if (speciesMatch) {
        const speciesSection = speciesMatch[1];
        // Extract lines starting with "- "
        const matches = speciesSection.matchAll(/^-\s*(.+)$/gm);
        for (const match of matches) {
            const species = match[1].trim();
            if (species && !speciesList.includes(species)) {
                speciesList.push(species);
            }
        }
    }
    
    return speciesList;
}

// Get animal icon based on species name
function getAnimalIcon(speciesName) {
    const name = speciesName.toLowerCase();
    
    // Common animals with their emojis
    const iconMap = {
        'deer': '🦌',
        'fox': '🦊',
        'wolf': '🐺',
        'bear': '🐻',
        'rabbit': '🐰',
        'squirrel': '🐿️',
        'raccoon': '🦝',
        'beaver': '🦫',
        'skunk': '🦨',
        'badger': '🦡',
        'otter': '🦦',
        'moose': '🫎',
        'bison': '🦬',
        'bird': '🐦',
        'eagle': '🦅',
        'owl': '🦉',
        'duck': '🦆',
        'turkey': '🦃',
        'goose': '🦢',
        'hawk': '🦅',
        'crow': '🐦‍⬛',
        'snake': '🐍',
        'turtle': '🐢',
        'frog': '🐸',
        'lizard': '🦎',
        'bat': '🦇',
        'mouse': '🐭',
        'rat': '🐀',
        'chipmunk': '🐿️',
        'porcupine': '🦔',
        'coyote': '🐺',
        'mountain lion': '🦁',
        'cougar': '🦁',
        'puma': '🦁',
        'bobcat': '🐈',
        'lynx': '🐈',
        'elk': '🦌',
        'caribou': '🦌',
        'antelope': '🦌'
    };
    
    // Find matching icon
    for (const [key, icon] of Object.entries(iconMap)) {
        if (name.includes(key)) {
            return icon;
        }
    }
    
    // Default icon
    return '🦊';
}

// Display Results (kept for backward compatibility)
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
