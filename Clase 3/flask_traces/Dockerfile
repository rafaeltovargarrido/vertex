# Usar imagen oficial ligera de Python
FROM python:3.11-slim

# Evitar que Python genere archivos .pyc y habilitar logs en stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Cloud Run inyecta la variable PORT (por defecto 8080)
ENV PORT=8080

# Comando para ejecutar la aplicación con Gunicorn
# 1 worker y 8 hilos para permitir concurrencia en Cloud Run
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app