// JIRA Similarity Tool Demo Application
class JIRASimilarityDemo {
    constructor() {
        this.apiBase = '/api/v1';
        this.currentResults = null;
        this.similarityChart = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateThresholdDisplay();
        this.showDemoInfo();
    }

    setupEventListeners() {
        // Threshold slider
        document.getElementById('threshold').addEventListener('input', (e) => {
            document.getElementById('thresholdValue').textContent = e.target.value;
        });

        // Ticket selection
        document.getElementById('ticketKey').addEventListener('change', (e) => {
            this.analyzeTicket();
        });
    }

    showDemoInfo() {
        console.log('🎮 Demo mode active - using sample data');
        console.log('📋 Available demo tickets: PLAT-39562, PLAT-39560, PLAT-39561, PLAT-39563, PLAT-39564, PLAT-39565');
    }

    async analyzeTicket() {
        const ticketKey = document.getElementById('ticketKey').value;
        const threshold = parseFloat(document.getElementById('threshold').value);
        const maxResults = parseInt(document.getElementById('maxResults').value);

        if (!ticketKey) {
            this.showAlert('Please select a ticket', 'warning');
            return;
        }

        this.showLoading(true);
        this.hideResults();

        try {
            const response = await fetch(`${this.apiBase}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ticketKey: ticketKey,
                    similarityThreshold: threshold,
                    maxResults: maxResults
                })
            });

            const result = await response.json();

            if (result.success) {
                this.currentResults = result;
                this.displayResults(result);
                this.showAlert('Demo analysis completed successfully!', 'success');
            } else {
                this.showAlert(`Demo analysis failed: ${result.error}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`Error: ${error.message}`, 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    displayResults(result) {
        this.displaySummaryMetrics(result.analysisSummary);
        this.displayReferenceTicket(result.referenceTicket);
        this.displaySimilarityChart(result.similarTickets);
        this.displaySimilarTickets(result.similarTickets);
        this.displayFixRecommendations(result.analysisSummary.topFixes);
        this.showResults();
    }

    displaySummaryMetrics(summary) {
        const metricsContainer = document.getElementById('summaryMetrics');
        metricsContainer.innerHTML = `
            <div class="col-md-2">
                <div class="metric-card">
                    <div class="metric-value">${summary.totalSimilar}</div>
                    <div class="metric-label">Total Similar</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="metric-card">
                    <div class="metric-value">${summary.highSimilarity}</div>
                    <div class="metric-label">High Similarity</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="metric-card">
                    <div class="metric-value">${summary.mediumSimilarity}</div>
                    <div class="metric-label">Medium Similarity</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="metric-card">
                    <div class="metric-value">${summary.resolvedCount}</div>
                    <div class="metric-label">Resolved</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="metric-card">
                    <div class="metric-value">${summary.averageSimilarity}</div>
                    <div class="metric-label">Avg Similarity</div>
                </div>
            </div>
            <div class="col-md-2">
                <div class="metric-card">
                    <div class="metric-value">${summary.timeSaved}</div>
                    <div class="metric-label">Time Saved</div>
                </div>
            </div>
        `;
    }

    displayReferenceTicket(ticket) {
        const container = document.getElementById('referenceTicket');
        container.innerHTML = `
            <div class="ticket-details">
                <div class="row">
                    <div class="col-md-6">
                        <h6><strong>Summary:</strong></h6>
                        <p class="text-muted">${ticket.summary}</p>
                        <h6><strong>Description:</strong></h6>
                        <p class="text-muted">${ticket.description || 'No description available'}</p>
                    </div>
                    <div class="col-md-6">
                        <div class="row">
                            <div class="col-6">
                                <h6><strong>Issue Type:</strong></h6>
                                <p class="text-muted">${ticket.issueType}</p>
                            </div>
                            <div class="col-6">
                                <h6><strong>Priority:</strong></h6>
                                <p class="text-muted">${ticket.priority}</p>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-6">
                                <h6><strong>Status:</strong></h6>
                                <p class="text-muted">${ticket.status}</p>
                            </div>
                            <div class="col-6">
                                <h6><strong>Assignee:</strong></h6>
                                <p class="text-muted">${ticket.assignee || 'Unassigned'}</p>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-12">
                                <h6><strong>Components:</strong></h6>
                                <p class="text-muted">${ticket.components.join(', ') || 'None'}</p>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-12">
                                <h6><strong>Labels:</strong></h6>
                                <p class="text-muted">${ticket.labels.join(', ') || 'None'}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    displaySimilarityChart(similarTickets) {
        const ctx = document.getElementById('similarityChart').getContext('2d');
        
        // Destroy existing chart
        if (this.similarityChart) {
            this.similarityChart.destroy();
        }

        const similarityScores = similarTickets.map(t => t.similarityScore);
        const labels = similarTickets.map(t => t.ticket.key);

        this.similarityChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Similarity Score',
                    data: similarityScores,
                    backgroundColor: similarityScores.map(score => {
                        if (score >= 0.7) return '#d62728';
                        if (score >= 0.4) return '#ff7f0e';
                        return '#2ca02c';
                    }),
                    borderColor: similarityScores.map(score => {
                        if (score >= 0.7) return '#d62728';
                        if (score >= 0.4) return '#ff7f0e';
                        return '#2ca02c';
                    }),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(2);
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Similarity: ${context.parsed.y.toFixed(3)}`;
                            }
                        }
                    }
                }
            }
        });
    }

    displaySimilarTickets(similarTickets) {
        const tbody = document.getElementById('similarTicketsBody');
        tbody.innerHTML = '';

        similarTickets.forEach(similar => {
            const ticket = similar.ticket;
            const row = document.createElement('tr');
            
            const similarityClass = similar.similarityScore >= 0.7 ? 'similarity-high' : 
                                  similar.similarityScore >= 0.4 ? 'similarity-medium' : 'similarity-low';

            row.innerHTML = `
                <td><strong>${ticket.key}</strong></td>
                <td>${ticket.summary}</td>
                <td class="${similarityClass}">${similar.similarityScore.toFixed(3)}</td>
                <td>
                    <span class="badge ${this.getStatusBadgeClass(ticket.status)}">
                        ${ticket.status}
                    </span>
                </td>
                <td>${ticket.issueType}</td>
                <td>
                    <span class="badge ${this.getPriorityBadgeClass(ticket.priority)}">
                        ${ticket.priority}
                    </span>
                </td>
            `;

            // Add click handler for ticket details
            row.style.cursor = 'pointer';
            row.addEventListener('click', () => {
                this.showTicketDetails(ticket);
            });

            tbody.appendChild(row);
        });
    }

    displayFixRecommendations(fixes) {
        const container = document.getElementById('fixRecommendations');
        
        if (fixes.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle"></i> No specific fixes available. Consider general best practices.
                </div>
            `;
            return;
        }

        container.innerHTML = fixes.map(fix => `
            <div class="fix-card">
                <i class="bi bi-check-circle"></i> ${fix}
            </div>
        `).join('');
    }

    showTicketDetails(ticket) {
        const modal = `
            <div class="modal fade" id="ticketModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${ticket.key} - ${ticket.summary}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6><strong>Issue Type:</strong></h6>
                                    <p>${ticket.issueType}</p>
                                    <h6><strong>Priority:</strong></h6>
                                    <p>${ticket.priority}</p>
                                    <h6><strong>Status:</strong></h6>
                                    <p>${ticket.status}</p>
                                    <h6><strong>Assignee:</strong></h6>
                                    <p>${ticket.assignee || 'Unassigned'}</p>
                                </div>
                                <div class="col-md-6">
                                    <h6><strong>Components:</strong></h6>
                                    <p>${ticket.components.join(', ') || 'None'}</p>
                                    <h6><strong>Labels:</strong></h6>
                                    <p>${ticket.labels.join(', ') || 'None'}</p>
                                    <h6><strong>Created:</strong></h6>
                                    <p>${new Date(ticket.created).toLocaleDateString()}</p>
                                    <h6><strong>Updated:</strong></h6>
                                    <p>${new Date(ticket.updated).toLocaleDateString()}</p>
                                </div>
                            </div>
                            <h6><strong>Description:</strong></h6>
                            <p>${ticket.description || 'No description available'}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('ticketModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modal);
        
        // Show modal
        const modalElement = document.getElementById('ticketModal');
        const modalInstance = new bootstrap.Modal(modalElement);
        modalInstance.show();

        // Clean up modal after hiding
        modalElement.addEventListener('hidden.bs.modal', () => {
            modalElement.remove();
        });
    }

    getStatusBadgeClass(status) {
        switch (status.toLowerCase()) {
            case 'resolved': return 'bg-success';
            case 'closed': return 'bg-secondary';
            case 'in progress': return 'bg-primary';
            case 'open': return 'bg-warning';
            default: return 'bg-info';
        }
    }

    getPriorityBadgeClass(priority) {
        switch (priority.toLowerCase()) {
            case 'high': return 'bg-danger';
            case 'medium': return 'bg-warning';
            case 'low': return 'bg-success';
            default: return 'bg-info';
        }
    }

    showLoading(show) {
        document.getElementById('loading').style.display = show ? 'block' : 'none';
    }

    showResults() {
        document.getElementById('results').style.display = 'block';
    }

    hideResults() {
        document.getElementById('results').style.display = 'none';
    }

    updateThresholdDisplay() {
        const slider = document.getElementById('threshold');
        const display = document.getElementById('thresholdValue');
        display.textContent = slider.value;
    }

    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.main-container');
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize the demo application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.demo = new JIRASimilarityDemo();
});

// Global functions for HTML onclick handlers
function analyzeTicket() {
    window.demo.analyzeTicket();
}

function selectTicket(ticketKey) {
    document.getElementById('ticketKey').value = ticketKey;
    window.demo.analyzeTicket();
} 