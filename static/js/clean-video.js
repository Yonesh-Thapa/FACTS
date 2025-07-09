/**
 * Clean Video Autoplay Handler for F.A.C.T.S
 * Ensures reliable autoplay across all devices and browsers
 */

class CleanVideoPlayer {
    constructor(videoId = 'mentor-video') {
        this.video = document.getElementById(videoId);
        this.container = this.video?.closest('.responsive-video-container');
        this.autoplayAttempted = false;
        
        if (!this.video) {
            console.warn('Video element not found');
            return;
        }
        
        this.init();
    }
    
    init() {
        // Set up event listeners
        this.setupEventListeners();
        
        // Set up fallback play button
        setupVideoFallback();
        
        // Attempt autoplay when ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.handleAutoplay());
        } else {
            this.handleAutoplay();
        }
    }
    
    setupEventListeners() {
        // Video events
        this.video.addEventListener('loadstart', () => this.showLoading());
        this.video.addEventListener('canplay', () => this.hideLoading());
        this.video.addEventListener('playing', () => this.onPlaying());
        this.video.addEventListener('pause', () => this.onPause());
        this.video.addEventListener('error', () => this.onError());
        
        // User interaction events for autoplay fallback
        const interactionEvents = ['click', 'touchstart', 'keydown'];
        interactionEvents.forEach(event => {
            document.addEventListener(event, () => this.retryAutoplay(), { once: true });
        });
        
        // Intersection Observer for performance
        this.setupIntersectionObserver();
    }
    
    setupIntersectionObserver() {
        if (!('IntersectionObserver' in window)) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.retryAutoplay();
                } else {
                    // Pause when out of view to save bandwidth
                    if (!this.video.paused) {
                        this.video.pause();
                    }
                }
            });
        }, {
            threshold: 0.5,
            rootMargin: '50px'
        });
        
        observer.observe(this.video);
    }
    
    async handleAutoplay() {
        if (this.autoplayAttempted) return;
        this.autoplayAttempted = true;
        
        try {
            // Ensure video is muted for autoplay
            this.video.muted = true;
            this.video.volume = 0;
            
            // Set additional attributes for better compatibility
            this.video.setAttribute('playsinline', '');
            this.video.setAttribute('webkit-playsinline', '');
            this.video.setAttribute('x5-playsinline', '');
            
            // Wait a bit for video metadata to load
            if (this.video.readyState < 2) {
                await new Promise(resolve => {
                    const handler = () => {
                        this.video.removeEventListener('loadedmetadata', handler);
                        this.video.removeEventListener('canplay', handler);
                        resolve();
                    };
                    this.video.addEventListener('loadedmetadata', handler);
                    this.video.addEventListener('canplay', handler);
                    
                    // Timeout after 3 seconds
                    setTimeout(resolve, 3000);
                });
            }
            
            console.log('Attempting video autoplay...');
            
            // Attempt to play
            const playPromise = this.video.play();
            
            if (playPromise !== undefined) {
                await playPromise;
                console.log('Video autoplay successful');
            }
        } catch (error) {
            console.log('Autoplay blocked (normal behavior):', error.message);
            // Retry after user interaction
            this.scheduleRetry();
        }
    }
    
    scheduleRetry() {
        // Retry autoplay after a short delay
        setTimeout(() => {
            if (this.video.paused && this.video.currentTime === 0) {
                this.autoplayAttempted = false;
                this.handleAutoplay();
            }
        }, 1000);
    }
    
    retryAutoplay() {
        if (this.video.paused && this.video.currentTime === 0) {
            this.handleAutoplay();
        }
    }
    
    showLoading() {
        if (this.container) {
            this.container.classList.add('loading');
        }
    }
    
    hideLoading() {
        if (this.container) {
            this.container.classList.remove('loading');
        }
    }
    
    onPlaying() {
        this.video.setAttribute('data-playing', 'true');
        this.hideLoading();
    }
    
    onPause() {
        this.video.setAttribute('data-playing', 'false');
    }
    
    onError() {
        console.error('Video error occurred');
        this.hideLoading();
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        new CleanVideoPlayer('mentor-video');
    });
} else {
    new CleanVideoPlayer('mentor-video');
}

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        // Page became visible, retry autoplay
        const video = document.getElementById('mentor-video');
        if (video && video.paused) {
            setTimeout(() => {
                new CleanVideoPlayer('mentor-video').retryAutoplay();
            }, 300);
        }
    }
});

// Global function for play button
window.playVideo = function() {
    const video = document.getElementById('mentor-video');
    const overlay = document.getElementById('video-play-overlay');
    
    if (video && overlay) {
        video.play().then(() => {
            overlay.style.display = 'none';
            console.log('Video started by user interaction');
        }).catch(error => {
            console.error('Error playing video:', error);
        });
    }
};

// Enhanced fallback detection
function setupVideoFallback() {
    const video = document.getElementById('mentor-video');
    const overlay = document.getElementById('video-play-overlay');
    
    if (!video || !overlay) return;
    
    // Check if video is playing after a delay
    setTimeout(() => {
        const isPlaying = !video.paused && !video.ended && video.currentTime > 0;
        
        if (!isPlaying && video.readyState >= 2) {
            // Video is loaded but not playing - show play button
            overlay.style.display = 'flex';
            console.log('Autoplay blocked - showing manual play button');
        }
    }, 2000);
    
    // Hide overlay when video starts playing
    video.addEventListener('playing', () => {
        overlay.style.display = 'none';
    });
    
    // Show overlay when video is paused
    video.addEventListener('pause', () => {
        if (video.currentTime === 0) {
            overlay.style.display = 'flex';
        }
    });
}

// Export for global access
window.CleanVideoPlayer = CleanVideoPlayer;
