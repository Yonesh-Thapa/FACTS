/**
 * Real-time synchronization client for live content updates
 * Connects to SocketIO server for instant content sync
 */

class RealTimeSync {
    constructor() {
        this.socket = null;
        this.isAdmin = false;
        this.connected = false;
        this.retryCount = 0;
        this.maxRetries = 5;
        this.retryDelay = 2000;
        
        this.init();
    }
    
    init() {
        // Initialize SocketIO connection
        this.socket = io({
            transports: ['websocket', 'polling'],
            upgrade: true,
            rememberUpgrade: true
        });
        
        this.setupEventListeners();
        this.startHeartbeat();
    }
    
    setupEventListeners() {
        // Connection events
        this.socket.on('connect', () => {
            console.log('Real-time sync connected');
            this.connected = true;
            this.retryCount = 0;
            this.hideConnectionError();
            
            // Check if we're on admin page and join admin room
            if (window.location.pathname.includes('/admin')) {
                this.joinAdminSession();
            }
        });
        
        this.socket.on('disconnect', (reason) => {
            console.log('Real-time sync disconnected:', reason);
            this.connected = false;
            
            if (reason === 'io server disconnect') {
                // Server initiated disconnect, try to reconnect
                this.attemptReconnect();
            }
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.showConnectionError();
            this.attemptReconnect();
        });
        
        // Content update events
        this.socket.on('live_content_update', (data) => {
            this.handleContentUpdate(data);
        });
        
        this.socket.on('refresh_preview', (data) => {
            this.handlePreviewRefresh(data);
        });
        
        this.socket.on('admin_notification', (data) => {
            if (this.isAdmin) {
                this.showAdminNotification(data.message, data.data);
            }
        });
        
        // Admin-specific events
        this.socket.on('admin_joined', (data) => {
            console.log('Admin joined:', data.admin_username);
        });
        
        this.socket.on('content_sync_response', (data) => {
            this.handleContentSync(data);
        });
        
        this.socket.on('error', (data) => {
            console.error('Socket error:', data.message);
            this.showError(data.message);
        });
    }
    
    joinAdminSession() {
        this.isAdmin = true;
        this.socket.emit('admin_join', {
            timestamp: Date.now()
        });
        console.log('Joined admin session');
    }
    
    handleContentUpdate(data) {
        if (!data.updates || !Array.isArray(data.updates)) {
            return;
        }
        
        console.log('Received content updates:', data.updates.length);
        
        // Apply updates to the current page
        data.updates.forEach(update => {
            this.applyContentUpdate(update);
        });
        
        // Show update notification
        if (data.source === 'admin' && !this.isAdmin) {
            this.showUpdateNotification(`Content updated by ${data.admin_username}`);
        }
    }
    
    applyContentUpdate(update) {
        const key = update.key;
        const value = update.value;
        
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
        
        // Handle navigation menu updates
        if (key.includes('menu') || key.includes('nav')) {
            this.updateNavigation(key, value);
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
    
    updateNavigation(key, value) {
        // Update navigation elements
        const navElements = document.querySelectorAll('nav a, .navbar a, .menu a');
        navElements.forEach(element => {
            if (element.textContent.toLowerCase().includes(key.toLowerCase().replace('nav_', ''))) {
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
    
    handlePreviewRefresh(data) {
        console.log('Preview refresh requested');
        
        // Only refresh if we're not in admin edit mode
        if (!this.isAdmin) {
            window.location.reload();
        }
    }
    
    handleContentSync(data) {
        console.log('Content sync received:', data.content.length, 'items');
        
        // Apply all content updates at once
        if (data.content && Array.isArray(data.content)) {
            data.content.forEach(item => {
                this.applyContentUpdate({
                    key: item.key,
                    value: item.value
                });
            });
        }
    }
    
    // Admin methods
    broadcastContentUpdate(updates) {
        if (!this.isAdmin || !this.connected) {
            return false;
        }
        
        this.socket.emit('content_update', {
            updates: updates,
            timestamp: Date.now()
        });
        
        return true;
    }
    
    requestContentSync() {
        if (!this.connected) {
            return false;
        }
        
        this.socket.emit('request_content_sync', {
            timestamp: Date.now()
        });
        
        return true;
    }
    
    requestPreviewRefresh() {
        if (!this.isAdmin || !this.connected) {
            return false;
        }
        
        this.socket.emit('preview_refresh', {
            timestamp: Date.now()
        });
        
        return true;
    }
    
    // UI Helper methods
    showUpdateNotification(message) {
        this.showNotification(message, 'info', 3000);
    }
    
    showAdminNotification(message, data) {
        this.showNotification(`Admin: ${message}`, 'warning', 5000);
    }
    
    showError(message) {
        this.showNotification(`Error: ${message}`, 'error', 5000);
    }
    
    showConnectionError() {
        this.showNotification('Connection lost. Attempting to reconnect...', 'error', 0);
    }
    
    hideConnectionError() {
        const errorNotifications = document.querySelectorAll('.realtime-notification.error');
        errorNotifications.forEach(notification => {
            if (notification.textContent.includes('Connection lost')) {
                notification.remove();
            }
        });
    }
    
    showNotification(message, type = 'info', duration = 3000) {
        // Remove existing notifications of the same type
        const existingNotifications = document.querySelectorAll(`.realtime-notification.${type}`);
        existingNotifications.forEach(notification => notification.remove());
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `realtime-notification ${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: '500',
            zIndex: '10000',
            maxWidth: '400px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            transform: 'translateX(400px)',
            transition: 'transform 0.3s ease'
        });
        
        // Set colors based on type
        switch (type) {
            case 'success':
                notification.style.backgroundColor = '#d4edda';
                notification.style.color = '#155724';
                notification.style.border = '1px solid #c3e6cb';
                break;
            case 'error':
                notification.style.backgroundColor = '#f8d7da';
                notification.style.color = '#721c24';
                notification.style.border = '1px solid #f5c6cb';
                break;
            case 'warning':
                notification.style.backgroundColor = '#fff3cd';
                notification.style.color = '#856404';
                notification.style.border = '1px solid #ffeaa7';
                break;
            default: // info
                notification.style.backgroundColor = '#d1ecf1';
                notification.style.color = '#0c5460';
                notification.style.border = '1px solid #bee5eb';
        }
        
        // Add to page
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto-remove after duration (if specified)
        if (duration > 0) {
            setTimeout(() => {
                notification.style.transform = 'translateX(400px)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }, duration);
        }
    }
    
    // Connection management
    attemptReconnect() {
        if (this.retryCount >= this.maxRetries) {
            console.log('Max reconnection attempts reached');
            this.showError('Unable to establish connection. Please refresh the page.');
            return;
        }
        
        this.retryCount++;
        console.log(`Reconnection attempt ${this.retryCount}/${this.maxRetries}`);
        
        setTimeout(() => {
            if (!this.connected) {
                this.socket.connect();
            }
        }, this.retryDelay * this.retryCount);
    }
    
    startHeartbeat() {
        // Send periodic heartbeat to maintain connection
        setInterval(() => {
            if (this.connected) {
                this.socket.emit('heartbeat', { timestamp: Date.now() });
            }
        }, 30000); // Every 30 seconds
    }
    
    // Public API methods
    isConnected() {
        return this.connected;
    }
    
    getSocket() {
        return this.socket;
    }
}

// Initialize real-time sync when page loads
let realtimeSync;

document.addEventListener('DOMContentLoaded', () => {
    realtimeSync = new RealTimeSync();
    
    // Make it available globally for admin interface
    window.realtimeSync = realtimeSync;
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealTimeSync;
}