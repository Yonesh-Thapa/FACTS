/**
 * Future Accountants Website JavaScript
 * Last updated: May 2025
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    
    // Initialize all primary functions
    initVideoAutoplay();
    initButtonTracking();
    initCountdownTimer();
    
    // Set current year in footer copyright
    const currentYearSpan = document.getElementById('current-year');
    if (currentYearSpan) {
        currentYearSpan.textContent = new Date().getFullYear();
    }
});

/**
 * Enhanced cross-platform video player initialization 
 * This implementation works reliably across all browsers and devices
 */
function initVideoAutoplay() {
    console.log('Initializing video autoplay');
    
    // Get all required elements
    const videoWrapper = document.getElementById('video-wrapper');
    const videoPoster = document.getElementById('video-poster');
    const videoElement = document.getElementById('intro-video');
    const playButton = document.getElementById('video-play-button');
    const muteToggle = document.getElementById('video-mute-toggle');
    const captionToggle = document.getElementById('video-caption-toggle');
    const fullscreenButton = document.getElementById('video-fullscreen');
    
    // Safety check
    if (!videoElement || !videoWrapper) {
        console.log('Required video elements not found');
        return;
    }
    
    // Video source is stored in data-src to prevent premature loading
    const videoSrc = videoElement.getAttribute('data-src');
    
    // Set video source and configure it properly
    videoElement.src = videoSrc;
    videoElement.muted = true;
    videoElement.loop = true;
    videoElement.defaultMuted = true;
    videoElement.setAttribute('muted', '');
    videoElement.setAttribute('playsinline', '');
    videoElement.setAttribute('webkit-playsinline', '');
    
    // Track video state
    let isPlaying = false;
    
    // Main play function that works on all platforms
    function playVideo() {
        if (videoElement.paused) {
            // Set up for autoplay
            videoElement.muted = true;
            
            // Hide poster and show video
            if (videoPoster) {
                videoPoster.style.opacity = '0';
                videoPoster.style.pointerEvents = 'none';
            }
            
            // Play with promise handling
            const playPromise = videoElement.play();
            
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    // Successful play
                    isPlaying = true;
                    videoWrapper.classList.add('playing');
                    
                    // Log success
                    console.log('Video playing successfully');
                }).catch(error => {
                    // Failed autoplay - this is common on mobile first interaction
                    console.error('Video play failed:', error);
                    
                    // Show play button
                    if (playButton) {
                        playButton.style.opacity = '1';
                        playButton.style.pointerEvents = 'auto';
                    }
                    
                    // Show poster
                    if (videoPoster) {
                        videoPoster.style.opacity = '1';
                        videoPoster.style.pointerEvents = 'auto';
                    }
                });
            }
        }
    }
    
    // Pause function
    function pauseVideo() {
        if (!videoElement.paused) {
            videoElement.pause();
            isPlaying = false;
            videoWrapper.classList.remove('playing');
        }
    }
    
    // Toggle play/pause
    function togglePlayPause() {
        if (videoElement.paused) {
            playVideo();
        } else {
            pauseVideo();
        }
    }
    
    // Handle mute toggle
    function toggleMute() {
        videoElement.muted = !videoElement.muted;
        
        // Update icon
        if (muteToggle) {
            if (videoElement.muted) {
                muteToggle.innerHTML = '<i class="fas fa-volume-mute"></i>';
                muteToggle.setAttribute('aria-label', 'Unmute video');
                muteToggle.classList.remove('active');
            } else {
                muteToggle.innerHTML = '<i class="fas fa-volume-up"></i>';
                muteToggle.setAttribute('aria-label', 'Mute video');
                muteToggle.classList.add('active');
            }
        }
    }
    
    // Handle captions
    function toggleCaptions() {
        if (videoElement.textTracks && videoElement.textTracks.length > 0) {
            const track = videoElement.textTracks[0];
            track.mode = (track.mode === 'showing') ? 'hidden' : 'showing';
            
            // Update icon
            if (captionToggle) {
                if (track.mode === 'showing') {
                    captionToggle.classList.add('active');
                    captionToggle.setAttribute('aria-label', 'Hide captions');
                } else {
                    captionToggle.classList.remove('active');
                    captionToggle.setAttribute('aria-label', 'Show captions');
                }
            }
        }
    }
    
    // Handle fullscreen
    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            videoWrapper.requestFullscreen().catch(err => {
                console.error(`Error attempting to enable fullscreen: ${err.message}`);
            });
        } else {
            document.exitFullscreen();
        }
    }
    
    // Set up event listeners
    
    // Main play button
    if (playButton) {
        playButton.addEventListener('click', playVideo);
    }
    
    // Click on poster image
    if (videoPoster) {
        videoPoster.addEventListener('click', playVideo);
    }
    
    // Click on video itself
    videoElement.addEventListener('click', togglePlayPause);
    
    // Mute toggle
    if (muteToggle) {
        muteToggle.addEventListener('click', toggleMute);
    }
    
    // Caption toggle
    if (captionToggle) {
        captionToggle.addEventListener('click', toggleCaptions);
    }
    
    // Fullscreen button
    if (fullscreenButton) {
        fullscreenButton.addEventListener('click', toggleFullscreen);
    }
    
    // Video ended - reset UI
    videoElement.addEventListener('ended', function() {
        if (videoElement.loop) {
            playVideo();
        } else {
            isPlaying = false;
            videoWrapper.classList.remove('playing');
            
            // Show poster and play button
            if (videoPoster) {
                videoPoster.style.opacity = '1';
                videoPoster.style.pointerEvents = 'auto';
            }
            
            if (playButton) {
                playButton.style.opacity = '1';
                playButton.style.pointerEvents = 'auto';
            }
        }
    });
    
    // Auto-initialize when interactions occur on page
    const autoPlayOnInteraction = function() {
        playVideo();
        // Only need this once
        document.removeEventListener('click', autoPlayOnInteraction);
        document.removeEventListener('touchstart', autoPlayOnInteraction);
        document.removeEventListener('scroll', autoPlayOnInteraction);
    };
    
    // Set up autoplay triggers
    document.addEventListener('click', autoPlayOnInteraction);
    document.addEventListener('touchstart', autoPlayOnInteraction);
    document.addEventListener('scroll', autoPlayOnInteraction);
    
    // Try initial play - will work on desktop, may fail on mobile
    // that's fine, we handle that with the interaction listeners
    setTimeout(playVideo, 500);
}

