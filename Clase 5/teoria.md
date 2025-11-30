# Clase 5 – Integración de logs y detección de anomalías con Vertex AI  
**Temas 6 y 7**

---

## 1. Objetivos de la clase

Al finalizar esta clase, el alumno será capaz de:

- Entender cómo integrar logs y eventos con los servicios de Google Cloud y Vertex AI.
- Explicar cómo se construye un pipeline de datos desde los logs hasta los modelos de IA.
- Comprender los conceptos básicos de detección de anomalías en infraestructura.
- Describir cómo Vertex AI y Cloud Monitoring se combinan para detectar y priorizar anomalías.
- Reconocer las limitaciones y métricas de efectividad de un sistema de detección de anomalías.

---

## 2. Tema 6: Integración de logs y eventos con Vertex AI

### 2.1. Visión general del flujo de datos

Los logs y eventos son la materia prima para AIOps. El flujo típico en Google Cloud es:

1. Aplicaciones e infraestructura generan logs y métricas.
2. Cloud Logging centraliza y almacena los logs.
3. Mediante sinks, los logs se envían a Pub/Sub, BigQuery o Cloud Storage.
4. Dataflow procesa y transforma eventos (en streaming o batch).
5. Los datos limpios se usan en Vertex AI / BigQuery ML para entrenar modelos.
6. Los resultados se devuelven a dashboards, alertas y sistemas de automatización.

**Idea clave:** pasar de “guardar logs” a “usar los logs como señal inteligente para tomar decisiones”.

---

### 2.2. Recolección de logs en Cloud Logging

Cloud Logging recibe eventos desde:

- Servicios gestionados de GCP: GKE, Compute Engine, Cloud Run, Load Balancer, etc.
- Aplicaciones que escriben en stdout/stderr (contenedores) o usan librerías de logging.
- Fuentes externas mediante agentes (Ops Agent, Fluent Bit) o API.

Conceptos importantes:

- **Log entry**: cada evento de log (timestamp, severidad, recurso, etiquetas, payload).
- **Buckets** de Logging: almacenan los logs con sus políticas de retención.
- **Log Router y Sinks**:
  - Filtran los logs según condiciones.
  - Envían los logs a destinos como Pub/Sub, BigQuery o Cloud Storage.

Buenas prácticas:

- Etiquetar logs con `service`, `environment`, `version`, `region`.
- Separar buckets por entorno (producción, preproducción, desarrollo).

---

### 2.3. Normalización de datos para modelos de IA

Antes de entrenar un modelo, los datos deben estar limpios y consistentes.

1. **Unificación de formatos**
   - Timestamps en formato estándar (UTC).
   - Tipos de datos consistentes para campos numéricos (latencia, código de estado, etc.).

2. **Limpieza de texto**
   - Eliminar IDs aleatorios o trazas largas que no aportan valor a la predicción.
   - Normalizar mensajes: minúsculas, quitar caracteres extraños.

3. **Creación de nuevas características (feature engineering)**
   - Agrupar códigos de error (`5xx`, `4xx`).
   - Contar errores por minuto, por servicio, por usuario.
   - Añadir contexto temporal: hora del día, día de la semana, festivo/laborable.

Herramientas típicas:

- **BigQuery** para procesamiento batch.
- **Dataflow** para procesamiento en streaming.

---

### 2.4. Detección de anomalías a partir de logs

A partir de los logs se pueden detectar comportamientos anómalos, por ejemplo:

- Incremento repentino de errores `500`.
- Aparición de mensajes de error nunca vistos.
- Cambios bruscos en la frecuencia de ciertos eventos (inicios de sesión fallidos, timeouts).

Enfoques:

- **Reglas simples**:
  - Umbrales fijos o dinámicos sobre contadores de logs.
- **Modelos estadísticos**:
  - Media, desviación estándar, percentiles.
- **Modelos de IA**:
  - Clasificación: normal vs anómalo.
  - Métodos no supervisados: clustering, outlier detection.

