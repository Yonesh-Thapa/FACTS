// Script to force cache clearing and remove any logo elements
document.addEventListener('DOMContentLoaded', function() {
    console.log("Cache clearing script running...");
    
    // Only force one refresh to avoid reload loops
    const cacheParam = 'cache_buster';
    const urlParams = new URLSearchParams(window.location.search);
    
    if (!urlParams.has(cacheParam)) {
        console.log("First load - adding cache buster and refreshing");
        const cacheBuster = Date.now();
        const separator = window.location.href.includes('?') ? '&' : '?';
        // Store a flag in sessionStorage to prevent infinite refresh loop
        sessionStorage.setItem('cache_cleared', 'true');
        window.location.href = window.location.href + separator + cacheParam + '=' + cacheBuster;
        return; // Stop further execution
    }
    
    console.log("Cache busted load - processing page");
    
    // Aggressively find and remove any logo elements
    function removeLogoElements() {
        console.log("Removing potential logo elements");
        
        // List of selectors that might contain logos
        const logoSelectors = [
            'img[src*="logo"]',
            'img[alt*="logo"]',
            '.logo',
            '.navbar-logo',
            '.brand-logo',
            '.facts-logo',
            '.footer-logo',
            '.site-logo',
            'a.navbar-brand img',
        ];
        
        // Combined selector
        const combinedSelector = logoSelectors.join(', ');
        const possibleLogos = document.querySelectorAll(combinedSelector);
        
        console.log(`Found ${possibleLogos.length} potential logo elements`);
        
        possibleLogos.forEach(function(element) {
            console.log("Removing element:", element);
            element.style.display = 'none';
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        });
    }
    
    // Force refresh all images with cache busters
    function refreshImages() {
        console.log("Refreshing all images");
        const images = document.querySelectorAll('img');
        
        for(let i = 0; i < images.length; i++) {
            let src = images[i].src;
            if (!src.includes(cacheParam)) {
                const imgCacheBuster = Date.now() + i; // Ensure unique value
                const separator = src.includes('?') ? '&' : '?';
                console.log(`Refreshing image: ${src}`);
                images[i].src = src + separator + cacheParam + '=' + imgCacheBuster;
            }
        }
    }
    
    // Run our cleanup immediately and then again after a delay to catch any dynamic content
    removeLogoElements();
    refreshImages();
    
    // Run again after a short delay to catch any dynamically loaded content
    setTimeout(function() {
        removeLogoElements();
        refreshImages();
    }, 500);
    
    // And one more time after the page is fully loaded
    window.addEventListener('load', function() {
        removeLogoElements();
        refreshImages();
    });
});