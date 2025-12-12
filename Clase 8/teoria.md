# Tema 12 – IA Generativa en AIOps con Vertex AI

## 0. Objetivo del tema

En este tema veremos cómo la **IA generativa** (principalmente LLMs) puede reducir el “toil” de Operaciones y SRE, acelerando:

- La creación de documentación técnica.
- La explicación y análisis de incidencias.
- La generación de resúmenes ejecutivos.
- La construcción de chatbots internos de soporte IT.
- La formación continua de los equipos de Operaciones.

Todo ello apoyado en **Vertex AI** (especialmente Generative AI Studio, APIs y endpoints) y datos provenientes de **Cloud Logging, Cloud Monitoring, BigQuery y Pub/Sub**.

---

## 1. Introducción a la IA generativa aplicada a Operaciones

### 1.1. ¿Qué es IA generativa?

La IA generativa agrupa modelos capaces de **producir contenido nuevo** (texto, código, resúmenes, explicaciones, etc.) a partir de un *prompt* o contexto de entrada.

En AIOps, el foco es principalmente en:

- **Texto técnico**: resúmenes de logs, explicaciones de métricas, descripciones de incidentes.
- **Código / consultas**: sugerir reglas de alerta, consultas en BigQuery, ejemplos de scripts, etc.
- **Documentación estructurada**: runbooks, playbooks, informes post-mortem, FAQs internas.

### 1.2. Diferencia con modelos “clásicos” de ML en AIOps

Hasta ahora en el curso, nos hemos centrado en:

- Modelos de predicción de series temporales (p.ej. carga, coste, capacidad).
- Modelos de clasificación / regresión para incidentes, anomalías, etc.

La IA generativa añade capacidades **cualitativas y de lenguaje natural**, útiles cuando el trabajo de Operaciones y SRE implica:

- Leer grandes volúmenes de logs / eventos.
- Comunicar incidencias a audiencias distintas (negocio vs técnico).
- Mantener documentación actualizada.

### 1.3. ¿Por qué es relevante para SRE e IT Operations?

- Reduce el tiempo invertido en **documentar y comunicar incidentes**.
- Estandariza el lenguaje utilizado en **post-mortems, informes y tickets**.
- Facilita la transferencia de conocimiento entre equipos (SRE, Dev, Soporte, NOC).
- Acelera el **onboarding** de nuevos ingenieros de Operaciones.

---

## 2. Generación de documentación técnica automática

### 2.1. Problema habitual en Operaciones

En muchos equipos de SRE / Operaciones:

- Los **runbooks** están desactualizados.
- Los **post-mortems** se redactan tarde o con poca calidad.
- La **documentación de alertas** y pipelines de observabilidad no está normalizada.

La IA generativa permite **convertir datos operativos** (logs, métricas, timelines de incidentes) en documentación legible casi en tiempo real.

### 2.2. Fuentes de datos para la documentación

Ejemplos de fuentes:

- **Cloud Logging**: eventos de error, stacktraces, payloads HTTP relevantes.
- **Cloud Monitoring**: métricas de CPU, latencia, saturación, errores 5xx, etc.
- **BigQuery**: datasets históricos de incidencias y costes.
- **Sistemas ITSM / ticketing** (Jira, ServiceNow): descripciones y estados de tickets.

### 2.3. Patrón típico en Vertex AI

1. **Extracción de datos**  
   - Desde BigQuery o APIs (Logging / Monitoring) se prepara un dataset con:
     - Timeline del incidente.
     - Métricas clave.
     - Logs representativos.

2. **Construcción del prompt**  
   - Se crea un prompt “plantilla” que instruye al modelo, por ejemplo:
     - Rol: “Eres un SRE senior que redacta documentación técnica”.
     - Tono: técnico, claro, conciso.
     - Formato: secciones fijas (Impacto, Causa raíz, Timeline, Acciones correctivas).

3. **Llamada al modelo generativo de Vertex AI**  
   - Uso de Vertex AI para enviar el contexto + prompt.
   - El modelo devuelve un documento estructurado (Markdown, HTML o texto plano).

