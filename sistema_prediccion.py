# Librerías para el sistema de predicción
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

class SistemaMantenimientoPredictivo:
    def __init__(self, ruta_modelo='../models/modelo_entrenado.pkl'):
        """
        Inicializa el sistema de predicción cargando el modelo entrenado
        """
        print("🔮 Inicializando Sistema de Mantenimiento Predictivo...")
        
        # Cargar modelo y preprocessing
        datos_modelo = joblib.load(ruta_modelo)
        self.modelo = datos_modelo['modelo']
        self.scaler = datos_modelo['scaler']
        self.columnas_caracteristicas = datos_modelo['columnas_caracteristicas']
        self.nombre_modelo = datos_modelo['nombre_modelo']
        self.metricas = datos_modelo['metricas']
        
        # Umbrales de alerta
        self.umbral_advertencia = 0.3
        self.umbral_critico = 0.7
        
        print(f"✅ Modelo cargado: {self.nombre_modelo}")
        print(f"✅ AUC del modelo: {self.metricas['auc']:.4f}")
        print(f"✅ Características: {len(self.columnas_caracteristicas)}")
    
    def preprocesar_nuevos_datos(self, datos_sensores):
        """
        Preprocesa nuevos datos de sensores para la predicción
        """
        # Convertir a DataFrame si es un diccionario
        if isinstance(datos_sensores, dict):
            df = pd.DataFrame([datos_sensores])
        else:
            df = datos_sensores.copy()
        
        # Asegurar que tenemos todas las columnas necesarias
        for columna in self.columnas_caracteristicas:
            if columna not in df.columns:
                # Si falta alguna característica, usar valor por defecto
                df[columna] = 0.0
        
        # Reordenar columnas como el modelo espera
        df = df[self.columnas_caracteristicas]
        
        # Escalar datos
        datos_escalados = self.scaler.transform(df)
        
        return datos_escalados
    
    def predecir_falla(self, datos_sensores):
        """
        Realiza predicción de falla inminente
        """
        try:
            # Preprocesar datos
            datos_preprocesados = self.preprocesar_nuevos_datos(datos_sensores)
            
            # Realizar predicción
            probabilidad_falla = self.modelo.predict_proba(datos_preprocesados)[0, 1]
            
            # Generar alerta y recomendación
            nivel_alerta, recomendacion = self._generar_alerta(probabilidad_falla)
            
            return {
                'exito': True,
                'probabilidad_falla': float(probabilidad_falla),
                'nivel_alerta': nivel_alerta,
                'recomendacion': recomendacion,
                'modelo_utilizado': self.nombre_modelo,
                'timestamp_prediccion': datetime.now().isoformat(),
                'umbrales': {
                    'advertencia': self.umbral_advertencia,
                    'critico': self.umbral_critico
                }
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': str(e),
                'timestamp_prediccion': datetime.now().isoformat()
            }
    
    def _generar_alerta(self, probabilidad):
        """
        Genera nivel de alerta basado en la probabilidad de falla
        """
        if probabilidad >= self.umbral_critico:
            return 'CRÍTICO', '⚠️ MANTENIMIENTO REQUERIDO INMEDIATAMENTE. Parar equipo y realizar mantenimiento correctivo.'
        
        elif probabilidad >= self.umbral_advertencia:
            return 'ADVERTENCIA', '🔶 Programar mantenimiento preventivo. Monitorear estrechamente los parámetros.'
        
        else:
            return 'NORMAL', '✅ Operación normal. Continuar monitoreo rutinario.'
    
    def predecir_lote(self, datos_lote):
        """
        Realiza predicciones para un lote de datos
        """
        try:
            # Preprocesar lote
            datos_preprocesados = self.preprocesar_nuevos_datos(datos_lote)
            
            # Predecir probabilidades
            probabilidades = self.modelo.predict_proba(datos_preprocesados)[:, 1]
            
            resultados = []
            for i, prob in enumerate(probabilidades):
                nivel_alerta, recomendacion = self._generar_alerta(prob)
                
                resultados.append({
                    'indice': i,
                    'probabilidad_falla': float(prob),
                    'nivel_alerta': nivel_alerta,
                    'recomendacion': recomendacion
                })
            
            return {
                'exito': True,
                'total_registros': len(probabilidades),
                'predicciones': resultados,
                'resumen_alertas': {
                    'CRÍTICO': len([r for r in resultados if r['nivel_alerta'] == 'CRÍTICO']),
                    'ADVERTENCIA': len([r for r in resultados if r['nivel_alerta'] == 'ADVERTENCIA']),
                    'NORMAL': len([r for r in resultados if r['nivel_alerta'] == 'NORMAL'])
                }
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }

