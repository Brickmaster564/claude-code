/* Meta Ads Dashboard - Client-side interactivity */

// Track chart instances for cleanup on re-render
let spendCplChart = null;
let leadsChart = null;

// Set initial refresh timestamp
document.addEventListener('DOMContentLoaded', () => {
    updateRefreshTimestamp();
});

function updateRefreshTimestamp() {
    const el = document.getElementById('last-refreshed');
    if (el) {
        const now = new Date();
        el.textContent = 'Updated ' + now.toLocaleTimeString();
    }
}

// Navigation helpers
function switchAccount(accountId) {
    const url = new URL(window.location.href);
    url.searchParams.set('account', accountId);
    window.location.href = url.toString();
}

function switchDays(days) {
    const url = new URL(window.location.href);
    url.searchParams.set('days', days);
    window.location.href = url.toString();
}

// Refresh via AJAX
async function refreshData() {
    const btn = document.getElementById('refresh-btn');
    btn.classList.add('loading');

    const isCampaignPage = window.location.pathname.startsWith('/campaign/');
    let apiUrl;

    if (isCampaignPage) {
        const campaignId = window.location.pathname.split('/campaign/')[1];
        apiUrl = `/api/campaign/${campaignId}?account=${CURRENT_ACCOUNT}&days=${CURRENT_DAYS}`;
    } else {
        apiUrl = `/api/data?account=${CURRENT_ACCOUNT}&days=${CURRENT_DAYS}`;
    }

    try {
        const response = await fetch(apiUrl);
        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }

        dashboardData = data;
        // Reload page with fresh data (simpler than DOM diffing for v1)
        window.location.reload();
    } catch (e) {
        alert('Failed to refresh: ' + e.message);
    } finally {
        btn.classList.remove('loading');
    }
}

// Chart rendering
function renderCharts(data) {
    const dailyData = data.daily_data || [];
    if (dailyData.length === 0) return;

    const labels = dailyData.map(d => {
        const date = new Date(d.date_start);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    const spendValues = dailyData.map(d => d.spend || 0);
    const cplValues = dailyData.map(d => d.cpl || null);
    const leadValues = dailyData.map(d => d.leads || 0);

    // Spend + CPL chart
    const spendCtx = document.getElementById('spend-cpl-chart');
    if (spendCtx) {
        if (spendCplChart) spendCplChart.destroy();
        spendCplChart = new Chart(spendCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Spend',
                        data: spendValues,
                        backgroundColor: 'rgba(24, 119, 242, 0.6)',
                        borderColor: 'rgba(24, 119, 242, 1)',
                        borderWidth: 1,
                        yAxisID: 'y',
                        order: 2,
                    },
                    {
                        label: 'CPL',
                        data: cplValues,
                        type: 'line',
                        borderColor: '#DC3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        borderWidth: 2,
                        pointRadius: 4,
                        pointBackgroundColor: '#DC3545',
                        tension: 0.3,
                        yAxisID: 'y1',
                        order: 1,
                        spanGaps: true,
                    }
                ]
            },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'top', labels: { usePointStyle: true, pointStyle: 'circle' } },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                const val = ctx.parsed.y;
                                if (val === null) return null;
                                return ctx.dataset.label + ': £' + val.toFixed(2);
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        position: 'left',
                        title: { display: true, text: 'Spend (£)' },
                        ticks: { callback: v => '£' + v },
                    },
                    y1: {
                        position: 'right',
                        title: { display: true, text: 'CPL (£)' },
                        ticks: { callback: v => '£' + v },
                        grid: { drawOnChartArea: false },
                    }
                }
            }
        });
    }

    // Leads chart
    const leadsCtx = document.getElementById('leads-chart');
    if (leadsCtx) {
        if (leadsChart) leadsChart.destroy();
        leadsChart = new Chart(leadsCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Leads',
                    data: leadValues,
                    backgroundColor: 'rgba(34, 139, 34, 0.6)',
                    borderColor: 'rgba(34, 139, 34, 1)',
                    borderWidth: 1,
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1, precision: 0 },
                        title: { display: true, text: 'Leads' },
                    }
                }
            }
        });
    }
}

// Creative preview toggle
function toggleCreativePreview(row) {
    const preview = row.nextElementSibling;
    if (preview && preview.classList.contains('creative-preview')) {
        const isHidden = preview.style.display === 'none';
        preview.style.display = isHidden ? 'table-row' : 'none';
    }
}
