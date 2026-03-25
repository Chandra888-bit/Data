# Change Data Capture (CDC) in Databricks - Complete Guide

## What is Change Data Capture?
Change Data Capture is a pattern that **tracks and propagates only the rows that changed** (INSERT, UPDATE, DELETE) in your source data, instead of reloading the entire dataset every time. This saves time, reduces costs, and keeps downstream tables synchronized with source data.

**Example**: Instead of copying 1 million rows when only 100 rows changed, CDC captures and processes just those 100 changed rows.

---

## What is Change Data Feed (CDF)?
CDF is **Delta Lake's built-in change tracking system**. When you enable CDF on a table, Delta automatically:
- Records every INSERT, UPDATE, and DELETE operation
- Stores metadata with each change (what changed, when, and what type)
- Allows you to query just the changes using `table_changes()` function

---

## Data Flow Architecture

```
SOURCE SYSTEM (New/Updated Data)
        ↓
BRONZE TABLE (Raw Data with CDF enabled)
   - Receives inserts, updates, deletes
   - CDF tracks all changes automatically
        ↓
READ CHANGES using table_changes()
   - Get only what changed since last run
   - Includes _change_type (insert, update_postimage, delete)
        ↓
SILVER TABLE (Apply changes via MERGE)
   - Insert new records
   - Update existing records
   - Delete removed records
        ↓
GOLD TABLE (Aggregations & Analytics)
   - Updated with latest silver data
   - Ready for reporting & analysis
```

---

# Notebook Guide

## Notebook 1: Source_File.ipynb
**Purpose**: Create the initial data infrastructure and enable CDC on the bronze table.

**⚠️ Run this FIRST before running change_data_feed.ipynb**

### What This Notebook Does (Step by Step)

#### **Step 1: Clean Up (Drop Existing Tables)**
```sql
DROP TABLE IF EXISTS bronze_table;
DROP TABLE IF EXISTS silver_table;
DROP TABLE IF EXISTS gold_table;
```
- Removes any old tables to start fresh
- Prevents conflicts if you run this multiple times

#### **Step 2: Create Bronze Table (Raw Source Data)**
```python
bronze_data = [
    (1, 'Sai Aditya', 284.34, 2026),
    (2, 'Rachel', 658.26, 2026),
    (3, 'Allen', 465.68, 2026),
    (4, 'Brooke', 349.34, 2026),
    (5, 'Charlie', 567.34, 2026)
]
```
- Creates a table with 5 customer records
- Columns: id, name, amount, year
- Adds `ingested_at` timestamp (current time in America/Chicago timezone)
- **Output**: bronze_table with raw data

**Example Data**:
```
| id | name       | amount | year | ingested_at          |
|----|------------|--------|------|----------------------|
| 1  | Sai Aditya | 284.34 | 2026 | 03/25/2026 02:30:45 |
| 2  | Rachel     | 658.26 | 2026 | 03/25/2026 02:30:45 |
...
```

#### **Step 3: Create Silver Table (Cleaned Data)**
- Creates an identical copy of bronze table
- This is where we'll apply changes later
- Serves as the "clean" version of source data
- **Output**: silver_table with same data as bronze_table

#### **Step 4: Create Gold Table (Aggregated Data)**
```sql
SELECT
    name,
    year,
    SUM(amount) AS total_amount,
    DENSE_RANK() OVER (PARTITION BY year ORDER BY total_amount DESC) AS rank
```
- Aggregates data by customer and year
- Calculates total amounts
- Ranks customers by amount (highest = rank 1)
- **Output**: gold_table with rankings

**Example Output**:
```
| name       | year | total_amount | rank |
|------------|------|--------------|------|
| Rachel     | 2026 | 658.26       | 1    |
| Charlie    | 2026 | 567.34       | 2    |
| Allen      | 2026 | 465.68       | 3    |
...
```

#### **Step 5: Enable Change Data Feed (CDF) on Bronze Table**
```python
spark.sql("ALTER TABLE bronze_table SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')")
```
- **Activates** change tracking on bronze_table
- Delta will now record every INSERT, UPDATE, DELETE
- This is the KEY step that enables CDC

