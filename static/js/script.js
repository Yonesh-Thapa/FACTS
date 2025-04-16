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
                });
                return;
            }
            
            // Calculate days, hours, minutes, and seconds
            const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);
            
            // Format with fixed-width elements to prevent layout shifts
            // Each number is wrapped in a digit container with fixed width
            // Remove any whitespace or newlines to prevent layout shifts
            const formattedTime = 
                `<span class="countdown-digit">${days.toString().padStart(3, '0')}</span><span class="countdown-label">d</span><span class="countdown-digit">${hours.toString().padStart(2, '0')}</span><span class="countdown-label">h</span><span class="countdown-digit">${minutes.toString().padStart(2, '0')}</span><span class="countdown-label">m</span><span class="countdown-digit">${seconds.toString().padStart(2, '0')}</span><span class="countdown-label">s</span>`;
            
            // Update all countdown elements
            validElements.forEach(element => {
                element.innerHTML = formattedTime;
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
