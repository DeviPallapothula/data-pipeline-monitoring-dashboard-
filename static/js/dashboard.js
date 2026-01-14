/**
 * Dashboard JavaScript
 * 
 * This script handles:
 * - Fetching data from the API
 * - Updating the dashboard UI
 * - Rendering charts
 * - Real-time updates
 */

const API_BASE = '/api';
let updateInterval;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    
    // Check API health
    checkHealth();
    
    // Load initial data
    loadSummary();
    loadPipelines();
    loadCharts();
    
    // Set up auto-refresh (every 30 seconds)
    updateInterval = setInterval(() => {
        loadSummary();
        loadPipelines();
        loadCharts();
    }, 30000);
    
    // Set up modal close
    setupModal();
});

/**
 * Check API health status
 */
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        const statusDot = statusIndicator.querySelector('.status-dot');
        
        if (data.status === 'healthy') {
            statusText.textContent = 'Connected';
            statusDot.classList.remove('disconnected');
        } else {
            statusText.textContent = 'Disconnected';
            statusDot.classList.add('disconnected');
        }
    } catch (error) {
        console.error('Health check failed:', error);
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        const statusDot = statusIndicator.querySelector('.status-dot');
        
        statusText.textContent = 'Disconnected';
        statusDot.classList.add('disconnected');
    }
}

/**
 * Load and display summary metrics
 */