#### **Step 6: Verify CDF is Enabled**
```sql
DESCRIBE EXTENDED bronze_table;
```
- Shows all table properties
- Look for: `delta.enableChangeDataFeed = true` in output
- Confirms CDF is ready to track changes

---

## Notebook 2: change_data_feed.ipynb
**Purpose**: Demonstrate a complete CDC pipeline with data modifications, change capture, and propagation.

**⚠️ Must run Source_File.ipynb first!**

### What This Notebook Does (Step by Step)

#### **Step 1: Import Required Libraries**
```python
from delta.tables import DeltaTable
from pyspark.sql import functions as F
```
- `DeltaTable`: For MERGE operations
- `F` (functions): For data transformations

#### **Step 2: First Data Modification - Update & Insert**
```python
bronze_data = [
    (1, 'Sai Aditya', 999.99, 2026),  # UPDATE: amount changed from 284.34 to 999.99
    (6, 'Maya', 712.50, 2026)          # INSERT: new customer
]
```
- **Updates** customer 1's amount
- **Inserts** a new customer 6 (Maya)
- Uses MERGE operation to apply to bronze_table

**Changes in Bronze Table**:
```
| id | name       | amount | year | Change Type |
|----|------------|--------|------|-------------|
| 1  | Sai Aditya | 999.99 | 2026 | UPDATED    |
| 6  | Maya       | 712.50 | 2026 | INSERTED   |
```

#### **Step 3: Delete Operation**
```sql
DELETE FROM bronze_table WHERE id = 2
```
- **Deletes** Rachel (customer id=2) from bronze_table
- CDF records this as a DELETE operation

**Change in Bronze Table**:
```
| id | name   | Change Type |
|----|--------|-------------|
| 2  | Rachel | DELETED    |
```

#### **Step 4: Read Changes from CDC**
```python
changes_df = spark.read.format("delta")
    .option('readChangeData', True)
    .option('startingVersion', 1)
    .table("bronze_table")
```
- Reads all changes made to bronze_table since version 1
- Returns:
  - **_commit_version**: Which version made the change
  - **_change_type**: INSERT, UPDATE, or DELETE
  - **_commit_timestamp**: When the change happened
  - **Original columns**: id, name, amount, year, ingested_at

**Example Output**:
```
| id | name       | amount | _change_type     | _commit_version | _commit_timestamp     |
|----|------------|--------|------------------|------------------|-----------------------|
| 1  | Sai Aditya | 999.99 | update_postimage | 2                | 2026-03-25 02:30:50 |
| 6  | Maya       | 712.50 | insert           | 2                | 2026-03-25 02:30:50 |
| 2  | Rachel     | 658.26 | delete           | 3                | 2026-03-25 02:30:51 |
```