4. **Almacenamiento del resultado**  
   - Guardar la documentación en:
     - Repositorio Git (runbooks versionados).
     - Confluence / Wiki de la organización.
     - Tablas en BigQuery para trazabilidad.

### 2.4. ¿Por qué hacerlo en Vertex AI?

- Centraliza la **gestión de modelos** (versiones, autorización, monitorización).
- Facilita el despliegue usando **endpoints** que pueden ser llamados desde Cloud Run, Functions o Workflows.
- Permite combinar IA generativa con modelos clásicos (por ejemplo, primero detectar anomalías, luego generar el informe).

---

## 3. Uso de LLMs para explicar incidencias

### 3.1. Explicar para entender mejor

El valor de un LLM no solo está en producir texto, sino en **reexplicar** información compleja:

- Transformar logs crípticos en explicaciones comprensibles.
- Conectar síntomas (errores 5xx, picos de latencia) con posibles causas técnicas.
- Adaptar la explicación al nivel de la audiencia:
  - “Explícalo para un desarrollador junior”.
  - “Explícalo a un Product Manager no técnico”.

### 3.2. Flujo típico

1. **Recopilación automática**  
   - Cloud Logging y Monitoring generan una “foto” del incidente (ventana de tiempo relevante).
   - Un proceso (Cloud Run / Function) agrega información en un payload estructurado (JSON).

2. **Contexto + prompt**  
   - Prompt tipo:
     - “Resume los eventos y explica qué ha pasado, cuáles son las hipótesis de causa y qué métricas deberían revisarse”.

3. **Respuesta del modelo**  
   - El LLM devuelve un texto estructurado:
     - Resumen del incidente.
     - Hipótesis de causa raíz.
     - Métricas / paneles que conviene revisar.
     - Posibles acciones de mitigación.

4. **Uso práctico**  
   - Publicar la explicación en:
     - Canal de incidentes de Slack / Google Chat.
     - Ticket de Jira/ServiceNow.
     - Página del post-mortem.

### 3.3. Beneficios

- Acelera el **entendimiento compartido** durante el incidente.
- Sirve de base para que el SRE valide y refine, en vez de escribir desde cero.
- Reduce la carga cognitiva en situaciones de estrés (incidentes críticos).

---

## 4. Creación de resúmenes de incidentes

### 4.1. Resúmenes operativos y ejecutivos

Podemos generar distintos tipos de resumen:

- **Técnico** (para SRE / Dev):
  - Detalles de logs, métricas, servicios afectados.
- **Ejecutivo** (para negocio / management):
  - Impacto en usuarios, duración, nivel de servicio afectado (SLO/SLA), coste aproximado.

### 4.2. Estructura recomendada de un resumen

Un resumen generado por IA puede seguir un formato estándar:

1. Impacto (qué servicios y usuarios se vieron afectados).
2. Línea temporal (inicio, detección, mitigación, resolución).
3. Causa raíz (si está confirmada).
4. Acciones inmediatas realizadas.
5. Plan de acciones preventivas y mejoras.

### 4.3. Proceso con Vertex AI

- Desde Vertex AI Generative AI Studio se diseña el **prompt base** de los resúmenes.
- Se prueba con incidentes históricos para ajustar:
  - Longitud, nivel de detalle, terminología.
- Una vez validado, se expone mediante **endpoint de predicción**.
- Se integra con el gestor de incidentes para generar el resumen automáticamente al cerrar el ticket.

---

## 5. Integración con Vertex AI Generative AI Studio

### 5.1. ¿Qué es Generative AI Studio?

Es la interfaz de Vertex AI en la consola de GCP donde:

- Se prueban modelos generativos (texto, chat, código).
- Se diseñan y ajustan prompts.
- Se configuran parámetros (temperatura, longitud, etc.).
- Se validan ejemplos antes de ir a producción.

### 5.2. Flujo recomendado para casos de AIOps

