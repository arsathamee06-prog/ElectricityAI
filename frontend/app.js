/**
 * Electricity Demand Forecasting Dashboard - JavaScript
 * Handles API interactions, chart rendering, and UI updates
 */

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Global state
let charts = {};
let currentForecastData = null;
let modelsData = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    loadDashboard();
});

/**
 * Initialize application
 */
function initializeApp() {
    console.log('Initializing Electricity AI Dashboard...');
    updateSystemStatus();
    setInterval(updateSystemStatus, 30000); // Update every 30 seconds
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            switchSection(link.dataset.section);
        });
    });

    // Dashboard controls
    document.getElementById('predictBtn').addEventListener('click', generateForecast);
    document.getElementById('refreshBtn').addEventListener('click', loadDashboard);

    // Logs controls
    document.getElementById('clearLogsBtn').addEventListener('click', clearLogs);
    document.getElementById('downloadLogsBtn').addEventListener('click', downloadLogs);
}

/**
 * Switch between sections
 */
function switchSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Show selected section
    document.getElementById(sectionId).classList.add('active');

    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');

    // Load section-specific data
    if (sectionId === 'models') {
        loadModelsComparison();
    } else if (sectionId === 'logs') {
        loadLogs();
    } else if (sectionId === 'insights') {
        loadInsights();
    }
}

/**
 * Update system status
 */
async function updateSystemStatus() {
    try {
        const response = await axios.get(`${API_BASE_URL}/status`);
        const status = response.data;

        // Update status indicator
        const statusIndicator = document.getElementById('statusIndicator');
        const statusDot = statusIndicator.querySelector('.status-dot');

        if (status.status === 'ready') {
            statusDot.classList.add('active');
            statusIndicator.innerHTML = '<span class="status-dot active"></span><span>Connected</span>';
        } else {
            statusDot.classList.remove('active');
            statusIndicator.innerHTML = `<span class="status-dot"></span><span>${status.status}</span>`;
        }

        // Update metrics
        document.getElementById('totalPredictions').textContent = status.total_predictions;
        if (status.last_prediction) {
            const lastTime = new Date(status.last_prediction.timestamp).toLocaleTimeString();
            document.getElementById('lastUpdate').textContent = lastTime;
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

/**
 * Load dashboard data
 */
async function loadDashboard() {
    try {
        // Load best model info
        const bestModelResponse = await axios.get(`${API_BASE_URL}/models/best`);
        const bestModel = bestModelResponse.data;
        document.getElementById('bestModel').textContent = bestModel.best_model.toUpperCase();

        // Load historical data
        await loadHistoricalData();

        // Generate default forecast
        await generateForecast();
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showNotification('Failed to load dashboard', 'error');
    }
}

/**
 * Load historical data and create chart
 */
async function loadHistoricalData() {
    try {
        const response = await axios.get(`${API_BASE_URL}/historical?days=30`);
        const data = response.data;

        // Create historical chart
        createHistoricalChart(data);
    } catch (error) {
        console.error('Error loading historical data:', error);
    }
}

/**
 * Generate forecast
 */
async function generateForecast() {
    try {
        const days = parseInt(document.getElementById('forecastDays').value) || 7;
        const model = document.getElementById('modelSelect').value || 'best';

        // Show loading state
        document.getElementById('predictBtn').disabled = true;
        document.getElementById('predictBtn').textContent = 'Generating...';

        const response = await axios.post(`${API_BASE_URL}/predict`, {
            days_ahead: days,
            model_type: model
        });

        const prediction = response.data;
        currentForecastData = prediction;

        // Create forecast chart
        createForecastChart(prediction);

        // Update UI
        document.getElementById('forecastPeriod').textContent = `${days} days`;

        showNotification(`Forecast generated using ${prediction.model.toUpperCase()}`, 'success');
    } catch (error) {
        console.error('Error generating forecast:', error);
        showNotification('Failed to generate forecast', 'error');
    } finally {
        document.getElementById('predictBtn').disabled = false;
        document.getElementById('predictBtn').textContent = 'Generate Forecast';
    }
}

/**
 * Create forecast chart
 */
function createForecastChart(data) {
    const ctx = document.getElementById('forecastChart').getContext('2d');

    // Destroy existing chart
    if (charts.forecast) {
        charts.forecast.destroy();
    }

    const predictions = data.predictions || [];
    const dates = data.dates || [];

    charts.forecast = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: `${data.model.toUpperCase()} Forecast`,
                    data: predictions,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointBackgroundColor: '#667eea',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Electricity Demand (MW)'
                    }
                }
            }
        }
    });
}

