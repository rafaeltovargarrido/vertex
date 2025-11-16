# Agenda — Sesión 1

- **09:00–11:00** · Tema 1: Fundamentos de AIOps en Google Cloud
- **11:00–11:15** · Break (15 minutos)
- **11:15–11:55** · Tema 1 (continuación)
- **11:55–12:00** · Feedback y examen

---
# Sesión 1 — Teoría (Tema 1: Fundamentos de AIOps en Google Cloud)

## 1. Definición y propósito de AIOps
AIOps es la aplicación de técnicas de inteligencia artificial y aprendizaje automático a la operación de sistemas y servicios. Su finalidad es mejorar la detección y el diagnóstico de incidentes, reducir el tiempo medio de recuperación (MTTR), optimizar costes y aumentar la disponibilidad mediante correlación de señales, predicción y automatización de respuestas.

## 2. ITOps, DevOps y AIOps
- **ITOps:** operación tradicional centrada en la ejecución y mantenimiento de infra y aplicaciones, con procesos mayoritariamente manuales y reactivos.
- **DevOps:** enfoque colaborativo que integra desarrollo y operaciones con automatización (CI/CD, IaC) y ciclos de feedback continuos.
- **AIOps:** capa analítica que utiliza datos operativos para detectar anomalías, anticipar fallos y orquestar acciones automáticas o semiautomáticas, potenciando prácticas DevOps y SRE.

## 3. Beneficios principales
- Reducción de MTTR y de falsos positivos de alerta.
- Mejora de la disponibilidad y de la experiencia de usuario.
- Optimización del uso de recursos y de costes operativos.
- Visibilidad integral mediante correlación de métricas, logs y trazas.
- Capacidad de predicción para capacity planning y prevención de incidentes.

## 4. Casos de uso habituales
- Detección y correlación de picos de latencia y errores 5xx en APIs.
- Priorización de incidentes según impacto en el servicio.
- Escalado predictivo en función de la demanda.
- Detección de regresiones tras despliegues y verificación continua.
- Reducción de ruido de alertas mediante agrupación, supresión contextual y desduplicación.

## 5. Relación con SRE: SLIs y SLOs
AIOps se alinea con SRE al utilizar SLIs (latencia, tasa de errores, disponibilidad, saturación) para priorizar y accionar. Las predicciones y detecciones se valoran por su efecto en el cumplimiento de SLOs, de forma que la automatización atienda primero las degradaciones con mayor impacto en el usuario y el negocio.

## 6. Herramientas nativas de Google Cloud para AIOps
### Observabilidad
- **Cloud Monitoring:** métricas, cuadros de mando, SLOs, alertas y *uptime checks*.
- **Cloud Logging:** ingestión, consulta, retención y *routing* de logs.
- **Cloud Trace:** trazas distribuidas para análisis de latencia extremo a extremo.
- **Cloud Profiler:** perfiles de CPU/memoria para localizar ineficiencias.
- **Error Reporting:** agregación y alerta sobre excepciones de aplicaciones.

### Datos y mensajería
- **BigQuery:** almacenamiento histórico y analítica a gran escala; base para *feature stores* y análisis de tendencias.
- **Dataflow:** procesamiento por lotes y *streaming* para ETL y *feature engineering*.
- **Pub/Sub:** mensajería orientada a eventos para desacoplar productores y consumidores y disparar flujos operativos.
- **Cloud Storage:** *data lake* de bajo coste para datasets y artefactos de modelos.

### Automatización y orquestación
- **Cloud Functions / Cloud Run:** ejecución de acciones reactivas y servicios ligeros para *runbooks* automatizados.
- **Workflows:** orquestación declarativa de pasos de remediación y procesos operativos.
- **Eventarc:** enrutamiento de eventos hacia Functions/Run para activar automatizaciones.

### Machine Learning
- **Vertex AI Training y Endpoints:** entrenamiento y despliegue de modelos para inferencia en línea o por lotes.
- **Vertex AI Pipelines:** orquestación reproducible de procesos de ML (MLOps).
- **Model Monitoring:** detección de *drift* y anomalías en datos/predicciones.
- **Feature Store:** gestión centralizada de características con control de versiones.

### Seguridad y gobierno
- **IAM y Cloud Audit Logs:** control de acceso y trazabilidad.
- **Secret Manager:** gestión de secretos para integraciones y despliegues.
- **Cloud Deploy / Artifact Registry / Cloud Build:** cadena de suministro de software para prácticas DevOps que alimentan AIOps.

### Flujo conceptual de datos a acción
```
Observabilidad (Monitoring/Logging/Trace/Profiler/Error Reporting)
          │
      ETL y almacenamiento (Dataflow/BigQuery/Cloud Storage)
          │
            Vertex AI (Feature Store / Training / Endpoints / Monitoring / Pipelines)
          │
  Predicciones y detección de anomalías
          │
 Orquestación de acciones (Pub/Sub, Eventarc, Cloud Functions, Cloud Run, Workflows)
```

## 7. De observabilidad a predicción y auto‑remediación
La madurez operativa progresa desde la visualización de métricas y logs, hacia la detección automática de anomalías, la predicción de riesgos operativos y, finalmente, la auto‑remediación controlada. El componente humano se mantiene para supervisar decisiones críticas y validar cambios en producción.

## 8. Limitaciones y riesgos
- **Datos:** calidad, completitud, sesgos, etiquetado, y representatividad de incidentes raros.
- **Modelos:** *drift*, necesidad de reentrenos y validaciones periódicas, explicabilidad y métricas de rendimiento.
- **Operación:** gobernanza, seguridad y permisos; estrategias de *fallback*; pruebas canary; límites y salvaguardas para automatizaciones.
- **Procesos:** alineación con SRE y gestión del cambio para adoptar decisiones basadas en datos.

## 9. Roadmap de adopción
1. **Piloto acotado:** selección de un servicio y un SLI crítico, definición de objetivos medibles.
2. **Estandarización de pipelines:** ingesta a BigQuery, ingeniería de características, entrenamiento e inferencia en Vertex AI.
3. **Integración operativa:** conexión con runbooks y flujos de acción mediante Pub/Sub, Eventarc, Cloud Functions, Cloud Run y Workflows.
4. **Medición de impacto:** evaluación continua sobre MTTR, disponibilidad, tasa de errores y coste.
5. **Escalado y gobierno:** extensión a más dominios, versionado de modelos y pipelines, políticas de seguridad y auditoría.

## 10. Fin
Examen: https://forms.gle/rAKMaTCMcAHcb4XT9
FeedBack: TODO