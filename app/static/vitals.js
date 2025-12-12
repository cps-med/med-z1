// Vitals Page JavaScript
// Handles chart rendering and view toggling for the vitals page

console.log('Vitals.js loaded successfully');

// Global chart instances
let bpChart = null;
let weightChart = null;
let painChart = null;

/**
 * Get current patient ICN from the page URL
 * @returns {string|null} Patient ICN or null
 */
function getCurrentPatientICN() {
    const path = window.location.pathname;
    const match = path.match(/\/patient\/([^\/]+)\/vitals/);
    return match ? match[1] : null;
}

/**
 * Initialize all charts when page loads
 */
function initializeCharts() {
    console.log('Initializing vitals charts...');

    const patientICN = getCurrentPatientICN();
    if (!patientICN) {
        console.error('No patient ICN found in URL');
        return;
    }

    // Fetch and create Blood Pressure chart
    fetchVitalsForChart(patientICN, 'BLOOD PRESSURE', 50)
        .then(vitals => {
            if (vitals.length > 0) {
                createBPChart(vitals);
            } else {
                showChartEmptyState('chart-bp', 'No Blood Pressure data available');
            }
        })
        .catch(err => {
            console.error('Error loading BP chart:', err);
            showChartError('chart-bp', 'Failed to load Blood Pressure data');
        });

    // Fetch and create Weight chart
    fetchVitalsForChart(patientICN, 'WEIGHT', 50)
        .then(vitals => {
            if (vitals.length > 0) {
                createWeightChart(vitals);
            } else {
                showChartEmptyState('chart-weight', 'No Weight data available');
            }
        })
        .catch(err => {
            console.error('Error loading Weight chart:', err);
            showChartError('chart-weight', 'Failed to load Weight data');
        });

    // Fetch and create Pain Score chart
    fetchVitalsForChart(patientICN, 'PAIN', 50)
        .then(vitals => {
            if (vitals.length > 0) {
                createPainChart(vitals);
            } else {
                showChartEmptyState('chart-pain', 'No Pain data available');
            }
        })
        .catch(err => {
            console.error('Error loading Pain chart:', err);
            showChartError('chart-pain', 'Failed to load Pain data');
        });
}

/**
 * Fetch vital signs data for charting
 * @param {string} icn - Patient ICN
 * @param {string} vitalType - Vital type name (e.g., "BLOOD PRESSURE")
 * @param {number} limit - Number of records to fetch
 * @returns {Promise<Array>} Array of vital sign records
 */
async function fetchVitalsForChart(icn, vitalType, limit = 50) {
    const response = await fetch(`/api/patient/${icn}/vitals?vital_type=${encodeURIComponent(vitalType)}&limit=${limit}`);

    if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
    }

    const data = await response.json();
    // Sort by date ascending (oldest first) for proper chart rendering
    return data.vitals.sort((a, b) => {
        return new Date(a.taken_datetime) - new Date(b.taken_datetime);
    });
}

/**
 * Create Blood Pressure trend chart
 * @param {Array} vitals - Array of BP vital records
 */
function createBPChart(vitals) {
    const ctx = document.getElementById('chart-bp');
    if (!ctx) {
        console.error('Canvas element #chart-bp not found');
        return;
    }

    // Extract dates and BP values
    const dates = vitals.map(v => {
        const date = new Date(v.taken_datetime);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    });

    const systolic = vitals.map(v => v.systolic || null);
    const diastolic = vitals.map(v => v.diastolic || null);

    // Destroy existing chart if it exists
    if (bpChart) {
        bpChart.destroy();
    }

    bpChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Systolic',
                    data: systolic,
                    borderColor: 'rgb(220, 38, 38)',
                    backgroundColor: 'rgba(220, 38, 38, 0.1)',
                    borderWidth: 2,
                    tension: 0.1,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Diastolic',
                    data: diastolic,
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    tension: 0.1,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: 12
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Blood Pressure Trend',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y + ' mmHg';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 40,
                    max: 200,
                    title: {
                        display: true,
                        text: 'mmHg'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });

    console.log('BP chart created successfully');
}

