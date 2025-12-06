# Detección de Anomalías en Costos de GCP con BigQuery ML

## Objetivo del Ejemplo

Este ejemplo demuestra cómo utilizar **BigQuery ML** con el modelo **ARIMA_PLUS** para detectar automáticamente anomalías en los costos diarios de servicios de Google Cloud Platform. El objetivo es identificar picos de gasto inesperados que puedan indicar:

- Configuraciones incorrectas (instancias no apagadas)
- Ataques DDoS o uso no autorizado
- Errores en procesos automatizados
- Cambios arquitecturales sin documentar

El modelo aprende patrones históricos de cada servicio y alerta cuando el costo se desvía significativamente del comportamiento esperado.

---

## Pasos en BigQuery: Explicación Detallada

### Paso 1: Crear la Tabla de Datos

```sql
CREATE OR REPLACE TABLE `formacionaiops-476808.test.gcp_costs` AS
SELECT PARSE_DATE('%Y-%m-%d', usage_date) AS usage_date, 
       service_name, 
       CAST(total_cost AS FLOAT64) AS total_cost
FROM UNNEST([...])
```

**Parámetros:**
- `PARSE_DATE('%Y-%m-%d', usage_date)`: Convierte strings de fecha a tipo DATE
- `CAST(total_cost AS FLOAT64)`: Convierte costos a número decimal
- `UNNEST([...])`: Convierte un array JSON en filas de tabla

**Propósito:** Crear una tabla estructurada con 3 columnas: fecha de uso, nombre del servicio y costo total.

---

### Paso 2: Crear el Modelo ARIMA_PLUS

```sql
CREATE OR REPLACE MODEL `formacionaiops-476808.test.cost_anomaly_model`
OPTIONS(
  model_type='ARIMA_PLUS',
  time_series_timestamp_col='usage_date',
  time_series_data_col='total_cost',
  time_series_id_col='service_name',
  holiday_region='ES',
  auto_arima=TRUE,
  data_frequency='DAILY'
) AS
SELECT usage_date, service_name, total_cost
FROM `formacionaiops-476808.test.gcp_costs`;
```

**Parámetros Explicados:**

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `model_type` | `'ARIMA_PLUS'` | Modelo de series temporales avanzado con detección automática de estacionalidad |
| `time_series_timestamp_col` | `'usage_date'` | Columna que contiene las fechas (eje temporal) |
| `time_series_data_col` | `'total_cost'` | Columna con los valores a predecir (costos) |
| `time_series_id_col` | `'service_name'` | Agrupa las series temporales por servicio (crea un modelo por servicio) |
| `holiday_region` | `'ES'` | Considera festivos españoles que puedan afectar patrones de uso |
| `auto_arima` | `TRUE` | Selecciona automáticamente los mejores parámetros (p,d,q) usando AIC |
| `data_frequency` | `'DAILY'` | Indica que los datos son diarios (puede ser WEEKLY, MONTHLY, etc.) |

**Proceso Interno:**
1. BigQuery entrena **un modelo ARIMA independiente** para cada `service_name`
2. El algoritmo `auto_arima` prueba múltiples combinaciones de parámetros (p,d,q) en paralelo
3. Selecciona el modelo con el **AIC más bajo** (mejor balance entre precisión y simplicidad)
4. Descompone la serie temporal en: tendencia + estacionalidad + ruido
5. Detecta automáticamente spikes, dips y cambios de nivel

---

### Paso 3: Detectar Anomalías

```sql
SELECT
  service_name,
  usage_date,
  total_cost,
  is_anomaly,
  anomaly_probability,
  lower_bound,
  upper_bound,
  ROUND(total_cost - upper_bound, 2) AS deviation_from_expected
FROM ML.DETECT_ANOMALIES(
  MODEL `formacionaiops-476808.test.cost_anomaly_model`,
  STRUCT(0.95 AS anomaly_prob_threshold)
)
WHERE is_anomaly = TRUE
ORDER BY anomaly_probability DESC, total_cost DESC;
```

**Parámetros de ML.DETECT_ANOMALIES:**

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `MODEL` | `cost_anomaly_model` | El modelo entrenado previamente |
| `anomaly_prob_threshold` | `0.95` | Umbral de confianza: marca como anomalía si probabilidad > 95% |

**Valores más comunes:**
- `0.90` (90%): Más sensible, detecta más anomalías (puede incluir falsos positivos)
- `0.95` (95%): Balance recomendado para producción
- `0.99` (99%): Solo anomalías extremas (menos falsos positivos)

