import os
import logging
from sklearn.linear_model import LinearRegression
import numpy as np
import joblib
from google.cloud import storage

logging.basicConfig(level=logging.INFO)

def train_and_save():
    logging.info("Iniciando entrenamiento...")
    
    # Datos de ejemplo
    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3
    
    # Entrenar
    model = LinearRegression()
    model.fit(X, y)
    logging.info("Modelo entrenado.")

    # Guardar localmente
    model_filename = "model.joblib"
    joblib.dump(model, model_filename)

    # Subir a GCS (Vertex AI establece AIP_MODEL_DIR automáticamente)
    model_dir = os.getenv("AIP_MODEL_DIR")
    
    if model_dir:
        logging.info(f"Subiendo modelo a: {model_dir}")
        # Lógica para subir al bucket gs://dataflow_vertex/...
        bucket_name = model_dir.replace("gs://", "").split("/")[0]
        blob_path = "/".join(model_dir.replace("gs://", "").split("/")[1:]) + f"/{model_filename}"
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(model_filename)
        logging.info("¡Subida completada!")
    else:
        logging.warning("AIP_MODEL_DIR no encontrado. Ejecución local.")

if __name__ == '__main__':
    train_and_save()