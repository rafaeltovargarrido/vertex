# 🔍 AIOps: Descubriendo "Personalidades" de Servidores con IA

Este proyecto demuestra cómo usar **Aprendizaje No Supervisado (K-Means)** en BigQuery ML para auditar automáticamente un parque de servidores.

En lugar de revisar logs uno por uno, dejamos que la IA agrupe los servidores según su comportamiento real (Salud), permitiéndonos detectar anomalías, equipos zombies o saturados sin escribir ni una sola regla `IF/ELSE`.

---

## 🎯 El Objetivo (Caso de Uso)

Imagina que eres responsable de **500 servidores**. No sabes cuáles están funcionando bien, cuáles están rotos y cuáles están "zombies" (encendidos pero sin uso).

**Problema:**
* Las alertas tradicionales (`CPU > 80%`) son ruidosas.
* Revisar logs manualmente es imposible.

**Solución con IA:**
Usamos **K-Means Clustering** para agrupar los servidores en 3 perfiles basándonos en dos métricas clave:
1.  **Tasa de Error (%):** ¿Cuántos logs son `ERROR` o `CRITICAL`?
2.  **Latencia Media (ms):** ¿Cuánto tarda en responder?

---

## 🛠️ Pasos Técnicos (Ejecución en BigQuery)

Sigue estos 4 pasos en la consola de BigQuery para replicar el experimento.

### Paso 1: Generar los Datos (Simulación)
Creamos 500 servidores virtuales con comportamientos ocultos (Sanos, Rotos, Lentos).

```sql
CREATE OR REPLACE TABLE `formacionaiops-476808.test.flask_logs_raw` AS

WITH server_list AS (
  SELECT x as server_id FROM UNNEST(GENERATE_ARRAY(1, 500)) AS x
),
behaviors AS (
  SELECT
    server_id,
    -- 1=Sano, 2=Roto, 3=Lento
    CAST(FLOOR(1 + RAND() * 3) AS INT64) as tipo_comportamiento
  FROM server_list
)

SELECT
  server_id,
  timestamp_sub(CURRENT_TIMESTAMP(), INTERVAL CAST(FLOOR(RAND()*3600) AS INT64) SECOND) as timestamp,
  
  -- Generamos gravedad (ERROR/CRITICAL si está roto)
  CASE
    WHEN tipo_comportamiento = 1 THEN IF(RAND() < 0.95, 'INFO', 'WARNING')
    WHEN tipo_comportamiento = 2 THEN IF(RAND() < 0.60, 'ERROR', 'CRITICAL')
    WHEN tipo_comportamiento = 3 THEN 'INFO'
  END as severity,

  -- Generamos latencia (Alta si es lento)
  CASE
    WHEN tipo_comportamiento = 1 THEN 20 + RAND()*50
    WHEN tipo_comportamiento = 2 THEN 50 + RAND()*100
    WHEN tipo_comportamiento = 3 THEN 2000 + RAND()*5000
  END as latency_ms

FROM behaviors, UNNEST(GENERATE_ARRAY(1, 100)) as log_count;
```


### Paso 2: Preparar el Resumen (Feature Engineering)

La IA no lee logs sueltos. Necesita un resumen por servidor. Calculamos el % de Error y la Latencia Media.

```
CREATE OR REPLACE VIEW `formacionaiops-476808.test.server_health_features` AS
SELECT
  server_id,
  ROUND(COUNTIF(severity IN ('ERROR', 'CRITICAL')) / COUNT(*) * 100, 2) as error_rate_pct,
  ROUND(AVG(latency_ms), 2) as avg_latency_ms
FROM
  `formacionaiops-476808.test.flask_logs_raw`
GROUP BY
  server_id;

```

### Paso 3: Entrenar el Modelo (K-Means)

Le pedimos a BigQuery que encuentre 3 grupos naturales en esos datos.

```
CREATE OR REPLACE MODEL `formacionaiops-476808.test.server_health_clusters`
OPTIONS(
  model_type = 'KMEANS',
  num_clusters = 3,           -- Buscamos 3 perfiles
  standardize_features = TRUE -- Obligatorio para comparar % con ms
) AS
SELECT
  error_rate_pct,
  avg_latency_ms
FROM
  `formacionaiops-476808.test.server_health_features`;
```

### Paso 4: El Reporte Final (Clasificación Automática)

Usamos ML.PREDICT para etiquetar cada servidor. (Nota: Revisa los IDs antes de ejecutar, pueden variar en cada entrenamiento).

```
SELECT
  server_id,
  error_rate_pct,
  avg_latency_ms,
  CENTROID_ID,
  CASE CENTROID_ID
    WHEN 1 THEN '🟢 Servidor Sano'
    WHEN 2 THEN '🔥 CRÍTICO: Tasa de Errores Alta' -- (Alto % Error)
    WHEN 3 THEN '🐢 WARNING: Latencia Degradada'   -- (Alta Latencia)
    ELSE 'Desconocido'
  END as estado_ia
FROM
  ML.PREDICT(MODEL `formacionaiops-476808.test.server_health_clusters`,
    (SELECT * FROM `formacionaiops-476808.test.server_health_features`)
  )
ORDER BY
  error_rate_pct DESC;
```

📊 ¿Qué hemos conseguido?
Automatización: No hemos configurado umbrales manuales.

Visibilidad: Detectamos servidores lentos (latencia alta) aunque no den errores (código 200 OK).

Accionable: Podemos apagar o arreglar los servidores agrupados en los clusters problemáticos cada mañana.


### Paso 5: crear reporte automatico

Primero necesitamos crear la tabla vacía donde se irán guardando los reportes diarios. Fíjate que añadimos la columna report_date.


```
CREATE TABLE IF NOT EXISTS `formacionaiops-476808.test.daily_server_health_report`
(
  report_date DATE,
  server_id INT64,
  error_rate_pct FLOAT64,
  avg_latency_ms FLOAT64,
  centroid_id INT64,
  estado_ia STRING
)
PARTITION BY report_date; -- Particionar por fecha hace que las consultas sean más baratas y rápidas
```

La Query para el Schedule.
Esta es la consulta que vamos a programar. Lo que hace es:

Calcula la fecha de hoy (CURRENT_DATE()).

Ejecuta el modelo (ML.PREDICT) sobre los datos actuales.

Etiqueta los resultados.

Prepara los datos para ser insertados.

```
-- Esta query se ejecutará cada noche automáticamente
SELECT
  CURRENT_DATE() as report_date, -- Fecha de la ejecución (La "foto" del día)
  server_id,
  error_rate_pct,
  avg_latency_ms,
  CENTROID_ID,
  -- ETIQUETADO AUTOMÁTICO (Asegúrate de que los IDs coincidan con tu último entrenamiento)
  CASE CENTROID_ID
    WHEN 1 THEN '🟢 Servidor Sano'
    WHEN 2 THEN '🔥 CRÍTICO: Tasa de Errores Alta'
    WHEN 3 THEN '🐢 WARNING: Latencia Degradada'
    ELSE 'Desconocido'
  END as estado_ia
FROM
  ML.PREDICT(MODEL `formacionaiops-476808.test.server_health_clusters`,
    (SELECT * FROM `formacionaiops-476808.test.server_health_features`)
  );

  ```