Vertex AI permite entrenar y desplegar estos modelos para integrarlos con los logs.

---

### 2.5. Uso de Pub/Sub para transmisión en tiempo real

Para trabajar en tiempo real con los logs:

1. Crear un **sink** en Cloud Logging con destino a un **topic de Pub/Sub**.
2. Cada log que cumpla el filtro se publica en el topic.
3. Los consumidores se suscriben al topic:
   - Pipelines de Dataflow (streaming).
   - Servicios en Cloud Run / Cloud Functions.
   - Procesos que llaman a modelos desplegados en Vertex AI.

Ventajas:

- Desacopla productores y consumidores.
- Permite escalar el procesamiento de eventos.
- Facilita arquitecturas basadas en eventos (**event-driven AIOps**).

---

### 2.6. Enriquecimiento de logs con datos adicionales

Los logs se pueden enriquecer añadiendo contexto:

- **Infraestructura**: tipo de máquina, zona, etiquetas de coste, cluster.
- **Negocio**: tipo de cliente, importancia de la transacción, criticidad del servicio.
- **Topología**: dependencias entre servicios, niveles de SLA.

Fuentes de información:

- Tablas de referencia en BigQuery (CMDB, catálogo de servicios).
- APIs internas que devuelven metadatos de clientes o servicios.

Este enriquecimiento se realiza normalmente en Dataflow o en BigQuery mediante joins.

---

### 2.7. Procesamiento de eventos con Dataflow

Dataflow permite crear pipelines de:

- **Streaming**: lectura de Pub/Sub y escritura a BigQuery, Storage u otros sistemas.
- **Batch**: procesamiento de grandes volúmenes de logs históricos.

Funciones típicas de un pipeline:

- Filtrar y agrupar logs por servicio y ventana de tiempo.
- Calcular métricas agregadas (errores por minuto, latencia media, usuarios únicos).
- Enriquecer eventos con datos de negocio.
- Generar features para modelos y almacenarlas en BigQuery.
- Invocar modelos de Vertex AI para obtener predicciones online.

---

### 2.8. Análisis semántico de logs con IA

Los mensajes de log contienen texto valioso (errores, stacktraces). Mediante IA se puede:

- **Clasificar mensajes** por tipo de problema (red, base de datos, aplicación, seguridad, etc.).
- **Detectar nuevos tipos de errores** usando embeddings y clustering.
- **Resumir incidentes** a partir de múltiples mensajes similares.

Pasos generales:

1. Transformar el texto en vectores (embeddings) con modelos de Vertex AI.
2. Usar clustering o modelos de clasificación para agrupar o etiquetar mensajes.
3. Utilizar las etiquetas para enrutar incidencias, generar dashboards y priorizar trabajos.

---

### 2.9. Integración con Vertex AI para clasificación automática

Caso de uso: clasificación automática de eventos en categorías como:

- `INFO_RUIDO`
- `ALERTA_CAPACIDAD`
- `INCIDENTE_CRÍTICO`

Pasos:

1. Construir un dataset con logs históricos etiquetados.
2. Entrenar un modelo en Vertex AI (AutoML o modelo personalizado).
3. Evaluar rendimiento y ajustar umbrales de decisión.
4. Desplegar un endpoint de predicción.
5. Integrar el endpoint en pipelines de Dataflow o servicios en Cloud Run.

Resultado:

- Cada nuevo evento obtiene una etiqueta y una probabilidad.
- Se pueden generar nuevas entradas de log enriquecidas o métricas en Cloud Monitoring.

---

### 2.10. Visualización de resultados en dashboards

Con los datos enriquecidos y las predicciones del modelo se construyen dashboards:

- **Cloud Monitoring**:
  - Métricas de errores por tipo, número de anomalías, probabilidad de incidente.
  - Dashboards por servicio, entorno y región.
- **Looker Studio / Grafana** sobre BigQuery:
  - Exploración histórica y análisis detallado.
  - Comparaciones entre periodos, servicios y regiones.

