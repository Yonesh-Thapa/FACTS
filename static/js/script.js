/**
 * F.A.C.T.S - Future Accountant Coaching and Training Services 
 * Main JavaScript - Optimized for performance
 */

// Use a single DOMContentLoaded event listener to improve performance
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    
    /**
     * Initialize multiple site functions
     * Grouped to reduce DOM ready event listeners
     */
    
    // Set current year in footer copyright
    const yearElement = document.getElementById('current-year');
    if (yearElement) yearElement.textContent = new Date().getFullYear();
    
    // Navigation scroll handler with debounce for better performance
    const navbar = document.querySelector('.navbar');
    const handleScroll = debounce(function() {
        if (window.scrollY > 50) {
            navbar?.classList.add('navbar-scrolled');
        } else {
            navbar?.classList.remove('navbar-scrolled');
        }
    }, 10);
    
    // Only attach scroll listener if navbar exists
    if (navbar) {
        window.addEventListener('scroll', handleScroll, { passive: true });
        // Initial call to set correct state on page load
        handleScroll();
    }
    
    // Ensure intro video plays with sound
    initVideoAutoplay();
    
    // Smooth scrolling for anchor links with event delegation
    initSmoothScrolling();
    
    // Auto-hide flash messages
    autoHideFlashMessages();
    
    // Contact form validation - only attach if form exists
    initContactFormValidation();
    
    // Initialize Bootstrap tooltips - only if any exist
    initBootstrapTooltips();
    
    // Initialize countdown timer for early bird offer
    console.log('About to initialize countdown timer');
    setTimeout(function() {
        // Delay initialization slightly to ensure DOM is fully processed
        initCountdownTimer();
    }, 100);
    
    // Initialize button click tracking for analytics
    initButtonTracking();
});

/**
 * Debounce function to limit function calls
 * @param {Function} func - The function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @return {Function} - Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            func.apply(context, args);
        }, wait);
    };
}

/**
 * Initialize smooth scrolling behavior
 */
function initSmoothScrolling() {
    const navbarHeight = document.querySelector('.navbar')?.offsetHeight || 0;
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    document.addEventListener('click', function(e) {
        // Find closest anchor with hash
        const anchor = e.target.closest('a[href^="#"]');
        if (!anchor || anchor.getAttribute('href') === '#') return;
        
        const targetId = anchor.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
            e.preventDefault();
            
            // Calculate position including offset
            const offsetTop = targetElement.getBoundingClientRect().top + window.pageYOffset - navbarHeight - 20;
            
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
            
            // Auto-collapse mobile menu if open
            if (navbarToggler && 
                navbarCollapse && 
                window.getComputedStyle(navbarToggler).display !== 'none' && 
                navbarCollapse.classList.contains('show')) {
                new bootstrap.Collapse(navbarCollapse).hide();
            }
        }
    });
}

/**
 * Auto-hide flash messages after delay
 */
function autoHideFlashMessages() {
    const flashMessages = document.querySelectorAll('.alert');
    if (flashMessages.length === 0) return;
    
    flashMessages.forEach(message => {
        setTimeout(() => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(message);
                bsAlert.close();
            } else {
                // Fallback if bootstrap JS isn't loaded yet
                message.classList.remove('show');
                setTimeout(() => message.remove(), 150);
            }
        }, 5000);
    });
}

/**
 * Initialize form validation
 */
function initContactFormValidation() {
    const contactForm = document.querySelector('.contact-form');
    if (!contactForm) return;
    
    contactForm.addEventListener('submit', function(e) {
        let valid = true;
        
        // Clear previous validation states
        contactForm.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        
        // Validate required fields
        const required = contactForm.querySelectorAll('[required]');
        required.forEach(field => {
            if (!field.value.trim()) {
                valid = false;
                field.classList.add('is-invalid');
            }
        });
        
        // Email validation
        const email = contactForm.querySelector('#email');
        if (email?.value.trim()) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email.value.trim())) {
                valid = false;
                email.classList.add('is-invalid');
            }
        }
        
        if (!valid) {
            e.preventDefault();
        }
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initBootstrapTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggers.length > 0 && typeof bootstrap !== 'undefined') {
        tooltipTriggers.forEach(el => new bootstrap.Tooltip(el));
    }
}

/**
 * Initialize countdown timer for early bird offer
 * Updated on May 14, 2025 to ensure accurate countdown to May 30, 2025
 */
