import joblib
import numpy as np

# 1. Cargar el modelo
print("Cargando el cerebro... 🧠")
modelo_cargado = joblib.load('model.joblib')

# 2. Preparar datos nuevos
# IMPORTANTE: Deben tener el mismo formato que usaste al entrenar (task.py)
# En tu ejemplo eran 2 números: [x1, x2]
datos_nuevos = [
    [1, 1],  # Ejemplo 1
    [2, 3],  # Ejemplo 2
    [10, 5]  # Ejemplo 3 (Inventado)
]

# 3. Hacer la predicción
predicciones = modelo_cargado.predict(datos_nuevos)

# 4. Ver resultados
print("\n--- RESULTADOS ---")
for i, dato in enumerate(datos_nuevos):
    resultado = predicciones[i]
    print(f"Entrada: {dato} -> Predicción: {resultado:.2f}")
    
    
#!gsutil cp gs://dataflow_vertex/model_output/model.joblib .    