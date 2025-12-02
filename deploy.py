import argparse
from google.cloud import aiplatform

def deploy_model(project_id, region, bucket_name, model_display_name):
    print(f"🚀 Iniciando despliegue para: {model_display_name}")
    print(f"   📍 Región: {region}")
    print(f"   📦 Bucket origen: gs://{bucket_name}/model_output/")
    
    # Inicializamos Vertex AI en la región correcta (Europa)
    aiplatform.init(project=project_id, location=region)

    # 1. IMPORTAR EL MODELO AL REGISTRO
    print("📥 Importando modelo al Registry...")
    try:
        model = aiplatform.Model.upload(
            display_name=model_display_name,
            artifact_uri=f"gs://{bucket_name}/model_output/",
            # Usamos la imagen oficial de Google para servir Scikit-learn (esta suele ser global)
            serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest",
        )
        print(f"✅ Modelo importado: {model.resource_name}")
    except Exception as e:
        print(f"❌ Error importando modelo (puede que ya exista): {e}")
        # Intentamos buscarlo si ya existe para no fallar el pipeline
        models = aiplatform.Model.list(filter=f"display_name={model_display_name}")
        if models:
            model = models[0]
            print(f"🔄 Usando modelo existente: {model.resource_name}")
        else:
            raise e

    # 2. CREAR (O BUSCAR) UN ENDPOINT
    endpoint_name = f"{model_display_name}-endpoint"
    endpoints = aiplatform.Endpoint.list(filter=f"display_name={endpoint_name}")
    
    if endpoints:
        endpoint = endpoints[0]
        print(f"🔄 Usando Endpoint existente: {endpoint.resource_name}")
    else:
        print("✨ Creando nuevo Endpoint...")
        endpoint = aiplatform.Endpoint.create(display_name=endpoint_name)
        print(f"✅ Nuevo Endpoint creado: {endpoint.resource_name}")

    # 3. DESPLEGAR EL MODELO AL ENDPOINT
    print("⏳ Desplegando modelo en la máquina (esto tarda unos 10-15 min)...")
    try:
        model.deploy(
            endpoint=endpoint,
            machine_type="n1-standard-2",
            traffic_split={"0": 100}, 
            min_replica_count=1,
            max_replica_count=1
        )
        print(f"🎉 ¡Despliegue completado! Tu API está lista.")
    except Exception as e:
        print(f"❌ Error en el despliegue: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_id', type=str, required=True)
    parser.add_argument('--region', type=str, required=True)
    parser.add_argument('--bucket', type=str, required=True)
    parser.add_argument('--name', type=str, required=True)
    args = parser.parse_args()
    
    deploy_model(args.project_id, args.region, args.bucket, args.name)