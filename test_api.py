# test_api.py - CON MODO INTERACTIVO
import requests
import json
from datetime import datetime

class TesterInteractivoMantenimiento:
    def __init__(self):
        self.url = "http://localhost:8000"
        self.config_predeterminada = {
            "vibracion_media_10": 2.5,
            "vibracion_std_10": 0.3,
            "vibracion_max_10": 2.8,
            "vibracion_min_10": 2.2,
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
            "hora": 12,
            "dia_semana": 3
        }
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal interactivo"""
        print("\n" + "🔧" * 50)
        print("🎮 SISTEMA INTERACTIVO - MANTENIMIENTO PREDICTIVO")
        print("🔧" * 50)
        print("1. 🎯 PREDICCIÓN MANUAL - Ingresar valores")
        print("2. 📊 PREDICCIÓN RÁPIDA - Usar valores predefinidos")
        print("3. ❤️  VERIFICAR ESTADO DEL SISTEMA")
        print("4. 📈 INFORMACIÓN DEL MODELO")
        print("5. 🚪 SALIR")
        print("🔧" * 50)
    
    def ingresar_valor_interactivo(self, parametro, valor_default, unidad=""):
        """Solicita un valor al usuario de forma interactiva"""
        try:
            mensaje = f"   📝 Ingrese {parametro} ({unidad}) [default: {valor_default}]: "
            valor = input(mensaje).strip()
            return float(valor) if valor else valor_default
        except ValueError:
            print(f"   ❌ Valor inválido, usando default: {valor_default}")
            return valor_default
    
    def modo_prediccion_manual(self):
        """Modo donde el usuario ingresa todos los valores"""
        print("\n🎯 MODO PREDICCIÓN MANUAL")
        print("   Ingrese los valores de los sensores:")
        print("   (Presione ENTER para usar valores por defecto)")
        print("-" * 40)
        
        datos = self.config_predeterminada.copy()
        
        # Sensores principales (los más importantes)
        datos["vibracion"] = self.ingresar_valor_interactivo("vibración", 3.0, "mm/s")
        datos["temperatura"] = self.ingresar_valor_interactivo("temperatura", 80.0, "°C")
        datos["presion"] = self.ingresar_valor_interactivo("presión", 110.0, "psi")
        datos["corriente"] = self.ingresar_valor_interactivo("corriente", 17.0, "A")
        datos["tiempo_desde_mantenimiento"] = self.ingresar_valor_interactivo(
            "tiempo desde mantenimiento", 500, "horas"
        )
        
        # Preguntar si quiere ajustar valores avanzados
        avanzados = input("\n   ¿Configurar valores avanzados? [s/N]: ").strip().lower()
        if avanzados == 's':
            print("\n   ⚙️  Valores avanzados:")
            datos["indice_degradacion"] = self.ingresar_valor_interactivo("índice de degradación", 1.5)
            datos["vibracion_media_10"] = self.ingresar_valor_interactivo("vibración media (10 muestras)", 2.5)
        
        return self.ejecutar_prediccion(datos, "MANUAL")
    
    def modo_prediccion_rapida(self):
        """Modo con escenarios predefinidos"""
        print("\n📊 MODO PREDICCIÓN RÁPIDA")
        print("   Seleccione un escenario:")
        print("   1. ✅ NORMAL - Máquina en óptimas condiciones")
        print("   2. ⚠️  ADVERTENCIA - Monitoreo requerido")
        print("   3. 🚨 CRÍTICO - Mantenimiento inmediato")
        print("   4. 🔄 PERSONALIZADO - Valores específicos")
        
        opcion = input("\n   Elija opción [1-4]: ").strip()
        
        escenarios = {
            "1": {"nombre": "NORMAL", "vibracion": 2.1, "temperatura": 75.0, "presion": 95.0, "corriente": 15.0, "tiempo": 100},
            "2": {"nombre": "ADVERTENCIA", "vibracion": 3.8, "temperatura": 87.0, "presion": 135.0, "corriente": 19.0, "tiempo": 600},
            "3": {"nombre": "CRÍTICO", "vibracion": 5.2, "temperatura": 98.0, "presion": 160.0, "corriente": 22.0, "tiempo": 950},
            "4": {"nombre": "PERSONALIZADO", "vibracion": 4.0, "temperatura": 85.0, "presion": 120.0, "corriente": 18.0, "tiempo": 400}
        }
        
        if opcion in escenarios:
            escenario = escenarios[opcion]
            datos = self.config_predeterminada.copy()
            datos.update({
                "vibracion": escenario["vibracion"],
                "temperatura": escenario["temperatura"],
                "presion": escenario["presion"],
                "corriente": escenario["corriente"],
                "tiempo_desde_mantenimiento": escenario["tiempo"],
                "indice_degradacion": 1.0 + (escenario["vibracion"] - 2.0) * 0.5
            })
            return self.ejecutar_prediccion(datos, escenario["nombre"])
        else:
            print("   ❌ Opción inválida")
            return False
    
    def ejecutar_prediccion(self, datos, tipo_prueba):
        """Ejecuta la predicción y muestra resultados"""
        try:
            print(f"\n   🚀 Ejecutando predicción ({tipo_prueba})...")
            print("   " + "⏳" * 10)
            
            inicio = datetime.now()
            respuesta = requests.post(f"{self.url}/predecir", json=datos, timeout=10)
            tiempo_respuesta = (datetime.now() - inicio).total_seconds()
            
            if respuesta.status_code == 200:
                resultado = respuesta.json()
                
                # Mostrar resultados de forma visual
                print("\n   " + "📊" * 20)
                print("   📈 RESULTADO DE LA PREDICCIÓN:")
                print("   " + "📊" * 20)
                
                prob = resultado['probabilidad_falla']
                if prob < 0.3:
                    icono = "✅"
                elif prob < 0.7:
                    icono = "⚠️"
                else:
                    icono = "🚨"
                
                print(f"   {icono} PROBABILIDAD: {prob:.3f}")
                print(f"   🚨 ALERTA: {resultado['nivel_alerta']}")
                print(f"   💡 RECOMENDACIÓN: {resultado['recomendacion']}")
                print(f"   ⚡ TIEMPO RESPUESTA: {tiempo_respuesta:.3f}s")
                print(f"   🤖 MODELO: {resultado['modelo_utilizado']}")
                
                return True
            else:
                print(f"   ❌ Error HTTP {respuesta.status_code}: {respuesta.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("   ❌ No se puede conectar a la API. ¿Está ejecutándose?")
            return False
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")
            return False
    
    def verificar_estado_sistema(self):
        """Verifica el estado general del sistema"""
        print("\n❤️  VERIFICANDO ESTADO DEL SISTEMA...")
        try:
            respuesta = requests.get(f"{self.url}/health", timeout=5)
            if respuesta.status_code == 200:
                estado = respuesta.json()
                print("   ✅ SISTEMA SALUDABLE")
                print(f"   🤖 Modelo: {estado['modelo']}")
                print(f"   📊 AUC: {estado['auc_modelo']:.4f}")
                print(f"   🕐 Última verificación: {estado['timestamp']}")
            else:
                print("   ❌ Sistema no responde correctamente")
        except Exception as e:
            print(f"   ❌ Error conectando al sistema: {e}")
    
    def mostrar_info_modelo(self):
        """Muestra información detallada del modelo"""
        print("\n📈 INFORMACIÓN DEL MODELO...")
        try:
            respuesta = requests.get(f"{self.url}/info-modelo", timeout=5)
            if respuesta.status_code == 200:
                info = respuesta.json()
                print(f"   🤖 NOMBRE: {info['nombre_modelo']}")
                print(f"   🎯 AUC: {info['metricas']['auc']:.6f}")
                print(f"   ✅ EXACTITUD: {info['metricas']['accuracy']:.4f}")
                print(f"   📋 CARACTERÍSTICAS: {info['total_caracteristicas']}")
                print(f"   ⚠️  UMBRAL ADVERTENCIA: {info['umbrales']['advertencia']}")
                print(f"   🚨 UMBRAL CRÍTICO: {info['umbrales']['critico']}")
            else:
                print("   ❌ No se pudo obtener información del modelo")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    def ejecutar(self):
        """Función principal que ejecuta el modo interactivo"""
        print("🎮 BIENVENIDO AL SISTEMA INTERACTIVO")
        print("   Mantenimiento Predictivo con Machine Learning")
        
        while True:
            self.mostrar_menu_principal()
            opcion = input("\n   Seleccione una opción [1-5]: ").strip()
            
            if opcion == "1":
                self.modo_prediccion_manual()
            elif opcion == "2":
                self.modo_prediccion_rapida()
            elif opcion == "3":
                self.verificar_estado_sistema()
            elif opcion == "4":
                self.mostrar_info_modelo()
            elif opcion == "5":
                print("\n👋 ¡Gracias por usar el sistema! Hasta pronto.")
                break
            else:
                print("   ❌ Opción inválida. Intente nuevamente.")
            
            # Pausa antes de mostrar menú again
            if opcion != "5":
                input("\n   Presione ENTER para continuar...")

# Ejecutar si es el archivo principal
if __name__ == "__main__":
    tester = TesterInteractivoMantenimiento()
    tester.ejecutar()