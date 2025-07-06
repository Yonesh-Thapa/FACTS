/**
 * Future Accountants Website JavaScript
 * Last updated: July 2025
 * Video player functionality is handled by the dedicated MentorVideoPlayer class in videoPlayer.js
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    
    // Initialize all primary functions
    initButtonTracking();
    initCountdownTimer();
    
    // Set current year in footer copyright
    const currentYearSpan = document.getElementById('current-year');
    if (currentYearSpan) {
        currentYearSpan.textContent = new Date().getFullYear();
    }
});

/**
 * Button click tracking for analytics
 */
function initButtonTracking() {
    const trackableButtons = document.querySelectorAll('[data-track-event]');
    console.log(`Found ${trackableButtons.length} trackable buttons for analytics`);
    
    trackableButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const eventName = this.getAttribute('data-track-event');
            const eventData = {
                button_text: this.textContent.trim(),
                page_url: window.location.href,
                timestamp: new Date().toISOString()
            };
            
            // Send tracking data to server
            fetch('/track-button-click', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    event_name: eventName,
                    event_data: eventData
                })
            }).catch(error => {
                console.debug('Analytics tracking failed:', error);
            });
        });
    });
}

/**
 * Countdown timer functionality
 */
function initCountdownTimer() {
    console.log('Initializing countdown timer...');
    
    const countdownElements = document.querySelectorAll('#countdown-timer, .countdown-timer');
    console.log('Found countdown elements:', Array.from(countdownElements));
    
    if (countdownElements.length === 0) {
        console.log('No countdown elements found');
        return;
    }
    
    // Filter for valid elements that exist in DOM
    const validElements = Array.from(countdownElements).filter(el => el && el.parentNode);
    console.log('Valid countdown elements:', validElements.length);
    
    if (validElements.length === 0) {
        console.log('No valid countdown elements found');
        return;
    }
    
    // Set deadline - December 31, 2025 at 11:59:59 PM (configurable via data attribute or default)
    const defaultDeadline = new Date('2025-12-31T23:59:59').getTime();
    console.log('Deadline set to:', new Date(defaultDeadline).toLocaleString());
    
    function updateCountdown() {
        const now = new Date().getTime();
        const timeLeft = defaultDeadline - now;
        
        if (timeLeft > 0) {
            const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
            
            const countdownText = `${days}d ${hours}h ${minutes}m ${seconds}s`;
            
            validElements.forEach(element => {
                if (element && element.parentNode) {
                    element.textContent = countdownText;
                }
            });
        } else {
            validElements.forEach(element => {
                if (element && element.parentNode) {
                    element.textContent = 'Offer Expired';
                    element.classList.add('expired');
                }
            });
        }
    }
    
    // Update immediately and then every second
    updateCountdown();
    setInterval(updateCountdown, 1000);
}

/**
 * Smooth scrolling for anchor links
 */
document.addEventListener('click', function(e) {
    if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

/**
 * Form validation helpers
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^[\+]?[\d\s\-\(\)]+$/;
    return re.test(phone);
}

/**
 * Contact form enhancements
 */
const contactForms = document.querySelectorAll('form[action*="contact"]');
contactForms.forEach(form => {
    form.addEventListener('submit', function(e) {
        let isValid = true;
        const formData = new FormData(form);
        
        // Validate email if present
        const email = formData.get('email');
        if (email && !validateEmail(email)) {
            isValid = false;
            showFormError('Please enter a valid email address');
        }
        
        // Validate phone if present
        const phone = formData.get('phone');
        if (phone && !validatePhone(phone)) {
            isValid = false;
            showFormError('Please enter a valid phone number');
        }
        
        if (!isValid) {
            e.preventDefault();
        }
    });
});

function showFormError(message) {
    // Create or update error message
    let errorDiv = document.querySelector('.form-error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'form-error-message alert alert-danger';
        const form = document.querySelector('form');
        if (form) {
            form.insertBefore(errorDiv, form.firstChild);
        }
    }
    errorDiv.textContent = message;
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}