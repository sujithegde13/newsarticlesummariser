// app.js - Client-side functionality for News Analyzer application

// Function to create an animated sentiment meter
function createSentimentMeter(container, positiveCount, negativeCount, neutralCount) {
    if (!container) return;
    
    const total = positiveCount + negativeCount + neutralCount;
    
    // Calculate percentages
    const positivePercent = total > 0 ? (positiveCount / total * 100) : 0;
    const negativePercent = total > 0 ? (negativeCount / total * 100) : 0;
    const neutralPercent = total > 0 ? (neutralCount / total * 100) : 0;
    
    // Create the sentiment meter
    const meterHtml = `
        <div class="sentiment-meter mb-4">
            <div class="d-flex justify-content-between mb-2">
                <h3>Sentiment Distribution</h3>
                <span>Total: ${total} articles</span>
            </div>
            <div class="progress" style="height: 30px;">
                <div class="progress-bar bg-success" style="width: 0%;" data-target="${positivePercent}%" 
                    role="progressbar" aria-valuenow="${positivePercent}" aria-valuemin="0" aria-valuemax="100">
                    Positive (${positiveCount})
                </div>
                <div class="progress-bar bg-warning" style="width: 0%;" data-target="${neutralPercent}%" 
                    role="progressbar" aria-valuenow="${neutralPercent}" aria-valuemin="0" aria-valuemax="100">
                    Neutral (${neutralCount})
                </div>
                <div class="progress-bar bg-danger" style="width: 0%;" data-target="${negativePercent}%" 
                    role="progressbar" aria-valuenow="${negativePercent}" aria-valuemin="0" aria-valuemax="100">
                    Negative (${negativeCount})
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = meterHtml;
    
    // Animate the sentiment meter
    const progressBars = container.querySelectorAll('.progress-bar');
    setTimeout(() => {
        progressBars.forEach(bar => {
            const target = bar.getAttribute('data-target');
            bar.style.width = target;
        });
    }, 200);
}

// Function to setup audio player with enhanced controls
function setupAudioPlayer() {
    const audioPlayer = document.getElementById('audio-player');
    if (!audioPlayer) return;
    
    // Add event listeners
    audioPlayer.addEventListener('play', function() {
        console.log('Audio playback started');
    });
    
    audioPlayer.addEventListener('ended', function() {
        console.log('Audio playback completed');
    });
    
    // Add playback speed controls if not already present
    if (!document.getElementById('playback-speed-controls')) {
        const speedControls = document.createElement('div');
        speedControls.id = 'playback-speed-controls';
        speedControls.className = 'mt-2 d-flex justify-content-center';
        speedControls.innerHTML = `
            <div class="btn-group btn-group-sm" role="group" aria-label="Playback Speed">
                <button type="button" class="btn btn-outline-secondary speed-btn" data-speed="0.75">0.75x</button>
                <button type="button" class="btn btn-outline-secondary speed-btn active" data-speed="1">1x</button>
                <button type="button" class="btn btn-outline-secondary speed-btn" data-speed="1.25">1.25x</button>
                <button type="button" class="btn btn-outline-secondary speed-btn" data-speed="1.5">1.5x</button>
            </div>
        `;
        
        const playerContainer = document.getElementById('audio-player-container');
        if (playerContainer) {
            playerContainer.appendChild(speedControls);
            
            // Add event listeners to speed buttons
            const speedButtons = speedControls.querySelectorAll('.speed-btn');
            speedButtons.forEach(btn => {
                btn.addEventListener('click', function() {
                    // Update active button
                    speedButtons.forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Set playback rate
                    const speed = parseFloat(this.getAttribute('data-speed'));
                    audioPlayer.playbackRate = speed;
                });
            });
        }
    }
}

// Function to copy JSON data to clipboard
function setupJsonCopy() {
    const copyBtn = document.getElementById('copy-json');
    const jsonContainer = document.getElementById('json-container');
    
    if (copyBtn && jsonContainer) {
        copyBtn.addEventListener('click', function() {
            navigator.clipboard.writeText(jsonContainer.textContent)
                .then(() => {
                    copyBtn.innerHTML = '<i class="fas fa-check me-1"></i> Copied!';
                    setTimeout(() => {
                        copyBtn.innerHTML = '<i class="fas fa-copy me-1"></i> Copy';
                    }, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy: ', err);
                });
        });
    }
}

// Function to refresh interface components
function refreshInterface() {
    // Setup audio player
    setupAudioPlayer();
    
    // Setup JSON copy button
    setupJsonCopy();
    
    // Create sentiment meter if data is available
    const sentimentContainer = document.getElementById('sentiment-meter-container');
    if (sentimentContainer) {
        const dataInput = document.getElementById('analysis-data');
        if (dataInput && dataInput.value) {
            try {
                const data = JSON.parse(dataInput.value);
                const sentiment = data.Comparative_Sentiment_Score?.Sentiment_Distribution || {};
                createSentimentMeter(
                    sentimentContainer,
                    sentiment.POSITIVE || 0,
                    sentiment.NEGATIVE || 0,
                    sentiment.NEUTRAL || 0
                );
            } catch (e) {
                console.error('Error parsing analysis data:', e);
            }
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    refreshInterface();
    
    // Poll for available companies to populate the dropdown
    fetchAvailableCompanies();
});

// Function to fetch available companies and update the datalist
function fetchAvailableCompanies() {
    fetch('/available-companies')
        .then(response => response.json())
        .then(data => {
            if (data.companies && Array.isArray(data.companies)) {
                const datalist = document.getElementById('company-options');
                if (datalist) {
                    // Clear existing options
                    datalist.innerHTML = '';
                    
                    // Add all companies to the datalist
                    data.companies.forEach(company => {
                        const option = document.createElement('option');
                        option.value = company;
                        datalist.appendChild(option);
                    });
                }
            }
        })
        .catch(error => {
            console.error('Error fetching available companies:', error);
        });
}