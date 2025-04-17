document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const chatMessages = document.getElementById('chat-messages');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    
    let isTypingIndicatorVisible = false;
    
    // Auto-resize textarea as user types
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    });
    
    // Handle form submission
    messageForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = messageInput.value.trim();
        
        if (message) {
            // Add user message to chat
            addMessage('user', message);
            
            // Send message to server
            socket.emit('message', { message });
            
            // Show typing indicator
            showTypingIndicator();
            
            // Clear input and reset height
            messageInput.value = '';
            messageInput.style.height = 'auto';
        }
    });
    
    // Handle Enter key to submit (Shift+Enter for new line)
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            messageForm.dispatchEvent(new Event('submit'));
        }
    });
    
    // Socket event listeners
    socket.on('connect', () => {
        console.log('Connected to server');
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });
    
    socket.on('message', (data) => {
        // Hide typing indicator if it's visible
        hideTypingIndicator();
        
        // Add received message to chat
        addMessage(data.user, data.message);
    });
    
    // Function to add a message to the chat
    function addMessage(role, content) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', role);
        messageElement.innerHTML = content;
        
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to show typing indicator
    function showTypingIndicator() {
        if (!isTypingIndicatorVisible) {
            isTypingIndicatorVisible = true;
            
            const typingIndicator = document.createElement('div');
            typingIndicator.classList.add('typing-indicator');
            typingIndicator.id = 'typing-indicator';
            
            typingIndicator.innerHTML = `
                AI is typing<span></span><span></span><span></span>
            `;
            
            chatMessages.appendChild(typingIndicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    // Function to hide typing indicator
    function hideTypingIndicator() {
        if (isTypingIndicatorVisible) {
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
            isTypingIndicatorVisible = false;
        }
    }
    
    // Show welcome message
    setTimeout(() => {
        addMessage('assistant', 'Please describe your loss and feeling : ');
    }, 500);
});