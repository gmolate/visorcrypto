document.addEventListener('DOMContentLoaded', function() {
    const graphButtons = document.querySelectorAll('.graph-btn');
    const chartContainer = document.getElementById('chart-container');
    const closeChartBtn = document.getElementById('close-chart-btn');
    const ctx = document.getElementById('crypto-chart').getContext('2d');
    let myChart;

    graphButtons.forEach(button => {
        button.addEventListener('click', function() {
            const currency = this.dataset.currency;
            fetch(`/api/historical_data/${currency}`)
                .then(response => response.json())
                .then(data => {
                    if (myChart) {
                        myChart.destroy();
                    }
                    myChart = new Chart(ctx, {
                        type: 'line',
                        data: data,
                        options: {
                            scales: {
                                x: {
                                    ticks: {
                                        callback: function(value, index, values) {
                                            return new Date(data.labels[index]).toLocaleDateString();
                                        }
                                    }
                                }
                            }
                        }
                    });
                    chartContainer.style.display = 'block';
                })
                .catch(error => console.error('Error fetching historical data:', error));
        });
    });

    closeChartBtn.addEventListener('click', function() {
        chartContainer.style.display = 'none';
    });
});