**Columnas de Salida:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `is_anomaly` | BOOL | TRUE si el valor es anómalo según el umbral |
| `anomaly_probability` | FLOAT64 | Probabilidad de que sea anomalía (0.0 a 1.0) |
| `lower_bound` | FLOAT64 | Límite inferior del intervalo de confianza esperado |
| `upper_bound` | FLOAT64 | Límite superior del intervalo de confianza esperado |
| `deviation_from_expected` | FLOAT64 | Diferencia entre costo real y límite superior |

**Interpretación:**
- Si `total_cost > upper_bound`: Anomalía **positiva** (gasto excesivo)
- Si `total_cost < lower_bound`: Anomalía **negativa** (gasto inusualmente bajo)

---

### Paso 4: Evaluar el Modelo

```sql
SELECT * FROM ML.EVALUATE(
  MODEL `formacionaiops-476808.test.cost_anomaly_model`
);
```

**Propósito:** Muestra métricas de calidad y parámetros aprendidos para cada serie temporal (cada servicio).

---

## Explicación de Cada Campo de ML.EVALUATE

### Ejemplo de Salida para BigQuery:

```json
{
  "service_name": "BigQuery",
  "non_seasonal_p": "0",
  "non_seasonal_d": "0",
  "non_seasonal_q": "0",
  "has_drift": "false",
  "log_likelihood": "-46.372031048770886",
  "AIC": "96.744062097541772",
  "variance": "28.362288888888894",
  "seasonal_periods": ["NO_SEASONALITY"],
  "has_holiday_effect": "false",
  "has_spikes_and_dips": "true",
  "has_step_changes": "false"
}
```

---

### Campos del Modelo ARIMA (p, d, q)

| Campo | Valor Ejemplo | Descripción Completa |
|-------|---------------|----------------------|
| **non_seasonal_p** | `0` | **Orden Autoregresivo:** Número de valores históricos (lags) que el modelo usa para predecir el valor actual. `p=0` significa que no considera valores pasados, `p=2` usaría los últimos 2 días. |
| **non_seasonal_d** | `0` | **Orden de Diferenciación:** Cuántas veces se resta el valor anterior para hacer la serie estacionaria. `d=0` (serie ya estacionaria), `d=1` (calcula diferencias día a día), `d=2` (diferencias de diferencias). |
| **non_seasonal_q** | `0` | **Orden de Media Móvil:** Número de errores de predicción pasados que se consideran. `q=0` no usa errores, `q=2` considera los últimos 2 errores de predicción. |

**Interpretación del Ejemplo:**
- **ARIMA(0,0,0)** para BigQuery indica un modelo de **ruido blanco** (valores aleatorios sin patrón temporal fuerte).
- Esto es común en servicios con uso irregular donde los costos varían sin un patrón predecible.

---

### Campos de Diagnóstico

| Campo | Tipo | Descripción Completa |
|-------|------|----------------------|
| **has_drift** | `false` | **Tendencia Lineal:** Indica si la serie tiene una tendencia creciente/decreciente constante a lo largo del tiempo. `true` = hay una pendiente lineal sostenida. Solo aplica cuando `d=1`. |
| **has_holiday_effect** | `false` | **Efecto de Festivos:** El modelo detectó que los días festivos (según `holiday_region`) afectan significativamente el patrón de costos. `true` = costos diferentes en festivos. |
| **has_spikes_and_dips** | `true` | **Picos y Caídas Súbitas:** La serie histórica contiene valores atípicos (outliers) que se desviaron drásticamente del patrón. BigQuery limpia estos automáticamente al entrenar. `true` = datos históricos tenían anomalías. |
| **has_step_changes** | `false` | **Cambios de Nivel Abruptos:** Detecta si hubo un cambio permanente en el nivel base de costos (ej: migración que duplicó costos permanentemente). `true` = hubo un salto de nivel. |

**Interpretación del Ejemplo:**
- BigQuery tiene **spikes and dips** (`true`), lo que explica por qué el modelo ARIMA(0,0,0) es apropiado: los costos son impredecibles con picos ocasionales.

---

### Campos de Calidad del Modelo

