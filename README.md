# E-Commerce & Modern Trade Data Analytics Platform

## 1. Project Overview

This project is an end-to-end **Data Engineering and Analytics platform** designed for a retail business handling E-Commerce, Modern Trade, and Retail sales data.

The platform processes customer, product, order, order-item, and payment data from source systems and transforms it into analytics-ready data for business reporting.

### Key objectives

* Build scalable ETL/ELT pipelines
* Process 100K+ records
* Implement incremental data loading
* Perform data-quality validation
* Implement source-to-target reconciliation
* Build a Snowflake analytical data warehouse
* Implement SCD Type 2 for historical changes
* Orchestrate pipelines using Airflow
* Support batch and streaming data processing
* Provide analytics through Power BI

---

# 2. Business Requirements

The business requires a centralized data platform to analyze:

### Sales Analytics

* Daily and monthly sales
* Total revenue
* Sales by channel
* Sales by product
* Sales by region
* Top-selling products

### Customer Analytics

* Customer purchase behavior
* Customer-wise revenue
* New and existing customers
* Customer activity by region

### Order Analytics

* Total orders
* Order status distribution
* Cancelled orders
* Average order value
* Order trends

### Payment Analytics

* Successful payments
* Failed payments
* Payment methods
* Payment reconciliation

### Data Engineering Requirements

* Daily data ingestion
* Incremental processing
* Data-quality checks
* Duplicate detection
* Null validation
* Referential-integrity checks
* Source-target count reconciliation
* Error handling and reprocessing
* Pipeline monitoring

---

# 3. Architecture

```text
                         SOURCE SYSTEM
                              |
                              v
                    PostgreSQL / REST API
                              |
                              v
                     Python ETL / Extract
                              |
                              v
                       AWS S3 - RAW
                              |
                              v
                     AWS Glue / PySpark
                              |
                              v
                    AWS S3 - PROCESSED
                              |
                              v
                         Snowflake
                              |
                +-------------+-------------+
                |             |             |
                v             v             v
             RAW Layer    STAGING Layer   ANALYTICS
                                              |
                                    +---------+---------+
                                    |         |         |
                                    v         v         v
                               Dimensions   Fact     DQ Checks
                                              |
                                              v
                                      Reconciliation
                                              |
                                              v
                                           Airflow
                                              |
                                              v
                                          Power BI
```

### Streaming Extension

```text
Application Events
       |
       v
     Kafka
       |
       v
Kafka Consumer
       |
       v
Processing
       |
       v
Snowflake
       |
       v
Power BI / Analytics
```

---

# 4. Technology Stack

| Technology | Purpose                               |
| ---------- | ------------------------------------- |
| Python     | ETL, data generation and processing   |
| Pandas     | Data transformation                   |
| PostgreSQL | Source transactional database         |
| AWS S3     | Data lake / raw and processed storage |
| AWS Glue   | ETL processing                        |
| PySpark    | Distributed data processing           |
| Snowflake  | Cloud data warehouse                  |
| SQL        | Data transformation and analytics     |
| Airflow    | Pipeline orchestration                |
| Kafka      | Real-time data streaming              |
| Power BI   | Business reporting                    |
| Docker     | Containerization                      |
| Git/GitHub | Version control                       |
| CI/CD      | Automated deployment                  |

---

# 5. Data Model

## Source Tables

### Customers

```text
customers
---------
customer_id
customer_name
email
phone
city
state
country
created_at
updated_at
```

### Products

```text
products
--------
product_id
product_name
category
brand
price
cost
created_at
updated_at
```

### Orders

```text
orders
------
order_id
customer_id
order_date
channel
order_status
total_amount
created_at
updated_at
```

### Order Items

```text
order_items
-----------
order_item_id
order_id
product_id
quantity
unit_price
discount
amount
created_at
updated_at
```

### Payments

```text
payments
--------
payment_id
order_id
payment_date
payment_method
payment_status
amount
transaction_id
created_at
updated_at
```

## Analytical Model

The Snowflake warehouse follows a **Star Schema**.

```text
                 DIM_CUSTOMER
                      |
                      |
DIM_PRODUCT ---- FACT_SALES ---- DIM_DATE
                      |
                      |
                 DIM_CHANNEL
```

### FACT_SALES

```text
sales_key
order_id
customer_key
product_key
date_key
channel_key
quantity
unit_price
discount
sales_amount
created_at
updated_at
```

