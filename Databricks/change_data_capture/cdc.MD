# Change Data Capture
Change Data Capture is a pattern refers to the practice of identifying and tracking row-level changes(INSERT, UPDATE, DELETE) in a source system and propagating those changes in a downstream rather than reloading entire datasets every time.
This can be implemeted when your source layer(raw or bronze layer) receives raw change events with operation types like INSERT, UPDATE, DELETE and you want to apply those changes to your intermidiate or Silver table to maintain a consistent current state or full history in SCD Type2.
For this Data Capture in Databricks you have a mechanism called Change Data Feed. 
## Change Data Feed(CDF)
CDF is Delta Lake's native mechanism for exposing row-level change events. when you enabled CDF on a delta table, Delta automatically tracks every INSERT, UPDATE and DELETE in a metadata layer called _change_data. You can query the log using table_changes().
### CDC Pattern 

Source System (Snowflake/OLTP/Bigquery) --- Insert/Update/Delete---> Raw or Bronze(Layer) Table ----- Table_Changes ----> Silver/ Intermidiate Table (applied/merged).

### Real Time Scenario