| Campo | Valor Ejemplo | Descripción Completa |
|-------|---------------|----------------------|
| **log_likelihood** | `-46.37` | **Log-Verosimilitud:** Mide qué tan bien el modelo explica los datos observados. Valores más altos (menos negativos) = mejor ajuste. Se usa para calcular AIC. Valor negativo es normal. |
| **AIC** | `96.74` | **Criterio de Información de Akaike:** Balancea precisión del modelo vs simplicidad. AIC = -2×log_likelihood + 2×(número de parámetros). **Menor AIC = mejor modelo.** Se usa para comparar modelos del mismo servicio. |
| **variance** | `28.36` | **Varianza Residual:** Mide la dispersión de los errores de predicción. Mayor varianza = mayor incertidumbre en las predicciones. Servicios con alta varianza son más difíciles de predecir. |

**Comparación de Varianzas:**
- **Compute Engine:** 1,400,458.38 → Extremadamente impredecible
- **BigQuery:** 28.36 → Moderadamente variable
- **Cloud Storage:** 0.00018 → Muy predecible
- **Cloud Build:** 0.0 → Costos constantes (cualquier cambio es anomalía)

---

### Campos de Estacionalidad

| Campo | Valor Ejemplo | Descripción Completa |
|-------|---------------|----------------------|
| **seasonal_periods** | `["NO_SEASONALITY"]` | **Periodicidad Estacional:** Patrones cíclicos detectados automáticamente. Valores posibles: `DAILY` (ciclo de 24h), `WEEKLY` (patrón semanal), `MONTHLY`, `QUARTERLY`, `YEARLY`, `NO_SEASONALITY` (sin patrón cíclico). |

**Ejemplo de Interpretación:**
- `["WEEKLY"]`: Costos más altos de lunes a viernes (horario laboral)
- `["MONTHLY", "YEARLY"]`: Picos mensuales de cierre + picos anuales de fin de año
- `["NO_SEASONALITY"]`: Uso irregular sin patrón recurrente

---

## Casos de Uso por Tipo de Modelo

### Servicios con ARIMA(0,0,0) - Ruido Blanco
**Ejemplos:** BigQuery, Cloud Build, Cloud Logging

**Características:**
- Costos variables sin patrón temporal
- Uso ad-hoc bajo demanda
- Anomalías = cualquier desviación > 2-3 desviaciones estándar

**Recomendación:** Usar alertas basadas en umbrales fijos (`total_cost > $X`) en lugar de modelos complejos.

---

### Servicios con ARIMA(0,1,0) - Random Walk
**Ejemplos:** Vertex AI, Cloud Run

**Características:**
- Tendencia cambiante a lo largo del tiempo
- Costos que aumentan/disminuyen gradualmente
- El valor de mañana = valor de hoy + ruido aleatorio

**Recomendación:** Monitorear cambios de tendencia semanales/mensuales.

---

### Servicios con ARIMA(0,2,0) - Aceleración
**Ejemplos:** Compute Engine

**Características:**
- Varianza extremadamente alta
- Cambios bruscos en la velocidad de crecimiento
- Requiere 2 niveles de diferenciación para estabilizar

**Recomendación:** Implementar alertas de presupuesto estrictas y revisión diaria.

---

### Servicios con ARIMA(2,0,0) - Autoregresivo
**Ejemplos:** Cloud SQL

**Características:**
- Patrón predecible basado en días anteriores
- El costo de hoy depende de los últimos 2 días
- Baja varianza (1.9e-12)

**Recomendación:** Perfecto para forecasting, el modelo es altamente confiable.

---

### Servicios con ARIMA(0,0,2) - Media Móvil
**Ejemplos:** Cloud Dataflow, Networking

**Características:**
- Reacción a errores de predicción recientes
- Patrón de ráfagas (bursts) de actividad
- El modelo se ajusta según errores pasados

**Recomendación:** Analizar qué causó errores anteriores para mejorar predicciones.

---

## Interpretación de Anomalías Detectadas

### Anomalía Crítica: Compute Engine

```json
{
  "service_name": "Compute Engine",
  "usage_date": "2025-12-02",
  "total_cost": "4583.36",
  "is_anomaly": "true",
  "anomaly_probability": "0.99974",
  "lower_bound": "-2315.26",
  "upper_bound": "2315.32",
  "deviation_from_expected": "2268.03"
}
```

**Análisis:**
1. **Probabilidad 99.97%**: Certeza casi absoluta de anomalía
2. **Desviación +$2,268**: Excede $2,268 sobre el límite superior esperado
3. **Intervalo [-2315, +2315]**: Rango enorme indica alta incertidumbre histórica del servicio
4. **Acción Requerida:** Investigar inmediatamente qué instancias se ejecutaron ese día

---

### Anomalía Negativa: Vertex AI