async function loadSummary() {
    try {
        const response = await fetch(`${API_BASE}/metrics/summary?days=7`);
        const data = await response.json();
        
        const summary = data.summary;
        
        document.getElementById('totalExecutions').textContent = summary.total_executions || 0;
        document.getElementById('successRate').textContent = 
            summary.success_rate ? `${summary.success_rate.toFixed(1)}%` : '-';
        document.getElementById('avgDuration').textContent = 
            summary.avg_duration_seconds ? `${formatDuration(summary.avg_duration_seconds)}` : '-';
        document.getElementById('pipelineCount').textContent = summary.pipeline_count || 0;
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

/**
 * Load and display pipeline status table
 */
async function loadPipelines() {
    try {
        const response = await fetch(`${API_BASE}/pipelines?days=7`);
        const data = await response.json();
        
        const tbody = document.getElementById('pipelinesTableBody');
        tbody.innerHTML = '';
        
        if (data.pipelines.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">No pipelines found</td></tr>';
            return;
        }
        
        data.pipelines.forEach(pipeline => {
            const row = document.createElement('tr');
            
            const statusClass = pipeline.latest_status === 'success' ? 'status-success' :
                               pipeline.latest_status === 'failed' ? 'status-failed' : 'status-running';
            
            row.innerHTML = `
                <td><strong>${pipeline.name}</strong></td>
                <td><span class="status-badge ${statusClass}">${pipeline.latest_status}</span></td>
                <td>${pipeline.latest_execution_time ? formatDate(pipeline.latest_execution_time) : 'N/A'}</td>
                <td>${pipeline.total_runs}</td>
                <td>${pipeline.success_rate.toFixed(1)}%</td>
                <td>${pipeline.avg_duration_seconds ? formatDuration(pipeline.avg_duration_seconds) : 'N/A'}</td>
                <td>
                    <button class="btn btn-primary" onclick="showPipelineDetails('${pipeline.name}')">
                        View Details
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading pipelines:', error);
        const tbody = document.getElementById('pipelinesTableBody');
        tbody.innerHTML = '<tr><td colspan="7" class="loading">Error loading pipelines</td></tr>';
    }
}

/**
 * Load and render charts
 */
async function loadCharts() {
    try {
        // Load execution trends (we'll use sample data for now)
        // In a real implementation, you'd fetch this from the API
        renderExecutionTrendChart();
        renderSystemMetricsChart();
    } catch (error) {
        console.error('Error loading charts:', error);
    }
}

/**
 * Render execution trend chart
 */
function renderExecutionTrendChart() {
    // Sample data - in production, fetch from API
    const data = [{
        x: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        y: [45, 52, 48, 61, 55, 50, 58],
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Successful',
        line: { color: '#4caf50' }
    }, {
        x: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        y: [5, 3, 7, 4, 6, 5, 3],
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Failed',
        line: { color: '#f44336' }
    }];
    
    const layout = {
        title: 'Pipeline Executions (Last 7 Days)',
        xaxis: { title: 'Day' },
        yaxis: { title: 'Number of Executions' },
        hovermode: 'closest'
    };
    
    Plotly.newPlot('executionTrendChart', data, layout);
}

/**
 * Render system metrics chart
 */
async function renderSystemMetricsChart() {
    try {
        const response = await fetch(`${API_BASE}/system/metrics?hours=24`);
        const data = await response.json();
        
        const metrics = data.system_metrics;
        
        const chartData = [
            {
                x: metrics.cpu.map(m => m.timestamp),
                y: metrics.cpu.map(m => m.value),
                type: 'scatter',
                mode: 'lines',
                name: 'CPU %',
                line: { color: '#667eea' }
            },
            {
                x: metrics.memory.map(m => m.timestamp),
                y: metrics.memory.map(m => m.value),
                type: 'scatter',
                mode: 'lines',
                name: 'Memory %',
                line: { color: '#4caf50' }
            },
            {
                x: metrics.disk.map(m => m.timestamp),
                y: metrics.disk.map(m => m.value),
                type: 'scatter',
                mode: 'lines',
                name: 'Disk %',
                line: { color: '#ff9800' }
            }
        ];
        
        const layout = {
            title: 'System Resource Usage (Last 24 Hours)',
            xaxis: { title: 'Time' },
            yaxis: { title: 'Usage %' },
            hovermode: 'closest'
        };
        
        Plotly.newPlot('systemMetricsChart', chartData, layout);
    } catch (error) {
        console.error('Error rendering system metrics:', error);
    }
}

/**
 * Show pipeline details in modal
 */
async function showPipelineDetails(pipelineName) {
    const modal = document.getElementById('pipelineModal');
    const modalContent = document.getElementById('modalContent');
    const modalTitle = document.getElementById('modalPipelineName');
    
    modalTitle.textContent = `${pipelineName} - Details`;
    modalContent.innerHTML = '<p>Loading...</p>';
    modal.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE}/pipelines/${pipelineName}/executions?limit=10`);
        const data = await response.json();
        
        let html = '<h3>Recent Executions</h3><table style="width:100%"><thead><tr>';
        html += '<th>Status</th><th>Start Time</th><th>Duration</th><th>Records</th></tr></thead><tbody>';
        
        data.executions.forEach(exec => {
            const statusClass = exec.status === 'success' ? 'status-success' :
                               exec.status === 'failed' ? 'status-failed' : 'status-running';
            html += `<tr>
                <td><span class="status-badge ${statusClass}">${exec.status}</span></td>
                <td>${formatDate(exec.start_time)}</td>
                <td>${exec.duration_seconds ? formatDuration(exec.duration_seconds) : 'N/A'}</td>
                <td>${exec.records_processed || 0}</td>
            </tr>`;
        });
        
        html += '</tbody></table>';
        modalContent.innerHTML = html;
    } catch (error) {
        console.error('Error loading pipeline details:', error);
        modalContent.innerHTML = '<p>Error loading pipeline details</p>';
    }
}

/**
 * Setup modal close functionality
 */
function setupModal() {
    const modal = document.getElementById('pipelineModal');
    const closeBtn = document.querySelector('.close');
    
    closeBtn.onclick = function() {
        modal.style.display = 'none';
    };
    
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    };
}

/**
 * Format duration in seconds to human-readable format
 */
function formatDuration(seconds) {
    if (seconds < 60) {
        return `${seconds.toFixed(1)}s`;
    } else if (seconds < 3600) {
        return `${(seconds / 60).toFixed(1)}m`;
    } else {
        return `${(seconds / 3600).toFixed(1)}h`;
    }
}

/**
 * Format ISO date string to readable format
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}