Recomendaciones:

- Dashboards operativos (tiempo real) y de tendencias (histórico).
- Filtros por servicio, entorno, severidad, tipo de anomalía.

---

## 3. Tema 7: Detección de anomalías en infraestructura

### 3.1. Qué son anomalías en sistemas IT

Una anomalía es un comportamiento que se desvía significativamente del patrón normal esperado.

Ejemplos:

- Latencia que se dispara frente a días anteriores.
- Caída brusca en el número de peticiones.
- Uso de CPU muy alto sostenido en un nodo específico.
- Tráfico de red inusual hacia IPs o regiones no habituales.

No todas las anomalías son incidentes, pero todas son señales que pueden anticipar problemas.

---

### 3.2. Métodos estadísticos vs IA para detección

#### Métodos estadísticos tradicionales

- Umbrales fijos (CPU > 80% durante 5 minutos).
- Umbrales dinámicos (media ± 3 desviaciones estándar).
- Percentiles (P95 de latencia por encima de un valor).

Ventajas:
- Simples de configurar.
- Fáciles de interpretar.

Desventajas:
- Falsos positivos en sistemas muy dinámicos.
- Falsos negativos cuando los patrones son complejos.

#### Métodos basados en IA

- Modelos de series temporales.
- Modelos de clustering o aislamiento de outliers.
- Modelos supervisados (clasificación normal / anómalo).

Ventajas:
- Se adaptan a estacionalidad y patrones complejos.
- Usan múltiples métricas a la vez.

Desventajas:
- Mayor complejidad de diseño y mantenimiento.
- Necesidad de buen volumen y calidad de datos.

En AIOps se combinan reglas simples con modelos avanzados para obtener mejores resultados.

---

### 3.3. Uso de AutoML en Vertex AI para detectar anomalías

Cuando existen datos históricos etiquetados, AutoML Tabular permite construir rápidamente un modelo:

1. Crear un dataset en BigQuery:
   - Cada fila representa una ventana de tiempo (ej. 1 minuto).
   - Campos: métricas agregadas (CPU, RAM, latencia, errores, QPS, etc.).
   - Metadatos: servicio, región, tipo de máquina, hora del día.
   - Etiqueta: `normal` o `anómalo`.

2. Importar el dataset a Vertex AI y entrenar un modelo AutoML de clasificación.

3. Evaluar el modelo:
   - Precision, recall, AUC.
   - Seleccionar umbrales que equilibren falsos positivos y negativos.

4. Desplegar el modelo:
   - **Batch prediction** para análisis diarios sobre BigQuery.
   - **Online prediction** para casi tiempo real desde Dataflow o servicios en Cloud Run.

---

### 3.4. Integración con métricas de Cloud Monitoring

Cloud Monitoring es la fuente de métricas de infraestructura y aplicaciones.

Tipos de métricas:

- CPU, memoria, disco, tráfico de red.
- Latencia, tasas de error, número de peticiones.
- Custom metrics definidas por el usuario.

Flujo típico:

1. Exportar métricas históricas de Monitoring a BigQuery.
2. Entrenar modelos de detección de anomalías en Vertex AI con esos datos.
3. Generar predicciones y devolverlas como:
   - Nuevas custom metrics (`anomaly_score`).
   - Eventos en Pub/Sub que disparan alertas y automatizaciones.

Con esto se pueden crear políticas de alerta basadas en `anomaly_score` en lugar de solo umbrales fijos.

---

### 3.5. Identificación de patrones fuera de lo común

Un modelo de anomalías debe distinguir entre:

- Picos esperados (horario laboral, campañas, cierre de mes).
- Cambios estructurales (nueva versión, nueva arquitectura).
- Comportamientos realmente anómalos.

Para ello se usan:

- Ventanas deslizantes con estadísticas históricas.
- Features temporales (hora, día, fines de semana, festivos).
- Modelos multivariantes que relacionan varias métricas (CPU, errores, latencia).