```json
{
  "service_name": "Vertex AI",
  "usage_date": "2025-11-22",
  "total_cost": "0.31",
  "is_anomaly": "true",
  "anomaly_probability": "0.9992",
  "lower_bound": "43.36",
  "upper_bound": "152.66",
  "deviation_from_expected": "-152.35"
}
```

**Análisis:**
1. **Anomalía Negativa:** Costo mucho menor de lo esperado ($0.31 vs $43-$152 esperados)
2. **Posibles Causas:**
   - Pipeline de ML detenido por error
   - Job programado que no se ejecutó
   - Cambio arquitectural (migración a otro servicio)
3. **Acción Requerida:** Verificar si la caída es intencional o un fallo operacional

---

## Mejores Prácticas

### 1. Ajuste de Umbrales según Varianza

| Rango de Varianza | Umbral Recomendado | Razón |
|-------------------|-------------------|--------|
| < 1.0 | 0.90 (90%) | Servicios predecibles, cualquier desviación es sospechosa |
| 1.0 - 100.0 | 0.95 (95%) | Balance estándar |
| 100.0 - 10,000 | 0.98 (98%) | Reducir falsos positivos en servicios variables |
| > 10,000 | 0.99 (99%) | Solo alertas críticas, ignorar ruido normal |

### 2. Frecuencia de Re-entrenamiento

- **Servicios estables (varianza < 10):** Re-entrenar mensualmente
- **Servicios variables (varianza 10-1000):** Re-entrenar semanalmente
- **Servicios caóticos (varianza > 1000):** Re-entrenar diariamente o usar estrategia diferente

### 3. Exclusión de Servicios Constantes

```sql
-- Filtrar servicios con varianza 0.0 antes de entrenar
SELECT * FROM gcp_costs
WHERE service_name NOT IN ('Cloud Build', 'Cloud Logging', 'Cloud Monitoring', 'Dataplex')
```

**Razón:** Servicios con costo constante siempre generan anomalías. Usar alertas simples (`IF total_cost != expected THEN alert`).

---

## Consultas SQL Adicionales Útiles

### Ver Solo Anomalías de Alto Impacto Económico

```sql
SELECT *
FROM ML.DETECT_ANOMALIES(
  MODEL `formacionaiops-476808.test.cost_anomaly_model`,
  STRUCT(0.95 AS anomaly_prob_threshold)
)
WHERE is_anomaly = TRUE
  AND ABS(total_cost - upper_bound) > 100  -- Solo desviaciones > $100
ORDER BY ABS(total_cost - upper_bound) DESC;
```

### Comparar Modelos de Diferentes Servicios

```sql
SELECT 
  service_name,
  CONCAT('ARIMA(', non_seasonal_p, ',', non_seasonal_d, ',', non_seasonal_q, ')') AS model_type,
  ROUND(variance, 2) AS variance,
  ROUND(AIC, 2) AS aic,
  has_spikes_and_dips,
  seasonal_periods
FROM ML.EVALUATE(MODEL `formacionaiops-476808.test.cost_anomaly_model`)
ORDER BY variance DESC;
```

### Detectar Cambios de Tendencia

```sql
SELECT 
  service_name,
  COUNT(*) AS anomaly_count,
  SUM(total_cost - upper_bound) AS total_excess_cost
FROM ML.DETECT_ANOMALIES(
  MODEL `formacionaiops-476808.test.cost_anomaly_model`,
  STRUCT(0.95 AS anomaly_prob_threshold)
)
WHERE is_anomaly = TRUE
  AND usage_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY service_name
HAVING anomaly_count > 3  -- Servicios con 3+ anomalías en última semana
ORDER BY total_excess_cost DESC;
```

---

## Resumen de Valores Clave

| Campo | Valor Óptimo | Señal de Alerta |
|-------|--------------|-----------------|
| **AIC** | Menor es mejor | Comparar solo dentro del mismo servicio |
| **Variance** | < 100 (estable) | > 10,000 (impredecible) |
| **anomaly_probability** | N/A | > 0.95 requiere investigación |
| **non_seasonal_d** | 0 o 1 | 2 indica alta inestabilidad |
| **has_spikes_and_dips** | `false` | `true` = datos históricos ruidosos |

---

## Referencias

- [Documentación oficial BigQuery ML - ARIMA_EVALUATE](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-arima-evaluate)
- [Documentación oficial BigQuery ML - DETECT_ANOMALIES](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-detect-anomalies)
- [Tutorial: Forecasting con ARIMA_PLUS](https://cloud.google.com/bigquery/docs/arima-multiple-time-series-forecasting-tutorial)