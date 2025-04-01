
let revenueChart = null;
document.addEventListener("DOMContentLoaded", function() {
    // Initialize Chart - with memory management
    const initChart = () => {
        const chartEl = document.querySelector('.revenue-chart');
        if (!chartEl) return;

        // Destroy previous chart instance if exists
        if (revenueChart) {
            revenueChart.destroy();
        }

        const dates = chartEl.dataset.dates.split(',');
        const amounts = chartEl.dataset.amounts.split(',').map(Number);

        revenueChart = new Chart(chartEl, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    data: amounts,
                    borderColor: '#4361ee',
                    backgroundColor: 'rgba(67, 97, 238, 0.05)',
                    tension: 0.4,
                    borderWidth: 2,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 1000 // Reduce animation duration
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => '$' + ctx.parsed.y.toFixed(2)
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    };

    // In your existing initStockBars function
    const initStockBars = () => {
        document.querySelectorAll(".progress-bar").forEach(bar => {
            const stock = parseFloat(bar.dataset.stock);
            const threshold = parseFloat(bar.dataset.threshold);
            const percentage = Math.min(100, (stock / threshold) * 100);
            
            bar.style.width = `${percentage}%`;
            
            // Color coding
            bar.classList.remove('critical', 'low', 'healthy');
            if (percentage < 25) {
                bar.classList.add('critical');
            } else if (percentage < 50) {
                bar.classList.add('low');
            } else {
                bar.classList.add('healthy');
            }
        });
    };

    // Initialize components
    initChart();
    initStockBars();

    // Clean up on page navigation
    window.addEventListener('beforeunload', () => {
        if (revenueChart) {
            revenueChart.destroy();
        }
    });
});
