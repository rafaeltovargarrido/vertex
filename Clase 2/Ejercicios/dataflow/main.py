import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions

# 1. Define the BigQuery Schema
# This tells BigQuery what columns to expect.
TABLE_SCHEMA = {
    'fields': [
        {'name': 'product_id', 'type': 'STRING', 'mode': 'REQUIRED'},
        {'name': 'product_name', 'type': 'STRING', 'mode': 'NULLABLE'},
        {'name': 'quantity_sold', 'type': 'INTEGER', 'mode': 'NULLABLE'},
        {'name': 'price_per_unit', 'type': 'FLOAT', 'mode': 'NULLABLE'},
        {'name': 'total_revenue', 'type': 'FLOAT', 'mode': 'NULLABLE'}, # We will calculate this
    ]
}

# 2. Define the Transformation Logic (The "DoFn")
class CalculateRevenue(beam.DoFn):
    def process(self, element):
        # element is a dictionary (row of data)
        row = element.copy()
        
        # Perform the transformation logic
        qty = row.get('quantity_sold', 0)
        price = row.get('price_per_unit', 0.0)
        
        # Calculate revenue and add it to the row
        row['total_revenue'] = round(qty * price, 2)
        
        yield row

def run_pipeline():
    # 3. Setup Pipeline Options
    # In a real scenario, use command line args (argparse)
    options = PipelineOptions()
    
    # If running on the Cloud (Dataflow Runner), uncomment and fill these:
    # google_cloud_options = options.view_as(GoogleCloudOptions)
    # google_cloud_options.project = 'YOUR_GCP_PROJECT_ID'
    # google_cloud_options.job_name = 'my-first-etl-job'
    # google_cloud_options.staging_location = 'gs://YOUR_BUCKET/staging'
    # google_cloud_options.temp_location = 'gs://YOUR_BUCKET/temp'
    # google_cloud_options.region = 'us-central1'
    
    # Define the output table: PROJECT:DATASET.TABLE
    # Replace with your actual details
    output_table = 'YOUR_PROJECT_ID:your_dataset.sales_report'

    # 4. The Pipeline Construction
    with beam.Pipeline(options=options) as p:
        (
            p
            # Step A: Create Data (Simulating reading from a CSV or GCS)
            | 'CreateRawData' >> beam.Create([
                {'product_id': 'A100', 'product_name': 'Laptop', 'quantity_sold': 2, 'price_per_unit': 1200.50},
                {'product_id': 'B200', 'product_name': 'Mouse', 'quantity_sold': 10, 'price_per_unit': 25.00},
                {'product_id': 'C300', 'product_name': 'Monitor', 'quantity_sold': 5, 'price_per_unit': 300.00},
            ])
            
            # Step B: Apply the Transformation
            | 'CalculateRevenue' >> beam.ParDo(CalculateRevenue())
            
            # Step C: Write to BigQuery
            | 'WriteToBQ' >> beam.io.WriteToBigQuery(
                output_table,
                schema=TABLE_SCHEMA,
                # CREATE_IF_NEEDED: Creates the table if it doesn't exist
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                # WRITE_TRUNCATE: Overwrites table. Use WRITE_APPEND to add data.
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE
            )
        )

if __name__ == '__main__':
    print("Starting pipeline...")
    run_pipeline()
    print("Pipeline finished.")