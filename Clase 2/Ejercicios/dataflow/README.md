
###Comandos

pip install apache-beam[gcp]


python main.py --region us-central1 --runner DataflowRunner --project formacionaiops-476808  --temp_location gs://dataflow_vertex/tmp --staging_location 
gs://dataflow_vertex/staging