---

# 6. ETL Pipeline

## Step 1 — Extract

Data is extracted from the PostgreSQL source database.

```text
PostgreSQL
    |
    v
Python Extraction
    |
    v
CSV / JSON
```

The extraction process supports both initial and incremental data extraction.

---

## Step 2 — Raw Data

Extracted data is stored in the AWS S3 raw layer.

```text
s3://bucket/raw/customers/
s3://bucket/raw/products/
s3://bucket/raw/orders/
s3://bucket/raw/order_items/
s3://bucket/raw/payments/
```

Raw data is retained for audit and reprocessing purposes.

---

## Step 3 — Transformation

AWS Glue / PySpark processes the raw data.

Typical transformations include:

* Removing duplicates
* Handling null values
* Standardizing data types
* Validating business rules
* Standardizing dates
* Validating customer/product references
* Calculating derived fields

---

## Step 4 — Snowflake Loading

Processed data is loaded into Snowflake.

```text
S3
 |
 v
Snowflake External/Internal Stage
 |
 v
RAW
 |
 v
STAGING
 |
 v
ANALYTICS
```

The analytical layer contains fact and dimension tables used by reporting tools.

---

# 7. Data Quality

Data-quality checks are performed before data reaches the final analytical layer.

### Null Validation

```sql
SELECT *
FROM orders
WHERE customer_id IS NULL;
```

### Duplicate Validation

```sql
SELECT email, COUNT(*)
FROM customers
GROUP BY email
HAVING COUNT(*) > 1;
```

### Invalid Amount

```sql
SELECT *
FROM orders
WHERE total_amount <= 0;
```

### Referential Integrity

```sql
SELECT o.*
FROM orders o
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

### Data-quality rules

* Required fields should not be NULL
* Primary keys must be unique
* Foreign keys must exist
* Amounts must be valid
* Dates must be valid
* Duplicate records must be identified
* Source and target counts must be reconciled

Invalid records are moved to a rejected/error area for investigation and reprocessing.

---

# 8. Reconciliation

Source-to-target reconciliation ensures that data processed by the pipeline is complete and accurate.

### Example

```text
Source Records       = 50,000
Processed Records    = 49,950
Rejected Records     = 50
Target Records       = 49,950
```

The pipeline compares:

```text
Source Count
     |
     v
Processed Count
     |
     v
Rejected Count
     |
     v
Target Count
```

### Audit Table

```text
PIPELINE_AUDIT
--------------
run_id
pipeline_name
source_count
target_count
rejected_count
start_time
end_time
status
error_message
```

This allows the team to identify missing records and investigate pipeline failures.

---

# 9. Incremental Loading

Instead of processing the complete dataset every day, the pipeline processes only new or changed records.

The `updated_at` column is used as the watermark.

```text
Last Successful Run
        |
        v
Read Last Watermark
        |
        v
Extract Changed Records
        |
        v
Transform
        |
        v
Load Snowflake
        |
        v
Update Watermark
```

Example:

```sql
SELECT *
FROM orders
WHERE updated_at > :last_watermark;
```

For Snowflake dimension/fact loading, `MERGE` can be used to insert new records and update existing records.

```sql
MERGE INTO target t
USING source s
ON t.order_id = s.order_id

WHEN MATCHED THEN
    UPDATE SET
        t.total_amount = s.total_amount,
        t.updated_at = s.updated_at

WHEN NOT MATCHED THEN
    INSERT (
        order_id,
        customer_id,
        total_amount,
        updated_at
    )
    VALUES (
        s.order_id,
        s.customer_id,
        s.total_amount,
        s.updated_at
    );
```

---

# 10. SCD Type 2

Slowly Changing Dimension Type 2 is used to maintain historical changes in dimension data.

For example, if a customer's city changes:

```text
Before

Customer ID | City    | Start Date | End Date   | Current
101         | Patna   | 2025-01-01 | 2026-05-10 | N
```

A new record is created:

```text
Customer ID | City      | Start Date | End Date | Current
101         | Bangalore | 2026-05-11 | NULL     | Y
```

Typical SCD Type 2 columns:

```text
customer_key
customer_id
customer_name
city
state
effective_start_date
effective_end_date
is_current
```

This allows historical reporting based on the customer's information at the time of the transaction.

---

# 11. Monitoring

Airflow is used to orchestrate and monitor the data pipeline.

Example DAG:

```text
Extract
   |
   v
