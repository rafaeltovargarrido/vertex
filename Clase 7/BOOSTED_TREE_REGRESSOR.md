# Forecasting de Costos de GCP con BOOSTED_TREE_REGRESSOR en BigQuery ML

## Objetivo del Ejemplo

Este ejemplo didáctico muestra cómo predecir los costos de GCP usando el modelo **BOOSTED_TREE_REGRESSOR** en BigQuery ML. A diferencia de ARIMA_PLUS, este modelo utiliza features adicionales (día del año, semana, mes, año) para capturar patrones no lineales y mejorar la predicción de costos futuros.

El objetivo es:
- Generar datos sintéticos de costos de GCP.
- Entrenar un modelo de forecasting usando BOOSTED_TREE_REGRESSOR.
- Predecir costos futuros y analizar los resultados.

---

## 1. Generar datos sintéticos

### 1.1 Crear la tabla con datos fake

```sql
CREATE OR REPLACE TABLE `formacionaiops-476808.billing.fake_costs_with_features` AS
SELECT
  DATE('2025-01-01') + INTERVAL day_number DAY AS usage_date,
  ROUND(100 + 50 * COS(2 * 3.141592653589793 * day_number / 365) + RAND() * 20, 2) AS total_cost,
  EXTRACT(DAYOFYEAR FROM DATE('2025-01-01') + INTERVAL day_number DAY) AS day_of_year,
  EXTRACT(WEEK FROM DATE('2025-01-01') + INTERVAL day_number DAY) AS week_of_year,
  EXTRACT(MONTH FROM DATE('2025-01-01') + INTERVAL day_number DAY) AS month,
  EXTRACT(YEAR FROM DATE('2025-01-01') + INTERVAL day_number DAY) AS year
FROM UNNEST(GENERATE_ARRAY(0, 364)) AS day_number;
```

**Esquema resultante:**
- `usage_date` (DATE): fecha del evento.
- `total_cost` (FLOAT64): costo total del día.
- `day_of_year` (INT64): día del año (1-365).
- `week_of_year` (INT64): semana del año (1-52).
- `month` (INT64): mes del año (1-12).
- `year` (INT64): año.

---

## 2. Entrenar el modelo de forecasting

### 2.1 Crear el modelo BOOSTED_TREE_REGRESSOR

```sql
CREATE OR REPLACE MODEL `formacionaiops-476808.billing.cost_forecast_boosted_tree`
OPTIONS(
  model_type = 'BOOSTED_TREE_REGRESSOR',
  input_label_cols = ['total_cost'],
  num_parallel_tree = 1,
  max_iterations = 50
) AS
SELECT
  day_of_year,
  week_of_year,
  month,
  year,
  total_cost
FROM `formacionaiops-476808.billing.fake_costs_with_features`;
```

**Parámetros explicados:**
- `model_type = 'BOOSTED_TREE_REGRESSOR'`: Modelo de regresión basado en árboles de decisión, ideal para capturar patrones no lineales.
- `input_label_cols = ['total_cost']`: Columna objetivo que el modelo intenta predecir.
- `num_parallel_tree = 1`: Número de árboles en paralelo (puedes aumentarlo para mejorar el rendimiento, pero consume más recursos).
- `max_iterations = 50`: Número máximo de iteraciones de entrenamiento.

---

## 3. Generar features para predicción futura

### 3.1 Crear la tabla con features futuros

```sql
CREATE OR REPLACE TABLE `formacionaiops-476808.billing.future_features` AS
SELECT
  DATE('2025-12-01') + INTERVAL day_number DAY AS usage_date,
  EXTRACT(DAYOFYEAR FROM DATE('2025-12-01') + INTERVAL day_number DAY) AS day_of_year,
  EXTRACT(WEEK FROM DATE('2025-12-01') + INTERVAL day_number DAY) AS week_of_year,
  EXTRACT(MONTH FROM DATE('2025-12-01') + INTERVAL day_number DAY) AS month,
  EXTRACT(YEAR FROM DATE('2025-12-01') + INTERVAL day_number DAY) AS year
FROM UNNEST(GENERATE_ARRAY(0, 29)) AS day_number;  -- Próximos 30 días
```

---

## 4. Predecir costos futuros

### 4.1 Predecir con el modelo entrenado

```sql
SELECT
  usage_date,
  predicted_total_cost
FROM ML.PREDICT(
  MODEL `formacionaiops-476808.billing.cost_forecast_boosted_tree`,
  (
    SELECT
      day_of_year,
      week_of_year,
      month,
      year
    FROM `formacionaiops-476808.billing.future_features`
  )
);
```

**Campos de salida:**
- `usage_date`: Fecha del día predicho.
- `predicted_total_cost`: Valor predicho para ese día.

---

## 5. Análisis de resultados

### 5.1 Interpretación de la predicción

El modelo BOOSTED_TREE_REGRESSOR captura patrones no lineales y relaciones complejas entre los features. Al comparar la predicción con los valores reales, puedes evaluar la precisión del modelo y ajustar los parámetros si es necesario.

### 5.2 Métricas de evaluación

Para evaluar el modelo, puedes usar:

```sql
SELECT *
FROM ML.EVALUATE(
  MODEL `formacionaiops-476808.billing.cost_forecast_boosted_tree`
);
```

**Interpretación**
mean_absolute_error (MAE): El error absoluto medio es de 4.20 EUR, lo que indica que, en promedio, las predicciones del modelo se desvían 4.20 EUR del valor real.

mean_squared_error (MSE): El error cuadrático medio es de 24.84, que penaliza más los errores grandes.

mean_squared_log_error (MSLE): El error logarítmico cuadrático medio es muy bajo, lo que sugiere que el modelo maneja bien los errores relativos.

median_absolute_error: El error absoluto mediano es de 3.96 EUR, indicando que la mitad de los errores están por debajo de este valor.

r2_score: El coeficiente de determinación es 0.981, lo que significa que el modelo explica el 98.1% de la varianza de los datos.

explained_variance: La varianza explicada es 0.981, confirmando que el modelo captura la mayor parte de la variabilidad de los datos.



### 5.3 Ventajas y desventajas

| Modelo | Ventajas | Desventajas |
|--------|----------|-------------|
| BOOSTED_TREE_REGRESSOR | Captura patrones no lineales, robusto a outliers | Más lento que modelos lineales, puede sobreajustarse si no se regulariza |

---

## 6. Resumen didáctico del flujo

1. **Generación de datos sintéticos:** Se crean datos de costos de GCP con un patrón estacional y ruido aleatorio.
2. **Entrenamiento del modelo:** Se entrena un modelo de regresión basado en árboles con features adicionales.
3. **Predicción futura:** Se generan features para los próximos 30 días y se predice el costo.
4. **Análisis de resultados:** Se evalúa la precisión del modelo y se interpretan los resultados.

Este patrón es reutilizable para muchos casos de forecasting en BigQuery ML.