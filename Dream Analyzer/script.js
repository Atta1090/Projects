// DOM Elements
const textInputBtn = document.getElementById('text-input-btn');
const voiceInputBtn = document.getElementById('voice-input-btn');
const dreamText = document.getElementById('dream-text');
const analyzeBtn = document.getElementById('analyze-btn');
const chatInput = document.getElementById('chat-input-field');
const sendChatBtn = document.getElementById('send-chat');
const chatMessages = document.getElementById('chat-messages');

// Toggle input methods
textInputBtn.addEventListener('click', () => {
    textInputBtn.classList.add('active');
    voiceInputBtn.classList.remove('active');
    dreamText.focus();
});

voiceInputBtn.addEventListener('click', () => {
    voiceInputBtn.classList.add('active');
    textInputBtn.classList.remove('active');
    startVoiceRecognition();
});

// Voice Recognition Setup
function startVoiceRecognition() {
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onstart = () => {
            dreamText.placeholder = 'Listening...';
            voiceInputBtn.style.backgroundColor = '#ff4444';
        };

        recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0])
                .map(result => result.transcript)
                .join('');
            
            dreamText.value = transcript;
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            voiceInputBtn.style.backgroundColor = '';
        };

        recognition.onend = () => {
            dreamText.placeholder = 'Describe your dream here...';
            voiceInputBtn.style.backgroundColor = '';
        };

        recognition.start();
    } else {
        alert('Speech recognition is not supported in your browser.');
    }
}

// Analyze Dream
analyzeBtn.addEventListener('click', async () => {
    if (!dreamText.value.trim()) {
        alert('Please enter your dream first!');
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';

    try {
        // Simulate API call with setTimeout
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Mock analysis results
        updateResults({
            emotions: ['Joy: 40%', 'Fear: 20%', 'Mystery: 40%'],
            symbols: ['Water', 'Flying', 'Mountains'],
            interpretation: 'Your dream suggests a journey of self-discovery...'
        });
    } catch (error) {
        console.error('Analysis error:', error);
        alert('Failed to analyze dream. Please try again.');
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="fas fa-magic"></i> Analyze Dream';
    }
});

// Update Results
function updateResults(results) {
    // Update emotion chart
    const emotionChart = document.getElementById('emotion-chart');
    emotionChart.innerHTML = `
        <ul class="emotion-list">
            ${results.emotions.map(emotion => `<li>${emotion}</li>`).join('')}
        </ul>
    `;

    // Update symbols
    const symbolsList = document.getElementById('symbols-list');
    symbolsList.innerHTML = `
        <ul class="symbols-list">
            ${results.symbols.map(symbol => `<li>${symbol}</li>`).join('')}
        </ul>
    `;

    // Update interpretation
    const interpretationText = document.getElementById('interpretation-text');
    interpretationText.textContent = results.interpretation;

    // Show results sections
    document.getElementById('analysis-results').style.display = 'block';
}

// Chat functionality
sendChatBtn.addEventListener('click', () => {
    const message = chatInput.value.trim();
    if (!message) return;

    addChatMessage('user', message);
    chatInput.value = '';

    // Simulate AI response
    setTimeout(() => {
        addChatMessage('ai', 'I understand your dream symbols. Would you like me to explain more about the meaning of water in your dream?');
    }, 1000);
});

function addChatMessage(type, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}-message`;
    messageDiv.innerHTML = `
        <div class="message-content">
            <span class="message-icon">
                ${type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>'}
            </span>
            <p>${message}</p>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add some initial styling for chat messages
const style = document.createElement('style');
style.textContent = `
    .chat-message {
        margin: 10px 0;
        padding: 10px;
        border-radius: 8px;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .ai-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    .message-content {
        display: flex;
        align-items: flex-start;
        gap: 10px;
    }
    .message-icon {
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #fff;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
`;
document.head.appendChild(style); 