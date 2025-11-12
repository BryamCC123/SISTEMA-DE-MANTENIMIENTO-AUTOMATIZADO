# Librerías para generar datos sintéticos
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generar_datos_sinteticos(n_muestras=10000, n_maquinas=10):
    """
    Genera datos sintéticos para simular sensores de equipos industriales
    """
    print("🔧 Generando datos sintéticos...")
    
    np.random.seed(42)
    datos = []
    fecha_actual = datetime(2024, 1, 1)
    
    for id_maquina in range(1, n_maquinas + 1):
        # Vida útil de cada máquina
        vida_util = np.random.normal(1000, 200)
        vida_actual = 0
        
        for _ in range(n_muestras // n_maquinas):
            vida_actual += 1
            tiempo_desde_mantenimiento = vida_actual
            
            # Factor de degradación progresiva
            degradacion = (vida_actual / vida_util) * 3.0
            
            # Generar lecturas de sensores con ruido y tendencia
            vibracion_base = np.random.normal(2.0, 0.2)
            temperatura_base = np.random.normal(75, 5)
            presion_base = np.random.normal(100, 10)
            corriente_base = np.random.normal(15, 2)
            
            vibracion = max(0, vibracion_base + degradacion + np.random.normal(0, 0.1))
            temperatura = max(0, temperatura_base + degradacion * 5 + np.random.normal(0, 1))
            presion = max(0, presion_base + degradacion * 8 + np.random.normal(0, 2))
            corriente = max(0, corriente_base + degradacion * 2 + np.random.normal(0, 0.5))
            
            # Determinar falla inminente (target variable)
            falla_inminente = int(
                (vibracion > 4.5) or 
                (temperatura > 95) or 
                (presion > 150) or
                (corriente > 25) or
                (vida_actual > vida_util * 0.9)
            )
            
            datos.append({
                'fecha_hora': fecha_actual,
                'id_maquina': f'MAQ_{id_maquina:02d}',
                'vibracion': vibracion,
                'temperatura': temperatura,
                'presion': presion,
                'corriente': corriente,
                'tiempo_desde_mantenimiento': tiempo_desde_mantenimiento,
                'falla_inminente': falla_inminente,
                'vida_util_restante': max(0, vida_util - vida_actual)
            })
            
            fecha_actual += timedelta(hours=1)
    
    df = pd.DataFrame(datos)
    
    # Crear directorio si no existe
    os.makedirs('../data', exist_ok=True)
    
    # Guardar datos
    df.to_csv('../data/datos_sinteticos.csv', index=False)
    print(f"✅ Datos guardados: {df.shape[0]} registros, {df.shape[1]} columnas")
    print(f"📊 Distribución de fallas: {df['falla_inminente'].value_counts().to_dict()}")
    
    return df

if __name__ == "__main__":
    df = generar_datos_sinteticos()
    print("\nPrimeras 5 filas:")
    print(df.head())