El objetivo es alertar solo cuando la señal rompe claramente el patrón habitual.

---

### 3.6. Priorización de anomalías según impacto

No todas las anomalías tienen la misma importancia. Se pueden priorizar usando:

- **Impacto técnico**:
  - Servicio crítico, entorno de producción, cercanía a SLOs.
- **Impacto de negocio**:
  - Usuarios afectados, ingresos en riesgo, procesos clave.
- **Contexto de seguridad**:
  - Anomalías que pueden indicar ataques o fugas de datos.

Se puede definir una puntuación de riesgo, por ejemplo:

> `risk_score = prob_anomalia × criticidad_servicio × impacto_negocio`

Esta puntuación ayuda a ordenar alertas y decidir cuáles requieren atención inmediata o automatización.

---

### 3.7. Casos prácticos en redes y seguridad

Ejemplos de uso en redes:

- Aumento inusual de tráfico saliente desde una VM.
- Incremento de errores de conexión entre microservicios.
- Cambios bruscos de latencia entre zonas o regiones.

Ejemplos de uso en seguridad:

- Pico de intentos de login fallidos en poco tiempo.
- Accesos a horas no habituales o desde países inesperados.
- Tráfico hacia puertos no utilizados o servicios no expuestos.

En estos casos, la detección temprana puede prevenir incidentes graves.

---

### 3.8. Automatización de respuestas a anomalías

Una vez detectadas las anomalías, se pueden automatizar acciones:

- **Escalado automático**:
  - Aumentar o reducir réplicas al detectar anomalías de capacidad.
- **Gestión de despliegues**:
  - Rebajar tráfico hacia una versión problemática (canary, rollback).
- **Seguridad**:
  - Bloquear IPs sospechosas, revocar credenciales, aislar recursos.
- **Gestión de incidencias**:
  - Crear tickets automáticamente en Jira, ServiceNow, PagerDuty.
  - Adjuntar contexto (métricas, logs, sugerencias generadas por IA).

Herramientas típicas:

- Cloud Functions / Cloud Run reaccionando a eventos de Pub/Sub.
- Workflows o Cloud Composer para orquestar procesos más complejos.

---

### 3.9. Limitaciones de la detección de anomalías

Aspectos a considerar:

- Falsos positivos que generan “ruido” y fatiga en el equipo.
- Falsos negativos que dejan pasar incidentes críticos.
- Dependencia de la calidad de datos (métricas mal medidas o incompletas).
- Cambios en el sistema que requieren reentrenar modelos (concept drift).
- Coste de cómputo y almacenamiento para mantener históricos y modelos.

Es necesario monitorizar y revisar periódicamente los modelos y reglas.

---

### 3.10. Métricas de efectividad en la detección

Para evaluar la efectividad del sistema de anomalías se utilizan:

#### Métricas de modelo

- **Precision**: de las anomalías detectadas, cuántas eran realmente problemas.
- **Recall**: de todos los problemas reales, cuántos fueron detectados.
- **F1-score**: equilibrio entre precision y recall.

#### Métricas operativas

- Reducción del **MTTR** (Mean Time To Repair).
- Número de incidentes graves no detectados a tiempo.
- Cantidad de alertas por día/persona.

#### Métricas de negocio

- Mejora en la disponibilidad (cumplimiento de SLA/SLO).
- Reducción de impacto económico por caídas o degradaciones.

---

## 4. Idea clave de la Clase 5

- Los logs y eventos, correctamente recolectados, normalizados y enriquecidos, son la base de AIOps.
- Vertex AI y Cloud Monitoring permiten construir sistemas inteligentes de detección de anomalías que entienden el contexto y el impacto de negocio.
- La combinación de reglas simples, modelos de IA y automatización reduce el ruido de alertas y mejora la capacidad de respuesta ante incidentes.


## FIN

Examen: https://forms.gle/4nbovSEABPR7MT9V8
FeedBack: (https://imagina-formacion.typeform.com/to/IkO83DnN)