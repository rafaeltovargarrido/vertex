#!/bin/bash

# Configuración
PROJECT_ID="formacionaiops-476808 "  # <--- CAMBIA ESTO
SERVICE_NAME="mi-flask-observability"
REGION="europe-west1"

echo "🚀 Configurando proyecto: $PROJECT_ID"
gcloud config set project $PROJECT_ID


echo "📦 Construyendo y Desplegando en Cloud Run..."
# Desplegamos desde código fuente (Cloud Build construirá el Dockerfile automáticamente)
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="ENABLE_PROFILER=true" \
    --set-env-vars="ENABLE_TRACING=true" \
    --set-env-vars="GCP_PROJECT=$PROJECT_ID"

echo "✅ Despliegue completado."