/**
 * Create historical vs predicted chart
 */
function createHistoricalChart(data) {
    const ctx = document.getElementById('historicalChart').getContext('2d');

    // Destroy existing chart
    if (charts.historical) {
        charts.historical.destroy();
    }

    charts.historical = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates || [],
            datasets: [
                {
                    label: 'Actual Demand',
                    data: data.actual || [],
                    borderColor: '#51cf66',
                    backgroundColor: 'rgba(81, 207, 102, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Predicted Demand',
                    data: data.predicted || [],
                    borderColor: '#ff922b',
                    backgroundColor: 'rgba(255, 146, 43, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

/**
 * Load models comparison
 */
async function loadModelsComparison() {
    try {
        const response = await axios.get(`${API_BASE_URL}/models/comparison`);
        const data = response.data;
        modelsData = data;

        // Populate table
        const tableBody = document.getElementById('modelsTableBody');
        tableBody.innerHTML = '';

        for (const [modelName, modelData] of Object.entries(data.comparison)) {
            if (modelData.metrics) {
                const row = document.createElement('tr');
                if (modelData.is_best) {
                    row.classList.add('best-model');
                }

                row.innerHTML = `
                    <td><strong>${modelName.toUpperCase()}</strong></td>
                    <td>${modelData.metrics.rmse?.toFixed(2) || 'N/A'}</td>
                    <td>${modelData.metrics.mae?.toFixed(2) || 'N/A'}</td>
                    <td>${modelData.metrics.mape?.toFixed(2) || 'N/A'}%</td>
                    <td>${modelData.metrics.r2?.toFixed(4) || 'N/A'}</td>
                    <td>${modelData.metrics.directional_accuracy?.toFixed(2) || 'N/A'}%</td>
                    <td>${modelData.is_best ? '⭐ Best' : 'Active'}</td>
                `;
                tableBody.appendChild(row);
            }
        }

        // Create performance chart
        createPerformanceChart(data);
    } catch (error) {
        console.error('Error loading models:', error);
    }
}

/**
 * Create performance comparison chart
 */
function createPerformanceChart(data) {
    const ctx = document.getElementById('performanceChart').getContext('2d');

    // Destroy existing chart
    if (charts.performance) {
        charts.performance.destroy();
    }

    const modelNames = Object.keys(data.comparison);
    const rmseValues = modelNames.map(name => 
        data.comparison[name].metrics?.rmse || 0
    );
    const maeValues = modelNames.map(name => 
        data.comparison[name].metrics?.mae || 0
    );

    charts.performance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: modelNames.map(n => n.toUpperCase()),
            datasets: [
                {
                    label: 'RMSE',
                    data: rmseValues,
                    backgroundColor: '#667eea',
                },
                {
                    label: 'MAE',
                    data: maeValues,
                    backgroundColor: '#764ba2',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Error (Lower is Better)'
                    }
                }
            }
        }
    });
}

/**
 * Load insights
 */
async function loadInsights() {
    try {
        const response = await axios.get(`${API_BASE_URL}/insights`);
        const insights = response.data;

        // Update insights display
        document.getElementById('seasonalPatterns').innerHTML = insights.seasonal_patterns
            ? Object.entries(insights.seasonal_patterns)
                .map(([key, value]) => `<li><strong>${key}:</strong> ${value}</li>`)
                .join('')
            : '<li>No data available</li>';

        document.getElementById('currentTrends').innerHTML = insights.trends
            ? Object.entries(insights.trends)
                .map(([key, value]) => `<li><strong>${key}:</strong> ${value}</li>`)
                .join('')
            : '<li>No data available</li>';

        // Create decomposition chart
        createDecompositionChart();
    } catch (error) {
        console.error('Error loading insights:', error);
    }
}