Upload to S3
   |
   v
Glue Processing
   |
   v
Snowflake Load
   |
   v
Data Quality
   |
   v
Reconciliation
   |
   v
Success / Failure
```

### Monitoring includes

* Pipeline status
* Execution time
* Record counts
* Failed records
* Data-quality failures
* Source-target mismatch
* Task retries
* Pipeline failures
* Error logs

Airflow retry logic can automatically retry transient failures.

---

# 12. Screenshots

Screenshots can be added here as the project progresses.

Recommended screenshots:

### PostgreSQL

```text
Screenshot:
PostgreSQL source tables and sample records
```

### Python ETL

```text
Screenshot:
Python ETL execution and generated record counts
```

### AWS S3

```text
Screenshot:
S3 raw and processed folders
```

### AWS Glue

```text
Screenshot:
Glue job execution
```

### Snowflake

```text
Screenshot:
Snowflake schemas, tables and query results
```

### Airflow

```text
Screenshot:
Airflow DAG and successful pipeline execution
```

### Power BI

```text
Screenshot:
Sales and business KPI dashboard
```

---

# 13. How to Run

## Prerequisites

Install:

* Python 3.x
* PostgreSQL
* VS Code
* Git

Optional cloud components:

* AWS account
* Snowflake account
* Airflow
* Kafka
* Power BI

---

## Step 1 — Clone Repository

```bash
git clone <repository-url>
cd ecommerce-data-engineering
```

## Step 2 — Create Virtual Environment

Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## Step 3 — Install Dependencies

```powershell
pip install -r requirements.txt
```

## Step 4 — Configure Environment

Create:

```text
config/.env
```

Example:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ecommerce_analytics
DB_USER=postgres
DB_PASSWORD=YOUR_PASSWORD
```

Do not commit `.env` to GitHub.

## Step 5 — Create Database Tables

Run:

```text
sql/source/01_create_source_tables.sql
```

against the PostgreSQL database.

## Step 6 — Generate Test Data

```powershell
python src/data_generator/generate_data.py
```

This generates realistic customer, product and order data.

## Step 7 — Run ETL

```powershell
python src/extract/extract_data.py
```

Then execute the transformation and loading pipelines.

---

# 14. Interview Discussion Points

This project can be discussed in interviews around the following areas.

### SQL

* Joins
* CTEs
* Window functions
* Duplicate handling
* Query optimization
* Aggregations
* Incremental queries

### ETL

* Full vs incremental load
* ETL vs ELT
* Error handling
* Retry mechanism
* Reprocessing
* Data validation
* Source-target reconciliation

### Snowflake

* Warehouses
* Databases and schemas
* Stages
* COPY INTO
* MERGE
* Time Travel
* Streams and Tasks
* Performance optimization
* RBAC

### AWS

* S3
* Glue
* Glue Catalog
* Glue Jobs
* IAM
* Data lake architecture

### Airflow

* DAGs
* Operators
* Dependencies
* Scheduling
* Retries
* Failure handling
* Monitoring

### Kafka

* Topics
* Partitions
* Producers
* Consumers
* Consumer groups
* Offsets
* Duplicate handling

### Data Quality

* Null checks
* Duplicate checks
* Referential integrity
* Business-rule validation
* Reconciliation
* Rejected records

### Scenario-Based Questions

Be prepared to explain:

1. What happens if the ETL pipeline fails halfway?
2. How would you process only changed records?
3. How would you handle duplicate records?
4. How would you reprocess failed records?
5. How would you identify missing records between source and Snowflake?
6. How would you handle a schema change?
7. How would you improve a slow SQL query?
8. How would you implement SCD Type 2?
9. How would you monitor a production pipeline?
10. How would you design the pipeline for millions of records?

---

# 15. Project Summary for Interview

> I worked on an end-to-end E-Commerce and Modern Trade Data Analytics platform. The source data was coming from transactional systems such as PostgreSQL. We extracted the data using ETL pipelines, stored raw data in S3, processed and validated it using AWS Glue and PySpark, and loaded it into Snowflake. In Snowflake, we maintained raw, staging, and analytics layers with fact and dimension tables. We implemented incremental loading, data-quality checks, source-to-target reconciliation, and SCD Type 2 for historical changes. Airflow was used for orchestration and monitoring, while Power BI consumed the curated data for business reporting.
