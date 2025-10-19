// Mock data for demonstration
const mockData = {
    stats: {
        distractions: 12,
        drowsiness: 2,
        phoneUsage: 5
    },
    incidents: [
        {
            type: 'phone',
            message: 'Phone Usage Detected',
            time: '2 minutes ago'
        },
        {
            type: 'drowsy',
            message: 'Drowsiness Alert',
            time: '15 minutes ago'
        },
        {
            type: 'distraction',
            message: 'Distraction Detected',
            time: '1 hour ago'
        }
    ],
    systemStatus: {
        camera: true,
        audio: true,
        recording: true
    }
};

// Update stats in real-time (mock)
function updateStats() {
    const stats = document.querySelectorAll('.stat-value');
    stats.forEach(stat => {
        const type = stat.parentElement.querySelector('.stat-label').textContent.toLowerCase();
        if (type.includes('distraction')) {
            stat.textContent = mockData.stats.distractions;
        } else if (type.includes('drowsiness')) {
            stat.textContent = mockData.stats.drowsiness;
        } else if (type.includes('phone')) {
            stat.textContent = mockData.stats.phoneUsage;
        }
    });
}

// Update incidents list
function updateIncidents() {
    const incidentsList = document.querySelector('.incidents-list');
    if (!incidentsList) return;

    incidentsList.innerHTML = mockData.incidents.map(incident => `
        <div class="incident-item">
            <div class="incident-icon ${incident.type}">
                <i class="fas ${getIncidentIcon(incident.type)}"></i>
            </div>
            <div class="incident-details">
                <span class="incident-type">${incident.message}</span>
                <span class="incident-time">${incident.time}</span>
            </div>
        </div>
    `).join('');
}

// Get appropriate icon for incident type
function getIncidentIcon(type) {
    switch (type) {
        case 'phone':
            return 'fa-mobile-alt';
        case 'drowsy':
            return 'fa-bed';
        case 'distraction':
            return 'fa-eye';
        default:
            return 'fa-exclamation-circle';
    }
}

// Update system status
function updateSystemStatus() {
    const statusItems = document.querySelectorAll('.status-item');
    if (!statusItems) return;

    statusItems.forEach(item => {
        const type = item.querySelector('span').textContent.toLowerCase();
        const icon = item.querySelector('i');
        
        if (type.includes('camera')) {
            icon.style.color = mockData.systemStatus.camera ? '#2ecc71' : '#e74c3c';
        } else if (type.includes('audio')) {
            icon.style.color = mockData.systemStatus.audio ? '#2ecc71' : '#e74c3c';
        } else if (type.includes('recording')) {
            icon.style.color = mockData.systemStatus.recording ? '#2ecc71' : '#e74c3c';
        }
    });
}

// Simulate real-time updates
function simulateUpdates() {
    setInterval(() => {
        // Randomly update stats
        mockData.stats.distractions += Math.floor(Math.random() * 2);
        mockData.stats.drowsiness += Math.floor(Math.random() * 2);
        mockData.stats.phoneUsage += Math.floor(Math.random() * 2);

        // Add new incident
        const newIncident = {
            type: ['phone', 'drowsy', 'distraction'][Math.floor(Math.random() * 3)],
            message: 'New Incident Detected',
            time: 'Just now'
        };
        mockData.incidents.unshift(newIncident);
        mockData.incidents.pop();

        // Update UI
        updateStats();
        updateIncidents();
        updateSystemStatus();
    }, 5000); // Update every 5 seconds
}

// Initialize the dashboard
function initDashboard() {
    updateStats();
    updateIncidents();
    updateSystemStatus();
    simulateUpdates();
}

// Handle navigation
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();

    // Handle active navigation
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath.split('/').pop()) {
            link.parentElement.classList.add('active');
        }
    });
}); 