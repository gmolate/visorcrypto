document.addEventListener('DOMContentLoaded', function() {
    const graphButtons = document.querySelectorAll('.graph-btn');
    const chartContainer = document.getElementById('chart-container');
    const closeChartBtn = document.getElementById('close-chart-btn');
    const configModal = document.getElementById('config-modal');
    const importExportModal = document.getElementById('import-export-modal');
    const modalOverlay = document.getElementById('modal-overlay');
    const ctx = document.getElementById('crypto-chart').getContext('2d');
    let myChart;

    // Función para actualizar datos usando AJAX
    window.refreshData = function() {
        const refreshBtn = document.getElementById('refresh-btn');
        const statusMessage = document.getElementById('status-message');
        
        if (!refreshBtn || !statusMessage) {
            location.reload();
            return;
        }
        
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '🔄 Actualizando...';
        statusMessage.textContent = 'Obteniendo datos de exchanges...';
        
        fetch('/api/refresh_data')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Actualizar el valor total del portafolio
                    const totalValue = document.getElementById('total-value');
                    if (totalValue) {
                        totalValue.textContent = data.total_portfolio_usd_value.toFixed(2);
                    }
                    
                    updateBalanceTables(data.all_balances, data.total_portfolio);
                    statusMessage.textContent = 'Datos actualizados correctamente';
                } else {
                    statusMessage.textContent = 'Error al actualizar datos';
                    console.error('Error:', data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                statusMessage.textContent = 'Error de conexión';
            })
            .finally(() => {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '🔄 ACTUALIZAR BALANCES';
                
                setTimeout(() => {
                    statusMessage.textContent = 'Listo para actualizar';
                }, 3000);
            });
    };

    // Función para mostrar gráfico general del portafolio
    window.showMainChart = function() {
        document.getElementById('chart-title').textContent = 'Distribución del Portafolio';
        
        fetch('/api/refresh_data')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.total_portfolio) {
                    const currencies = Object.keys(data.total_portfolio);
                    const amounts = Object.values(data.total_portfolio);
                    
                    if (myChart) {
                        myChart.destroy();
                    }
                    
                    myChart = new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: currencies,
                            datasets: [{
                                data: amounts,
                                backgroundColor: [
                                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                                ]
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    labels: {
                                        color: 'white'
                                    }
                                }
                            }
                        }
                    });
                    
                    showModal(chartContainer);
                }
            })
            .catch(error => {
                console.error('Error loading portfolio chart:', error);
            });
    };

    // Función para abrir configuración
    window.openConfig = function() {
        showModal(configModal);
    };

    // Función para importar datos
    window.importData = function() {
        document.getElementById('import-export-title').textContent = '📥 Importar Datos';
        showModal(importExportModal);
    };

    // Función para exportar datos
    window.exportData = function() {
        document.getElementById('import-export-title').textContent = '📤 Exportar Datos';
        showModal(importExportModal);
    };

    // Función para manejar importación
    window.handleImport = function() {
        const fileInput = document.getElementById('import-file');
        const file = fileInput.files[0];
        
        if (!file) {
            alert('Por favor selecciona un archivo');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const data = JSON.parse(e.target.result);
                console.log('Datos importados:', data);
                alert('Datos importados correctamente (función en desarrollo)');
                closeModal();
            } catch (error) {
                alert('Error al leer el archivo: ' + error.message);
            }
        };
        reader.readAsText(file);
    };

    // Función para manejar exportación
    window.handleExport = function() {
        const format = document.getElementById('export-format').value;
        
        fetch('/api/refresh_data')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    let exportData;
                    let filename;
                    let mimeType;

                    if (format === 'json') {
                        exportData = JSON.stringify(data, null, 2);
                        filename = 'portfolio_' + new Date().toISOString().split('T')[0] + '.json';
                        mimeType = 'application/json';
                    } else if (format === 'csv') {
                        exportData = convertToCSV(data);
                        filename = 'portfolio_' + new Date().toISOString().split('T')[0] + '.csv';
                        mimeType = 'text/csv';
                    }

                    downloadFile(exportData, filename, mimeType);
                    closeModal();
                }
            })
            .catch(error => {
                console.error('Error exporting data:', error);
                alert('Error al exportar datos');
            });
    };

    // Función para convertir datos a CSV
    function convertToCSV(data) {
        let csv = 'Exchange,Moneda,Cantidad\n';
        
        for (const [exchange, balances] of Object.entries(data.all_balances)) {
            for (const [currency, amount] of Object.entries(balances)) {
                csv += `${exchange},${currency},${amount}\n`;
            }
        }
        
        return csv;
    }

    // Función para descargar archivo
    function downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Función para mostrar modal
    function showModal(modal) {
        modalOverlay.style.display = 'block';
        modal.style.display = 'block';
    }

    // Función para cerrar modal
    function closeModal() {
        modalOverlay.style.display = 'none';
        chartContainer.style.display = 'none';
        configModal.style.display = 'none';
        importExportModal.style.display = 'none';
    }

    // Función para actualizar las tablas sin recargar la página
    function updateBalanceTables(allBalances, totalPortfolio) {
        const balanceTableBody = document.querySelector('.table-container table tbody');
        if (balanceTableBody) {
            balanceTableBody.innerHTML = '';
            
            for (const [exchange, balances] of Object.entries(allBalances)) {
                for (const [currency, amount] of Object.entries(balances)) {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${exchange}</td>
                        <td>${currency}</td>
                        <td>${amount.toFixed(8)}</td>
                        <td><button class="graph-btn" data-exchange="${exchange}" data-currency="${currency}">Ver Gráfico</button></td>
                    `;
                    balanceTableBody.appendChild(row);
                }
            }
            
            attachGraphButtonListeners();
        }
        
        const totalTableBody = document.querySelectorAll('.table-container')[1]?.querySelector('table tbody');
        if (totalTableBody) {
            totalTableBody.innerHTML = '';
            
            for (const [currency, amount] of Object.entries(totalPortfolio)) {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${currency}</td>
                    <td>${amount.toFixed(8)}</td>
                `;
                totalTableBody.appendChild(row);
            }
        }
    }

    // Función para agregar event listeners a los botones de gráfico
    function attachGraphButtonListeners() {
        const graphButtons = document.querySelectorAll('.graph-btn');
        graphButtons.forEach(button => {
            button.addEventListener('click', function() {
                const currency = this.dataset.currency;
                showChart(currency);
            });
        });
    }

    // Función para mostrar gráfico de moneda específica
    function showChart(currency) {
        document.getElementById('chart-title').textContent = `Gráfico de ${currency}`;
        
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
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                labels: {
                                    color: 'white'
                                }
                            }
                        },
                        scales: {
                            x: {
                                ticks: {
                                    color: 'white',
                                    callback: function(value, index, values) {
                                        return new Date(data.labels[index]).toLocaleDateString();
                                    }
                                }
                            },
                            y: {
                                ticks: {
                                    color: 'white'
                                }
                            }
                        }
                    }
                });
                showModal(chartContainer);
            })
            .catch(error => {
                console.error('Error loading chart data:', error);
                alert('Error al cargar datos del gráfico');
            });
    }

    // Event listeners para cerrar modales
    closeChartBtn.addEventListener('click', closeModal);
    document.getElementById('close-config-btn').addEventListener('click', closeModal);
    document.getElementById('close-import-export-btn').addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', closeModal);

    // Inicializar event listeners
    attachGraphButtonListeners();
});
