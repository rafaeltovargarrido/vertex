# Dockerfile
FROM python:3.9-slim

# Instalar librerías necesarias
RUN pip install scikit-learn numpy joblib google-cloud-storage

# Copiar tu código al contenedor
COPY task.py /app/task.py

# Definir el directorio de trabajo
WORKDIR /app

# El comando que ejecutará Vertex AI al arrancar
ENTRYPOINT ["python", "task.py"]