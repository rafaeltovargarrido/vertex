# 🧠 Guía MLOps: Pipeline de Entrenamiento y Despliegue en Vertex AI

Este proyecto implementa una tubería de CI/CD para Machine Learning utilizando **Google Cloud Build** y **Vertex AI**.

El objetivo es automatizar el ciclo de vida completo de un modelo: desde que escribes el código (`git push`) hasta que tienes una API lista para predecir (`Endpoint`).

---

## 📋 Scope (Alcance)

El pipeline realiza las siguientes tareas de forma secuencial y automatizada:

1.  **Empaquetado:** Crea un contenedor Docker con tu código de entrenamiento y librerías.
2.  **Publicación:** Sube la imagen a **Artifact Registry** (Europa).
3.  **Entrenamiento (Custom Job):** Lanza un trabajo en la infraestructura de Vertex AI para entrenar un modelo `Scikit-learn`.
4.  **Exportación:** Guarda el modelo resultante (`model.joblib`) en **Cloud Storage**.
5.  **Despliegue:** Crea automáticamente un **Endpoint** en Vertex AI y despliega el modelo para servir predicciones en tiempo real.

---

## ⚙️ Prerrequisitos

Antes de ejecutar, asegúrate de tener:

1.  **APIs Habilitadas:**
    * `aiplatform.googleapis.com` (Vertex AI)
    * `cloudbuild.googleapis.com` (Cloud Build)
    * `artifactregistry.googleapis.com` (Artifact Registry)
2.  **Recursos Creados:**
    * Un Bucket de Storage: `gs://dataflow_vertex`
    * Un Repositorio Docker en Europa: `europe-docker.pkg.dev/formacionaiops-476808/images`

---

## 📂 Estructura del Proyecto

Asegúrate de que tu carpeta tenga estos 4 archivos:

```text
/
├── task.py           # Script de entrenamiento (Matemáticas)
├── deploy.py         # Script de infraestructura (Crear Endpoint)
├── Dockerfile        # Receta para empaquetar el código
└── cloudbuild.yaml   # Pasos del pipeline (Orquestador)
```
https://cloud.google.com/blog/products/identity-security/enabling-keyless-authentication-from-github-actions