def demostrar_sistema():
    """
    Función para demostrar el funcionamiento del sistema
    """
    print("\n" + "="*60)
    print("🎯 DEMOSTRACIÓN DEL SISTEMA DE PREDICCIÓN")
    print("="*60)
    
    # Inicializar sistema
    sistema = SistemaMantenimientoPredictivo()
    
    # Casos de prueba
    casos_prueba = [
        {
            'nombre': '✅ Caso NORMAL',
            'datos': {
                'vibracion': 2.1,
                'temperatura': 72.0,
                'presion': 95.0,
                'corriente': 14.5,
                'tiempo_desde_mantenimiento': 100,
                'vibracion_media_10': 2.0,
                'vibracion_std_10': 0.1,
                'vibracion_max_10': 2.3,
                'vibracion_min_10': 1.9,
                'vibracion_tendencia': 0.01,
                'temperatura_media_10': 71.0,
                'temperatura_std_10': 1.2,
                'temperatura_max_10': 73.0,
                'temperatura_min_10': 70.0,
                'temperatura_tendencia': 0.5,
                'presion_media_10': 94.0,
                'presion_std_10': 2.1,
                'presion_max_10': 96.0,
                'presion_min_10': 92.0,
                'presion_tendencia': 0.3,
                'corriente_media_10': 14.3,
                'corriente_std_10': 0.4,
                'corriente_max_10': 15.0,
                'corriente_min_10': 14.0,
                'corriente_tendencia': 0.1,
                'indice_degradacion': 1.2,
                'hora': 10,
                'dia_semana': 2
            }
        },
        {
            'nombre': '⚠️ Caso ADVERTENCIA', 
            'datos': {
                'vibracion': 3.8,
                'temperatura': 85.0,
                'presion': 130.0,
                'corriente': 18.0,
                'tiempo_desde_mantenimiento': 800,
                'vibracion_media_10': 3.5,
                'vibracion_std_10': 0.5,
                'vibracion_max_10': 4.0,
                'vibracion_min_10': 3.0,
                'vibracion_tendencia': 0.2,
                'temperatura_media_10': 82.0,
                'temperatura_std_10': 3.0,
                'temperatura_max_10': 86.0,
                'temperatura_min_10': 79.0,
                'temperatura_tendencia': 1.5,
                'presion_media_10': 125.0,
                'presion_std_10': 8.0,
                'presion_max_10': 135.0,
                'presion_min_10': 120.0,
                'presion_tendencia': 2.0,
                'corriente_media_10': 17.0,
                'corriente_std_10': 1.2,
                'corriente_max_10': 19.0,
                'corriente_min_10': 16.0,
                'corriente_tendencia': 0.8,
                'indice_degradacion': 2.1,
                'hora': 14,
                'dia_semana': 4
            }
        },
        {
            'nombre': '🚨 Caso CRÍTICO',
            'datos': {
                'vibracion': 5.2,
                'temperatura': 98.0,
                'presion': 160.0,
                'corriente': 22.0,
                'tiempo_desde_mantenimiento': 950,
                'vibracion_media_10': 4.8,
                'vibracion_std_10': 0.8,
                'vibracion_max_10': 5.5,
                'vibracion_min_10': 4.0,
                'vibracion_tendencia': 0.5,
                'temperatura_media_10': 92.0,
                'temperatura_std_10': 5.0,
                'temperatura_max_10': 99.0,
                'temperatura_min_10': 88.0,
                'temperatura_tendencia': 3.0,
                'presion_media_10': 150.0,
                'presion_std_10': 12.0,
                'presion_max_10': 165.0,
                'presion_min_10': 140.0,
                'presion_tendencia': 5.0,
                'corriente_media_10': 20.0,
                'corriente_std_10': 2.0,
                'corriente_max_10': 23.0,
                'corriente_min_10': 18.0,
                'corriente_tendencia': 1.5,
                'indice_degradacion': 3.5,
                'hora': 16,
                'dia_semana': 5
            }
        }
    ]
    
    # Probar cada caso
    for caso in casos_prueba:
        print(f"\n{caso['nombre']}")
        print("-" * 40)
        
        resultado = sistema.predecir_falla(caso['datos'])
        
        if resultado['exito']:
            print(f"📊 Probabilidad de falla: {resultado['probabilidad_falla']:.3f}")
            print(f"🚨 Nivel de alerta: {resultado['nivel_alerta']}")
            print(f"💡 Recomendación: {resultado['recomendacion']}")
        else:
            print(f"❌ Error: {resultado['error']}")
    
    # Demostrar predicción por lote
    print(f"\n📦 DEMOSTRACIÓN PREDICCIÓN POR LOTE")
    print("-" * 40)
    
    lote_datos = pd.DataFrame([caso['datos'] for caso in casos_prueba])
    resultado_lote = sistema.predecir_lote(lote_datos)
    
    if resultado_lote['exito']:
        print(f"Total registros procesados: {resultado_lote['total_registros']}")
        print(f"Resumen de alertas: {resultado_lote['resumen_alertas']}")

if __name__ == "__main__":
    demostrar_sistema()