# Change Data Capture
Change Data Capture is a pattern refers to the practice of identifying and tracking row-level changes(INSERT, UPDATE, DELETE) in a source system and propagating those changes in a downstream rather than reloading entire datasets every time.
This can be implemeted when your source layer(raw or bronze layer) receives raw change events with operation types like INSERT, UPDATE, DELETE and you want to apply those changes to your intermidiate or Silver table to maintain a consistent current state or full history in SCD Type2.
For this Data Capture in Databricks you have a mechanism called Change Data Feed. 
## Change Data Feed(CDF)
CDF is Delta Lake's native mechanism for exposing row-level change events. when you enabled CDF on a delta table, Delta automatically tracks every INSERT, UPDATE and DELETE in a metadata layer called _change_data. You can query the log using table_changes().
### CDC Pattern 

Source System (Snowflake/OLTP/Bigquery) --- Insert/Update/Delete---> Raw or Bronze(Layer) Table ----- Table_Changes ----> Silver/ Intermidiate Table (applied/merged).

### Real Time Scenario
You are working for a banking domain for credit card platform. Your team has realeased a new credit card into market with double reward points for buying any thing using this new credit card. There are 5 new customers with this credit card and there will be new customers adding upon day to day. Your job is to know who are the top 3 customers for the fiscal_year so we can give extra promotions to the customers. 
### Step 1(source):
The Source will be coming from some transactional table which is loaded in to your RAW or Bronze Layer(Delta Table) by INSERT,UPDATE and DELETE Operations. For this Bronze LAYER(DELTA TABLE) we will be ENABLING CHANGE DATA FEED = TRUE. 

### Step 2(Silver Table/Intermidiate Table): 


