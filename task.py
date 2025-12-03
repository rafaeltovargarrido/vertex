import os
import logging
import argparse # <--- IMPORTANTE
from sklearn.linear_model import LinearRegression
import numpy as np
import joblib
from google.cloud import storage

logging.basicConfig(level=logging.INFO)

def train_and_save(model_dir):
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

    # Subir a GCS
    if model_dir:
        logging.info(f"Subiendo modelo a: {model_dir}")
        bucket_name = model_dir.replace("gs://", "").split("/")[0]
        # Truco para limpiar la ruta si viene con o sin / al final
        blob_path = "/".join(model_dir.replace("gs://", "").split("/")[1:]).strip("/") + f"/{model_filename}"
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(model_filename)
        logging.info("¡Subida completada!")
    else:
        logging.warning("No se especificó --model_dir. El modelo se guardó localmente.")

if __name__ == '__main__':
    # 1. Configurar el lector de argumentos
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_dir', type=str, default=os.getenv('AIP_MODEL_DIR'))
    args = parser.parse_args()

    # 2. Ejecutar con el argumento
    train_and_save(args.model_dir)