#### **Step 5: Create Version Tracking Table**
```python
version_data = [(1,)]
version_df = spark.createDataFrame(version_data, ["last_version"])
version_df.write.format("delta").mode("overwrite").saveAsTable("versions_table")
```
- Creates a small table to track the last processed version
- Prevents reprocessing the same changes
- Current value: 1 (meaning we've processed up to version 1)

#### **Step 6: Get Latest Changes Only**
```python
spark.sql(f"""
    SELECT * FROM (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY id ORDER BY _commit_timestamp DESC) as RN
        FROM table_changes('bronze_table', {latest_max_value})
        WHERE _change_type IN ('update_postimage', 'insert', 'delete')
    ) WHERE RN = 1
""")
```
- Gets only the **latest change** for each customer
- Ignores duplicates (if same customer updated multiple times)
- Creates temp_changes view for the next MERGE

**Why?** If customer 1 was updated 3 times, we only need the final state, not all 3 updates.

#### **Step 7: Merge Changes into Silver Table**
```sql
MERGE INTO silver_table
USING temp_changes
ON silver_table.id = temp_changes.id
WHEN MATCHED AND _change_type = 'update_postimage' THEN
    UPDATE SET name = temp_changes.name, amount = temp_changes.amount
WHEN MATCHED AND _change_type = 'delete' THEN
    DELETE
WHEN NOT MATCHED AND _change_type = 'insert' THEN
    INSERT (id, name, amount, year, ingested_at)
    VALUES (...)
```

**This MERGE does three things**:
1. **For UPDATES**: Updates the customer record with new values
2. **For DELETES**: Removes the customer record
3. **For INSERTS**: Adds the new customer record

**Before MERGE**:
```
silver_table:
| id | name   | amount | year |
|----|--------|--------|------|
| 1  | Sai Aditya | 284.34 | 2026 |
| 2  | Rachel | 658.26 | 2026 |
```

**After MERGE**:
```
silver_table:
| id | name       | amount | year |
|----|------------|--------|------|
| 1  | Sai Aditya | 999.99 | 2026 |  ← UPDATED
| 6  | Maya       | 712.50 | 2026 |  ← INSERTED
```
(Rachel deleted, so row 2 removed)

#### **Step 8: Update Version Tracker**
```python
latest_commit_version = spark.sql(
    "SELECT max(_commit_version) FROM table_changes('bronze_table', 1)"
).collect()[0][0]
spark.sql(f"UPDATE versions_table SET last_version={latest_commit_version}")
```
- Gets the highest commit version from bronze changes
- Updates versions_table so next run starts from this version
- Prevents reprocessing the same changes

**versions_table after update**:
```
| last_version |
|--------------|
| 3            |  ← Now we've processed up to version 3
```

#### **Step 9: Regenerate Gold Table**
```python
gold_df = spark.sql("""
    WITH aggregated AS (
        SELECT name, year, SUM(amount) AS total_amount
        FROM silver_table
        GROUP BY name, year
    )
    SELECT name, year, total_amount,
           DENSE_RANK() OVER (PARTITION BY year ORDER BY total_amount DESC) AS rank
    FROM aggregated
""")
```
- Recalculates aggregations based on updated silver_table
- Includes new customer, reflects updates, excludes deleted customers

**Updated Gold Table**:
```
| name       | year | total_amount | rank |
|------------|------|--------------|------|
| Sai Aditya | 2026 | 999.99       | 1    |  ← UPDATED amount
| Maya       | 2026 | 712.50       | 2    |  ← NEW
| Charlie    | 2026 | 567.34       | 3    |
| Allen      | 2026 | 465.68       | 4    |
```
(Rachel removed from rankings)

#### **Step 10: Repeat Cycle**
The notebook demonstrates running the entire cycle again with different data to show how CDC handles multiple change batches.

---

## Summary: How CDC Works in This Example

| Step | Action | Result |
|------|--------|--------|
| 1 | Source_File.ipynb creates tables & enables CDF | Tables ready, CDF active |
| 2 | Data changes in bronze_table (insert/update/delete) | Changes recorded by CDF |
| 3 | Read changes using `table_changes()` | Get list of what changed |
| 4 | MERGE into silver_table | Silver table synchronized |
| 5 | Update gold_table | Analytics reflect latest data |
| 6 | Track version | Ready for next batch of changes |

---

## How to Run

1. **Open Source_File.ipynb**
   - Click "Run All" or run each cell sequentially
   - Wait for completion (should see 3 tables created)
   - Verify bronze_table has CDF enabled

2. **Open change_data_feed.ipynb**
   - Click "Run All" or run each cell sequentially
   - Watch data flow through the pipeline
   - See changes from bronze → silver → gold

3. **Modify & Experiment**
   - Change customer names/amounts in cell 2
   - Add more delete operations
   - Re-run to see CDC in action

---

## Key Terms

| Term | Meaning |
|------|---------|
| **Bronze** | Raw, unprocessed source data |
| **Silver** | Cleaned, deduplicated data with CDC applied |
| **Gold** | Aggregated, analytical-ready data |
| **CDF** | Change Data Feed - Delta's change tracking |
| **_change_type** | Type of change: insert, update_postimage, delete |
| **_commit_version** | Version number of the change |
| **MERGE** | SQL operation to insert/update/delete records |
| **table_changes()** | Function to read CDC data |

