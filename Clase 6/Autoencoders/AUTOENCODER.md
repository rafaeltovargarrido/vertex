# 🕵️‍♂️ AIOps: Detección de Ciberataques (Anomalías) con Autoencoders

Este laboratorio demuestra cómo usar **Aprendizaje No Supervisado (Deep Learning)** en BigQuery ML para detectar ciberataques desconocidos.

A diferencia de las reglas tradicionales ("Si sube > 1GB, avisa"), el **Autoencoder** aprende qué es el tráfico "normal" de la empresa y alerta sobre cualquier cosa que se desvíe de ese patrón, permitiendo detectar ataques de día cero o exfiltraciones sutiles.

---

## 🎯 El Caso de Uso: Exfiltración de Datos

**El Escenario:**
Los empleados de la empresa navegan por internet (descargan mucho, suben poco) y hacen videollamadas.
Un hacker ha infectado un servidor y está intentando **robar datos (exfiltración)**: subiendo archivos pesados en muy poco tiempo.

**El Desafío:**
* No tenemos etiquetas de "Ataque" anteriores.
* El hacker intenta pasar desapercibido.

**La Solución:**
Entrenamos un **Autoencoder** solo con datos normales. Cuando el modelo intente procesar el ataque, "fallará" matemáticamente (error de reconstrucción alto), y esa será nuestra alerta.

---

## 🛠️ Pasos Técnicos (Ejecución en BigQuery)

### Paso 1: Generar Datos de Entrenamiento (Lo "Normal")
Simulamos tráfico legítimo (Navegación Web y Video).
* **Web:** Mucha bajada, casi nula subida.
* **Video:** Bajada y subida moderadas, duración larga.

```sql
CREATE OR REPLACE TABLE `formacionaiops-476808.test.network_traffic_train` AS

WITH GENERATOR AS (
  SELECT x FROM UNNEST(GENERATE_ARRAY(1, 5000)) AS x
),
RAW_DATA AS (
  SELECT
    x as connection_id,
    -- Simulamos tráfico normal
    IF(RAND() < 0.7, 'WEB', 'VIDEO') as traffic_type,
    RAND() as ruido
  FROM GENERATOR
)

SELECT
  connection_id,
  CASE
    WHEN traffic_type = 'WEB' THEN ROUND(500 + (ruido * 2000), 2)   -- Download (Normal)
    WHEN traffic_type = 'VIDEO' THEN ROUND(5000 + (ruido * 5000), 2)
  END as bytes_received,

  CASE
    WHEN traffic_type = 'WEB' THEN ROUND(10 + (ruido * 50), 2)      -- Upload (Bajo)
    WHEN traffic_type = 'VIDEO' THEN ROUND(2000 + (ruido * 2000), 2)
  END as bytes_sent,

  CASE
    WHEN traffic_type = 'WEB' THEN ROUND(1 + (ruido * 60), 2)       -- Duración
    WHEN traffic_type = 'VIDEO' THEN ROUND(600 + (ruido * 3000), 2)
  END as duration_sec

FROM RAW_DATA;

```

### Paso 2: Entrenar el Autoencoder ("Enseñar la Normalidad")
Creamos una Red Neuronal con forma de "reloj de arena". Intenta comprimir los datos y descomprimirlos. Aprenderá la correlación entre Subida, Bajada y Tiempo.


```
CREATE OR REPLACE MODEL `formacionaiops-476808.test.anomaly_detector_network`
OPTIONS(
  model_type = 'AUTOENCODER',
  activation_fn = 'RELU',
  batch_size = 16,
  dropout = 0.1,                      -- Técnica para evitar memorización exacta
  hidden_units = [32, 16, 4, 16, 32]  -- Arquitectura de "Cuello de botella" (Compresión)
) AS
SELECT
  bytes_received,
  bytes_sent,
  duration_sec
FROM
  `formacionaiops-476808.test.network_traffic_train`;
```
### Paso 2.1: Verificar la "Normalidad" (Línea Base) 🆕
Antes de atacar, probamos el modelo con los propios datos normales para establecer una Línea Base. Queremos ver qué error da cuando "todo va bien".

Objetivo: Confirmar que el error de reconstrucción es bajo.

Contamination = 0.0: Asumimos que estos datos están limpios.


```
SELECT
  *
FROM
  ML.DETECT_ANOMALIES(
    MODEL `formacionaiops-476808.test.anomaly_detector_network`,
    STRUCT(0.0 AS contamination),
    (SELECT * FROM `formacionaiops-476808.test.network_traffic_train` LIMIT 100)
  )
ORDER BY
  mean_squared_error DESC;
```

Nota: Deberías ver un mean_squared_error muy pequeño (ej: 0.5 o 1.2). Recuerda este número, será tu referencia de "Normalidad".


### Paso 3: Simular el Ataque (Datos de Prueba)
Creamos un set de datos nuevo que mezcla tráfico inocente con 5 conexiones de hackers.

El Ataque: Sube 50 MB (bytes_sent = 50000) en solo 10 segundos.


```
CREATE OR REPLACE TABLE `formacionaiops-476808.test.network_traffic_test` AS

-- 1. Tráfico Normal (Para despistar y validar falsos positivos)
SELECT
  CONCAT('test_normal_', x) as connection_id,
  500.0 as bytes_received,
  20.0 as bytes_sent,
  30.0 as duration_sec
FROM UNNEST(GENERATE_ARRAY(1, 100)) as x

UNION ALL

-- 2. EL ATAQUE (Exfiltración Masiva)
SELECT
  CONCAT('ATTACK_HACKER_', x) as connection_id,
  10.0 as bytes_received,
  50000.0 as bytes_sent, -- <--- ANOMALÍA: Upload masivo
  10.0 as duration_sec   -- <--- ANOMALÍA: Tiempo muy corto
FROM UNNEST(GENERATE_ARRAY(1, 5)) as x;
```

### Paso 4: La Detección (El Momento de la Verdad)

Usamos ML.DETECT_ANOMALIES.

Contamination: Le decimos al modelo que esperamos que aprox. el 5% de los datos sean "raros".

```
SELECT
  *
FROM
  ML.DETECT_ANOMALIES(
    MODEL `formacionaiops-476808.test.anomaly_detector_network`,
    STRUCT(0.05 AS contamination),
    (SELECT * FROM `formacionaiops-476808.test.network_traffic_test`)
  )
ORDER BY
  mean_squared_error DESC; -- Los errores más grandes arriba (Los ataques)
```


### Interpretación de Resultados
Al ejecutar la última query, fíjate en la columna mean_squared_error (Error de reconstrucción):

Tráfico Normal: El error será bajo (ej: 0.5). El modelo dice: "Esto me lo sé, encaja en mis patrones".

Ataque (HACKER): El error será GIGANTE (ej: 400.0 o más). El modelo dice: "¡Imposible! Nunca he visto tanto Upload en tan poco tiempo. No sé comprimir esto."