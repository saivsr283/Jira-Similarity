// JIRA Similarity Tool - Frontend JavaScript
class JIRASimilarityTool {
    constructor() {
        alert('JIRASimilarityTool constructor called!');
        console.log('🚀 JIRASimilarityTool initialized!');
        this.currentAnalysis = null;
        this.chart = null;
        this.initializeEventListeners();
        this.updateThresholdDisplay();
    }

    initializeEventListeners() {
        console.log('🔧 Setting up event listeners...');
        
        // Update threshold display when slider changes
        document.getElementById('similarityThreshold').addEventListener('input', (e) => {
            this.updateThresholdDisplay();
        });

        // Enter key to analyze ticket
        document.getElementById('ticketKey').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.analyzeTicket();
            }
        });
        
        console.log('✅ Event listeners initialized');
    }

    updateThresholdDisplay() {
        const threshold = document.getElementById('similarityThreshold').value;
        document.getElementById('thresholdValue').textContent = threshold;
    }

    async testConnection() {
        const button = document.querySelector('button[onclick="testConnection()"]');
        const originalText = button.innerHTML;
        
        try {
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing...';
            button.disabled = true;

            const response = await fetch('/api/v1/test');
            const data = await response.json();

            if (data.success) {
                this.showAlert('Connection successful!', 'success');
                document.getElementById('connectionStatus').textContent = 'Connected';
                document.getElementById('currentMode').textContent = data.mode || 'Production';
            } else {
                this.showAlert('Connection failed: ' + data.message, 'danger');
                document.getElementById('connectionStatus').textContent = 'Failed';
            }
        } catch (error) {
            this.showAlert('Connection error: ' + error.message, 'danger');
            document.getElementById('connectionStatus').textContent = 'Error';
        } finally {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }

    async analyzeTicket() {
        alert('Button clicked! analyzeTicket function called!');
        console.log('🔍 analyzeTicket function called!');
        
        // Check if elements exist
        const ticketKeyElement = document.getElementById('ticketKey');
        const loadingSpinnerElement = document.getElementById('loadingSpinner');
        const resultsSectionElement = document.getElementById('resultsSection');
        
        if (!ticketKeyElement) {
            console.error('❌ ticketKey element not found!');
            this.showAlert('Error: Ticket input field not found', 'danger');
            return;
        }
        
        if (!loadingSpinnerElement) {
            console.error('❌ loadingSpinner element not found!');
        }
        
        if (!resultsSectionElement) {
            console.error('❌ resultsSection element not found!');
        }
        
        const ticketKey = ticketKeyElement.value.trim();
        console.log('📋 Ticket key:', ticketKey);
        
        if (!ticketKey) {
            this.showAlert('Please enter a ticket key', 'warning');
            return;
        }

        const similarityThreshold = parseFloat(document.getElementById('similarityThreshold').value);
        const maxResults = parseInt(document.getElementById('maxResults').value);

        // Show loading spinner with better messaging
        if (loadingSpinnerElement) {
            loadingSpinnerElement.style.display = 'block';
        }
        if (resultsSectionElement) {
            resultsSectionElement.style.display = 'none';
        }
        
        // Update loading message
        const loadingMessage = document.querySelector('#loadingSpinner p');
        if (loadingMessage) {
            loadingMessage.innerHTML = `
                <i class="fas fa-search"></i> Fetching ticket data...<br>
                <small class="text-muted">Analyzing ${ticketKey} and finding similar issues...</small>
            `;
        }

        try {
            const response = await fetch('/api/v1/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ticketKey: ticketKey,
                    similarityThreshold: similarityThreshold,
                    maxResults: maxResults
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentAnalysis = data;
                this.displayResults(data);
                this.showAlert('Analysis completed successfully!', 'success');
            } else {
                this.showAlert(`Analysis failed: ${data.error}`, 'danger');
                // Show detailed error information
                this.showDetailedError(data);
            }
        } catch (error) {
            this.showAlert('Analysis error: ' + error.message, 'danger');
        } finally {
            document.getElementById('loadingSpinner').style.display = 'none';
        }
    }

    displayResults(data) {
        document.getElementById('resultsSection').style.display = 'block';

        // Display reference ticket
        this.displayReferenceTicket(data.referenceTicket);

        // Display summary metrics
        this.displaySummaryMetrics(data);

        // Display similarity chart
        this.displaySimilarityChart(data.similarTickets);

        // Display similar tickets table
        this.displaySimilarTicketsTable(data.similarTickets);

        // Display fix recommendations
        this.displayFixRecommendations(data.fixRecommendations);
    }

    displayReferenceTicket(ticket) {
        const container = document.getElementById('referenceTicketInfo');
        
        const statusClass = this.getStatusClass(ticket.status);
        const priorityClass = this.getPriorityClass(ticket.priority);

        container.innerHTML = `
            <div class="row">
                <div class="col-md-8">
                    <h5 class="mb-3">${ticket.key}: ${ticket.summary}</h5>
                    <p class="text-muted mb-3">${ticket.description}</p>
                    <div class="row">
                        <div class="col-md-6">
                            <strong>Type:</strong> ${ticket.issueType}<br>
                            <strong>Priority:</strong> <span class="badge ${priorityClass}">${ticket.priority}</span><br>
                            <strong>Status:</strong> <span class="badge ${statusClass}">${ticket.status}</span>
                        </div>
                        <div class="col-md-6">
                            <strong>Assignee:</strong> ${ticket.assignee || 'Unassigned'}<br>
                            <strong>Reporter:</strong> ${ticket.reporter}<br>
                            <strong>Created:</strong> ${new Date(ticket.created).toLocaleDateString()}
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h6>Components</h6>
                            ${ticket.components.map(comp => `<span class="badge bg-secondary me-1">${comp}</span>`).join('')}
                            <hr>
                            <h6>Labels</h6>
                            ${ticket.labels.map(label => `<span class="badge bg-info me-1">${label}</span>`).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    displaySummaryMetrics(data) {
        const tickets = data.similarTickets;
        const totalTickets = tickets.length;
        const avgSimilarity = totalTickets > 0 ? 
            (tickets.reduce((sum, t) => sum + t.similarity, 0) / totalTickets * 100).toFixed(1) : 0;
        const resolvedCount = tickets.filter(t => t.status === 'Resolved').length;
        const highSimilarity = tickets.filter(t => t.similarity >= 0.7).length;

        document.getElementById('totalTickets').textContent = totalTickets;
        document.getElementById('avgSimilarity').textContent = avgSimilarity + '%';
        document.getElementById('resolvedCount').textContent = resolvedCount;
        document.getElementById('highSimilarity').textContent = highSimilarity;
    }

    displaySimilarityChart(tickets) {
        const ctx = document.getElementById('similarityChart').getContext('2d');
        
        if (this.chart) {
            this.chart.destroy();
        }

        const similarityRanges = {
            '0.8-1.0': tickets.filter(t => t.similarity >= 0.8).length,
            '0.6-0.8': tickets.filter(t => t.similarity >= 0.6 && t.similarity < 0.8).length,
            '0.4-0.6': tickets.filter(t => t.similarity >= 0.4 && t.similarity < 0.6).length,
            '0.2-0.4': tickets.filter(t => t.similarity >= 0.2 && t.similarity < 0.4).length,
            '0.0-0.2': tickets.filter(t => t.similarity < 0.2).length
        };

        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(similarityRanges),
                datasets: [{
                    label: 'Number of Tickets',
                    data: Object.values(similarityRanges),
                    backgroundColor: [
                        '#dc3545',
                        '#fd7e14',
                        '#ffc107',
                        '#20c997',
                        '#6c757d'
                    ],
                    borderColor: [
                        '#dc3545',
                        '#fd7e14',
                        '#ffc107',
                        '#20c997',
                        '#6c757d'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    displaySimilarTicketsTable(tickets) {
        const tbody = document.querySelector('#similarTicketsTable tbody');
        
        tbody.innerHTML = tickets.map(ticket => {
            const statusClass = this.getStatusClass(ticket.status);
            const priorityClass = this.getPriorityClass(ticket.priority);
            const similarityClass = this.getSimilarityClass(ticket.similarity);

            return `
                <tr>
                    <td>
                        <strong>${ticket.key}</strong><br>
                        <small class="text-muted">${new Date(ticket.created).toLocaleDateString()}</small>
                    </td>
                    <td>${ticket.summary}</td>
                    <td><span class="badge ${statusClass}">${ticket.status}</span></td>
                    <td>
                        <div class="similarity-score ${similarityClass}">${(ticket.similarity * 100).toFixed(1)}%</div>
                        <div class="progress mt-1">
                            <div class="progress-bar" style="width: ${ticket.similarity * 100}%"></div>
                        </div>
                    </td>
                    <td><span class="badge ${priorityClass}">${ticket.priority}</span></td>
                    <td>${ticket.assignee || 'Unassigned'}</td>
                </tr>
            `;
        }).join('');
    }

    displayFixRecommendations(recommendations) {
        const container = document.getElementById('fixRecommendations');
        
        if (!recommendations || recommendations.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> No specific fix recommendations available for this ticket type.
                </div>
            `;
            return;
        }

        container.innerHTML = recommendations.map((rec, index) => {
            const cardClass = rec.type === 'success' ? 'recommendation-card' : 
                             rec.type === 'warning' ? 'warning-card' : 'info-card';
            
            return `
                <div class="card ${cardClass} mb-3">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="fas fa-lightbulb"></i> Recommendation ${index + 1}
                        </h6>
                        <p class="card-text">${rec.description}</p>
                        ${rec.steps ? `
                            <h6>Steps:</h6>
                            <ol>
                                ${rec.steps.map(step => `<li>${step}</li>`).join('')}
                            </ol>
                        ` : ''}
                        ${rec.examples ? `
                            <h6>Examples:</h6>
                            <ul>
                                ${rec.examples.map(example => `<li>${example}</li>`).join('')}
                            </ul>
                        ` : ''}
                        <small class="text-muted">
                            <i class="fas fa-chart-line"></i> 
                            Based on ${rec.confidence}% confidence from similar resolved tickets
                        </small>
                    </div>
                </div>
            `;
        }).join('');
    }

    getStatusClass(status) {
        const statusMap = {
            'Open': 'bg-warning',
            'In Progress': 'bg-info',
            'Resolved': 'bg-success',
            'Closed': 'bg-secondary',
            'Reopened': 'bg-danger'
        };
        return statusMap[status] || 'bg-secondary';
    }

    getPriorityClass(priority) {
        const priorityMap = {
            'Highest': 'bg-danger',
            'High': 'bg-warning',
            'Medium': 'bg-info',
            'Low': 'bg-success',
            'Lowest': 'bg-secondary'
        };
        return priorityMap[priority] || 'bg-secondary';
    }

    getSimilarityClass(similarity) {
        if (similarity >= 0.8) return 'text-danger';
        if (similarity >= 0.6) return 'text-warning';
        if (similarity >= 0.4) return 'text-info';
        return 'text-success';
    }

    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.querySelector('.main-content').insertBefore(alertDiv, document.querySelector('.main-content').firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    showDetailedError(data) {
        const errorContainer = document.createElement('div');
        errorContainer.className = 'alert alert-danger';
        errorContainer.innerHTML = `
            <h6><i class="fas fa-exclamation-triangle"></i> Analysis Error Details</h6>
            <p><strong>Error:</strong> ${data.error}</p>
            <p><strong>Ticket:</strong> ${data.ticketKey || 'Unknown'}</p>
            <p><strong>Analysis Time:</strong> ${data.analysisTime || 'Unknown'}ms</p>
            <hr>
            <h6>Troubleshooting Steps:</h6>
            <ol>
                <li>Check if the ticket key is correct</li>
                <li>Verify JIRA credentials in the sidebar</li>
                <li>Test connection using the "Test Connection" button</li>
                <li>Ensure you have access to the ticket</li>
            </ol>
            <button class="btn btn-outline-danger btn-sm" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i> Dismiss
            </button>
        `;
        
        document.querySelector('.main-content').insertBefore(errorContainer, document.querySelector('.main-content').firstChild);
    }

    async exportResults(format) {
        if (!this.currentAnalysis) {
            this.showAlert('No analysis results to export', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/v1/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    analysis: this.currentAnalysis,
                    format: format
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `jira-analysis-${this.currentAnalysis.referenceTicket.key}-${format}.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showAlert(`Results exported as ${format.toUpperCase()}`, 'success');
            } else {
                this.showAlert('Export failed', 'danger');
            }
        } catch (error) {
            this.showAlert('Export error: ' + error.message, 'danger');
        }
    }
}

// Initialize the tool when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.jiraTool = new JIRASimilarityTool();
});

// Global functions for onclick handlers
function testConnection() {
    window.jiraTool.testConnection();
}

function analyzeTicket() {
    window.jiraTool.analyzeTicket();
}

function exportResults(format) {
    window.jiraTool.exportResults(format);
} 