function initCountdownTimer() {
    console.log('Initializing countdown timer...');
    
    // Find all countdown timer elements on the page
    const countdownElements = [
        document.getElementById('countdown-timer'),
        document.getElementById('program-countdown-timer'),
        document.getElementById('pricing-countdown-timer')
    ];
    
    console.log('Found countdown elements:', countdownElements);
    
    // Filter out null elements
    const validElements = countdownElements.filter(element => element !== null);
    console.log('Valid countdown elements:', validElements.length);
    
    if (validElements.length === 0) {
        console.log('No valid countdown elements found, exiting function.');
        return;
    }
    
    // Set the deadline date to May 30, 2025 - using explicit date format to avoid any confusion
    const earlyBirdDeadline = new Date('2025-05-30T23:59:59');
    const deadline = earlyBirdDeadline.getTime();
    console.log('Deadline set to:', earlyBirdDeadline.toLocaleString());
    
    // Set up cache for previous values to avoid unnecessary DOM updates
    const previousValues = {};
    
    // Set up ARIA attributes once, not on every update
    validElements.forEach(element => {
        // Add ARIA attributes for accessibility
        element.setAttribute('aria-live', 'off'); // Changed to off to prevent frequent announcements
        element.setAttribute('aria-atomic', 'true');
        element.setAttribute('role', 'timer');
    });
    
    // Immediately update countdown once before interval starts
    updateCountdown();
    
    // Update the countdown every second
    const countdown = setInterval(updateCountdown, 1000);
    
    function updateCountdown() {
        try {
            // Get current date and time
            const now = new Date().getTime();
            
            // Calculate the time remaining
            const timeRemaining = deadline - now;
            
            // If the countdown is finished, clear the interval and display a message
            if (timeRemaining < 0) {
                console.log('Countdown finished, offer expired');
                clearInterval(countdown);
                validElements.forEach(element => {
                    // Only update if the content has changed
                    if (element.textContent !== 'Offer has expired') {
                        element.textContent = 'Offer has expired';
                        element.setAttribute('aria-label', 'The Early Bird offer has expired');
                        element.setAttribute('role', 'status');
                    }
                });
                return;
            }
            
            // Calculate days, hours, minutes, and seconds
            const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);
            
            // Create a cache key to check if values have changed
            const cacheKey = `${days}:${hours}:${minutes}:${seconds}`;
            
            // Format the result without using padStart to avoid zero flickering issues
            const formattedTime = `${days}d ${hours}h ${minutes}m ${seconds}s`;
            
            // Create a more descriptive text for screen readers (updated less frequently)
            const ariaText = `${days} days, ${hours} hours, ${minutes} minutes, and ${seconds} seconds remaining until the Early Bird offer ends`;
            
            // Only update the DOM if the values have changed
            validElements.forEach((element, index) => {
                const elementCacheKey = `${index}:${cacheKey}`;
                
                // Check if we need to update this element
                if (previousValues[elementCacheKey] !== formattedTime) {
                    element.textContent = formattedTime;
                    
                    // Only update the ARIA label occasionally to reduce screen reader noise
                    if (seconds % 15 === 0) { // Update ARIA label every 15 seconds
                        element.setAttribute('aria-label', ariaText);
                    }
                    
                    // Save the new value in our cache
                    previousValues[elementCacheKey] = formattedTime;
                }
            });
        } catch (error) {
            console.error('Error in countdown timer:', error);
            clearInterval(countdown);
        }
    }
}

/**
 * Initialize button click tracking for analytics
 */
function initButtonTracking() {
    // First, mark important CTAs with the tracking attribute
    const trackableSelectors = [
        ".btn-primary", 
        ".btn-success", 
        ".cta-button", 
        ".enroll-button",
        ".program-apply-btn",
        ".info-session-btn",
        ".contact-submit",
        "a[href=\"/contact\"]",
        "a[href=\"/pricing\"]",
        "a[href=\"/program\"]"
    ];
    
    // Add data-tracking attribute to all trackable elements
    trackableSelectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(element => {
            if (!element.hasAttribute("data-tracking")) {
                element.setAttribute("data-tracking", "true");
                
                // If the element does not have an ID, assign one based on text content
                if (!element.id) {
                    const buttonText = element.textContent.trim().toLowerCase().replace(/[^a-z0-9]/g, "-");
                    element.id = `btn-${buttonText}-${Math.floor(Math.random() * 1000)}`;
                }
            }
        });
    });
    
    // Track all buttons with data-tracking attribute
    const trackableButtons = document.querySelectorAll("[data-tracking=\"true\"]");
    console.log(`Found ${trackableButtons.length} trackable buttons for analytics`);
    
    trackableButtons.forEach(button => {
        button.addEventListener("click", function(e) {
            // Get button data attributes
            const buttonId = this.id || "unknown-button";
            const buttonText = this.textContent.trim() || "";
            const pagePath = window.location.pathname;
            
            console.log(`Tracking button click: ${buttonId} (${buttonText}) on ${pagePath}`);
            
            // Make API request to track click
            fetch("/api/track-click", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    button_id: buttonId,
                    button_text: buttonText,
                    page_path: pagePath
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(data => {
                console.log("Button click tracked successfully", data);
            })
            .catch(error => {
                console.error("Error tracking button click:", error);
            });
        });
    });
}

/**
 * Ensure video autoplay with sound works across browsers
 */