/**
 * Create decomposition chart
 */
function createDecompositionChart() {
    const ctx = document.getElementById('decompositionChart').getContext('2d');

    // Destroy existing chart
    if (charts.decomposition) {
        charts.decomposition.destroy();
    }

    const days = Array.from({length: 30}, (_, i) => `Day ${i+1}`);
    const trend = Array.from({length: 30}, () => 100 + Math.random() * 20);
    const seasonal = Array.from({length: 30}, (_, i) => 50 + 30 * Math.sin(i / 5));
    const residual = Array.from({length: 30}, () => (Math.random() - 0.5) * 10);

    charts.decomposition = new Chart(ctx, {
        type: 'line',
        data: {
            labels: days,
            datasets: [
                {
                    label: 'Trend',
                    data: trend,
                    borderColor: '#667eea',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Seasonal',
                    data: seasonal,
                    borderColor: '#51cf66',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Residual',
                    data: residual,
                    borderColor: '#ff922b',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

/**
 * Load prediction logs
 */
async function loadLogs() {
    try {
        const response = await axios.get(`${API_BASE_URL}/logs?limit=100`);
        const logs = response.data;

        // Update logs table
        const logsBody = document.getElementById('logsTableBody');
        logsBody.innerHTML = '';

        if (logs.logs.length === 0) {
            logsBody.innerHTML = '<tr><td colspan="4">No logs available</td></tr>';
        } else {
            logs.logs.forEach(log => {
                const row = document.createElement('tr');
                const timestamp = new Date(log.timestamp).toLocaleString();
                row.innerHTML = `
                    <td>${timestamp}</td>
                    <td>${log.model.toUpperCase()}</td>
                    <td>${log.forecast_days}</td>
                    <td>${log.predictions_count}</td>
                `;
                logsBody.appendChild(row);
            });
        }

        // Update system health
        const statusResponse = await axios.get(`${API_BASE_URL}/status`);
        const status = statusResponse.data;

        document.getElementById('apiStatus').className = 'status-badge ' + 
            (status.status === 'ready' ? 'ready' : 'error');
        document.getElementById('apiStatus').textContent = 
            status.status === 'ready' ? '✓ Ready' : '✗ Error';

        document.getElementById('modelsLoadedStatus').className = 'status-badge ' + 
            (status.models_loaded ? 'ready' : 'error');
        document.getElementById('modelsLoadedStatus').textContent = 
            status.models_loaded ? '✓ Loaded' : '✗ Not Loaded';
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

/**
 * Clear logs
 */
async function clearLogs() {
    if (confirm('Are you sure you want to clear all logs?')) {
        try {
            await axios.post(`${API_BASE_URL}/clear-logs`);
            showNotification('Logs cleared', 'success');
            loadLogs();
        } catch (error) {
            console.error('Error clearing logs:', error);
            showNotification('Failed to clear logs', 'error');
        }
    }
}

/**
 * Download logs as CSV
 */
function downloadLogs() {
    try {
        const response = axios.get(`${API_BASE_URL}/logs?limit=1000`);
        response.then(res => {
            const logs = res.data.logs;
            const csv = [
                ['Timestamp', 'Model', 'Forecast Days', 'Predictions Count'],
                ...logs.map(log => [
                    log.timestamp,
                    log.model,
                    log.forecast_days,
                    log.predictions_count
                ])
            ];

            const csvContent = csv.map(row => row.join(',')).join('\n');
            const blob = new Blob([csvContent], {type: 'text/csv'});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `electricity-logs-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            showNotification('Logs downloaded', 'success');
        });
    } catch (error) {
        console.error('Error downloading logs:', error);
        showNotification('Failed to download logs', 'error');
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#51cf66' : type === 'error' ? '#ff6b6b' : '#4dabf7'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

// Add notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