1. **Prototipado en el Studio**
   - Pegamos ejemplos de logs, alertas y descripciones reales.
   - Ajustamos el prompt hasta que el modelo:
     - Use la nomenclatura interna de la empresa (nombres de servicios, SLAs, etc.).
     - Devuelva exactamente la estructura deseada (ej. Markdown con secciones específicas).

2. **Definición de plantillas de prompts**
   - Se documentan como “plantillas” estándar:
     - Prompt para resúmenes de incidentes.
     - Prompt para runbooks.
     - Prompt para chatbots de soporte interno.

3. **Industrialización**
   - El prompt se lleva al backend (Cloud Run / Functions / Workflows).
   - Se invoca el modelo de Vertex AI desde código usando el mismo prompt ajustado en el Studio.
   - Se añaden controles: logging, trazabilidad, timeouts, reintentos.

4. **Monitorización**
   - Se monitoriza:
     - Latencia de las llamadas al modelo.
     - Coste por número de tokens / peticiones.
     - Calidad percibida (feedback de usuarios internos).

### 5.3. ¿Por qué pasar siempre por el Studio antes de código?

- Permite al equipo de SRE **iterar rápidamente en prompts** sin despliegues.
- Facilita la colaboración con otros roles (arquitectos, Dev, managers).
- Reduce errores de diseño en la API (se prueba primero la lógica de lenguaje).

---

## 6. Casos de chatbots internos para soporte IT

### 6.1. Objetivo de un chatbot interno

Un chatbot interno puede:

- Responder dudas frecuentes de SRE, DevOps y desarrolladores.
- Guiar sobre cómo actuar ante ciertos síntomas (errores 5xx, alertas de CPU, saturación de pods).
- Explicar procedimientos: “¿cómo reinicio este servicio en Kubernetes?”, “¿qué dashboard reviso para latencia de X?”.

### 6.2. Arquitectura típica con Vertex AI

1. **Fuente de conocimiento**
   - Documentación interna (Confluence, Git, Markdown).
   - Runbooks y post-mortems históricos.
   - Esquemas de infraestructura y pipelines CI/CD.

2. **Ingesta y búsqueda**
   - Indexar el contenido en:
     - BigQuery.
     - Vertex AI Search / Enterprise Search (si se usa).
   - Se habilita un mecanismo de **RAG (Retrieval-Augmented Generation)**:
     - Buscar documentos relevantes.
     - Incluir fragmentos en el contexto del prompt.

3. **Modelo generativo**
   - Un modelo de Vertex AI recibe:
     - Pregunta del usuario.
     - Fragmentos relevantes de documentación.
   - Responde con una respuesta específica, citando la fuente interna.

4. **Canales de acceso**
   - Interfaz web interna.
   - Integración con Google Chat / Slack.
   - Posible integración con herramientas de NOC.

### 6.3. Consideraciones de seguridad

- Limitar el contexto a **información autorizada** según el usuario (IAM / grupos).
- Registrar todas las preguntas y respuestas para auditoría.
- Evitar exponer información sensible (claves, contraseñas, datos personales) presente en logs.

---

## 7. Aplicaciones en formación y capacitación

### 7.1. Generación de contenido formativo

La IA generativa puede acelerar la formación de equipos de Operaciones:

- Creación de:
  - Cuestionarios sobre incidentes reales de la organización.
  - Escenarios de simulación (“game days” o “chaos drills”).
  - Explicaciones adaptadas al nivel de cada perfil.

### 7.2. Uso de datos reales (anónimos)

- A partir de incidentes históricos (almacenados en BigQuery / sistemas ITSM) el modelo puede:
  - Crear enunciados de ejercicios.
  - Proponer preguntas tipo test o escenarios abiertos.
- Importante: **anonimizar** datos sensibles antes de usarlos como contexto.

### 7.3. Beneficio

- Acelera el diseño de contenido de formación.
- Permite entrenar a nuevos SRE con **casos reales** de la propia plataforma.

---

## 8. Limitaciones actuales de la IA generativa

### 8.1. Alucinaciones

Los modelos generativos pueden inventar detalles:

- Explicar causas que no están respaldadas por datos.
- Mencionar servicios, dashboards o métricas inexistentes.

