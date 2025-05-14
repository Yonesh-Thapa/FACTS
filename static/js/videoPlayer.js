/**
 * Universal Video Player Implementation
 * Works reliably on all major browsers and mobile devices
 * Supports autoplay even on strict platforms (iOS, Safari)
 */

// Initialize when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the mentor video player
    initializeMentorVideo();
});

function initializeMentorVideo() {
    // Get all the elements we need
    const videoPlayer = document.getElementById('mentor-video-player');
    const videoElement = document.getElementById('mentor-video');
    const posterContainer = videoPlayer?.querySelector('.poster-container');
    const playPauseBtn = videoPlayer?.querySelector('.play-pause');
    const muteUnmuteBtn = videoPlayer?.querySelector('.mute-unmute');
    const captionsBtn = videoPlayer?.querySelector('.captions');
    const fullscreenBtn = videoPlayer?.querySelector('.fullscreen');
    
    // Safety check - if elements don't exist, exit
    if (!videoElement || !videoPlayer) {
        console.log('Video elements not found');
        return;
    }
    
    // Flag to track if video has been interacted with
    let userInteracted = false;
    
    // Functions for video control
    
    // Play the video and handle the UI changes
    function playVideo() {
        // Hide poster
        if (posterContainer) {
            posterContainer.classList.add('hidden');
        }
        
        // Ensure video is muted initially (required for autoplay)
        videoElement.muted = true;
        
        // This plays the video with promise handling for cross-browser compatibility
        const playPromise = videoElement.play();
        
        if (playPromise !== undefined) {
            playPromise.then(() => {
                // Success - video is playing
                userInteracted = true;
                
                // Update play button icon
                if (playPauseBtn) {
                    playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
                    playPauseBtn.setAttribute('aria-label', 'Pause');
                }
                
                console.log('Video playing successfully');
            }).catch(error => {
                // Failed to play (common on mobile)
                console.error('Failed to play video:', error);
                
                // Show poster again
                if (posterContainer) {
                    posterContainer.classList.remove('hidden');
                }
                
                // Update play button icon
                if (playPauseBtn) {
                    playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
                    playPauseBtn.setAttribute('aria-label', 'Play');
                }
            });
        }
    }
    
    // Pause the video and update UI
    function pauseVideo() {
        videoElement.pause();
        
        // Update play button icon
        if (playPauseBtn) {
            playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
            playPauseBtn.setAttribute('aria-label', 'Play');
        }
    }
    
    // Toggle play/pause state
    function togglePlayPause() {
        if (videoElement.paused) {
            playVideo();
        } else {
            pauseVideo();
        }
    }
    
    // Toggle mute state
    function toggleMute() {
        videoElement.muted = !videoElement.muted;
        
        // Update mute button icon
        if (muteUnmuteBtn) {
            if (videoElement.muted) {
                muteUnmuteBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
                muteUnmuteBtn.setAttribute('aria-label', 'Unmute');
                muteUnmuteBtn.classList.remove('active');
            } else {
                muteUnmuteBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
                muteUnmuteBtn.setAttribute('aria-label', 'Mute');
                muteUnmuteBtn.classList.add('active');
            }
        }
    }
    
    // Toggle captions
    function toggleCaptions() {
        if (videoElement.textTracks && videoElement.textTracks.length > 0) {
            const track = videoElement.textTracks[0];
            
            // Toggle between showing and hiding
            track.mode = (track.mode === 'showing') ? 'hidden' : 'showing';
            
            // Update button appearance
            if (captionsBtn) {
                if (track.mode === 'showing') {
                    captionsBtn.classList.add('active');
                    captionsBtn.setAttribute('aria-label', 'Hide Captions');
                } else {
                    captionsBtn.classList.remove('active');
                    captionsBtn.setAttribute('aria-label', 'Show Captions');
                }
            }
        }
    }
    
    // Toggle fullscreen
    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            // Enter fullscreen
            if (videoPlayer.requestFullscreen) {
                videoPlayer.requestFullscreen();
            } else if (videoPlayer.webkitRequestFullscreen) { /* Safari */
                videoPlayer.webkitRequestFullscreen();
            } else if (videoPlayer.msRequestFullscreen) { /* IE11 */
                videoPlayer.msRequestFullscreen();
            }
            
            // Update button
            if (fullscreenBtn) {
                fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>';
                fullscreenBtn.setAttribute('aria-label', 'Exit Fullscreen');
            }
        } else {
            // Exit fullscreen
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) { /* Safari */
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) { /* IE11 */
                document.msExitFullscreen();
            }
            
            // Update button
            if (fullscreenBtn) {
                fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
                fullscreenBtn.setAttribute('aria-label', 'Fullscreen');
            }
        }
    }
    
    // Set up event listeners
    
    // Main play button in the middle of poster
    if (posterContainer) {
        posterContainer.addEventListener('click', playVideo);
    }
    
    // Play/Pause button in controls
    if (playPauseBtn) {
        playPauseBtn.addEventListener('click', togglePlayPause);
    }
    
    // Mute/Unmute button
    if (muteUnmuteBtn) {
        muteUnmuteBtn.addEventListener('click', toggleMute);
    }
    
    // Captions button
    if (captionsBtn) {
        captionsBtn.addEventListener('click', toggleCaptions);
    }
    
    // Fullscreen button
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', toggleFullscreen);
    }
    
    // Handle clicking on the video itself
    videoElement.addEventListener('click', togglePlayPause);
    
    // Try to play automatically, will work on desktop
    try {
        // Delay slightly to ensure everything's loaded
        setTimeout(playVideo, 300);
    } catch (e) {
        console.error('Initial autoplay failed:', e);
    }
    
    // Set up global interaction listeners (for mobile)
    // These will auto-play the video on the first interaction with the page
    function autoplayOnUserInteraction() {
        if (!userInteracted) {
            playVideo();
            userInteracted = true;
        }
        
        // Remove these listeners after first interaction
        document.removeEventListener('touchstart', autoplayOnUserInteraction);
        document.removeEventListener('click', autoplayOnUserInteraction);
        document.removeEventListener('scroll', autoplayOnUserInteraction);
    }
    
    // Add the auto-play interaction listeners
    document.addEventListener('touchstart', autoplayOnUserInteraction);
    document.addEventListener('click', autoplayOnUserInteraction);
    document.addEventListener('scroll', autoplayOnUserInteraction);
    
    // Handle video end - with looping
    videoElement.addEventListener('ended', function() {
        if (videoElement.loop) {
            playVideo();
        } else {
            // Show poster again
            if (posterContainer) {
                posterContainer.classList.remove('hidden');
            }
            
            // Update play button
            if (playPauseBtn) {
                playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
                playPauseBtn.setAttribute('aria-label', 'Play');
            }
        }
    });
    
    // Additional mobile-specific autoplaying tricks
    
    // For iOS and Safari
    document.addEventListener('touchend', function iosTouchHandler() {
        if (!userInteracted) {
            playVideo();
            userInteracted = true;
        }
        document.removeEventListener('touchend', iosTouchHandler);
    }, { once: true });
    
    // This can trigger autoplay on some mobile browsers
    window.addEventListener('scroll', function scrollHandler() {
        if (!userInteracted && isElementInViewport(videoElement)) {
            playVideo();
            userInteracted = true;
        }
        
        if (userInteracted) {
            window.removeEventListener('scroll', scrollHandler);
        }
    });
    
    // Force autoplay attempt when visible
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !userInteracted) {
                playVideo();
            }
        });
    }, { threshold: 0.5 });
    
    observer.observe(videoElement);
}

// Helper function to check if element is in viewport
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}