/**
 * Create Weight trend chart
 * @param {Array} vitals - Array of weight vital records
 */
function createWeightChart(vitals) {
    const ctx = document.getElementById('chart-weight');
    if (!ctx) {
        console.error('Canvas element #chart-weight not found');
        return;
    }

    // Extract dates and weight values
    const dates = vitals.map(v => {
        const date = new Date(v.taken_datetime);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    });

    const weights = vitals.map(v => v.numeric_value || null);
    const unit = vitals[0]?.unit_of_measure || 'lb';

    // Destroy existing chart if it exists
    if (weightChart) {
        weightChart.destroy();
    }

    weightChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: `Weight (${unit})`,
                data: weights,
                borderColor: 'rgb(34, 197, 94)',
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                borderWidth: 2,
                tension: 0.1,
                pointRadius: 4,
                pointHoverRadius: 6,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: 12
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Weight Trend',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y;
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: unit
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });

    console.log('Weight chart created successfully');
}

/**
 * Create Pain Score trend chart
 * @param {Array} vitals - Array of pain score vital records
 */
function createPainChart(vitals) {
    const ctx = document.getElementById('chart-pain');
    if (!ctx) {
        console.error('Canvas element #chart-pain not found');
        return;
    }

    // Extract dates and pain scores
    const dates = vitals.map(v => {
        const date = new Date(v.taken_datetime);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    });

    const painScores = vitals.map(v => v.numeric_value || null);

    // Destroy existing chart if it exists
    if (painChart) {
        painChart.destroy();
    }

    painChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Pain Score',
                data: painScores,
                borderColor: 'rgb(249, 115, 22)',
                backgroundColor: 'rgba(249, 115, 22, 0.1)',
                borderWidth: 2,
                tension: 0.1,
                pointRadius: 4,
                pointHoverRadius: 6,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: 12
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Pain Score Trend (0-10 scale)',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += context.parsed.y + ' / 10';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    min: 0,
                    max: 10,
                    ticks: {
                        stepSize: 1
                    },
                    title: {
                        display: true,
                        text: 'Pain Level (0-10)'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });

    console.log('Pain chart created successfully');
}

/**
 * Show empty state message in chart container
 * @param {string} canvasId - Canvas element ID
 * @param {string} message - Message to display
 */
function showChartEmptyState(canvasId, message) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const container = canvas.parentElement;
    container.innerHTML = `
        <div class="chart-empty-state">
            <i class="fa-solid fa-chart-line fa-2x"></i>
            <p>${message}</p>
        </div>
    `;
}

/**
 * Show error message in chart container
 * @param {string} canvasId - Canvas element ID
 * @param {string} message - Error message to display
 */
function showChartError(canvasId, message) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const container = canvas.parentElement;
    container.innerHTML = `
        <div class="chart-error-state">
            <i class="fa-solid fa-triangle-exclamation fa-2x"></i>
            <p>${message}</p>
        </div>
    `;
}

/**
 * Toggle between grid view and charts view
 */
function toggleView() {
    const gridView = document.getElementById('grid-view');
    const chartsView = document.getElementById('charts-view');
    const toggleBtn = document.getElementById('view-toggle-btn');

    if (!gridView || !chartsView || !toggleBtn) {
        console.error('View toggle elements not found');
        return;
    }

    if (gridView.style.display === 'none') {
        // Switch to grid view
        gridView.style.display = 'block';
        chartsView.style.display = 'none';
        toggleBtn.innerHTML = '<i class="fa-solid fa-chart-line"></i> View Charts';
    } else {
        // Switch to charts view
        gridView.style.display = 'none';
        chartsView.style.display = 'block';
        toggleBtn.innerHTML = '<i class="fa-solid fa-table"></i> View Grid';

        // Initialize charts if not already done
        if (!bpChart && !weightChart && !painChart) {
            initializeCharts();
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Vitals page DOM loaded');

    // Attach view toggle handler
    const toggleBtn = document.getElementById('view-toggle-btn');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleView);
        console.log('View toggle button initialized');
    }

    // Don't initialize charts on page load - wait for user to click "View Charts"
    // This improves initial page load performance
});
