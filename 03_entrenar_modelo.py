# Librerías para entrenamiento de modelos
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (classification_report, confusion_matrix, 
                           roc_auc_score, precision_recall_curve, auc)
from xgboost import XGBClassifier
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

class EntrenadorModelo:
    def __init__(self):
        self.modelos = {
            'Random Forest': RandomForestClassifier(random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(random_state=42),
            'XGBoost': XGBClassifier(random_state=42, eval_metric='logloss')
        }
        self.mejor_modelo = None
        self.scaler = StandardScaler()
        self.resultados = {}
    
    def ingenieria_caracteristicas(self, df):
        """
        Realiza ingeniería de características para mejorar el modelo
        """
        print("🔧 Realizando ingeniería de características...")
        
        df_features = df.copy()
        
        # Características estadísticas rolling por máquina
        for col in ['vibracion', 'temperatura', 'presion', 'corriente']:
            # Estadísticas en ventana temporal
            df_features[f'{col}_media_10'] = df.groupby('id_maquina')[col].rolling(10).mean().values
            df_features[f'{col}_std_10'] = df.groupby('id_maquina')[col].rolling(10).std().values
            df_features[f'{col}_max_10'] = df.groupby('id_maquina')[col].rolling(10).max().values
            df_features[f'{col}_min_10'] = df.groupby('id_maquina')[col].rolling(10).min().values
            
            # Tendencia (derivada)
            df_features[f'{col}_tendencia'] = df.groupby('id_maquina')[col].diff(5)
        
        # Índice de degradación compuesto
        df_features['indice_degradacion'] = (
            df_features['vibracion'] / df_features['vibracion'].mean() +
            df_features['temperatura'] / df_features['temperatura'].mean() +
            df_features['presion'] / df_features['presion'].mean() +
            df_features['corriente'] / df_features['corriente'].mean()
        )
        
        # Características de tiempo
        df_features['hora'] = pd.to_datetime(df_features['fecha_hora']).dt.hour
        df_features['dia_semana'] = pd.to_datetime(df_features['fecha_hora']).dt.dayofweek
        
        # Llenar valores NaN
        df_features = df_features.fillna(method='bfill').fillna(method='ffill')
        
        print(f"✅ Características creadas. Total features: {len([col for col in df_features.columns if col not in ['fecha_hora', 'id_maquina', 'falla_inminente', 'vida_util_restante']])}")
        
        return df_features
    
    def preparar_datos(self, df):
        """
        Prepara los datos para entrenamiento
        """
        print("📋 Preparando datos para entrenamiento...")
        
        # Aplicar ingeniería de características
        df_features = self.ingenieria_caracteristicas(df)
        
        # Definir características y target
        caracteristicas_excluir = ['fecha_hora', 'id_maquina', 'falla_inminente', 'vida_util_restante']
        self.columnas_caracteristicas = [col for col in df_features.columns if col not in caracteristicas_excluir]
        
        X = df_features[self.columnas_caracteristicas]
        y = df_features['falla_inminente']
        
        # Dividir datos
        X_entrenamiento, X_prueba, y_entrenamiento, y_prueba = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Escalar características
        X_entrenamiento_esc = self.scaler.fit_transform(X_entrenamiento)
        X_prueba_esc = self.scaler.transform(X_prueba)
        
        print(f"📊 Conjunto de entrenamiento: {X_entrenamiento_esc.shape}")
        print(f"📊 Conjunto de prueba: {X_prueba_esc.shape}")
        
        return X_entrenamiento_esc, X_prueba_esc, y_entrenamiento, y_prueba
    
    def entrenar_modelos(self, X_entrenamiento, X_prueba, y_entrenamiento, y_prueba):
        """
        Entrena y evalúa múltiples modelos
        """
        print("🤖 Entrenando modelos...")
        
        for nombre, modelo in self.modelos.items():
            print(f"\n--- Entrenando {nombre} ---")
            
            # Entrenar modelo
            modelo.fit(X_entrenamiento, y_entrenamiento)
            
            # Predicciones
            y_pred = modelo.predict(X_prueba)
            y_pred_proba = modelo.predict_proba(X_prueba)[:, 1]
            
            # Métricas
            auc_score = roc_auc_score(y_prueba, y_pred_proba)
            accuracy = modelo.score(X_prueba, y_prueba)
            
            # Validación cruzada
            cv_scores = cross_val_score(modelo, X_entrenamiento, y_entrenamiento, 
                                      cv=5, scoring='roc_auc')
            
            self.resultados[nombre] = {
                'modelo': modelo,
                'auc': auc_score,
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'predicciones': y_pred,
                'probabilidades': y_pred_proba
            }
            
            print(f"✅ AUC: {auc_score:.4f}")
            print(f"✅ Accuracy: {accuracy:.4f}")
            print(f"✅ CV AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    def seleccionar_mejor_modelo(self):
        """
        Selecciona el mejor modelo basado en AUC
        """
        self.mejor_nombre = max(self.resultados, key=lambda x: self.resultados[x]['auc'])
        self.mejor_modelo = self.resultados[self.mejor_nombre]['modelo']
        
        print(f"\n🎯 MEJOR MODELO SELECCIONADO: {self.mejor_nombre}")
        print(f"🎯 AUC: {self.resultados[self.mejor_nombre]['auc']:.4f}")
    
    def guardar_modelo(self, ruta_modelo='../models/modelo_entrenado.pkl'):
        """
        Guarda el modelo y preprocessing
        """
        os.makedirs('../models', exist_ok=True)
        
        datos_modelo = {
            'modelo': self.mejor_modelo,
            'scaler': self.scaler,
            'columnas_caracteristicas': self.columnas_caracteristicas,
            'nombre_modelo': self.mejor_nombre,
            'metricas': self.resultados[self.mejor_nombre]
        }
        
        joblib.dump(datos_modelo, ruta_modelo)
        print(f"💾 Modelo guardado en: {ruta_modelo}")
    
    def evaluar_modelos(self, X_prueba, y_prueba):
        """
        Evalúa y visualiza el rendimiento de los modelos
        """
        print("\n📈 Evaluando modelos...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Comparación de AUC
        modelos_nombres = list(self.resultados.keys())
        auc_scores = [self.resultados[nombre]['auc'] for nombre in modelos_nombres]
        
        bars = axes[0, 0].bar(modelos_nombres, auc_scores, color=['skyblue', 'lightgreen', 'lightcoral'])
        axes[0, 0].set_title('Comparación de AUC entre Modelos')
        axes[0, 0].set_ylabel('AUC Score')
        axes[0, 0].set_ylim(0, 1)
        
        # Añadir valores en las barras
        for bar, auc_val in zip(bars, auc_scores):
            axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                           f'{auc_val:.4f}', ha='center', va='bottom')
        
        # 2. Matriz de confusión del mejor modelo
        mejor_resultado = self.resultados[self.mejor_nombre]
        cm = confusion_matrix(y_prueba, mejor_resultado['predicciones'])
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0, 1],
                   xticklabels=['No Falla', 'Falla'], 
                   yticklabels=['No Falla', 'Falla'])
        axes[0, 1].set_title(f'Matriz de Confusión - {self.mejor_nombre}')
        axes[0, 1].set_xlabel('Predicción')
        axes[0, 1].set_ylabel('Real')
        
        # 3. Curva Precision-Recall
        for nombre, resultados in self.resultados.items():
            precision, recall, _ = precision_recall_curve(y_prueba, resultados['probabilidades'])
            pr_auc = auc(recall, precision)
            axes[1, 0].plot(recall, precision, label=f'{nombre} (AUC={pr_auc:.3f})')
        
        axes[1, 0].set_xlabel('Recall')
        axes[1, 0].set_ylabel('Precision')
        axes[1, 0].set_title('Curva Precision-Recall')
        axes[1, 0].legend()
        axes[1, 0].grid(alpha=0.3)
        
        # 4. Importancia de características (si está disponible)
        if hasattr(self.mejor_modelo, 'feature_importances_'):
            importancias = self.mejor_modelo.feature_importances_
            indices = np.argsort(importancias)[-15:]  # Top 15 características
            
            axes[1, 1].barh(range(len(indices)), importancias[indices], color='teal', alpha=0.7)
            axes[1, 1].set_yticks(range(len(indices)))
            axes[1, 1].set_yticklabels([self.columnas_caracteristicas[i] for i in indices])
            axes[1, 1].set_xlabel('Importancia')
            axes[1, 1].set_title(f'Top 15 Características - {self.mejor_nombre}')
        
        plt.tight_layout()
        plt.savefig('../data/evaluacion_modelos.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Reporte de clasificación del mejor modelo
        print(f"\n📊 REPORTE DE CLASIFICACIÓN - {self.mejor_nombre}:")
        print(classification_report(y_prueba, mejor_resultado['predicciones']))

def main():
    """
    Función principal para entrenar el modelo
    """
    print("🚀 INICIANDO ENTRENAMIENTO DEL MODELO")
    
    # Cargar datos
    df = pd.read_csv('../data/datos_sinteticos.csv')
    
    # Entrenar modelo
    entrenador = EntrenadorModelo()
    X_entrenamiento, X_prueba, y_entrenamiento, y_prueba = entrenador.preparar_datos(df)
    entrenador.entrenar_modelos(X_entrenamiento, X_prueba, y_entrenamiento, y_prueba)
    entrenador.seleccionar_mejor_modelo()
    entrenador.evaluar_modelos(X_prueba, y_prueba)
    entrenador.guardar_modelo()
    
    print("\n✅ ENTRENAMIENTO COMPLETADO")

if __name__ == "__main__":
    main()