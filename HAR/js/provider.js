// Patient Activity Chart
const ctx = document.getElementById('patientActivityChart').getContext('2d');
const patientActivityChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Average Activity Level',
            data: [6, 7, 5, 8, 6, 4, 5],
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 10,
                ticks: {
                    stepSize: 2
                }
            }
        }
    }
});

// Search Functionality
const searchInput = document.querySelector('.search-box input');
searchInput.addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    // Implement search functionality here
    console.log('Searching for:', searchTerm);
});

// Notification System
const notifications = document.querySelector('.notifications');
let notificationCount = 3;

notifications.addEventListener('click', function() {
    // Show notification panel
    showNotificationPanel();
});

function showNotificationPanel() {
    // Create notification panel if it doesn't exist
    let panel = document.querySelector('.notification-panel');
    if (!panel) {
        panel = document.createElement('div');
        panel.className = 'notification-panel';
        panel.innerHTML = `
            <div class="notification-header">
                <h3>Notifications</h3>
                <button class="close-notifications"><i class="fas fa-times"></i></button>
            </div>
            <div class="notification-list">
                <div class="notification-item">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div class="notification-content">
                        <h4>Critical Alert</h4>
                        <p>Patient #12345 - Fall Detected</p>
                    </div>
                </div>
                <div class="notification-item">
                    <i class="fas fa-exclamation-circle"></i>
                    <div class="notification-content">
                        <h4>Warning</h4>
                        <p>Patient #12346 - Irregular Heart Rate</p>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(panel);
    }

    // Toggle panel visibility
    panel.classList.toggle('show');
}

// Close notification panel when clicking outside
document.addEventListener('click', function(e) {
    const panel = document.querySelector('.notification-panel');
    const notifications = document.querySelector('.notifications');
    
    if (panel && !panel.contains(e.target) && !notifications.contains(e.target)) {
        panel.classList.remove('show');
    }
});

// Handle alert actions
document.querySelectorAll('.btn-action').forEach(button => {
    button.addEventListener('click', function(e) {
        const action = e.target.textContent;
        const alertItem = e.target.closest('.alert-item');
        const patientId = alertItem.querySelector('h4').textContent.split(' - ')[0];
        
        if (action === 'View Details') {
            showPatientDetails(patientId);
        } else if (action === 'Contact Patient') {
            showContactOptions(patientId);
        }
    });
});

function showPatientDetails(patientId) {
    // Implement patient details view
    console.log('Showing details for:', patientId);
}

function showContactOptions(patientId) {
    // Implement contact options
    console.log('Showing contact options for:', patientId);
}

// Real-time updates simulation
function updatePatientStats() {
    const stats = {
        totalPatients: Math.floor(Math.random() * 5) + 22,
        highRisk: Math.floor(Math.random() * 3) + 4,
        activeAlerts: Math.floor(Math.random() * 5) + 8
    };

    document.querySelector('.stat:nth-child(1) .stat-value').textContent = stats.totalPatients;
    document.querySelector('.stat:nth-child(2) .stat-value').textContent = stats.highRisk;
    document.querySelector('.stat:nth-child(3) .stat-value').textContent = stats.activeAlerts;
}

// Update stats every 30 seconds
setInterval(updatePatientStats, 30000);

// WebSocket connection for real-time updates
function initializeWebSocket() {
    const ws = new WebSocket('ws://your-websocket-server');
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
    
    ws.onclose = function() {
        console.log('WebSocket connection closed');
        // Attempt to reconnect after 5 seconds
        setTimeout(initializeWebSocket, 5000);
    };
}

function handleWebSocketMessage(data) {
    switch(data.type) {
        case 'alert':
            addNewAlert(data);
            break;
        case 'patient_update':
            addPatientUpdate(data);
            break;
        case 'stats_update':
            updatePatientStats(data);
            break;
    }
}

function addNewAlert(alertData) {
    const alertsList = document.querySelector('.alerts-list');
    const alertHTML = `
        <div class="alert-item ${alertData.priority}">
            <div class="alert-header">
                <i class="fas ${alertData.priority === 'critical' ? 'fa-exclamation-triangle' : 'fa-exclamation-circle'}"></i>
                <span class="alert-priority">${alertData.priority}</span>
            </div>
            <div class="alert-content">
                <h4>${alertData.patientId} - ${alertData.title}</h4>
                <p>${alertData.message}</p>
            </div>
            <div class="alert-actions">
                <button class="btn-action">View Details</button>
                <button class="btn-action">Contact Patient</button>
            </div>
        </div>
    `;
    
    alertsList.insertAdjacentHTML('afterbegin', alertHTML);
    
    // Update notification badge
    notificationCount++;
    document.querySelector('.notification-badge').textContent = notificationCount;
}

function addPatientUpdate(updateData) {
    const updatesList = document.querySelector('.updates-list');
    const updateHTML = `
        <div class="update-item">
            <div class="update-header">
                <img src="${updateData.avatar}" alt="Patient" class="patient-avatar">
                <div class="update-info">
                    <h4>${updateData.name}</h4>
                    <span class="update-time">${updateData.time}</span>
                </div>
            </div>
            <p>${updateData.message}</p>
            <div class="update-metrics">
                ${updateData.metrics.map(metric => `
                    <span><i class="fas ${metric.icon}"></i> ${metric.value}</span>
                `).join('')}
            </div>
        </div>
    `;
    
    updatesList.insertAdjacentHTML('afterbegin', updateHTML);
    
    // Remove oldest update if there are more than 5
    if (updatesList.children.length > 5) {
        updatesList.removeChild(updatesList.lastChild);
    }
}

// Initialize WebSocket connection
initializeWebSocket(); 