Mitigación:

- Siempre proporcionar **contexto real** (logs, métricas, documentos).
- Indicar en el prompt que no debe inventar información si no aparece en el contexto.
- Requerir que el modelo indique cuando “no tiene suficiente información”.

### 8.2. Actualización y frescura

- El modelo base puede no conocer:
  - Tecnologías muy nuevas.
  - Particularidades internas de la empresa.
- Se necesita **RAG** o contexto dinámico para compensar.

### 8.3. Privacidad y cumplimiento

- Los logs y métricas pueden contener:
  - Datos de usuarios.
  - Identificadores sensibles.
- Es crítico:
  - Filtrar / anonimizar antes de enviar al modelo.
  - Respetar normativas (GDPR, políticas internas de seguridad).

### 8.4. Coste y latencia

- Llamadas frecuentes al modelo pueden tener un coste relevante.
- Latencias de varios cientos de ms o segundos pueden ser aceptables para:
  - Documentación y resúmenes.
- Pero no para **paths críticos de baja latencia** (p.ej. tráfico de usuario final).

---

## 9. Beneficios en la comunicación de incidentes

### 9.1. Un lenguaje común

- Un modelo bien ajustado crea textos consistentes:
  - Estructura homogénea de incidentes.
  - Terminología alineada con la cultura SRE de la organización.

### 9.2. Adaptación a diferentes audiencias

- A partir de la misma información de base:
  - Un resumen técnico para el equipo SRE.
  - Un resumen ejecutivo para dirección.
- Esto evita que el SRE tenga que “traducir” manualmente el problema varias veces.

### 9.3. Comunicación multilingüe

- Posibilidad de:
  - Redactar en un idioma base (ej. inglés) y traducir a otros (ej. español) o viceversa.
  - Reducir fricción en equipos globales.

---

## 10. Ejemplos de casos reales (patrones)

> Nota: estos ejemplos son patrones genéricos basados en prácticas habituales en AIOps; el objetivo es ilustrar cómo podría usarse Vertex AI en entornos reales de operaciones.

### 10.1. Resumen automático en canales de incidentes

- Un pipeline en GCP:
  - Escucha alertas críticas de Cloud Monitoring vía Pub/Sub.
  - Recoge métricas y logs de una ventana de tiempo.
  - Invoca un modelo de Vertex AI que genera:
    - Un resumen técnico instantáneo.
  - Envía el resumen a un canal de “#incidentes-criticos” en Google Chat.

### 10.2. Asistente SRE para Kubernetes

- Chatbot interno que:
  - Le das un log de pod en CrashLoopBackOff + descripción del síntoma.
  - El modelo explica:
    - Posibles causas.
    - Pasos sugeridos de diagnóstico.
    - Referencias a runbooks internos.

### 10.3. Post-mortems semiautomáticos

- Tras cerrar un incidente:
  - Se dispara un workflow (Cloud Workflows) que:
    - Consulta el timeline de tickets y alertas.
    - Llama a Vertex AI para generar un primer borrador de post-mortem.
  - El SRE responsable revisa, corrige y aprueba el documento.

---

## 11. Resumen del Tema 12

En este tema hemos visto que la **IA generativa** aplicada a AIOps no sustituye a los equipos de Operaciones o SRE, sino que:

- **Reduce el trabajo repetitivo** (redacción de informes, resúmenes, documentación).
- Mejora la **comunicación interna y externa** de los incidentes.
- Acelera la **formación** y el **onboarding** en entornos complejos.
- Se integra de forma natural con el ecosistema de GCP:
  - Vertex AI (Generative AI Studio, endpoints).
  - Cloud Logging, Cloud Monitoring, BigQuery y Pub/Sub.

El reto principal para los equipos SRE es **diseñar bien los flujos**, prompts y controles alrededor de estos modelos, asegurando:

- Calidad de la información.
- Seguridad y cumplimiento.
- Coste y latencia razonables.


https://forms.gle/15Gh111zhcQawv379

FeedBack: (https://imagina-formacion.typeform.com/to/IkO83DnN)
