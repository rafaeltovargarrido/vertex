# Ejemplo práctico: búsqueda semántica de tickets de soporte con BigQuery y Vertex AI

## 1. Objetivo de la clase

En esta clase vamos a construir **un ejemplo completo** de cómo:

1. Guardar tickets de soporte en BigQuery.
2. Generar **embeddings de texto** usando Vertex AI (`text-embedding-004`) mediante un **modelo remoto de BigQuery**.
3. Guardar esos embeddings en una tabla.
4. Hacer **búsqueda semántica** sobre los tickets con `VECTOR_SEARCH`, sin necesidad de índice vectorial (por ser un dataset pequeño).

Al final, serás capaz de lanzar una consulta en lenguaje natural como:

> "problema con la base de datos"

y recuperar los tickets más parecidos semánticamente.

---

## 2. Caso de uso: soporte técnico y búsqueda semántica

Contexto típico:

- Tienes un equipo de **soporte** que recibe muchos tickets.
- Cada ticket tiene un texto libre, por ejemplo:
  - *"He olvidado mi contraseña y no puedo acceder al panel."*
  - *"El servidor de base de datos se ha reiniciado inesperadamente."*
- El equipo quiere **reutilizar el conocimiento** de tickets anteriores:
  - Encontrar incidencias similares.
  - Ver cómo se resolvieron.
  - Sugerir soluciones más rápido.

Con embeddings + búsqueda vectorial, podemos:

- Representar cada descripción como un **vector** (embedding).
- Dado un nuevo texto (consulta), generar su embedding.
- Buscar los **tickets más cercanos** en el espacio vectorial (semánticamente similares).

---

## 3. Arquitectura del ejemplo

Componentes principales:

- **BigQuery**
  - Tabla original de tickets: `tickets_soporte`.
  - Tabla de embeddings: `tickets_soporte_embeddings`.
- **Vertex AI (Text Embeddings)**
  - Modelo: `text-embedding-004`.
  - Acceso desde BigQuery mediante un **modelo remoto**.
- **Funciones de BigQuery ML**
  - `AI.GENERATE_EMBEDDING` para obtener embeddings.
  - `VECTOR_SEARCH` para realizar la búsqueda semántica.

Región del ejemplo: `eu` (asegúrate de que tu dataset de BigQuery y tu conexión a Vertex están en la misma región).

---

## 4. Prerrequisitos

Antes de ejecutar el ejemplo:

1. Proyecto de GCP (por ejemplo: `formacionaiops-476808`).
2. BigQuery habilitado y un dataset (por ejemplo: `test`).
3. Conexión a Vertex AI creada en BigQuery, por ejemplo:
   - `projects/formacionaiops-476808/locations/eu/connections/mi-conexion-vertex`
4. Permisos para usar Vertex AI desde BigQuery (BigQuery Service Account con acceso a Vertex).

---

## 5. Paso 1: crear la tabla de tickets

Creamos una tabla sencilla con 7 tickets de soporte de ejemplo:

```sql
CREATE OR REPLACE TABLE `formacionaiops-476808.test.tickets_soporte`
(
  ticket_id INT64,
  descripcion STRING
);

INSERT INTO `formacionaiops-476808.test.tickets_soporte` (ticket_id, descripcion)
VALUES 
  (1, 'El servidor de base de datos se ha reiniciado inesperadamente.'),
  (2, 'Los usuarios reportan que las páginas tardan mucho en cargar.'),
  (3, 'He olvidado mi contraseña y no puedo acceder al panel.'),
  (4, 'Fallo de conexión con la API de pagos, da timeout.'),
  (5, 'La pantalla se queda en blanco al intentar exportar el reporte.'),
  (6, 'Intento de inicio de sesión sospechoso desde una IP desconocida.'),
  (7, 'El disco duro del servidor principal está lleno al 99%.');
```

---

## 6. Paso 2: crear el modelo remoto de embeddings

Creamos un modelo remoto en BigQuery que apunta al endpoint de Vertex AI `text-embedding-004`:

```sql
CREATE OR REPLACE MODEL `formacionaiops-476808.test.modelo_embedding_v1`
REMOTE WITH CONNECTION `projects/formacionaiops-476808/locations/eu/connections/mi-conexion-vertex`
OPTIONS(endpoint = 'text-embedding-004');
```

**Qué hace esto:**

- No entrenamos nada en BigQuery.
- Solo definimos un **"puente"** para poder llamar a Vertex AI desde SQL usando este modelo.

---

## 7. Paso 3: generar y guardar los embeddings

Ahora vamos a generar embeddings para cada descripción de ticket y guardar el resultado en una nueva tabla.

```sql
CREATE OR REPLACE TABLE `formacionaiops-476808.test.tickets_soporte_embeddings` AS
SELECT
  ticket_id,
  descripcion,
  embedding
FROM AI.GENERATE_EMBEDDING(
  MODEL `formacionaiops-476808.test.modelo_embedding_v1`,
  (
    SELECT
      ticket_id,
      descripcion AS content,
      descripcion
    FROM `formacionaiops-476808.test.tickets_soporte`
  )
  -- Opcional: especificar el tipo de tarea
  -- ,STRUCT('RETRIEVAL_DOCUMENT' AS task_type)
);
```

**Notas importantes:**

