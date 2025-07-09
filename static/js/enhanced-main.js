/**
 * Enhanced JavaScript utilities for F.A.C.T.S website
 * Includes improved form handling, analytics, and user experience features
 */

// Utility functions
const Utils = {
    // Debounce function for performance
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Format currency
    formatCurrency(cents) {
        return new Intl.NumberFormat('en-AU', {
            style: 'currency',
            currency: 'AUD'
        }).format(cents / 100);
    },

    // Validate email
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    // Validate Australian phone number
    isValidPhone(phone) {
        const cleaned = phone.replace(/\D/g, '');
        return cleaned.length >= 8 && cleaned.length <= 15;
    },

    // Show toast notification
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    },

    // Track user interaction for analytics
    trackEvent(eventName, properties = {}) {
        // Send to analytics endpoint
        fetch('/api/track-click', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.getAttribute('content')
            },
            body: JSON.stringify({
                event: eventName,
                properties: properties,
                timestamp: Date.now(),
                page: window.location.pathname
            })
        }).catch(err => console.warn('Analytics tracking failed:', err));
    }
};

// Enhanced form handling
class FormHandler {
    constructor(formElement) {
        this.form = formElement;
        this.submitButton = formElement.querySelector('button[type="submit"]');
        this.originalButtonText = this.submitButton?.textContent;
        this.init();
    }

    init() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        this.addRealTimeValidation();
        this.addAccessibilityFeatures();
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        if (!this.validateForm()) {
            return false;
        }

        this.setLoading(true);
        
        try {
            const formData = new FormData(this.form);
            const response = await fetch(this.form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.getAttribute('content')
                }
            });

            if (response.ok) {
                this.handleSuccess();
                Utils.trackEvent('form_submit_success', {
                    form_id: this.form.id,
                    form_action: this.form.action
                });
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            this.handleError(error);
            Utils.trackEvent('form_submit_error', {
                form_id: this.form.id,
                error: error.message
            });
        } finally {
            this.setLoading(false);
        }
    }

    validateForm() {
        let isValid = true;
        const inputs = this.form.querySelectorAll('input[required], textarea[required], select[required]');
        
        inputs.forEach(input => {
            const fieldValid = this.validateField(input);
            if (!fieldValid) isValid = false;
        });

        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }

        // Email validation
        if (field.type === 'email' && value && !Utils.isValidEmail(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }

        // Phone validation
        if (field.type === 'tel' && value && !Utils.isValidPhone(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid phone number';
        }

        // Update field appearance
        this.updateFieldValidation(field, isValid, errorMessage);
        return isValid;
    }

    updateFieldValidation(field, isValid, errorMessage) {
        const formGroup = field.closest('.form-group') || field.parentElement;
        const existingError = formGroup.querySelector('.field-error');

        if (existingError) {
            existingError.remove();
        }

        field.classList.toggle('is-invalid', !isValid);
        field.classList.toggle('is-valid', isValid && field.value.trim());

        if (!isValid && errorMessage) {
            const errorElement = document.createElement('div');
            errorElement.className = 'field-error text-danger small mt-1';
            errorElement.textContent = errorMessage;
            formGroup.appendChild(errorElement);
        }
    }

    addRealTimeValidation() {
        const inputs = this.form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', Utils.debounce(() => {
                if (input.classList.contains('is-invalid')) {
                    this.validateField(input);
                }
            }, 300));
        });
    }

    addAccessibilityFeatures() {
        // Add ARIA attributes
        const inputs = this.form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            if (input.hasAttribute('required')) {
                input.setAttribute('aria-required', 'true');
            }
        });
    }

    setLoading(loading) {
        if (!this.submitButton) return;

        this.submitButton.disabled = loading;
        
        if (loading) {
            this.submitButton.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Sending...
            `;
        } else {
            this.submitButton.textContent = this.originalButtonText;
        }
    }

    handleSuccess() {
        Utils.showToast('Your message has been sent successfully!', 'success');
        this.form.reset();
        
        // Remove validation classes
        this.form.querySelectorAll('.is-valid, .is-invalid').forEach(el => {
            el.classList.remove('is-valid', 'is-invalid');
        });
        this.form.querySelectorAll('.field-error').forEach(el => el.remove());
    }

    handleError(error) {
        Utils.showToast('There was an error sending your message. Please try again.', 'error');
        console.error('Form submission error:', error);
    }
}

// Enhanced video player with accessibility
class VideoPlayer {
    constructor(videoElement) {
        this.video = videoElement;
        this.init();
    }

    init() {
        this.addKeyboardControls();
        this.addLoadingState();
        this.addErrorHandling();
        this.trackVideoEvents();
    }

    addKeyboardControls() {
        this.video.addEventListener('keydown', (e) => {
            switch(e.key) {
                case ' ':
                case 'k':
                    e.preventDefault();
                    this.togglePlayPause();
                    break;
                case 'm':
                    e.preventDefault();
                    this.toggleMute();
                    break;
                case 'f':
                    e.preventDefault();
                    this.toggleFullscreen();
                    break;
            }
        });
    }

    addLoadingState() {
        this.video.addEventListener('loadstart', () => {
            this.video.classList.add('loading');
        });

        this.video.addEventListener('canplay', () => {
            this.video.classList.remove('loading');
        });
    }

    addErrorHandling() {
        this.video.addEventListener('error', () => {
            const errorOverlay = document.createElement('div');
            errorOverlay.className = 'video-error-overlay';
            errorOverlay.innerHTML = `
                <div class="error-content">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Unable to load video</p>
                    <button onclick="location.reload()" class="btn btn-sm btn-primary">Reload Page</button>
                </div>
            `;
            
            this.video.parentElement.appendChild(errorOverlay);
        });
    }

    trackVideoEvents() {
        this.video.addEventListener('play', () => {
            Utils.trackEvent('video_play', { video_src: this.video.currentSrc });
        });

        this.video.addEventListener('ended', () => {
            Utils.trackEvent('video_complete', { video_src: this.video.currentSrc });
        });
    }

    togglePlayPause() {
        if (this.video.paused) {
            this.video.play();
        } else {
            this.video.pause();
        }
    }

    toggleMute() {
        this.video.muted = !this.video.muted;
    }

    toggleFullscreen() {
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            this.video.requestFullscreen();
        }
    }
}

// Performance optimization for images
function optimizeImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize form handlers
    document.querySelectorAll('form').forEach(form => {
        if (!form.classList.contains('no-enhance')) {
            new FormHandler(form);
        }
    });

    // Initialize video players
    document.querySelectorAll('video').forEach(video => {
        new VideoPlayer(video);
    });

    // Initialize image optimization
    optimizeImages();

    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Track page view
    Utils.trackEvent('page_view', {
        page: window.location.pathname,
        referrer: document.referrer
    });
});

// Export for global use
window.Utils = Utils;
window.FormHandler = FormHandler;
window.VideoPlayer = VideoPlayer;
