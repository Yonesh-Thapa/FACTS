/**
 * F.A.C.T.S - Future Accountant Coaching and Training Services 
 * Main JavaScript - Optimized for performance
 */

// Use a single DOMContentLoaded event listener to improve performance
document.addEventListener('DOMContentLoaded', function() {
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
