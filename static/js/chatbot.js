/**
 * Study Assistant Chatbot
 * Interactive AI-powered chatbot for accounting students
 */

document.addEventListener('DOMContentLoaded', function() {
    // Only initialize the chatbot if we're on a page that should have it
    if (!document.querySelector('.chatbot-container')) {
        return;
    }
    
    // Elements
    const chatbotContainer = document.querySelector('.chatbot-container');
    const chatbotTrigger = document.querySelector('.chatbot-trigger');
    const chatbotMessages = document.querySelector('.chatbot-messages');
    const chatbotInput = document.querySelector('.chatbot-input-field');
    const chatbotSendBtn = document.querySelector('.chatbot-send-btn');
    const chatbotMinimizeBtn = document.querySelector('.chatbot-minimize-btn');
    
    // State
    let isChatbotActive = false;
    let isWaitingForResponse = false;
    
    // Initialize with welcome message
    addMessage('Hello! I\'m your AI accounting assistant. How can I help you today? You can ask me about accounting principles, Xero, MYOB, career advice, and more.', 'assistant');
    
    // Toggle chatbot visibility
    function toggleChatbot() {
        isChatbotActive = !isChatbotActive;
        chatbotContainer.classList.toggle('active', isChatbotActive);
        chatbotTrigger.classList.toggle('active', isChatbotActive);
        
        if (isChatbotActive) {
            chatbotInput.focus();
        }
    }
    
    // Add a message to the chat
    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `message-${sender}`);
        
        if (sender === 'error') {
            messageElement.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        } else {
            messageElement.textContent = message;
        }
        
        chatbotMessages.appendChild(messageElement);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
    
    // Add typing indicator
    function addTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.classList.add('message', 'message-typing');
        typingElement.id = 'typing-indicator';
        
        typingElement.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        chatbotMessages.appendChild(typingElement);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
    
    // Remove typing indicator
    function removeTypingIndicator() {
        const typingElement = document.getElementById('typing-indicator');
        if (typingElement) {
            typingElement.remove();
        }
    }
    
    // Send message to API
    function sendMessage() {
        const message = chatbotInput.value.trim();
        
        if (!message || isWaitingForResponse) {
            return;
        }
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        chatbotInput.value = '';
        
        // Set waiting flag
        isWaitingForResponse = true;
        chatbotSendBtn.disabled = true;
        
        // Show typing indicator
        addTypingIndicator();
        
        // Send to API
        fetch('/api/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            removeTypingIndicator();
            
            if (data.success) {
                addMessage(data.content, 'assistant');
            } else {
                addMessage(data.error || 'Sorry, I encountered an error. Please try again later.', 'error');
            }
        })
        .catch(error => {
            removeTypingIndicator();
            addMessage('Connection error. Please check your internet connection and try again.', 'error');
            console.error('Chatbot error:', error);
        })
        .finally(() => {
            isWaitingForResponse = false;
            chatbotSendBtn.disabled = false;
        });
    }
    
    // Event Listeners
    if (chatbotTrigger) {
        chatbotTrigger.addEventListener('click', toggleChatbot);
    }
    
    if (chatbotMinimizeBtn) {
        chatbotMinimizeBtn.addEventListener('click', toggleChatbot);
    }
    
    if (chatbotSendBtn) {
        chatbotSendBtn.addEventListener('click', sendMessage);
    }
    
    if (chatbotInput) {
        // Send on Enter, new line on Shift+Enter
        chatbotInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Auto-resize input field
        chatbotInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight < 100 ? this.scrollHeight : 100) + 'px';
        });
    }
    
    // Handle window resize for mobile view adjustments
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 576) {
            // Mobile adjustments if needed
        } else {
            // Desktop adjustments if needed
        }
    });
});