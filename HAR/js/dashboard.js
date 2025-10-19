// Update date and time
function updateDateTime() {
    const now = new Date();
    const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit' };
    
    document.getElementById('current-date').textContent = now.toLocaleDateString(undefined, dateOptions);
    document.getElementById('current-time').textContent = now.toLocaleTimeString(undefined, timeOptions);
}

// Update every second
setInterval(updateDateTime, 1000);
updateDateTime();

// Activity Chart
const ctx = document.getElementById('activityChart').getContext('2d');
const activityChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
        datasets: [{
            label: 'Activity Level',
            data: [0, 2, 5, 3, 4, 2],
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

// Simulate real-time activity updates
function updateActivityData() {
    const activities = ['Walking', 'Running', 'Sitting', 'Standing', 'Lying'];
    const activityIcons = {
        'Walking': 'fa-walking',
        'Running': 'fa-running',
        'Sitting': 'fa-chair',
        'Standing': 'fa-user',
        'Lying': 'fa-bed'
    };
    
    const randomActivity = activities[Math.floor(Math.random() * activities.length)];
    const confidence = Math.floor(Math.random() * 20) + 80; // Random confidence between 80-100
    
    document.querySelector('.activity-status i').className = `fas ${activityIcons[randomActivity]}`;
    document.querySelector('.activity-info h4').textContent = randomActivity;
    document.querySelector('.activity-info p').textContent = `Confidence: ${confidence}%`;
}

// Update activity every 5 seconds
setInterval(updateActivityData, 5000);

// Simulate real-time health metrics updates
function updateHealthMetrics() {
    const heartRate = Math.floor(Math.random() * 20) + 60; // Random heart rate between 60-80
    const steps = Math.floor(Math.random() * 1000) + 8000; // Random steps between 8000-9000
    const calories = Math.floor(Math.random() * 50) + 300; // Random calories between 300-350
    
    document.querySelector('.metric:nth-child(1) strong').textContent = `${heartRate} BPM`;
    document.querySelector('.metric:nth-child(2) strong').textContent = steps.toLocaleString();
    document.querySelector('.metric:nth-child(3) strong').textContent = calories;
}

// Update health metrics every 10 seconds
setInterval(updateHealthMetrics, 10000);

// Handle sidebar menu active state
document.querySelectorAll('.sidebar-menu a').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelector('.sidebar-menu li.active').classList.remove('active');
        this.parentElement.classList.add('active');
    });
});

// Simulate real-time alerts
function addNewAlert() {
    const alerts = [
        {
            type: 'warning',
            icon: 'fa-exclamation-circle',
            title: 'Low Activity Warning',
            message: 'You\'ve been sedentary for 2 hours',
            time: '2h ago'
        },
        {
            type: 'success',
            icon: 'fa-check-circle',
            title: 'Goal Achieved',
            message: 'Daily step goal reached!',
            time: '1h ago'
        },
        {
            type: 'warning',
            icon: 'fa-exclamation-circle',
            title: 'Heart Rate Alert',
            message: 'Heart rate above normal range',
            time: '30m ago'
        }
    ];
    
    const randomAlert = alerts[Math.floor(Math.random() * alerts.length)];
    const alertsList = document.querySelector('.alerts-list');
    
    // Remove oldest alert if there are more than 5
    if (alertsList.children.length >= 5) {
        alertsList.removeChild(alertsList.lastChild);
    }
    
    const alertHTML = `
        <div class="alert-item">
            <i class="fas ${randomAlert.icon}"></i>
            <div class="alert-content">
                <h4>${randomAlert.title}</h4>
                <p>${randomAlert.message}</p>
            </div>
            <span class="alert-time">${randomAlert.time}</span>
        </div>
    `;
    
    alertsList.insertAdjacentHTML('afterbegin', alertHTML);
}

// Add new alert every 30 seconds
setInterval(addNewAlert, 30000);

// Initialize WebSocket connection for real-time updates
function initializeWebSocket() {
    const ws = new WebSocket('ws://your-websocket-server');
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        // Handle different types of real-time updates
        switch(data.type) {
            case 'activity':
                updateActivityData(data);
                break;
            case 'metrics':
                updateHealthMetrics(data);
                break;
            case 'alert':
                addNewAlert(data);
                break;
        }
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

// Initialize WebSocket connection
initializeWebSocket(); 