/**
 * Initialize button tracking for analytics
 */
function initButtonTracking() {
    const trackableButtons = document.querySelectorAll('[data-track="true"]');
    console.log(`Found ${trackableButtons.length} trackable buttons for analytics`);
    
    trackableButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const buttonId = this.id || 'unnamed-button';
            const buttonText = this.innerText.trim() || 'No Text';
            const pagePath = window.location.pathname;
            
            // Make AJAX call to backend
            fetch('/track_button_click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    button_id: buttonId,
                    button_text: buttonText,
                    page_path: pagePath
                })
            }).catch(error => {
                console.error('Error tracking button click:', error);
            });
        });
    });
}

/**
 * Initialize countdown timer for early bird offer
 * Updated on May 14, 2025 to ensure accurate countdown to May 30, 2025
 */
function initCountdownTimer() {
    console.log('Initializing countdown timer...');
    
    // Find all countdown timers on the page
    const heroCountdown = document.getElementById('countdown-timer');
    const offerSectionCountdown = document.getElementById('homepage-offer-timer');
    const pricingCountdown = document.getElementById('pricing-countdown-timer');
    
    // Create an array of valid countdown elements
    const countdownElements = [heroCountdown, offerSectionCountdown, pricingCountdown].filter(el => el !== null);
    console.log('Found countdown elements:', countdownElements);
    console.log('Valid countdown elements:', countdownElements.length);
    
    // If no countdown elements are found, exit the function
    if (countdownElements.length === 0) {
        console.log('No valid countdown elements found, exiting function.');
        return;
    }
    
    // Set the deadline date to May 30, 2025 - using explicit date format to avoid any confusion
    const earlyBirdDeadline = new Date('2025-05-30T23:59:59');
    const deadline = earlyBirdDeadline.getTime();
    console.log('Deadline set to:', earlyBirdDeadline.toLocaleString());
    
    // Set up cache for previous values to avoid unnecessary DOM updates
    const previousValues = {};
    
    // Update function for the countdown
    function updateCountdown() {
        try {
            const now = new Date().getTime();
            const timeRemaining = deadline - now;
            
            // Check if countdown is finished
            if (timeRemaining < 0) {
                console.log('Countdown finished, offer expired');
                const expiredText = 'Offer has expired';
                
                // Update all countdown elements
                countdownElements.forEach(element => {
                    if (element && element.textContent !== expiredText) {
                        element.textContent = expiredText;
                    }
                });
                return;
            }
            
            // Calculate time units
            const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);
            
            // Format for display
            const displayText = `${days}d ${hours}h ${minutes}m ${seconds}s`;
            const cacheKey = `${days}:${hours}:${minutes}:${seconds}`;
            
            // Update each countdown element if the value has changed
            countdownElements.forEach((element, index) => {
                const elementId = element.id || `countdown-${index}`;
                if (previousValues[elementId] !== cacheKey) {
                    element.textContent = displayText;
                    previousValues[elementId] = cacheKey;
                }
            });
        } catch (error) {
            console.error('Error in countdown timer:', error);
        }
    }
    
    // Run the update function immediately
    updateCountdown();
    
    // Set up interval for updates
    setInterval(updateCountdown, 1000);
}