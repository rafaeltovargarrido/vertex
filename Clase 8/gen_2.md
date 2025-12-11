{
  "incident_start": "2025-12-11T09:00:00Z",
  "incident_end": "2025-12-11T09:15:00Z",
  "total_errors_5xx": 4,
  "total_requests": 5,
  "p95_latency_ms": 510,
  "affected_regions": ["europe-west1"],
  "severities_present": ["ERROR", "WARNING"],
  "sample_error_messages": [
    "DB connection timeout to payments-db",
    "Retries exhausted calling payments-db"
  ]
}


Eres un ingeniero SRE senior en un equipo de pagos.

A partir del siguiente contexto JSON de un incidente, genera dos salidas:

1) Un resumen técnico orientado a SRE/Desarrollo.
2) Un resumen ejecutivo orientado a negocio.

El contexto contiene métricas agregadas, ventana temporal, regiones afectadas y ejemplos de mensajes de error.

Usa el siguiente formato en Markdown:

### Resumen técnico

[Texto técnico aquí]

### Resumen ejecutivo

[Texto ejecutivo aquí]

No inventes datos que no aparezcan en el contexto. Si algo no está en el contexto, indícalo explícitamente.

Contexto JSON:
{{PEGA_AQUÍ_EL_JSON_DE_BIGQUERY}}
