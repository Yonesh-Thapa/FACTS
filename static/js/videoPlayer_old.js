/**
 * Production-Ready Video Player Implementation
 * Meets all requirements for autoplay, cross-browser compatibility, and error handling
 */

class MentorVideoPlayer {
    constructor() {
        this.videoPlayer = null;
        this.videoElement = null;
        this.posterContainer = null;
        this.controls = {};
        this.isPlaying = false;
        this.isMuted = true;
        this.captionsEnabled = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupPlayer());
        } else {
            this.setupPlayer();
        }
    }
    
    setupPlayer() {
        try {
            this.findElements();
            if (!this.validateElements()) {
                console.warn('Video player elements not found, skipping initialization');
                return;
            }
            
            this.setupVideoElement();
            this.setupControls();
            this.setupEventListeners();
            this.attemptAutoplay();
        } catch (error) {
            console.error('Error setting up video player:', error);
        }
    }
    
    findElements() {
        this.videoPlayer = document.getElementById('mentor-video-player');
        this.videoElement = document.getElementById('mentor-video');
        this.posterContainer = this.videoPlayer?.querySelector('.poster-container');
        
        // Find control buttons
        this.controls = {
            playPause: this.videoPlayer?.querySelector('.play-pause'),
            muteUnmute: this.videoPlayer?.querySelector('.mute-unmute'),
            captions: this.videoPlayer?.querySelector('.captions'),
            fullscreen: this.videoPlayer?.querySelector('.fullscreen')
        };
    }
    
    validateElements() {
        return this.videoElement && this.videoPlayer && this.posterContainer;
    }
    
    setupVideoElement() {
        // Configure video for optimal autoplay compatibility
        this.videoElement.muted = true;
        this.videoElement.defaultMuted = true;
        this.videoElement.volume = 0;
        this.videoElement.playsInline = true;
        this.videoElement.setAttribute('playsinline', '');
        this.videoElement.setAttribute('webkit-playsinline', '');
        this.videoElement.setAttribute('x5-playsinline', '');
        
        // Preload metadata for faster startup
        this.videoElement.preload = 'metadata';
        
        // Set up video event listeners
        this.videoElement.addEventListener('loadedmetadata', () => this.onVideoLoaded());
        this.videoElement.addEventListener('canplay', () => this.onVideoCanPlay());
        this.videoElement.addEventListener('play', () => this.onVideoPlay());
        this.videoElement.addEventListener('pause', () => this.onVideoPause());
        this.videoElement.addEventListener('ended', () => this.onVideoEnded());
        this.videoElement.addEventListener('error', (e) => this.onVideoError(e));
        this.videoElement.addEventListener('loadstart', () => this.onVideoLoadStart());
        this.videoElement.addEventListener('stalled', () => this.onVideoStalled());
    }
    
    setupControls() {
        // Play/Pause control
        if (this.controls.playPause) {
            this.controls.playPause.addEventListener('click', () => this.togglePlayPause());
            this.controls.playPause.setAttribute('aria-label', 'Play video');
        }
        
        // Mute/Unmute control
        if (this.controls.muteUnmute) {
            this.controls.muteUnmute.addEventListener('click', () => this.toggleMute());
            this.controls.muteUnmute.setAttribute('aria-label', 'Unmute video');
        }
        
        // Captions control
        if (this.controls.captions) {
            this.controls.captions.addEventListener('click', () => this.toggleCaptions());
            this.controls.captions.setAttribute('aria-label', 'Toggle captions');
        }
        
        // Fullscreen control
        if (this.controls.fullscreen) {
            this.controls.fullscreen.addEventListener('click', () => this.toggleFullscreen());
            this.controls.fullscreen.setAttribute('aria-label', 'Enter fullscreen');
        }
        
        // Initial control states
        this.updateControlStates();
    }
    
    setupEventListeners() {
        // Poster click to play
        if (this.posterContainer) {
            this.posterContainer.addEventListener('click', () => this.handlePosterClick());
        }
        
        // Keyboard accessibility
        this.videoPlayer.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        // Fullscreen change events
        document.addEventListener('fullscreenchange', () => this.onFullscreenChange());
        document.addEventListener('webkitfullscreenchange', () => this.onFullscreenChange());
        document.addEventListener('mozfullscreenchange', () => this.onFullscreenChange());
        document.addEventListener('MSFullscreenChange', () => this.onFullscreenChange());
    }
    
    attemptAutoplay() {
        if (!this.videoElement.src) {
            console.warn('No video source provided');
            return;
        }
        
        // Load the video first
        this.videoElement.load();
        
        // Attempt autoplay after a short delay to ensure proper loading
        setTimeout(() => {
            const playPromise = this.videoElement.play();
            
            if (playPromise !== undefined) {
                playPromise
                    .then(() => {
                        console.log('Autoplay succeeded');
                        this.onAutoplaySuccess();
                    })
                    .catch((error) => {
                        console.log('Autoplay failed:', error.message);
                        this.onAutoplayFailed();
                    });
            } else {
                // Older browsers without promise support
                setTimeout(() => {
                    if (this.videoElement.paused) {
                        this.onAutoplayFailed();
                    } else {
                        this.onAutoplaySuccess();
                    }
                }, 500);
            }
        }, 100);
    }
    
    onAutoplaySuccess() {
        this.hidePoster();
        this.isPlaying = true;
        this.updateControlStates();
    }
    
    onAutoplayFailed() {
        this.showPoster();
        this.isPlaying = false;
        this.updateControlStates();
        
        // Retry autoplay up to maxRetries times
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            setTimeout(() => this.attemptAutoplay(), 1000 * this.retryCount);
        }
    }
    
    handlePosterClick() {
        this.playVideo();
    }
    
    playVideo() {
        const playPromise = this.videoElement.play();
        
        if (playPromise !== undefined) {
            playPromise
                .then(() => {
                    this.hidePoster();
                    this.isPlaying = true;
                    this.updateControlStates();
                })
                .catch((error) => {
                    console.error('Failed to play video:', error);
                });
        }
    }
    
    pauseVideo() {
        this.videoElement.pause();
        this.isPlaying = false;
        this.updateControlStates();
    }
    
    togglePlayPause() {
        if (this.videoElement.paused) {
            this.playVideo();
        } else {
            this.pauseVideo();
        }
    }
    
    toggleMute() {
        this.videoElement.muted = !this.videoElement.muted;
        this.isMuted = this.videoElement.muted;
        this.updateControlStates();
    }
    
    toggleCaptions() {
        const tracks = this.videoElement.textTracks;
        if (tracks.length > 0) {
            const track = tracks[0];
            if (track.mode === 'showing') {
                track.mode = 'hidden';
                this.captionsEnabled = false;
            } else {
                track.mode = 'showing';
                this.captionsEnabled = true;
            }
            this.updateControlStates();
        }
    }
    
    toggleFullscreen() {
        if (!document.fullscreenElement && !document.webkitFullscreenElement && 
            !document.mozFullScreenElement && !document.msFullscreenElement) {
            this.enterFullscreen();
        } else {
            this.exitFullscreen();
        }
    }
    
    enterFullscreen() {
        const element = this.videoElement;
        
        if (element.requestFullscreen) {
            element.requestFullscreen();
        } else if (element.webkitRequestFullscreen) {
            element.webkitRequestFullscreen();
        } else if (element.mozRequestFullScreen) {
            element.mozRequestFullScreen();
        } else if (element.msRequestFullscreen) {
            element.msRequestFullscreen();
        }
    }
    
    exitFullscreen() {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    }
    
    showPoster() {
        if (this.posterContainer) {
            this.posterContainer.style.display = 'flex';
        }
    }
    
    hidePoster() {
        if (this.posterContainer) {
            this.posterContainer.style.display = 'none';
        }
    }
    
    updateControlStates() {
        // Update play/pause button
        if (this.controls.playPause) {
            const icon = this.controls.playPause.querySelector('i');
            if (icon) {
                icon.className = this.isPlaying ? 'fas fa-pause' : 'fas fa-play';
            }
            this.controls.playPause.setAttribute('aria-label', this.isPlaying ? 'Pause video' : 'Play video');
        }
        
        // Update mute/unmute button
        if (this.controls.muteUnmute) {
            const icon = this.controls.muteUnmute.querySelector('i');
            if (icon) {
                icon.className = this.isMuted ? 'fas fa-volume-mute' : 'fas fa-volume-up';
            }
            this.controls.muteUnmute.setAttribute('aria-label', this.isMuted ? 'Unmute video' : 'Mute video');
        }
        
        // Update captions button
        if (this.controls.captions) {
            this.controls.captions.classList.toggle('active', this.captionsEnabled);
        }
    }
    
    handleKeydown(event) {
        switch (event.key) {
            case ' ':
            case 'k':
                event.preventDefault();
                this.togglePlayPause();
                break;
            case 'm':
                event.preventDefault();
                this.toggleMute();
                break;
            case 'f':
                event.preventDefault();
                this.toggleFullscreen();
                break;
            case 'c':
                event.preventDefault();
                this.toggleCaptions();
                break;
        }
    }
    
    // Video event handlers
    onVideoLoaded() {
        console.log('Video metadata loaded');
    }
    
    onVideoCanPlay() {
        console.log('Video can play');
        this.hideVideoLoading();
    }
    
    onVideoPlay() {
        this.isPlaying = true;
        this.hidePoster();
        this.updateControlStates();
    }
    
    onVideoPause() {
        this.isPlaying = false;
        this.updateControlStates();
    }
    
    onVideoEnded() {
        this.isPlaying = false;
        this.updateControlStates();
        // For looping videos, this shouldn't trigger, but handle it gracefully
    }
    
    onVideoError(event) {
        console.error('Video error:', event);
        this.showVideoError();
        this.isPlaying = false;
        this.updateControlStates();
    }
    
    showVideoError() {
        const errorElement = this.videoPlayer.querySelector('.video-error');
        if (errorElement) {
            errorElement.style.display = 'flex';
            
            // Set up retry button
            const retryBtn = errorElement.querySelector('.retry-btn');
            if (retryBtn) {
                retryBtn.addEventListener('click', () => this.retryVideo());
            }
        }
    }
    
    hideVideoError() {
        const errorElement = this.videoPlayer.querySelector('.video-error');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }
    
    retryVideo() {
        this.hideVideoError();
        this.retryCount = 0;
        this.videoElement.load();
        this.attemptAutoplay();
    }
    
    onVideoLoadStart() {
        console.log('Video load started');
    }
    
    onVideoStalled() {
        console.log('Video loading stalled');
        this.showVideoLoading();
    }
    
    showVideoLoading() {
        const loadingElement = this.posterContainer?.querySelector('.video-loading');
        if (loadingElement) {
            loadingElement.style.display = 'flex';
        }
    }
    
    hideVideoLoading() {
        const loadingElement = this.posterContainer?.querySelector('.video-loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }
    
    onFullscreenChange() {
        const isFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement || 
                               document.mozFullScreenElement || document.msFullscreenElement);
        
        if (this.controls.fullscreen) {
            const icon = this.controls.fullscreen.querySelector('i');
            if (icon) {
                icon.className = isFullscreen ? 'fas fa-compress' : 'fas fa-expand';
            }
            this.controls.fullscreen.setAttribute('aria-label', isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen');
        }
    }
}

// Initialize the video player
let mentorVideoPlayer;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        mentorVideoPlayer = new MentorVideoPlayer();
    });
} else {
    mentorVideoPlayer = new MentorVideoPlayer();
}
                        console.log('Video autoplay successful');
                    }).catch(err => {
                        console.error('Failed to play video:', err);
                    });
                }
            } catch (e) {
                console.error('Error in alternate video play:', e);
            }
        }
        return;
    }
    
    // Flag to track if video has been interacted with
    let userInteracted = false;
    
    // Functions for video control
    
    // Play the video and handle the UI changes
    function playVideo() {
        try {
            // iOS Safari specific optimization
            if (isIOS()) {
                // This helps on iOS Safari which is particularly strict
                videoElement.setAttribute('autoplay', 'autoplay');
                videoElement.setAttribute('playsinline', 'playsinline');
                videoElement.setAttribute('webkit-playsinline', 'webkit-playsinline');
                
                // For iOS Safari, we need both the video to be muted and have user interaction
                videoElement.muted = true;
                videoElement.defaultMuted = true;
                videoElement.setAttribute('muted', 'muted');
            }
            
            // Hide poster
            if (posterContainer) {
                posterContainer.classList.add('hidden');
            }
            
            // Force load (needed for some mobile browsers)
            videoElement.load();
            
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
                    
                    // iOS-specific fallback
                    if (isIOS()) {
                        console.log('Attempting iOS-specific video play method');
                        
                        // This is a special trick for iOS
                        videoElement.controls = true;
                        setTimeout(() => {
                            videoElement.controls = false;
                        }, 50);
                    }
                });
            }
        } catch (e) {
            console.error('Error in playVideo:', e);
        }
    }
    
    // Helper to detect iOS
    function isIOS() {
        return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
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
        try {
            if (!document.fullscreenElement) {
                // Use the video element itself for fullscreen, not the wrapper
                // This is more reliable across browsers
                if (videoElement.requestFullscreen) {
                    videoElement.requestFullscreen();
                } else if (videoElement.webkitRequestFullscreen) { /* Safari */
                    videoElement.webkitRequestFullscreen();
                } else if (videoElement.msRequestFullscreen) { /* IE11 */
                    videoElement.msRequestFullscreen();
                } else if (videoElement.webkitEnterFullscreen) { /* iOS Safari */
                    videoElement.webkitEnterFullscreen();
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
        } catch (error) {
            console.error('Fullscreen error:', error);
            // Fallback for iOS: use the native video fullscreen
            if (videoElement.webkitEnterFullscreen) {
                videoElement.webkitEnterFullscreen();
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
    
    // Ensure video is muted for autoplay compliance
    videoElement.muted = true;
    videoElement.defaultMuted = true;
    videoElement.volume = 0;
    videoElement.setAttribute('muted', 'muted');
    
    // Try to play automatically, will work on desktop
    try {
        console.log('Initializing video autoplay');
        // Delay slightly to ensure everything's loaded
        setTimeout(() => {
            // Double-check muted state before autoplay
            videoElement.muted = true;
            playVideo();
        }, 300);
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