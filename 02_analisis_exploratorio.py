# Librerías para análisis exploratorio
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def analisis_exploratorio():
    """
    Realiza análisis exploratorio de los datos generados
    """
    print("📊 Realizando análisis exploratorio...")
    
    # Cargar datos
    df = pd.read_csv('../data/datos_sinteticos.csv')
    df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
    
    # Configurar estilo de gráficos
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Crear figura con subplots
    fig = plt.figure(figsize=(20, 15))
    
    # 1. Distribución de variables numéricas
    variables = ['vibracion', 'temperatura', 'presion', 'corriente']
    
    for i, var in enumerate(variables, 1):
        plt.subplot(3, 3, i)
        sns.histplot(data=df, x=var, hue='falla_inminente', kde=True, alpha=0.6)
        plt.title(f'Distribución de {var.title()}')
        plt.xlabel(var.title())
    
    # 2. Matriz de correlación
    plt.subplot(3, 3, 5)
    correlaciones = df[variables + ['falla_inminente', 'tiempo_desde_mantenimiento']].corr()
    mask = np.triu(np.ones_like(correlaciones, dtype=bool))
    sns.heatmap(correlaciones, mask=mask, annot=True, cmap='coolwarm', center=0,
                square=True, fmt='.2f', cbar_kws={"shrink": .8})
    plt.title('Matriz de Correlación')
    
    # 3. Tasa de fallas por máquina
    plt.subplot(3, 3, 6)
    tasa_fallas = df.groupby('id_maquina')['falla_inminente'].mean().sort_values()
    tasa_fallas.plot(kind='barh', color='skyblue')
    plt.title('Tasa de Fallas por Máquina')
    plt.xlabel('Tasa de Fallas')
    plt.grid(axis='x', alpha=0.3)
    
    # 4. Evolución temporal de vibración (ejemplo con una máquina)
    plt.subplot(3, 3, 7)
    maq_ejemplo = df[df['id_maquina'] == 'MAQ_01'].tail(200)
    plt.plot(maq_ejemplo['fecha_hora'], maq_ejemplo['vibracion'], 
             label='Vibración', color='red', alpha=0.7)
    plt.plot(maq_ejemplo['fecha_hora'], maq_ejemplo['temperatura']/20, 
             label='Temperatura/20', color='orange', alpha=0.7)
    
    # Resaltar puntos con falla
    fallas = maq_ejemplo[maq_ejemplo['falla_inminente'] == 1]
    plt.scatter(fallas['fecha_hora'], fallas['vibracion'], 
                color='red', s=50, zorder=5, label='Falla Inminente')
    
    plt.title('Evolución Temporal - Máquina MAQ_01')
    plt.xlabel('Fecha')
    plt.ylabel('Valores Normalizados')
    plt.legend()
    plt.xticks(rotation=45)
    
    # 5. Boxplot por estado de falla
    plt.subplot(3, 3, 8)
    datos_melted = df.melt(id_vars=['falla_inminente'], 
                          value_vars=variables,
                          var_name='Sensor', 
                          value_name='Valor')
    
    sns.boxplot(data=datos_melted, x='Sensor', y='Valor', hue='falla_inminente')
    plt.title('Distribución por Sensor y Estado de Falla')
    plt.xticks(rotation=45)
    
    # 6. Scatter plot vibración vs temperatura
    plt.subplot(3, 3, 9)
    scatter = plt.scatter(df['vibracion'], df['temperatura'], 
                         c=df['falla_inminente'], alpha=0.6, 
                         cmap='viridis', s=30)
    plt.colorbar(scatter, label='Falla Inminente')
    plt.xlabel('Vibración')
    plt.ylabel('Temperatura')
    plt.title('Vibración vs Temperatura')
    plt.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../data/analisis_exploratorio.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Estadísticas descriptivas
    print("\n📈 Estadísticas Descriptivas:")
    print(df[variables + ['tiempo_desde_mantenimiento']].describe())
    
    print(f"\n🎯 Balance de clases (Falla Inminente):")
    print(df['falla_inminente'].value_counts(normalize=True).map(lambda x: f"{x:.2%}"))

if __name__ == "__main__":
    analisis_exploratorio()