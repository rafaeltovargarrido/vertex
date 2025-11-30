import functions_framework
from google.cloud import monitoring_v3
from google.cloud import bigquery
import time

# --- CONFIGURACIÓN ---
PROJECT_ID = "formacionaiops-476808"
BQ_DATASET = "ml_test" # Asegúrate de que este dataset exista en BigQuery
BQ_TABLE = "cpu_usage_rate"

@functions_framework.cloud_event
def export_metric_to_bq(cloud_event):
    print(f"Iniciando exportación triggered by event: {cloud_event['id']}")

    client_monitoring = monitoring_v3.QueryServiceClient()
    client_bq = bigquery.Client()

    # --- LA QUERY GANADORA (MQL) ---
    mql_query = """
    fetch gce_instance
    | metric 'agent.googleapis.com/cpu/usage_time'
    | align rate(5m)
    | every 5m
    | group_by [resource.instance_id], 
               [cpu_total_cores: sum(value.usage_time)]
    """

    try:
        results = client_monitoring.query_time_series(
            request={
                "name": f"projects/{PROJECT_ID}",
                "query": mql_query,
            }
        )

        rows_to_insert = []
        for data in results.time_series_data:
            # En MQL, las etiquetas agrupadas vienen en label_values
            # El orden depende del group_by. Aquí solo hay uno: resource.instance_id
            instance_id = data.label_values[0].string_value
            
            for point in data.point_data:
                ts = point.time_interval.end_time.strftime("%Y-%m-%d %H:%M:%S")
                val = point.values[0].double_value
                
                rows_to_insert.append({
                    "timestamp": ts,
                    "instance_id": instance_id,
                    "cpu_total_cores": val
                })

        if rows_to_insert:
            table_id = f"{PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}"
            # Asegúrate de que la tabla tenga el esquema correcto: 
            # timestamp:TIMESTAMP, instance_id:STRING, cpu_total_cores:FLOAT
            errors = client_bq.insert_rows_json(table_id, rows_to_insert)
            
            if not errors:
                print(f"✅ Éxito: {len(rows_to_insert)} filas insertadas.")
            else:
                print(f"❌ Errores insertando en BigQuery: {errors}")
        else:
            print("⚠️ La query funcionó pero no devolvió datos recientes.")

    except Exception as e:
        print(f"❌ Error crítico en la función: {e}")
        raise e