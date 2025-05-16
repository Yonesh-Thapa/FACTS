/**
 * Chat Widget JavaScript
 * Handles the functionality of the floating chat widget
 */

document.addEventListener('DOMContentLoaded', function() {
    // Create chat UI elements
    createChatUI();
    
    // Get all chat elements
    const chatBubble = document.querySelector('.chat-bubble');
    const chatContainer = document.querySelector('.chat-container');
    const chatInput = document.querySelector('.chat-input');
    const chatSubmit = document.querySelector('.chat-submit');
    const chatMessages = document.querySelector('.chat-messages');
    const closeBtn = document.querySelector('.close-btn');
    
    // Toggle chat on bubble click
    chatBubble.addEventListener('click', function() {
        toggleChat();
    });
    
    // Close chat on button click
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            toggleChat(false);
        });
    }
    
    // Submit message on button click
    if (chatSubmit) {
        chatSubmit.addEventListener('click', function() {
            sendMessage();
        });
    }
    
    // Submit message on Enter (but allow Shift+Enter for new line)
    if (chatInput) {
        chatInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
            
            // Auto-resize the input
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight < 80) ? this.scrollHeight + 'px' : '80px';
        });
    }
    
    /**
     * Toggle the chat widget open/closed
     * @param {boolean|undefined} forceState - Optional state to force
     */
    function toggleChat(forceState) {
        const isOpen = forceState !== undefined ? forceState : !chatContainer.classList.contains('open');
        
        if (isOpen) {
            chatContainer.classList.add('open');
            chatBubble.classList.add('open');
            chatInput.focus();
        } else {
            chatContainer.classList.remove('open');
            chatBubble.classList.remove('open');
        }
    }
    
    /**
     * Send the user message to the server and handle the response
     */
    function sendMessage() {
        const message = chatInput.value.trim();
        
        if (!message) return;
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        chatInput.value = '';
        chatInput.style.height = 'auto';
        
        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Disable submit button while waiting
        chatSubmit.disabled = true;
        
        // Send to server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            // Add response to chat
            if (data.success) {
                addMessage(data.reply, 'bot');
            } else {
                addMessage("I'm sorry, I couldn't process your request. " + (data.error || "Please try again later."), 'bot');
                console.error("Chat error:", data.error);
            }
        })
        .catch(error => {
            // Remove typing indicator
            if (typingIndicator) {
                typingIndicator.remove();
            }
            
            // Add more helpful error message
            addMessage("I'm having trouble connecting to our service. This may be due to connection issues or high traffic. Please try again shortly.", 'bot');
            console.error("Chat fetch error:", error);
        })
        .finally(() => {
            // Re-enable submit button
            chatSubmit.disabled = false;
        });
    }
    
    /**
     * Add a message to the chat window
     * @param {string} text - The message text
     * @param {string} sender - 'user' or 'bot'
     */
    function addMessage(text, sender) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${sender === 'user' ? 'user-message' : 'bot-message'}`;
        
        // Handle links in bot messages
        if (sender === 'bot') {
            // Simple link detection and conversion to anchors
            text = text.replace(
                /(https?:\/\/[^\s]+)/g, 
                '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
            );
        }
        
        messageEl.innerHTML = text;
        chatMessages.appendChild(messageEl);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    /**
     * Create the chat UI elements and append them to the body
     */
    function createChatUI() {
        // Create chat bubble
        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble';
        bubble.innerHTML = '<i class="fas fa-comments chat-icon"></i><i class="fas fa-times close-icon"></i>';
        
        // Create chat container
        const container = document.createElement('div');
        container.className = 'chat-container';
        container.innerHTML = `
            <div class="chat-header">
                <h3><i class="fas fa-robot"></i> F.A.C.T.S Assistant</h3>
                <button class="close-btn"><i class="fas fa-times"></i></button>
            </div>
            <div class="chat-messages">
                <div class="welcome-message">
                    Ask me anything about F.A.C.T.S courses, pricing, or schedule!
                </div>
            </div>
            <div class="chat-input-container">
                <textarea class="chat-input" placeholder="Ask me anything about F.A.C.T.S courses…" rows="1"></textarea>
                <button class="chat-submit"><i class="fas fa-paper-plane"></i></button>
            </div>
        `;
        
        // Add elements to the body
        document.body.appendChild(bubble);
        document.body.appendChild(container);
    }
});