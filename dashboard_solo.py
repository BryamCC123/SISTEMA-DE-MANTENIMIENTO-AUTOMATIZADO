# dashboard_web.py - CON TODOS LOS GRÁFICOS POSIBLES
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests
import json
from datetime import datetime, timedelta
import sqlite3
import random

app = FastAPI(title="Dashboard Mantenimiento Predictivo")

# URL de tu API de ML
API_URL = "http://localhost:8000"

# HTML COMPLETO CON TODOS LOS GRÁFICOS
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Mantenimiento Predictivo</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header { 
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { 
            font-size: 2.5em; 
            margin-bottom: 10px;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border-left: 5px solid #3498db;
        }
        .card-full {
            grid-column: 1 / -1;
        }
        .card h3 { 
            color: #2c3e50; 
            margin-bottom: 15px;
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .form-group { margin-bottom: 15px; }
        .form-group label { 
            display: block; 
            margin-bottom: 5px; 
            font-weight: 600;
            color: #34495e;
        }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ecf0f1;
            border-radius: 8px;
            font-size: 16px;
        }
        .btn {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
        }
        .btn:hover { opacity: 0.9; }
        .resultado {
            margin-top: 20px;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.2em;
            font-weight: 600;
        }
        .normal { background: #d5f4e6; color: #27ae60; border-left: 4px solid #28a745; }
        .advertencia { background: #fef5e7; color: #f39c12; border-left: 4px solid #ffc107; }
        .critico { background: #fdeaea; color: #e74c3c; border-left: 4px solid #dc3545; }
        .error { background: #fdeaea; color: #e74c3c; border-left: 4px solid #dc3545; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }
        .stat-label {
            color: #6c757d;
            font-size: 0.9em;
        }
        .status {
            padding: 10px;
            border-radius: 6px;
            margin: 10px 0;
        }
        .online { background: #d4edda; color: #155724; }
        .offline { background: #f8d7da; color: #721c24; }
        .chart-container {
            position: relative;
            height: 300px;
            width: 100%;
            margin-top: 15px;
        }
        .mini-chart {
            height: 120px;
            margin-top: 10px;
        }
        .sensor-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        .gauge {
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .gauge-value {
            font-size: 1.5em;
            font-weight: bold;
            margin: 10px 0;
        }
        .gauge-label {
            color: #6c757d;
            font-size: 0.9em;
        }
        .alert-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .alert-low { background: #28a745; }
        .alert-medium { background: #ffc107; }
        .alert-high { background: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 Dashboard Avanzado - Mantenimiento Predictivo</h1>
            <p>Sistema de Machine Learning con Análisis Visual Completo</p>
        </div>

        <div class="dashboard-grid">
            <!-- Panel de Estado -->
            <div class="card">
                <h3>🔗 Estado del Sistema</h3>
                <div id="conexionStatus" class="status offline">
                    🔄 Verificando conexión...
                </div>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="totalPredicciones">0</div>
                        <div class="stat-label">Total Predicciones</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="modeloAUC">0.00</div>
                        <div class="stat-label">AUC Modelo</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="tiempoPromedio">0s</div>
                        <div class="stat-label">Tiempo Respuesta</div>
                    </div>
                </div>
            </div>

            <!-- Panel de Sensores en Tiempo Real -->
            <div class="card">
                <h3>📊 Sensores en Tiempo Real</h3>
                <div class="sensor-grid">
                    <div class="gauge">
                        <div>🌡️ Vibración</div>
                        <div class="gauge-value" id="vibracionValue">0.0</div>
                        <div class="gauge-label">mm/s</div>
                        <div class="chart-container mini-chart">
                            <canvas id="vibracionChart"></canvas>
                        </div>
                    </div>
                    <div class="gauge">
                        <div>🔥 Temperatura</div>
                        <div class="gauge-value" id="temperaturaValue">0.0</div>
                        <div class="gauge-label">°C</div>
                        <div class="chart-container mini-chart">
                            <canvas id="temperaturaChart"></canvas>
                        </div>
                    </div>
                    <div class="gauge">
                        <div>💨 Presión</div>
                        <div class="gauge-value" id="presionValue">0.0</div>
                        <div class="gauge-label">psi</div>
                        <div class="chart-container mini-chart">
                            <canvas id="presionChart"></canvas>
                        </div>
                    </div>
                    <div class="gauge">
                        <div>⚡ Corriente</div>
                        <div class="gauge-value" id="corrienteValue">0.0</div>
                        <div class="gauge-label">A</div>
                        <div class="chart-container mini-chart">
                            <canvas id="corrienteChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Panel de Predicción -->
            <div class="card card-full">
                <h3>🎯 Realizar Predicción</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                    <div>
                        <form onsubmit="realizarPrediccion(); return false;">
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                                <div class="form-group">
                                    <label>Vibración (mm/s):</label>
                                    <input type="number" step="0.1" id="vibracion" value="3.0" required>
                                </div>
                                <div class="form-group">
                                    <label>Temperatura (°C):</label>
                                    <input type="number" step="0.1" id="temperatura" value="80.0" required>
                                </div>
                                <div class="form-group">
                                    <label>Presión (psi):</label>
                                    <input type="number" step="0.1" id="presion" value="110.0" required>
                                </div>
                                <div class="form-group">
                                    <label>Corriente (A):</label>
                                    <input type="number" step="0.1" id="corriente" value="17.0" required>
                                </div>
                            </div>
                            <button type="submit" class="btn" style="margin-top: 20px;">🔮 Realizar Predicción</button>
                        </form>
                        <div id="resultado" style="display: none; margin-top: 20px;"></div>
                    </div>
                    <div>
                        <div class="chart-container">
                            <canvas id="probabilidadChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Gráfico de Distribución de Alertas -->
            <div class="card">
                <h3>📈 Distribución de Alertas</h3>
                <div class="chart-container">
                    <canvas id="alertasChart"></canvas>
                </div>
            </div>

            <!-- Tendencia de Probabilidades -->
            <div class="card">
                <h3>📊 Tendencia de Fallas</h3>
                <div class="chart-container">
                    <canvas id="tendenciaChart"></canvas>
                </div>
            </div>

            <!-- Historial de Predicciones -->
            <div class="card card-full">
                <h3>📋 Historial de Predicciones</h3>
                <div class="chart-container">
                    <canvas id="historialChart"></canvas>
                </div>
            </div>

            <!-- Análisis de Sensores -->
            <div class="card card-full">
                <h3>🔍 Análisis de Sensores</h3>
                <div class="chart-container">
                    <canvas id="correlacionChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Variables globales para los charts
        let charts = {};
        let historialData = [];
        let sensorData = {
            vibracion: [],
            temperatura: [],
            presion: [],
            corriente: []
        };

        // Inicializar al cargar la página
        document.addEventListener('DOMContentLoaded', function() {
            verificarConexion();
            inicializarGraficos();
            cargarEstadisticas();
            iniciarMonitoreoSensores();
        });

        function inicializarGraficos() {
            // Gráfico de probabilidad
            charts.probabilidad = new Chart(document.getElementById('probabilidadChart'), {
                type: 'doughnut',
                data: {
                    labels: ['Baja', 'Media', 'Alta'],
                    datasets: [{
                        data: [70, 20, 10],
                        backgroundColor: ['#28a745', '#ffc107', '#dc3545']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: 'Distribución de Probabilidad' },
                        legend: { position: 'bottom' }
                    }
                }
            });

            // Gráfico de alertas
            charts.alertas = new Chart(document.getElementById('alertasChart'), {
                type: 'pie',
                data: {
                    labels: ['Normal', 'Advertencia', 'Crítico'],
                    datasets: [{
                        data: [60, 25, 15],
                        backgroundColor: ['#28a745', '#ffc107', '#dc3545']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });

            // Gráfico de tendencia
            charts.tendencia = new Chart(document.getElementById('tendenciaChart'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Probabilidad de Falla',
                        data: [],
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            min: 0,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });

            // Gráfico de historial
            charts.historial = new Chart(document.getElementById('historialChart'), {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Probabilidad de Falla',
                        data: [],
                        backgroundColor: function(context) {
                            const value = context.raw;
                            if (value < 30) return '#28a745';
                            if (value < 70) return '#ffc107';
                            return '#dc3545';
                        }
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });

            // Gráfico de correlación
            charts.correlacion = new Chart(document.getElementById('correlacionChart'), {
                type: 'radar',
                data: {
                    labels: ['Vibración', 'Temperatura', 'Presión', 'Corriente', 'Tiempo Mantenimiento'],
                    datasets: [{
                        label: 'Valores Actuales',
                        data: [3.0, 80.0, 110.0, 17.0, 50],
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        pointBackgroundColor: 'rgba(54, 162, 235, 1)'
                    }, {
                        label: 'Límites Normales',
                        data: [3.5, 85.0, 120.0, 18.0, 70],
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        pointBackgroundColor: 'rgba(255, 99, 132, 1)'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 150
                        }
                    }
                }
            });

            // Gráficos de sensores en tiempo real
            const sensorOptions = {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                plugins: { legend: { display: false } },
                elements: {
                    point: { radius: 0 }
                }
            };

            charts.vibracion = new Chart(document.getElementById('vibracionChart'), {
                type: 'line',
                data: {
                    labels: Array(20).fill(''),
                    datasets: [{
                        data: Array(20).fill(0),
                        borderColor: '#3498db',
                        borderWidth: 2,
                        fill: false
                    }]
                },
                options: sensorOptions
            });

            charts.temperatura = new Chart(document.getElementById('temperaturaChart'), {
                type: 'line',
                data: {
                    labels: Array(20).fill(''),
                    datasets: [{
                        data: Array(20).fill(0),
                        borderColor: '#e74c3c',
                        borderWidth: 2,
                        fill: false
                    }]
                },
                options: sensorOptions
            });

            charts.presion = new Chart(document.getElementById('presionChart'), {
                type: 'line',
                data: {
                    labels: Array(20).fill(''),
                    datasets: [{
                        data: Array(20).fill(0),
                        borderColor: '#9b59b6',
                        borderWidth: 2,
                        fill: false
                    }]
                },
                options: sensorOptions
            });

            charts.corriente = new Chart(document.getElementById('corrienteChart'), {
                type: 'line',
                data: {
                    labels: Array(20).fill(''),
                    datasets: [{
                        data: Array(20).fill(0),
                        borderColor: '#f39c12',
                        borderWidth: 2,
                        fill: false
                    }]
                },
                options: sensorOptions
            });
        }

        function iniciarMonitoreoSensores() {
            // Simular datos de sensores en tiempo real
            setInterval(() => {
                const ahora = new Date();
                const timestamp = ahora.toLocaleTimeString();
                
                // Actualizar valores de sensores con variación aleatoria
                const vibracion = 2.5 + Math.random() * 2;
                const temperatura = 75 + Math.random() * 10;
                const presion = 100 + Math.random() * 30;
                const corriente = 15 + Math.random() * 4;

                document.getElementById('vibracionValue').textContent = vibracion.toFixed(1);
                document.getElementById('temperaturaValue').textContent = temperatura.toFixed(1);
                document.getElementById('presionValue').textContent = presion.toFixed(1);
                document.getElementById('corrienteValue').textContent = corriente.toFixed(1);

                // Actualizar gráficos de sensores
                actualizarSensorChart('vibracion', vibracion);
                actualizarSensorChart('temperatura', temperatura);
                actualizarSensorChart('presion', presion);
                actualizarSensorChart('corriente', corriente);

            }, 2000);
        }

        function actualizarSensorChart(sensor, valor) {
            if (charts[sensor]) {
                const chart = charts[sensor];
                chart.data.datasets[0].data.push(valor);
                if (chart.data.datasets[0].data.length > 20) {
                    chart.data.datasets[0].data.shift();
                }
                chart.update('none');
            }
        }

        async function verificarConexion() {
            try {
                const response = await fetch('/api/verificar-conexion');
                const data = await response.json();
                
                const statusDiv = document.getElementById('conexionStatus');
                if (data.conectado) {
                    statusDiv.className = 'status online';
                    statusDiv.innerHTML = `✅ CONECTADO - API ML en http://localhost:8000`;
                } else {
                    statusDiv.className = 'status offline';
                    statusDiv.innerHTML = `❌ DESCONECTADO - Error: ${data.error}`;
                }
            } catch (error) {
                document.getElementById('conexionStatus').innerHTML = '❌ Error verificando conexión';
            }
        }

        async function realizarPrediccion() {
            const vibracion = document.getElementById('vibracion').value;
            const temperatura = document.getElementById('temperatura').value;
            const presion = document.getElementById('presion').value;
            const corriente = document.getElementById('corriente').value;
            const resultadoDiv = document.getElementById('resultado');

            // Mostrar loading
            resultadoDiv.innerHTML = '<div class="status">🔄 Procesando predicción...</div>';
            resultadoDiv.style.display = 'block';

            try {
                const response = await fetch('/api/predecir', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        vibracion: parseFloat(vibracion),
                        temperatura: parseFloat(temperatura),
                        presion: parseFloat(presion),
                        corriente: parseFloat(corriente),
                        tiempo_desde_mantenimiento: 500
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const resultado = data.resultado;
                    const clase = resultado.nivel_alerta.toLowerCase();
                    const probabilidad = resultado.probabilidad_falla * 100;
                    
                    // Mostrar resultado
                    resultadoDiv.innerHTML = `
                        <div class="resultado ${clase}">
                            <h3>${obtenerIcono(resultado.nivel_alerta)} ${resultado.nivel_alerta}</h3>
                            <p><strong>Probabilidad de falla:</strong> ${probabilidad.toFixed(1)}%</p>
                            <p><strong>Recomendación:</strong> ${resultado.recomendacion}</p>
                            <p><small>Tiempo de respuesta: ${data.tiempo_respuesta.toFixed(3)}s</small></p>
                        </div>
                    `;

                    // Actualizar gráficos con nueva predicción
                    actualizarGraficosPrediccion(probabilidad, resultado.nivel_alerta);
                    
                } else {
                    resultadoDiv.innerHTML = `
                        <div class="resultado error">
                            <h3>❌ Error en la Predicción</h3>
                            <p><strong>Error:</strong> ${data.error}</p>
                        </div>
                    `;
                }
            } catch (error) {
                resultadoDiv.innerHTML = `
                    <div class="resultado error">
                        <h3>❌ Error de Conexión</h3>
                        <p>No se pudo conectar con el servidor</p>
                    </div>
                `;
            }
        }

        function actualizarGraficosPrediccion(probabilidad, nivelAlerta) {
            const ahora = new Date();
            const timestamp = ahora.toLocaleTimeString();
            
            // Actualizar gráfico de probabilidad
            let baja = 0, media = 0, alta = 0;
            if (probabilidad < 30) baja = 100;
            else if (probabilidad < 70) media = 100;
            else alta = 100;
            
            charts.probabilidad.data.datasets[0].data = [baja, media, alta];
            charts.probabilidad.update();

            // Actualizar gráfico de tendencia
            charts.tendencia.data.labels.push(timestamp);
            charts.tendencia.data.datasets[0].data.push(probabilidad);
            
            if (charts.tendencia.data.labels.length > 10) {
                charts.tendencia.data.labels.shift();
                charts.tendencia.data.datasets[0].data.shift();
            }
            charts.tendencia.update();

            // Actualizar gráfico de historial
            charts.historial.data.labels.push(timestamp);
            charts.historial.data.datasets[0].data.push(probabilidad);
            
            if (charts.historial.data.labels.length > 8) {
                charts.historial.data.labels.shift();
                charts.historial.data.datasets[0].data.shift();
            }
            charts.historial.update();

            // Actualizar estadísticas de alertas
            actualizarEstadisticasAlertas(nivelAlerta);
        }

        function actualizarEstadisticasAlertas(nuevaAlerta) {
            // Simular actualización de estadísticas de alertas
            const alertas = { 'NORMAL': 60, 'ADVERTENCIA': 25, 'CRÍTICO': 15 };
            alertas[nuevaAlerta] += 5;
            
            // Normalizar
            const total = Object.values(alertas).reduce((a, b) => a + b, 0);
            Object.keys(alertas).forEach(key => {
                alertas[key] = Math.round((alertas[key] / total) * 100);
            });

            charts.alertas.data.datasets[0].data = [
                alertas['NORMAL'],
                alertas['ADVERTENCIA'], 
                alertas['CRÍTICO']
            ];
            charts.alertas.update();
        }

        function obtenerIcono(nivel) {
            const iconos = {
                'NORMAL': '✅',
                'ADVERTENCIA': '⚠️', 
                'CRÍTICO': '🚨'
            };
            return iconos[nivel] || '🔍';
        }

        async function cargarEstadisticas() {
            try {
                const response = await fetch('/api/estadisticas');
                const stats = await response.json();
                document.getElementById('totalPredicciones').textContent = stats.total_predicciones;
                document.getElementById('tiempoPromedio').textContent = stats.tiempo_respuesta_promedio + 's';
                
                // Cargar AUC del modelo
                const modeloResponse = await fetch('/api/info-modelo');
                const modeloInfo = await modeloResponse.json();
                const auc = modeloInfo.metricas ? modeloInfo.metricas.auc.toFixed(4) : '0.0000';
                document.getElementById('modeloAUC').textContent = auc;
                
            } catch (error) {
                console.log('Error cargando estadísticas');
            }
        }

        // Actualizar cada 30 segundos
        setInterval(() => {
            cargarEstadisticas();
        }, 30000);
    </script>
</body>
</html>
"""

# SISTEMA DE LOGS MEJORADO
class SistemaLogs:
    def __init__(self):
        self.conexion = sqlite3.connect('mantenimiento_logs.db', check_same_thread=False)
        self.crear_tabla()
    
    def crear_tabla(self):
        cursor = self.conexion.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predicciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                vibracion REAL,
                temperatura REAL,
                presion REAL,
                corriente REAL,
                probabilidad_falla REAL,
                nivel_alerta TEXT,
                recomendacion TEXT,
                modelo_utilizado TEXT,
                tiempo_respuesta REAL
            )
        ''')
        self.conexion.commit()
    
    def guardar_prediccion(self, datos_sensores, resultado, tiempo_respuesta):
        cursor = self.conexion.cursor()
        cursor.execute('''
            INSERT INTO predicciones 
            (timestamp, vibracion, temperatura, presion, corriente, 
             probabilidad_falla, nivel_alerta, recomendacion, modelo_utilizado, tiempo_respuesta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            datos_sensores.get('vibracion'),
            datos_sensores.get('temperatura'),
            datos_sensores.get('presion'),
            datos_sensores.get('corriente'),
            resultado.get('probabilidad_falla'),
            resultado.get('nivel_alerta'),
            resultado.get('recomendacion'),
            resultado.get('modelo_utilizado'),
            tiempo_respuesta
        ))
        self.conexion.commit()
    
    def obtener_estadisticas(self):
        cursor = self.conexion.cursor()
        cursor.execute('SELECT COUNT(*) FROM predicciones')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(tiempo_respuesta) FROM predicciones')
        avg_tiempo = cursor.fetchone()[0] or 0
        
        # Generar datos de ejemplo para gráficos
        return {
            'total_predicciones': total,
            'tiempo_respuesta_promedio': round(avg_tiempo, 3),
            'alertas_distribucion': {
                'NORMAL': random.randint(50, 70),
                'ADVERTENCIA': random.randint(20, 30),
                'CRÍTICO': random.randint(5, 15)
            }
        }

# Inicializar sistema de logs
sistema_logs = SistemaLogs()

# ENDPOINTS
@app.get("/")
async def dashboard_principal(request: Request):
    return HTMLResponse(content=HTML_DASHBOARD)

@app.get("/api/verificar-conexion")
async def verificar_conexion():
    """Verifica si la API de ML está disponible"""
    try:
        respuesta = requests.get(f"{API_URL}/health", timeout=3)
        if respuesta.status_code == 200:
            return {"conectado": True, "estado": respuesta.json()}
        else:
            return {"conectado": False, "error": f"HTTP {respuesta.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"conectado": False, "error": "No se puede conectar al puerto 8000"}
    except Exception as e:
        return {"conectado": False, "error": str(e)}

@app.post("/api/predecir")
async def predecir_falla_web(request: Request):
    try:
        datos = await request.json()
        inicio = datetime.now()
        
        # DATOS COMPLETOS QUE LA API ESPERA
        datos_completos = {
            "vibracion": datos.get("vibracion", 3.0),
            "temperatura": datos.get("temperatura", 80.0),
            "presion": datos.get("presion", 110.0),
            "corriente": datos.get("corriente", 17.0),
            "tiempo_desde_mantenimiento": datos.get("tiempo_desde_mantenimiento", 500),
            "vibracion_media_10": 3.0,
            "vibracion_std_10": 0.3,
            "vibracion_max_10": 3.5,
            "vibracion_min_10": 2.5,
            "vibracion_tendencia": 0.1,
            "temperatura_media_10": 78.0,
            "temperatura_std_10": 2.0,
            "temperatura_max_10": 80.0,
            "temperatura_min_10": 76.0,
            "temperatura_tendencia": 0.5,
            "presion_media_10": 105.0,
            "presion_std_10": 5.0,
            "presion_max_10": 110.0,
            "presion_min_10": 100.0,
            "presion_tendencia": 1.0,
            "corriente_media_10": 16.0,
            "corriente_std_10": 0.8,
            "corriente_max_10": 17.0,
            "corriente_min_10": 15.0,
            "corriente_tendencia": 0.3,
            "indice_degradacion": 1.5,
            "hora": datetime.now().hour,
            "dia_semana": datetime.now().weekday()
        }
        
        respuesta = requests.post(f"{API_URL}/predecir", json=datos_completos, timeout=10)
        tiempo_respuesta = (datetime.now() - inicio).total_seconds()
        
        if respuesta.status_code == 200:
            resultado = respuesta.json()
            sistema_logs.guardar_prediccion(datos_completos, resultado, tiempo_respuesta)
            
            return {
                "success": True,
                "resultado": resultado,
                "tiempo_respuesta": tiempo_respuesta
            }
        else:
            error_detalle = respuesta.text if respuesta.content else f"HTTP {respuesta.status_code}"
            return {
                "success": False,
                "error": f"Error {respuesta.status_code}: {error_detalle}"
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False, 
            "error": "No se puede conectar a la API de ML. Verifica que esté ejecutándose en puerto 8000."
        }
    except Exception as e:
        return {"success": False, "error": f"Error inesperado: {str(e)}"}

@app.get("/api/info-modelo")
async def info_modelo():
    try:
        respuesta = requests.get(f"{API_URL}/info-modelo", timeout=3)
        if respuesta.status_code == 200:
            return respuesta.json()
    except:
        pass
    
    return {
        "nombre_modelo": "No disponible",
        "metricas": {"auc": 0.0, "accuracy": 0.0}
    }

@app.get("/api/estadisticas")
async def estadisticas():
    return sistema_logs.obtener_estadisticas()

if __name__ == "__main__":
    import uvicorn
    print("🚀 DASHBOARD AVANZADO INICIADO - CON TODOS LOS GRÁFICOS")
    print("📍 URL: http://localhost:8001")
    print("📊 Gráficos: Probabilidad, Alertas, Tendencia, Historial, Sensores, Correlación")
    uvicorn.run(app, host="0.0.0.0", port=8001)