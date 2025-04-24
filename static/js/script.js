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
 * Updated on April 11, 2025 to ensure accurate countdown to April 30, 2025
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
    
    // Set the deadline date to April 30, 2025 - using explicit date format to avoid any confusion
    const earlyBirdDeadline = new Date('2025-04-30T23:59:59');
    const deadline = earlyBirdDeadline.getTime();
    console.log('Deadline set to:', earlyBirdDeadline.toLocaleString());
    
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
                    element.innerHTML = '<span class="countdown-expired">Offer has expired</span>';
                    element.setAttribute('aria-live', 'polite');
                    element.setAttribute('aria-atomic', 'true');
                    element.setAttribute('role', 'status');
                    element.setAttribute('aria-label', 'The Early Bird offer has expired');
                });
                return;
            }
            
            // Calculate days, hours, minutes, and seconds
            const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);
            
            // Format the result with leading zeros for better formatting
            const formattedDays = days.toString();
            const formattedHours = hours.toString().padStart(2, '0');
            const formattedMinutes = minutes.toString().padStart(2, '0');
            const formattedSeconds = seconds.toString().padStart(2, '0');
            
            // Create a more descriptive text for screen readers
            const ariaText = `${days} days, ${hours} hours, ${minutes} minutes, and ${seconds} seconds remaining until the Early Bird offer ends`;
            
            // Update all countdown elements
            validElements.forEach(element => {
                // Check if element exists
                if (!element) return;
                
                // Use fixed-width HTML for smoother updates
                const countdownHTML = `<span class="countdown-timer"><span class="countdown-days">${formattedDays}</span>d <span class="countdown-hours">${formattedHours}</span>h <span class="countdown-minutes">${formattedMinutes}</span>m <span class="countdown-seconds">${formattedSeconds}</span>s</span>`;
                
                // Only update if content is different to reduce DOM operations
                if (element.innerHTML !== countdownHTML) {
                    element.innerHTML = countdownHTML;
                }
                
                // Add ARIA attributes for accessibility
                element.setAttribute('aria-live', 'off'); // Changed to 'off' to prevent excessive announcements
                element.setAttribute('aria-atomic', 'true');
                element.setAttribute('role', 'timer');
                element.setAttribute('aria-label', ariaText);
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
    console.log('Video source:', introVideo.querySelector('source')?.src);
    
    // Add a dynamic timestamp to the video sources to prevent caching issues
    const sources = introVideo.querySelectorAll('source');
    sources.forEach(source => {
        // Get current source and add a timestamp if not already present
        let currentSrc = source.getAttribute('src');
        if (currentSrc.indexOf('?') === -1) {
            // No query parameters, add timestamp
            source.setAttribute('src', `${currentSrc}?v=${Date.now()}`);
        } else if (currentSrc.indexOf('v=') === -1) {
            // Has query parameters but no version, add timestamp
            source.setAttribute('src', `${currentSrc}&v=${Date.now()}`);
        }
    });
    
    // Make sure HTML attributes are set properly
    introVideo.muted = true; // Must start muted to autoplay in most browsers
    introVideo.setAttribute('playsinline', ''); // Required for iOS
    introVideo.setAttribute('muted', ''); // Ensure muted is set as an attribute too
    introVideo.setAttribute('autoplay', ''); // Ensure autoplay is set as an attribute
    
    // Handle mobile device screen sizes
    function updateVideoObjectFit() {
        // In portrait orientation or on small screens, use cover instead of contain
        if (window.innerWidth < 768 || window.innerHeight > window.innerWidth) {
            introVideo.style.objectFit = 'cover';
        } else {
            introVideo.style.objectFit = 'contain';
        }
    }
    
    // Apply initial object-fit setting
    updateVideoObjectFit();
    
    // Update on resize and orientation change
    window.addEventListener('resize', updateVideoObjectFit);
    window.addEventListener('orientationchange', updateVideoObjectFit);
    
    // Get the video controls elements
    const playPauseBtn = document.getElementById('play-pause-btn');
    const volumeToggle = document.getElementById('volume-toggle');
    const videoControls = document.querySelector('.video-controls');
    
    // Create a large play button overlay for better visibility
    const videoContainer = introVideo.closest('.responsive-video-wrapper');
    if (videoContainer) {
        // Remove any existing play button (in case of multiple initializations)
        const existingButton = videoContainer.querySelector('.large-play-button');
        if (existingButton) {
            existingButton.remove();
        }
        
        const largePlayButton = document.createElement('div');
        largePlayButton.className = 'large-play-button';
        largePlayButton.innerHTML = '<i class="fas fa-play"></i>';
        largePlayButton.setAttribute('aria-label', 'Play video');
        largePlayButton.setAttribute('role', 'button');
        largePlayButton.setAttribute('tabindex', '0');
        
        // Add the large play button to the container
        videoContainer.appendChild(largePlayButton);
        
        // Set up click handler for the large play button
        largePlayButton.addEventListener('click', function() {
            // Force reload the video element before playing
            introVideo.load();
            
            setTimeout(() => {
                introVideo.play()
                    .then(() => {
                        console.log('Video playing from large button click');
                        this.style.display = 'none';
                        if (videoControls) videoControls.style.opacity = '0.6';
                    })
                    .catch(e => {
                        console.error('Play failed from button click:', e);
                        // Try once more with a user interaction event
                        document.addEventListener('click', function playVideoOnce() {
                            introVideo.play().catch(err => console.error('Final play attempt failed:', err));
                            document.removeEventListener('click', playVideoOnce);
                        }, { once: true });
                    });
            }, 50);
        });
        
        // Also handle keyboard accessibility
        largePlayButton.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    }
    
    // Add styling for the large play button
    const styleId = 'video-controls-style';
    if (!document.getElementById(styleId)) {
        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            .large-play-button {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background-color: rgba(0, 122, 204, 0.8);
                color: white;
                border: none;
                border-radius: 50%;
                width: 80px;
                height: 80px;
                font-size: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                z-index: 10;
                transition: background-color 0.3s, transform 0.3s;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
            }
            .large-play-button:hover, .large-play-button:focus {
                background-color: rgba(0, 122, 204, 1);
                transform: translate(-50%, -50%) scale(1.1);
                outline: none;
            }
            @media (max-width: 767px) {
                .large-play-button {
                    width: 60px;
                    height: 60px;
                    font-size: 24px;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Force reload the video
    introVideo.load();
    
    // Multiple approaches to ensure autoplay works across browsers
    
    // Approach 1: Standard autoplay
    const playPromise = introVideo.play();
    
    if (playPromise !== undefined) {
        playPromise
            .then(() => {
                console.log('Video playing successfully (standard autoplay)');
                // Hide the large play button if autoplay works
                const largePlayButton = document.querySelector('.large-play-button');
                if (largePlayButton) largePlayButton.style.display = 'none';
            })
            .catch(error => {
                console.warn('Standard autoplay failed:', error);
                
                // Approach 2: Try playing again after a short delay
                setTimeout(() => {
                    introVideo.play()
                        .then(() => {
                            console.log('Video playing successfully (delayed autoplay)');
                            const largePlayButton = document.querySelector('.large-play-button');
                            if (largePlayButton) largePlayButton.style.display = 'none';
                        })
                        .catch(error2 => {
                            console.warn('Delayed autoplay failed:', error2);
                            // Make sure video controls are visible if autoplay fails
                            if (videoControls) videoControls.style.opacity = '1';
                            // Keep the large play button visible
                            const largePlayButton = document.querySelector('.large-play-button');
                            if (largePlayButton) largePlayButton.style.display = 'flex';
                            
                            // Approach 3: Use a browser interaction hack
                            document.addEventListener('mousemove', function playVideoOnce() {
                                if (introVideo.paused) {
                                    introVideo.play().catch(e => console.error('Mouse interaction play failed:', e));
                                }
                                document.removeEventListener('mousemove', playVideoOnce);
                            }, { once: true });
                        });
                }, 500);
            });
    }
    
    // Listen for video play and pause events to update button state
    introVideo.addEventListener('play', function() {
        console.log('Video play event fired');
        const largePlayButton = document.querySelector('.large-play-button');
        if (largePlayButton) largePlayButton.style.display = 'none';
        
        if (playPauseBtn) {
            playPauseBtn.innerHTML = '<i class="fas fa-pause"></i>';
            playPauseBtn.setAttribute('aria-label', 'Pause video');
        }
    });
    
    introVideo.addEventListener('pause', function() {
        console.log('Video pause event fired');
        const largePlayButton = document.querySelector('.large-play-button');
        if (largePlayButton) largePlayButton.style.display = 'flex';
        
        if (playPauseBtn) {
            playPauseBtn.innerHTML = '<i class="fas fa-play"></i>';
            playPauseBtn.setAttribute('aria-label', 'Play video');
        }
    });
    
    // Set up play/pause button functionality if it exists
    if (playPauseBtn) {
        playPauseBtn.addEventListener('click', function() {
            if (introVideo.paused) {
                introVideo.play()
                    .then(() => console.log('Video played from control button'))
                    .catch(e => console.error('Play from control button failed:', e));
            } else {
                introVideo.pause();
            }
        });
    }
    
    // Set up volume toggle functionality if it exists
    if (volumeToggle) {
        volumeToggle.addEventListener('click', function() {
            introVideo.muted = !introVideo.muted;
            if (introVideo.muted) {
                volumeToggle.innerHTML = '<i class="fas fa-volume-mute"></i>';
                volumeToggle.setAttribute('aria-label', 'Unmute video');
            } else {
                volumeToggle.innerHTML = '<i class="fas fa-volume-up"></i>';
                volumeToggle.setAttribute('aria-label', 'Mute video');
            }
        });
    }
    
    // Fallback: Try to start playback after page has been visible for a while
    setTimeout(() => {
        if (introVideo.paused) {
            console.log('Final attempt to autoplay after timeout');
            introVideo.play().catch(e => {
                console.warn('Final autoplay attempt failed:', e);
                // At this point we need user interaction, so make sure the play button is visible
                const largePlayButton = document.querySelector('.large-play-button');
                if (largePlayButton) {
                    largePlayButton.style.display = 'flex';
                    // Add a pulsing animation to draw attention
                    largePlayButton.style.animation = 'pulse 2s infinite';
                    // Add the keyframe animation if not added
                    if (!document.getElementById('pulse-animation')) {
                        const pulseStyle = document.createElement('style');
                        pulseStyle.id = 'pulse-animation';
                        pulseStyle.textContent = `
                            @keyframes pulse {
                                0% { transform: translate(-50%, -50%) scale(1); }
                                50% { transform: translate(-50%, -50%) scale(1.1); }
                                100% { transform: translate(-50%, -50%) scale(1); }
                            }
                        `;
                        document.head.appendChild(pulseStyle);
                    }
                }
            });
        }
    }, 2000);
}