function initVideoAutoplay() {
    console.log('Initializing video autoplay');
    const introVideo = document.getElementById('intro-video');
    if (!introVideo) {
        console.log('No video element found with id "intro-video"');
        return;
    }
    
    console.log('Video element found:', introVideo);
    
    // Define force play function
    function forcePlay() {
        console.log('Force playing video');
        
        // Ensure proper settings for autoplay
        introVideo.muted = true;
        introVideo.defaultMuted = true;
        introVideo.setAttribute('muted', '');
        introVideo.setAttribute('playsinline', '');
        introVideo.setAttribute('autoplay', '');
        
        // Try playing with promise handling
        const playPromise = introVideo.play();
        if (playPromise !== undefined) {
            playPromise.then(() => {
                // Autoplay successful
                console.log('Autoplay successful');
                const largePlayButton = document.getElementById('large-play-button');
                if (largePlayButton) {
                    largePlayButton.style.display = 'none';
                }
            }).catch(error => {
                // Autoplay prevented by browser
                console.log('Autoplay failed:', error);
                console.error('Error playing video:', error);
                
                // Make sure the play button is visible
                const largePlayButton = document.getElementById('large-play-button');
                if (largePlayButton) {
                    largePlayButton.style.display = 'flex';
                }
            });
        }
    }
    
    // Load and try to play immediately
    introVideo.load();
    forcePlay();
    
    // Get the control buttons
    const largePlayButton = document.getElementById('large-play-button');
    const playPauseBtn = document.getElementById('play-pause-btn');
    const volumeToggle = document.getElementById('volume-toggle');
    const captionToggle = document.getElementById('caption-toggle');
    
    // Set up play button overlay
    if (largePlayButton) {
        largePlayButton.addEventListener('click', function() {
            forcePlay();
            largePlayButton.style.display = 'none';
        });
    }
    
    // Set up play/pause button
    if (playPauseBtn) {
        playPauseBtn.addEventListener('click', function() {
            if (introVideo.paused) {
                introVideo.play().then(() => {
                    playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
                    playPauseBtn.setAttribute('aria-label', 'Pause video');
                    if (largePlayButton) largePlayButton.style.display = 'none';
                }).catch(e => console.error('Error playing video:', e));
            } else {
                introVideo.pause();
                playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
                playPauseBtn.setAttribute('aria-label', 'Play video');
                if (largePlayButton) largePlayButton.style.display = 'flex';
            }
        });
    }
    
    // Set up volume toggle
    if (volumeToggle) {
        volumeToggle.addEventListener('click', function() {
            introVideo.muted = !introVideo.muted;
            volumeToggle.innerHTML = introVideo.muted ? 
                '<i class="fas fa-volume-mute"></i>' : 
                '<i class="fas fa-volume-up"></i>';
            volumeToggle.setAttribute('aria-label', 
                introVideo.muted ? 'Unmute video' : 'Mute video');
        });
    }
    
    // Set up caption toggle
    if (captionToggle && introVideo.textTracks && introVideo.textTracks.length > 0) {
        const track = introVideo.textTracks[0];
        track.mode = 'hidden'; // Start with captions off
        
        captionToggle.addEventListener('click', function() {
            track.mode = (track.mode === 'showing') ? 'hidden' : 'showing';
            captionToggle.innerHTML = track.mode === 'showing' ? 
                '<i class="fas fa-closed-captioning" style="opacity: 1;"></i>' : 
                '<i class="fas fa-closed-captioning"></i>';
            captionToggle.setAttribute('aria-label', 
                track.mode === 'showing' ? 'Hide captions' : 'Show captions');
        });
    }
    
    // Update UI on video events
    introVideo.addEventListener('play', function() {
        if (playPauseBtn) {
            playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
            playPauseBtn.setAttribute('aria-label', 'Pause video');
        }
        if (largePlayButton) largePlayButton.style.display = 'none';
    });
    
    introVideo.addEventListener('pause', function() {
        if (playPauseBtn) {
            playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
            playPauseBtn.setAttribute('aria-label', 'Play video');
        }
        if (largePlayButton) largePlayButton.style.display = 'flex';
    });
    
    // Handle responsive behavior
    function updateVideoObjectFit() {
        // Use cover for all screen sizes for consistent appearance
        introVideo.style.objectFit = 'cover';
    }
    
    // Apply the object-fit setting
    updateVideoObjectFit();
    
    // Update on window resize and orientation change
    window.addEventListener('resize', updateVideoObjectFit);
    window.addEventListener('orientationchange', updateVideoObjectFit);
    
    // Try playing on any user interaction for browsers with strict autoplay policies
    document.addEventListener('click', function userInteractionHandler() {
        if (introVideo.paused) {
            forcePlay();
        }
        // Remove this handler after first use
        document.removeEventListener('click', userInteractionHandler);
    }, { once: true });
    
    // For iOS compatibility specifically
    document.addEventListener('touchend', function iosTouchHandler() {
        if (introVideo.paused) {
            forcePlay();
        }
        document.removeEventListener('touchend', iosTouchHandler);
    }, { once: true });
}
