# Librerías para la API
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import pandas as pd
from typing import List, Optional
import json
from datetime import datetime

# Importar nuestro sistema de predicción
from sistema_prediccion import SistemaMantenimientoPredictivo

# Inicializar FastAPI
app = FastAPI(
    title="API de Mantenimiento Predictivo",
    description="API para predecir fallas en equipos industriales usando Machine Learning",
    version="1.0.0"
)

# Inicializar sistema de predicción
try:
    sistema_predictivo = SistemaMantenimientoPredictivo()
    print("✅ Sistema de predicción inicializado correctamente")
except Exception as e:
    print(f"❌ Error al inicializar el sistema: {e}")
    sistema_predictivo = None

# Modelos Pydantic para validación de datos
class DatosSensor(BaseModel):
    vibracion: float
    temperatura: float
    presion: float
    corriente: float
    tiempo_desde_mantenimiento: int
    vibracion_media_10: float
    vibracion_std_10: float
    vibracion_max_10: float
    vibracion_min_10: float
    vibracion_tendencia: float
    temperatura_media_10: float
    temperatura_std_10: float
    temperatura_max_10: float
    temperatura_min_10: float
    temperatura_tendencia: float
    presion_media_10: float
    presion_std_10: float
    presion_max_10: float
    presion_min_10: float
    presion_tendencia: float
    corriente_media_10: float
    corriente_std_10: float
    corriente_max_10: float
    corriente_min_10: float
    corriente_tendencia: float
    indice_degradacion: float
    hora: int
    dia_semana: int

class LoteDatosSensor(BaseModel):
    datos: List[DatosSensor]

# Endpoints de la API
@app.get("/")
async def root():
    """
    Endpoint raíz - Información de la API
    """
    return {
        "mensaje": "API de Mantenimiento Predictivo",
        "version": "1.0.0",
        "estado": "operacional",
        "modelo_cargado": sistema_predictivo.nombre_modelo if sistema_predictivo else "No disponible"
    }

@app.get("/health")
async def health_check():
    """
    Endpoint de salud - Verifica que el sistema esté funcionando
    """
    if sistema_predictivo is None:
        raise HTTPException(status_code=503, detail="Sistema de predicción no disponible")
    
    return {
        "status": "healthy",
        "modelo": sistema_predictivo.nombre_modelo,
        "auc_modelo": sistema_predictivo.metricas['auc'],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predecir")
async def predecir_falla(datos_sensor: DatosSensor):
    """
    Endpoint para predecir falla individual
    """
    if sistema_predictivo is None:
        raise HTTPException(status_code=503, detail="Sistema de predicción no disponible")
    
    try:
        # Convertir a diccionario
        datos_dict = datos_sensor.dict()
        
        # Realizar predicción
        resultado = sistema_predictivo.predecir_falla(datos_dict)
        
        if resultado['exito']:
            return resultado
        else:
            raise HTTPException(status_code=400, detail=resultado['error'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la predicción: {str(e)}")

@app.post("/predecir-lote")
async def predecir_falla_lote(lote_datos: LoteDatosSensor):
    """
    Endpoint para predecir fallas en lote
    """
    if sistema_predictivo is None:
        raise HTTPException(status_code=503, detail="Sistema de predicción no disponible")
    
    try:
        # Convertir a DataFrame
        datos_lista = [datos.dict() for datos in lote_datos.datos]
        df_lote = pd.DataFrame(datos_lista)
        
        # Realizar predicción en lote
        resultado = sistema_predictivo.predecir_lote(df_lote)
        
        if resultado['exito']:
            return resultado
        else:
            raise HTTPException(status_code=400, detail=resultado['error'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la predicción por lote: {str(e)}")

@app.get("/info-modelo")
async def info_modelo():
    """
    Endpoint para obtener información del modelo
    """
    if sistema_predictivo is None:
        raise HTTPException(status_code=503, detail="Sistema de predicción no disponible")
    
    return {
        "nombre_modelo": sistema_predictivo.nombre_modelo,
        "metricas": {
            "auc": sistema_predictivo.metricas['auc'],
            "accuracy": sistema_predictivo.metricas['accuracy'],
            "cross_validation_mean": sistema_predictivo.metricas['cv_mean'],
            "cross_validation_std": sistema_predictivo.metricas['cv_std']
        },
        "caracteristicas": sistema_predictivo.columnas_caracteristicas,
        "total_caracteristicas": len(sistema_predictivo.columnas_caracteristicas),
        "umbrales": {
            "advertencia": sistema_predictivo.umbral_advertencia,
            "critico": sistema_predictivo.umbral_critico
        }
    }

# Ejemplo de uso para desarrollo
@app.get("/ejemplo-datos")
async def ejemplo_datos():
    """
    Endpoint que retorna un ejemplo de datos para testing
    """
    ejemplo = {
        "vibracion": 3.2,
        "temperatura": 80.0,
        "presion": 110.0,
        "corriente": 16.0,
        "tiempo_desde_mantenimiento": 500,
        "vibracion_media_10": 3.0,
        "vibracion_std_10": 0.3,
        "vibracion_max_10": 3.5,
        "vibracion_min_10": 2.8,
        "vibracion_tendencia": 0.1,
        "temperatura_media_10": 78.0,
        "temperatura_std_10": 2.0,
        "temperatura_max_10": 81.0,
        "temperatura_min_10": 76.0,
        "temperatura_tendencia": 1.0,
        "presion_media_10": 105.0,
        "presion_std_10": 5.0,
        "presion_max_10": 112.0,
        "presion_min_10": 100.0,
        "presion_tendencia": 1.5,
        "corriente_media_10": 15.5,
        "corriente_std_10": 0.8,
        "corriente_max_10": 16.5,
        "corriente_min_10": 14.8,
        "corriente_tendencia": 0.3,
        "indice_degradacion": 1.8,
        "hora": 14,
        "dia_semana": 2
    }
    
    return ejemplo

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )