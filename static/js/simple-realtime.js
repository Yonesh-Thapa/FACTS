/**
 * Simple real-time sync using polling instead of WebSockets
 * More stable and reliable for production use
 */

class SimpleRealTimeSync {
    constructor() {
        this.polling = false;
        this.pollingInterval = null;
        this.lastUpdate = Date.now() / 1000;
        this.pollFrequency = 30000; // Poll every 30 seconds
        this.isAdmin = false;
        
        this.init();
    }
    
    init() {
        // Check if we're on admin page
        if (window.location.pathname.includes('/admin')) {
            this.isAdmin = true;
            this.pollFrequency = 10000; // Poll more frequently for admin
        }
        
        this.startPolling();
        console.log('Simple real-time sync initialized (polling mode)');
    }
    
    startPolling() {
        if (this.polling) return;
        
        this.polling = true;
        this.pollingInterval = setInterval(() => {
            this.pollForUpdates();
        }, this.pollFrequency);
        
        // Do initial poll
        this.pollForUpdates();
    }
    
    stopPolling() {
        this.polling = false;
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }
    
    async pollForUpdates() {
        try {
            const response = await fetch(`/api/realtime/poll?since=${this.lastUpdate}`);
            const result = await response.json();
            
            if (result.success && result.data.changes.length > 0) {
                this.handleContentUpdates(result.data.changes);
                this.lastUpdate = result.data.timestamp;
            }
        } catch (error) {
            console.error('Polling error:', error);
            // Don't show error notifications for polling failures
        }
    }
    
    handleContentUpdates(changes) {
        console.log('Received content updates:', changes.length);
        
        changes.forEach(change => {
            this.applyContentUpdate(change);
        });
        
        if (changes.length > 0 && !this.isAdmin) {
            this.showUpdateNotification(`Content updated (${changes.length} changes)`);
        }
    }
    
    applyContentUpdate(change) {
        const key = change.key;
        const value = change.value;
        
        // Find elements with data attributes matching the content key
        const elements = document.querySelectorAll(`[data-content-key="${key}"]`);
        
        elements.forEach(element => {
            if (element.tagName === 'IMG') {
                element.src = value;
            } else if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.value = value;
            } else {
                element.innerHTML = value;
            }
        });
        
        // Special handling for common content types
        this.applySpecialContentUpdates(key, value);
    }
    
    applySpecialContentUpdates(key, value) {
        // Handle countdown timer updates
        if (key.includes('deadline') || key.includes('countdown')) {
            this.updateCountdownTimer(value);
        }
        
        // Handle pricing updates
        if (key.includes('price') || key.includes('cost')) {
            this.updatePricing(key, value);
        }
        
        // Handle hero section updates
        if (key.includes('hero') || key.includes('banner')) {
            this.updateHeroSection(key, value);
        }
    }
    
    updateCountdownTimer(deadline) {
        // Update countdown timer with new deadline
        window.countdownDeadline = deadline;
        if (window.updateCountdown) {
            window.updateCountdown();
        }
    }
    
    updatePricing(key, value) {
        // Update pricing elements
        const priceElements = document.querySelectorAll('.price, .pricing-amount, [class*="price"]');
        priceElements.forEach(element => {
            if (element.textContent.includes('$') || element.textContent.includes('A$')) {
                element.textContent = value;
            }
        });
    }
    
    updateHeroSection(key, value) {
        // Update hero section content
        const heroElements = document.querySelectorAll('.hero h1, .hero h2, .hero p, .banner h1, .banner h2, .banner p');
        heroElements.forEach(element => {
            if (key.includes('title') && (element.tagName === 'H1' || element.tagName === 'H2')) {
                element.textContent = value;
            } else if (key.includes('subtitle') && element.tagName === 'P') {
                element.textContent = value;
            }
        });
    }
    
    showUpdateNotification(message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'simple-realtime-notification';
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '10px 16px',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: '500',
            zIndex: '10000',
            backgroundColor: '#d1ecf1',
            color: '#0c5460',
            border: '1px solid #bee5eb',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
            transform: 'translateX(400px)',
            transition: 'transform 0.3s ease'
        });
        
        // Add to page
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }, 3000);
    }
    
    // Public API methods
    broadcastContentUpdate(updates) {
        // For admin use - trigger immediate poll after content update
        if (this.isAdmin) {
            setTimeout(() => this.pollForUpdates(), 1000);
        }
        return true;
    }
    
    isConnected() {
        return this.polling;
    }
}

// Initialize simple real-time sync when page loads
let simpleRealtime;

document.addEventListener('DOMContentLoaded', () => {
    simpleRealtime = new SimpleRealTimeSync();
    
    // Make it available globally for admin interface
    window.simpleRealtime = simpleRealtime;
    window.realtimeSync = simpleRealtime; // Compatibility with existing admin code
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SimpleRealTimeSync;
}