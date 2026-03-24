# Auto loader in Databricks
Auto Loader incrementally and efficiently processes new data files as they arrive in cloud storage without any additional setup. It provides a structured streaming source called **cloudFiles**. Given an input directory path on the cloud file storage, the cloudFiles source automatically processes new files as they arrive, with the option of also processing existing files in that directory. Auto Loader has support for both Python and SQL in Lakeflow Spark Declarative Pipelines.
You can use Auto Loader to process billions of files to migrate or backfill a table. Auto Loader scales to support near real-time ingestion of millions of files per hour.

## Supported Sources for Autoloader
Auto Loader can load data files from the following sources: S3, ADLS, GCS,Azure BLOB STORAGE and DBFS also.

Auto loader can ingest CSV, XML, PARQUET, JSON, AVRO, ORC, TEXT and BINARY FILE formats. 

For more information open this link : https://learn.microsoft.com/en-us/azure/databricks/ingestion/cloud-object-storage/auto-loader/