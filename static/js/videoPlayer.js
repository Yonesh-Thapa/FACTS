/**
 * Production-Ready Video Player Implementation
 * Clean implementation with comprehensive autoplay, cross-browser compatibility, and error handling
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
        this.userHasInteracted = false;
        
        // Enhanced device detection for better autoplay
        this.deviceInfo = this.detectDevice();
        
        this.init();
    }
    
    detectDevice() {
        const userAgent = navigator.userAgent;
        return {
            isMobile: /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent),
            isIOS: /iPad|iPhone|iPod/.test(userAgent),
            isAndroid: /Android/.test(userAgent),
            isSafari: /^((?!chrome|android).)*safari/i.test(userAgent),
            isChrome: /Chrome/.test(userAgent),
            isFirefox: /Firefox/.test(userAgent),
            isEdge: /Edge/.test(userAgent),
            supportsIntersectionObserver: 'IntersectionObserver' in window
        };
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
                console.log('Video player elements not found, skipping initialization');
                return;
            }
            
            console.log('Video player found, initializing...');
            this.setupVideoElement();
            this.setupControls();
            this.setupEventListeners();
            this.setupInteractionListeners();
            this.setupIntersectionObserver();
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
            playPause: this.videoPlayer?.querySelector('.play-pause-btn'),
            mute: this.videoPlayer?.querySelector('.mute-btn'),
            captions: this.videoPlayer?.querySelector('.captions-btn'),
            fullscreen: this.videoPlayer?.querySelector('.fullscreen-btn')
        };
    }
    
    validateElements() {
        return this.videoPlayer && this.videoElement;
    }
    
    setupVideoElement() {
        // Configure video for autoplay
        this.videoElement.muted = true;
        this.videoElement.defaultMuted = true;
        this.videoElement.setAttribute('muted', '');
        this.videoElement.setAttribute('playsinline', '');
        this.videoElement.setAttribute('webkit-playsinline', '');
        this.videoElement.preload = 'metadata';
        
        // Set volume to 0 for extra safety
        this.videoElement.volume = 0;
    }
    
    setupControls() {
        // Initially hide controls until video is playing
        const controlsContainer = this.videoPlayer.querySelector('.video-controls');
        if (controlsContainer) {
            controlsContainer.style.opacity = '0';
        }
    }
    
    setupEventListeners() {
        // Click on poster to play
        if (this.posterContainer) {
            this.posterContainer.addEventListener('click', () => this.playVideo());
            this.posterContainer.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.playVideo();
                }
            });
        }
        
        // Video element click to toggle play/pause
        this.videoElement.addEventListener('click', () => this.togglePlayPause());
        
        // Control button listeners
        if (this.controls.playPause) {
            this.controls.playPause.addEventListener('click', () => this.togglePlayPause());
        }
        
        if (this.controls.mute) {
            this.controls.mute.addEventListener('click', () => this.toggleMute());
        }
        
        if (this.controls.captions) {
            this.controls.captions.addEventListener('click', () => this.toggleCaptions());
        }
        
        if (this.controls.fullscreen) {
            this.controls.fullscreen.addEventListener('click', () => this.toggleFullscreen());
        }
        
        // Video events
        this.videoElement.addEventListener('loadeddata', () => {
            console.log('Video data loaded');
        });
        
        this.videoElement.addEventListener('play', () => {
            this.isPlaying = true;
            this.onPlay();
        });
        
        this.videoElement.addEventListener('pause', () => {
            this.isPlaying = false;
            this.onPause();
        });
        
        this.videoElement.addEventListener('ended', () => {
            this.onEnded();
        });
        
        this.videoElement.addEventListener('error', (e) => {
            console.error('Video error:', e);
            this.handleVideoError();
        });
    }
    
    setupInteractionListeners() {
        // Set up listeners for user interaction to enable autoplay on mobile
        const interactionEvents = ['touchstart', 'click', 'scroll', 'keydown'];
        
        const handleInteraction = () => {
            if (!this.userHasInteracted && !this.isPlaying) {
                this.userHasInteracted = true;
                this.attemptAutoplay();
                
                // Remove listeners after first interaction
                interactionEvents.forEach(event => {
                    document.removeEventListener(event, handleInteraction);
                });
            }
        };
        
        interactionEvents.forEach(event => {
            document.addEventListener(event, handleInteraction, { passive: true });
        });
    }
    
    setupIntersectionObserver() {
        if (!this.deviceInfo.supportsIntersectionObserver || !this.videoElement) return;
        
        const options = {
            root: null,
            rootMargin: '50px',
            threshold: 0.25
        };
        
        this.intersectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Video is in viewport, attempt autoplay if not already playing
                    if (!this.isPlaying && this.videoElement.paused) {
                        setTimeout(() => this.attemptAutoplay(), 100);
                    }
                } else {
                    // Video is out of viewport, pause to save bandwidth
                    if (this.isPlaying && !this.videoElement.paused) {
                        this.videoElement.pause();
                    }
                }
            });
        }, options);
        
        this.intersectionObserver.observe(this.videoElement);
    }
    
    async attemptAutoplay() {
        if (this.isPlaying || !this.videoElement) return;
        
        try {
            // Enhanced autoplay logic for all devices
            this.videoElement.muted = true;
            this.videoElement.volume = 0;
            this.videoElement.defaultMuted = true;
            
            // Set additional mobile-friendly attributes
            this.videoElement.setAttribute('playsinline', '');
            this.videoElement.setAttribute('webkit-playsinline', '');
            this.videoElement.setAttribute('x5-playsinline', '');
            this.videoElement.setAttribute('x5-video-player-type', 'h5');
            
            console.log('Attempting enhanced video autoplay...');
            
            // Multiple autoplay strategies
            const strategies = [
                // Strategy 1: Direct play
                () => this.videoElement.play(),
                
                // Strategy 2: Load then play
                () => {
                    this.videoElement.load();
                    return new Promise(resolve => {
                        this.videoElement.addEventListener('loadeddata', () => {
                            resolve(this.videoElement.play());
                        }, { once: true });
                    });
                },
                
                // Strategy 3: Short delay then play
                () => new Promise(resolve => {
                    setTimeout(() => resolve(this.videoElement.play()), 100);
                })
            ];
            
            for (let i = 0; i < strategies.length; i++) {
                try {
                    const playPromise = await strategies[i]();
                    if (playPromise !== undefined) {
                        await playPromise;
                    }
                    console.log(`Video autoplay successful with strategy ${i + 1}`);
                    this.onAutoplaySuccess();
                    return;
                } catch (strategyError) {
                    console.log(`Autoplay strategy ${i + 1} failed:`, strategyError.message);
                    if (i === strategies.length - 1) {
                        throw strategyError;
                    }
                }
            }
        } catch (error) {
            console.log('All autoplay strategies failed (normal on mobile):', error.message);
            this.onAutoplayFailed();
        }
    }
    
    async playVideo() {
        try {
            // Mark user interaction
            this.userHasInteracted = true;
            
            // Ensure muted for policy compliance
            this.videoElement.muted = true;
            
            const playPromise = this.videoElement.play();
            
            if (playPromise !== undefined) {
                await playPromise;
                console.log('Video play successful');
            }
        } catch (error) {
            console.error('Failed to play video:', error);
            this.handlePlayError(error);
        }
    }
    
    pauseVideo() {
        if (!this.videoElement.paused) {
            this.videoElement.pause();
        }
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
        this.updateMuteButton();
    }
    
    toggleCaptions() {
        const tracks = this.videoElement.textTracks;
        if (tracks.length > 0) {
            const track = tracks[0];
            track.mode = track.mode === 'showing' ? 'hidden' : 'showing';
            this.captionsEnabled = track.mode === 'showing';
            this.updateCaptionsButton();
        }
    }
    
    toggleFullscreen() {
        try {
            if (!document.fullscreenElement) {
                this.videoPlayer.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        } catch (error) {
            console.error('Fullscreen error:', error);
        }
    }
    
    onPlay() {
        // Hide poster
        if (this.posterContainer) {
            this.posterContainer.classList.add('hidden');
        }
        
        // Show controls
        const controlsContainer = this.videoPlayer.querySelector('.video-controls');
        if (controlsContainer) {
            controlsContainer.style.opacity = '1';
        }
        
        // Update play button
        if (this.controls.playPause) {
            this.controls.playPause.innerHTML = '<i class="fas fa-pause"></i>';
            this.controls.playPause.setAttribute('aria-label', 'Pause');
        }
        
        // Add playing class
        this.videoPlayer.classList.add('playing');
    }
    
    onPause() {
        // Update play button
        if (this.controls.playPause) {
            this.controls.playPause.innerHTML = '<i class="fas fa-play"></i>';
            this.controls.playPause.setAttribute('aria-label', 'Play');
        }
        
        // Remove playing class
        this.videoPlayer.classList.remove('playing');
    }
    
    onEnded() {
        // Reset to beginning if looped, otherwise show poster
        if (this.videoElement.loop) {
            this.videoElement.currentTime = 0;
            this.playVideo();
        } else {
            // Show poster again
            if (this.posterContainer) {
                this.posterContainer.classList.remove('hidden');
            }
            this.onPause();
        }
    }
    
    onAutoplaySuccess() {
        console.log('Autoplay successful - video started automatically');
    }
    
    onAutoplayFailed() {
        // Show poster prominently for user to click
        if (this.posterContainer) {
            this.posterContainer.classList.remove('hidden');
            this.posterContainer.style.opacity = '1';
        }
    }
    
    handleVideoError() {
        console.error('Video failed to load');
        
        // Show fallback or error message
        if (this.posterContainer) {
            this.posterContainer.classList.remove('hidden');
        }
        
        // Try to retry loading if we haven't exceeded retry limit
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            console.log(`Retrying video load (attempt ${this.retryCount}/${this.maxRetries})`);
            
            setTimeout(() => {
                this.videoElement.load();
                this.attemptAutoplay();
            }, 1000 * this.retryCount);
        }
    }
    
    handlePlayError(error) {
        if (error.name === 'NotAllowedError') {
            console.log('Play blocked by browser - user interaction required');
            this.onAutoplayFailed();
        } else {
            console.error('Unexpected play error:', error);
        }
    }
    
    updateMuteButton() {
        if (this.controls.mute) {
            if (this.isMuted) {
                this.controls.mute.innerHTML = '<i class="fas fa-volume-mute"></i>';
                this.controls.mute.setAttribute('aria-label', 'Unmute');
            } else {
                this.controls.mute.innerHTML = '<i class="fas fa-volume-up"></i>';
                this.controls.mute.setAttribute('aria-label', 'Mute');
            }
        }
    }
    
    updateCaptionsButton() {
        if (this.controls.captions) {
            if (this.captionsEnabled) {
                this.controls.captions.classList.add('active');
                this.controls.captions.setAttribute('aria-label', 'Hide captions');
            } else {
                this.controls.captions.classList.remove('active');
                this.controls.captions.setAttribute('aria-label', 'Show captions');
            }
        }
    }
}

// Initialize video player when DOM is ready
let mentorVideoPlayer;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        mentorVideoPlayer = new MentorVideoPlayer();
        setupGlobalVideoHandlers();
    });
} else {
    mentorVideoPlayer = new MentorVideoPlayer();
    setupGlobalVideoHandlers();
}

// Setup global video event handlers
function setupGlobalVideoHandlers() {
    // Handle page visibility changes for better autoplay
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden && mentorVideoPlayer) {
            // Page became visible, retry autoplay if video is paused
            setTimeout(() => {
                if (mentorVideoPlayer.videoElement && 
                    mentorVideoPlayer.videoElement.paused && 
                    !mentorVideoPlayer.isPlaying) {
                    mentorVideoPlayer.attemptAutoplay();
                }
            }, 300);
        }
    });
    
    // Additional retry mechanism for challenging cases
    setTimeout(() => {
        if (mentorVideoPlayer && 
            mentorVideoPlayer.videoElement && 
            mentorVideoPlayer.videoElement.paused && 
            mentorVideoPlayer.videoElement.currentTime === 0) {
            console.log('Video still not playing, final retry attempt');
            mentorVideoPlayer.attemptAutoplay();
        }
    }, 2000);
}