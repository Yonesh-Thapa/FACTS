/**
 * Universal Video Autoplay Solution for F.A.C.T.S
 * Ensures video autoplays on all devices and browsers
 * Handles iOS, Android, desktop, and smart device restrictions
 */

class UniversalVideoAutoplay {
    constructor(videoId = 'mentor-video') {
        this.video = document.getElementById(videoId);
        this.posterContainer = document.querySelector('.poster-container');
        this.playButton = document.querySelector('.play-icon-large');
        this.videoContainer = document.querySelector('.video-container');
        this.isAutoplayAttempted = false;
        this.userInteracted = false;
        
        if (!this.video) {
            console.warn('Video element not found');
            return;
        }
        
        this.init();
    }
    
    init() {
        // Detect device and browser capabilities
        this.detectCapabilities();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Attempt autoplay when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.attemptAutoplay());
        } else {
            this.attemptAutoplay();
        }
        
        // Retry autoplay on user interaction
        this.setupUserInteractionHandlers();
        
        // Handle visibility changes (tab switching)
        this.handleVisibilityChanges();
    }
    
    detectCapabilities() {
        this.isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        this.isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        this.isAndroid = /Android/.test(navigator.userAgent);
        this.isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
        this.isChrome = /Chrome/.test(navigator.userAgent);
        this.isFirefox = /Firefox/.test(navigator.userAgent);
        
        // Check if browser supports autoplay with sound
        this.supportsAutoplayWithSound = !this.isMobile && !this.isSafari;
        
        console.log('Device detection:', {
            isMobile: this.isMobile,
            isIOS: this.isIOS,
            isAndroid: this.isAndroid,
            isSafari: this.isSafari,
            supportsAutoplayWithSound: this.supportsAutoplayWithSound
        });
    }
    
    setupEventListeners() {
        // Video event listeners
        this.video.addEventListener('loadstart', () => this.onLoadStart());
        this.video.addEventListener('loadedmetadata', () => this.onLoadedMetadata());
        this.video.addEventListener('canplay', () => this.onCanPlay());
        this.video.addEventListener('canplaythrough', () => this.onCanPlayThrough());
        this.video.addEventListener('play', () => this.onPlay());
        this.video.addEventListener('pause', () => this.onPause());
        this.video.addEventListener('error', (e) => this.onError(e));
        this.video.addEventListener('stalled', () => this.onStalled());
        this.video.addEventListener('waiting', () => this.onWaiting());
        
        // User interaction listeners
        if (this.posterContainer) {
            this.posterContainer.addEventListener('click', () => this.handleUserPlay());
            this.posterContainer.addEventListener('touchstart', () => this.handleUserPlay(), { passive: true });
        }
        
        if (this.playButton) {
            this.playButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this.handleUserPlay();
            });
        }
        
        // Keyboard accessibility
        this.video.addEventListener('keydown', (e) => this.handleKeydown(e));
        if (this.posterContainer) {
            this.posterContainer.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.handleUserPlay();
                }
            });
        }
    }
    
    setupUserInteractionHandlers() {
        // Global interaction detection for iOS and mobile devices
        const interactionEvents = ['touchstart', 'touchend', 'click', 'keydown', 'scroll'];
        
        const handleFirstInteraction = () => {
            this.userInteracted = true;
            console.log('User interaction detected, retrying autoplay');
            
            // Remove listeners after first interaction
            interactionEvents.forEach(event => {
                document.removeEventListener(event, handleFirstInteraction, true);
            });
            
            // Retry autoplay after user interaction
            setTimeout(() => this.attemptAutoplay(), 100);
        };
        
        // Add listeners for first user interaction
        interactionEvents.forEach(event => {
            document.addEventListener(event, handleFirstInteraction, true);
        });
    }
    
    handleVisibilityChanges() {
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.video && !this.video.ended) {
                // Page became visible again, retry autoplay
                setTimeout(() => this.attemptAutoplay(), 500);
            }
        });
    }
    
    async attemptAutoplay() {
        if (this.isAutoplayAttempted && this.video.currentTime > 0) {
            return; // Already playing
        }
        
        this.isAutoplayAttempted = true;
        
        try {
            // Ensure video is muted for autoplay policy compliance
            this.video.muted = true;
            this.video.playsInline = true;
            
            // Set additional mobile-specific attributes
            if (this.isMobile) {
                this.video.setAttribute('webkit-playsinline', 'true');
                this.video.setAttribute('playsinline', 'true');
            }
            
            // iOS specific handling
            if (this.isIOS) {
                this.video.setAttribute('autoplay', 'true');
                this.video.setAttribute('muted', 'true');
                this.video.setAttribute('playsinline', 'true');
                this.video.setAttribute('webkit-playsinline', 'true');
            }
            
            // Load the video first
            if (this.video.readyState < 2) {
                await new Promise((resolve) => {
                    const onLoadedData = () => {
                        this.video.removeEventListener('loadeddata', onLoadedData);
                        resolve();
                    };
                    this.video.addEventListener('loadeddata', onLoadedData);
                    this.video.load();
                });
            }
            
            // Attempt to play
            console.log('Attempting autoplay...');
            const playPromise = this.video.play();
            
            if (playPromise !== undefined) {
                await playPromise;
                console.log('Autoplay successful');
                this.onAutoplaySuccess();
            }
            
        } catch (error) {
            console.log('Autoplay failed:', error.message);
            this.onAutoplayFailed(error);
        }
    }
    
    onAutoplaySuccess() {
        // Hide poster when autoplay succeeds
        if (this.posterContainer) {
            this.posterContainer.classList.add('hidden');
        }
        
        // Update play button state
        this.updatePlayButtonState();
        
        // Track successful autoplay
        if (window.Utils && window.Utils.trackEvent) {
            window.Utils.trackEvent('video_autoplay_success', {
                device: this.isMobile ? 'mobile' : 'desktop',
                browser: this.getBrowserName()
            });
        }
    }
    
    onAutoplayFailed(error) {
        console.log('Autoplay blocked, showing poster');
        
        // Show poster when autoplay fails
        if (this.posterContainer) {
            this.posterContainer.classList.remove('hidden');
        }
        
        // Update UI to indicate manual play needed
        this.showManualPlayUI();
        
        // Track failed autoplay
        if (window.Utils && window.Utils.trackEvent) {
            window.Utils.trackEvent('video_autoplay_failed', {
                device: this.isMobile ? 'mobile' : 'desktop',
                browser: this.getBrowserName(),
                error: error.message
            });
        }
    }
    
    async handleUserPlay() {
        try {
            // Ensure video is ready
            if (this.video.readyState < 2) {
                this.showLoadingState();
                await new Promise((resolve) => {
                    const onCanPlay = () => {
                        this.video.removeEventListener('canplay', onCanPlay);
                        resolve();
                    };
                    this.video.addEventListener('canplay', onCanPlay);
                    this.video.load();
                });
                this.hideLoadingState();
            }
            
            // Toggle play/pause
            if (this.video.paused) {
                await this.video.play();
            } else {
                this.video.pause();
            }
            
        } catch (error) {
            console.error('Manual play failed:', error);
            this.showErrorState('Unable to play video. Please try refreshing the page.');
        }
    }
    
    showManualPlayUI() {
        if (this.posterContainer) {
            this.posterContainer.style.display = 'flex';
            this.posterContainer.classList.remove('hidden');
        }
        
        if (this.playButton) {
            this.playButton.style.display = 'flex';
            // Add pulse animation to draw attention
            this.playButton.style.animation = 'pulse 2s infinite';
        }
    }
    
    showLoadingState() {
        const loadingElement = this.videoContainer?.querySelector('.video-loading');
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }
        
        if (this.playButton) {
            this.playButton.style.display = 'none';
        }
    }
    
    hideLoadingState() {
        const loadingElement = this.videoContainer?.querySelector('.video-loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }
    
    showErrorState(message) {
        // Create error overlay if it doesn't exist
        let errorOverlay = this.videoContainer?.querySelector('.video-error-overlay');
        if (!errorOverlay) {
            errorOverlay = document.createElement('div');
            errorOverlay.className = 'video-error-overlay';
            errorOverlay.innerHTML = `
                <div class="error-content">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h4>Video Error</h4>
                    <p>${message}</p>
                    <button onclick="location.reload()" class="btn btn-sm btn-primary">
                        <i class="fas fa-redo me-1"></i>Reload Page
                    </button>
                </div>
            `;
            this.videoContainer?.appendChild(errorOverlay);
        }
    }
    
    updatePlayButtonState() {
        const playPauseButton = document.querySelector('.play-pause i');
        if (playPauseButton) {
            if (this.video.paused) {
                playPauseButton.className = 'fas fa-play';
            } else {
                playPauseButton.className = 'fas fa-pause';
            }
        }
    }
    
    getBrowserName() {
        if (this.isChrome) return 'Chrome';
        if (this.isFirefox) return 'Firefox';
        if (this.isSafari) return 'Safari';
        return 'Other';
    }
    
    handleKeydown(e) {
        switch(e.key) {
            case ' ':
            case 'k':
                e.preventDefault();
                this.handleUserPlay();
                break;
            case 'm':
                e.preventDefault();
                this.video.muted = !this.video.muted;
                break;
        }
    }
    
    // Event handlers
    onLoadStart() {
        console.log('Video load started');
        this.showLoadingState();
    }
    
    onLoadedMetadata() {
        console.log('Video metadata loaded');
        this.hideLoadingState();
    }
    
    onCanPlay() {
        console.log('Video can play');
        this.hideLoadingState();
        
        // Retry autoplay if not already attempted after user interaction
        if (this.userInteracted && !this.video.currentTime) {
            this.attemptAutoplay();
        }
    }
    
    onCanPlayThrough() {
        console.log('Video can play through');
    }
    
    onPlay() {
        console.log('Video started playing');
        if (this.posterContainer) {
            this.posterContainer.classList.add('hidden');
        }
        this.updatePlayButtonState();
    }
    
    onPause() {
        console.log('Video paused');
        this.updatePlayButtonState();
    }
    
    onError(e) {
        console.error('Video error:', e);
        this.showErrorState('Video failed to load. Please check your connection and try again.');
    }
    
    onStalled() {
        console.log('Video stalled');
        this.showLoadingState();
    }
    
    onWaiting() {
        console.log('Video waiting');
        this.showLoadingState();
    }
}

// Intersection Observer for performance optimization
class VideoIntersectionObserver {
    constructor(videoAutoplay) {
        this.videoAutoplay = videoAutoplay;
        this.init();
    }
    
    init() {
        if ('IntersectionObserver' in window) {
            this.observer = new IntersectionObserver(
                (entries) => this.handleIntersection(entries),
                {
                    threshold: 0.5,
                    rootMargin: '50px'
                }
            );
            
            if (this.videoAutoplay.videoContainer) {
                this.observer.observe(this.videoAutoplay.videoContainer);
            }
        }
    }
    
    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Video is visible, ensure it's playing if autoplay succeeded
                if (!this.videoAutoplay.video.paused) {
                    console.log('Video is visible and should be playing');
                }
                this.videoAutoplay.attemptAutoplay();
            } else {
                // Video is not visible, can pause to save bandwidth
                if (!this.videoAutoplay.video.paused && this.videoAutoplay.video.currentTime > 0) {
                    console.log('Video not visible, pausing to save bandwidth');
                    this.videoAutoplay.video.pause();
                }
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Universal Video Autoplay');
    
    // Initialize video autoplay
    const videoAutoplay = new UniversalVideoAutoplay('mentor-video');
    
    // Initialize intersection observer for performance
    new VideoIntersectionObserver(videoAutoplay);
    
    // Additional retry mechanism for stubborn cases
    setTimeout(() => {
        if (videoAutoplay.video && videoAutoplay.video.paused && videoAutoplay.video.currentTime === 0) {
            console.log('Video still not playing, final retry attempt');
            videoAutoplay.attemptAutoplay();
        }
    }, 2000);
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // Page became visible, retry autoplay
        const video = document.getElementById('mentor-video');
        if (video && video.paused) {
            setTimeout(() => {
                const autoplay = new UniversalVideoAutoplay('mentor-video');
                autoplay.attemptAutoplay();
            }, 300);
        }
    }
});

// Export for global use
window.UniversalVideoAutoplay = UniversalVideoAutoplay;
