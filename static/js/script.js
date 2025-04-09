/* 
* F.A.C.T.S - Future Accountant Coaching and Training Services 
* Main JavaScript
*/

// Document Ready Function
document.addEventListener('DOMContentLoaded', function() {
    // Set current year in footer copyright
    document.getElementById('current-year').textContent = new Date().getFullYear();
    
    // Navigation background change on scroll - debounced for performance
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        if (!scrollTimeout) {
            scrollTimeout = setTimeout(function() {
                const navbar = document.querySelector('.navbar');
                if (window.scrollY > 50) {
                    navbar.style.padding = '10px 0';
                    navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
                } else {
                    navbar.style.padding = '15px 0';
                    navbar.style.boxShadow = '0 2px 15px rgba(0, 0, 0, 0.1)';
                }
                scrollTimeout = null;
            }, 10);
        }
    });
    
    // Smooth scrolling for anchor links - optimized with event delegation
    const navbarHeight = document.querySelector('.navbar')?.offsetHeight || 0;
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    document.addEventListener('click', function(e) {
        // Check if the clicked element is an anchor with hash
        const anchor = e.target.closest('a[href^="#"]');
        if (!anchor) return;
        
        // Get the target element
        const targetId = anchor.getAttribute('href');
        
        // Skip if the href is just "#"
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
            e.preventDefault();
            
            // Calculate position with header height and padding
            const offsetTop = targetElement.offsetTop - navbarHeight - 20;
            
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
            
            // If on mobile, collapse the navbar menu
            if (navbarToggler && navbarCollapse && 
                window.getComputedStyle(navbarToggler).display !== 'none' && 
                navbarCollapse.classList.contains('show')) {
                new bootstrap.Collapse(navbarCollapse).toggle();
            }
        }
    });
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(message);
            bsAlert.close();
        }, 5000);
    });
    
    // Contact form validation
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            let valid = true;
            
            // Simple validation for required fields
            const required = contactForm.querySelectorAll('[required]');
            required.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.classList.add('is-invalid');
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            // Email validation
            const email = contactForm.querySelector('#email');
            if (email && email.value.trim()) {
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
});

// Initialize Bootstrap tooltips - only if there are any tooltips on the page
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.forEach(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
});