- `AI.GENERATE_EMBEDDING` espera una columna llamada `content` con el texto a convertir en embedding.
- Devuelve la tabla de entrada **más** una columna `embedding` (tipo `ARRAY<FLOAT64>`).
- En la tabla resultante `tickets_soporte_embeddings` tendremos:
  - `ticket_id` (INT64)
  - `descripcion` (STRING)
  - `embedding` (ARRAY<FLOAT64`)

---

## 8. Paso 4: búsqueda semántica con VECTOR_SEARCH (sin índice)

Como nuestra tabla solo tiene 7 filas, BigQuery **no permite crear un índice vectorial** (el mínimo para `TREE_AH` son 5000 filas).  
En vez de eso, usaremos `VECTOR_SEARCH` directamente, que internamente hará una búsqueda exhaustiva (brute force).

### 8.1. Definir el texto de búsqueda

Podemos usar una variable en SQL (en la UI de BigQuery):

```sql
DECLARE query_text STRING DEFAULT 'problema con la base de datos';
```

### 8.2. Generar embedding de la consulta

Usamos `AI.GENERATE_EMBEDDING` para el texto de búsqueda:

```sql
WITH query_embedding AS (
  SELECT
    embedding
  FROM
    AI.GENERATE_EMBEDDING(
      MODEL `formacionaiops-476808.test.modelo_embedding_v1`,
      (SELECT query_text AS content)
      -- Opcional: tipo de tarea como query
      -- ,STRUCT('RETRIEVAL_QUERY' AS task_type)
    )
)
```

### 8.3. Ejecutar VECTOR_SEARCH

Ahora usamos `VECTOR_SEARCH` para encontrar los tickets más parecidos:

```sql
WITH query_embedding AS (
  SELECT
    embedding
  FROM
    AI.GENERATE_EMBEDDING(
      MODEL `formacionaiops-476808.test.modelo_embedding_v1`,
      (SELECT 'problema con la base de datos' AS content)
    )
)

SELECT
  base.ticket_id,
  base.descripcion,
  distance
FROM
  VECTOR_SEARCH(
    TABLE `formacionaiops-476808.test.tickets_soporte_embeddings`,
    'embedding',                          -- columna de embeddings en la tabla base
    (SELECT embedding FROM query_embedding),
    'embedding',                          -- nombre de la columna de embedding de la query
    top_k       => 3,
    distance_type => 'COSINE'
  )
ORDER BY distance;
```

### 8.4. Interpretación de los resultados

Un posible resultado:

```json
[
  {
    "ticket_id": "1",
    "descripcion": "El servidor de base de datos se ha reiniciado inesperadamente.",
    "distance": "0.2664..."
  },
  {
    "ticket_id": "3",
    "descripcion": "He olvidado mi contraseña y no puedo acceder al panel.",
    "distance": "0.5214..."
  },
  {
    "ticket_id": "2",
    "descripcion": "Los usuarios reportan que las páginas tardan mucho en cargar.",
    "distance": "0.5288..."
  }
]
```

- La **distancia** se calcula con `COSINE`.
- Cuanto **más pequeña** es la distancia, **más similar** es el texto al query.
- En este ejemplo:
  - El ticket 1 (problema claro de *base de datos*) es el más cercano a "problema con la base de datos".
  - El ticket 3 (acceso al panel) y el 2 (rendimiento) son menos similares.

---

## 9. Variaciones interesantes para la clase

Algunas ideas para hacerlo más didáctico:

1. **Cambiar el texto de búsqueda**:
   - `query_text = 'no puedo acceder al panel'` → debería traer primero el ticket 3.
   - `query_text = 'la página va muy lenta'` → debería traer primero el ticket 2.

2. **Añadir categorías a los tickets**:
   - Añadir una columna `categoria` en `tickets_soporte` con valores como:
     - `Base de Datos`
     - `Acceso`
     - `Rendimiento`
     - `Seguridad`
   - Después de encontrar los vecinos más cercanos, puedes:
     - Hacer un simple voto mayoritario sobre la categoría.
     - Mostrar en la demo cómo se podría **predecir categoría** de un nuevo ticket.

3. **Conectar con un modelo generativo (RAG muy básico)**:
   - Usar los tickets recuperados como contexto para un modelo generativo (`ML.GENERATE_TEXT` con un modelo tipo Gemini) y:
     - Generar una respuesta para el usuario.
     - Sugerir pasos de resolución.

---

## 10. Notas sobre índices vectoriales en BigQuery

En este ejemplo **no creamos un índice vectorial** porque:

- `CREATE VECTOR INDEX` con tipos como `TREE_AH` o `IVF` requiere que la tabla tenga **al menos 5000 filas**.
- Con pocos registros, BigQuery recomienda usar directamente `VECTOR_SEARCH` (búsqueda brute force).

En un escenario real, con decenas o cientos de miles de tickets:

1. Crearías la tabla de embeddings con muchos registros.
2. Definirías un índice vectorial:
   ```sql
   CREATE VECTOR INDEX `formacionaiops-476808.test.idx_tickets_soporte_embeddings`
   ON `formacionaiops-476808.test.tickets_soporte_embeddings`(embedding)
   OPTIONS(
     index_type   = 'TREE_AH',
     distance_type = 'COSINE',
     tree_ah_options = '{"normalization_type": "L2"}'
   );
   ```
3. Esperarías a que el índice esté en estado `READY`.
4. Usarías `VECTOR_SEARCH` especificando ese índice para acelerar consultas.

En datasets pequeños (como el de clase), esto **no es necesario** y nos quedaríamos solo con `VECTOR_SEARCH` sin índice.

---

## 11. Conclusiones

- **Embeddings de texto** permiten representar el significado de las descripciones de tickets en forma de vectores numéricos.
- Con BigQuery + Vertex AI:
  - No hace falta crear infraestructura adicional: todo se hace con SQL.
  - Puedes generar embeddings con `AI.GENERATE_EMBEDDING`.
  - Puedes hacer búsquedas semánticas con `VECTOR_SEARCH`.
- Este patrón es muy útil para:
  - Soporte técnico.
  - FAQ inteligentes.
  - Recomendación de artículos de conocimiento.
  - Cualquier escenario donde quieras **buscar por significado**, no solo por palabras clave.