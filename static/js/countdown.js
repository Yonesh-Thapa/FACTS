/**
 * Countdown Timer - Stable and consistent implementation
 * This specialized JavaScript ensures the countdown display never flickers or shifts
 */

class CountdownTimer {
  constructor(options) {
    // Default settings
    this.settings = {
      deadline: new Date('2025-04-30T23:59:59'),
      updateInterval: 1000,
      onExpired: null,
      countdownIds: ['countdown-timer', 'homepage-offer-timer', 'program-countdown-timer', 'pricing-countdown-timer']
    };

    // Override with custom options
    if (options) {
      Object.keys(options).forEach(key => {
        this.settings[key] = options[key];
      });
    }

    // Store elements and state
    this.elements = [];
    this.interval = null;
    this.isExpired = false;
    
    // Initialize
    this.initialize();
  }

  // Set up the countdown
  initialize() {
    console.log('Initializing stable countdown timer...');
    
    // Find all valid countdown elements
    this.settings.countdownIds.forEach(id => {
      const element = document.getElementById(id);
      if (element) {
        this.elements.push(element);
        
        // Set initial HTML structure for stable layout
        element.innerHTML = this.createCountdownHTML('000', '00', '00', '00');
      }
    });
    
    console.log(`Found ${this.elements.length} countdown elements`);
    
    // If no valid elements found, exit
    if (this.elements.length === 0) {
      console.log('No countdown elements found');
      return;
    }
    
    // Update once immediately
    this.update();
    
    // Then update regularly
    this.interval = setInterval(() => this.update(), this.settings.updateInterval);
  }
  
  // Create consistent HTML structure
  createCountdownHTML(days, hours, minutes, seconds) {
    return `
      <div class="countdown-display">
        <div class="countdown-unit">
          <span class="countdown-number">${days}</span>
          <span class="countdown-label">days</span>
        </div>
        <span class="countdown-separator">:</span>
        <div class="countdown-unit">
          <span class="countdown-number">${hours}</span>
          <span class="countdown-label">hours</span>
        </div>
        <span class="countdown-separator">:</span>
        <div class="countdown-unit">
          <span class="countdown-number">${minutes}</span>
          <span class="countdown-label">mins</span>
        </div>
        <span class="countdown-separator">:</span>
        <div class="countdown-unit">
          <span class="countdown-number">${seconds}</span>
          <span class="countdown-label">secs</span>
        </div>
      </div>
    `;
  }
  
  // Create expired message HTML
  createExpiredHTML() {
    return '<div class="countdown-expired">Offer has expired</div>';
  }
  
  // Update all countdown displays
  update() {
    try {
      // Get current time and calculate remaining time
      const now = new Date().getTime();
      const timeRemaining = this.settings.deadline.getTime() - now;
      
      // Check if countdown has expired
      if (timeRemaining <= 0) {
        if (!this.isExpired) {
          console.log('Countdown expired');
          this.isExpired = true;
          
          // Update all elements with expired message
          this.elements.forEach(element => {
            element.innerHTML = this.createExpiredHTML();
          });
          
          // Clear interval to stop updates
          clearInterval(this.interval);
          
          // Call onExpired callback if provided
          if (typeof this.settings.onExpired === 'function') {
            this.settings.onExpired();
          }
        }
        return;
      }
      
      // Calculate time units
      const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
      const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);
      
      // Format with padding
      const daysStr = days.toString().padStart(3, '0');
      const hoursStr = hours.toString().padStart(2, '0');
      const minutesStr = minutes.toString().padStart(2, '0');
      const secondsStr = seconds.toString().padStart(2, '0');
      
      // Update all elements with new values
      this.elements.forEach(element => {
        element.innerHTML = this.createCountdownHTML(daysStr, hoursStr, minutesStr, secondsStr);
      });
    } catch (error) {
      console.error('Error updating countdown:', error);
      clearInterval(this.interval);
    }
  }
  
  // Stop the countdown
  stop() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
  }
}

// Initialize countdown when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  // Create countdown instance with April 30, 2025 deadline
  const countdown = new CountdownTimer({
    deadline: new Date('2025-04-30T23:59:59'),
    onExpired: function() {
      console.log('Countdown has expired, callback executed');
    }
  });
});