# End-to-End Banking Analytics Data Pipeline

A production-grade data pipeline that simulates real banking operations, captures changes in real-time, stages data in a data lake, and transforms it into analytics-ready tables with historical tracking (SCD Type 2) and temporal joins.

## Project Overview

This pipeline demonstrates a complete modern data stack architecture used by financial institutions and large enterprises. It captures transactional data from a PostgreSQL OLTP database, streams changes via Kafka+Debezium CDC, stages Parquet files in MinIO, loads them into Snowflake, and transforms them using dbt with SCD Type 2 dimensional modeling. Everything is orchestrated by Airflow with automated CI/CD via GitHub Actions.

**Use Case:** Track customer and account changes over time while maintaining referential integrity in fact tables using temporal joins.

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Source** | PostgreSQL | OLTP database with logical replication |
| **CDC** | Debezium + Kafka | Real-time change capture and streaming |
| **Data Lake** | MinIO | S3-compatible object storage for Parquet staging |
| **Orchestration** | Apache Airflow | DAG scheduling and pipeline automation |
| **Cloud DW** | Snowflake | Scalable cloud data warehouse |
| **Transformation** | dbt | Data transformation with SCD Type 2 and temporal joins |
| **Testing** | GitHub Actions | CI/CD for automated testing and deployment |
| **Language** | Python | Data scripts and DAG development |

---

## Implementation Overview

### 1. Data Simulation (Faker + PostgreSQL)

- 1,000 customers with realistic attributes
- 2,000 accounts with varying balances, types, and currencies
- 5,000 transactions with realistic timestamps

Data generator creates synthetic banking data and inserts it into PostgreSQL. Every INSERT is captured by PostgreSQL's WAL, enabling Debezium to detect changes without modifying application code.

---

### 2. Kafka + Debezium CDC (Change Data Capture)

- Zero-loss change capture from PostgreSQL WAL
- Streaming changes to Kafka topics in real-time
- Exactly-once delivery semantics

Debezium monitors PostgreSQL's transaction log and publishes every INSERT, UPDATE, and DELETE to Kafka topics. Downstream systems react to data changes near real-time. The connector runs continuously in the background.

---

### 3. MinIO Data Lake (Parquet Staging)

- Parquet files organized by table directory
- Columnar compression (70-80% savings vs JSON)
- S3-compatible storage for standard data tools
- Historical Parquet files retained for point-in-time recovery

Kafka consumer service converts incoming change events into Parquet format and uploads to MinIO. This serves as a reliable intermediate layer between streaming CDC and the data warehouse.

---

### 4. Airflow Orchestration (Data Loading)

- Daily scheduled DAGs at 00:00 UTC
- Automatic Parquet download and Snowflake upload
- Schema validation and row count verification
- Manual trigger capability from Airflow UI

First Airflow DAG downloads latest Parquet files from MinIO, creates fresh Snowflake tables with correct schema, uploads files to Snowflake staging, executes COPY commands to load data, and verifies row counts. Failed tasks automatically retry.

---

### 5. dbt Transformations (SCD Type 2 + Temporal Joins)

- Snapshots track customer/account changes over time
- Staging layer cleans and renames raw columns
- Dimensions with effective date ranges preserve history
- Facts with temporal joins ensure correct dimension versions per transaction date
- Data quality tests validate all transformations

Second Airflow DAG triggers dbt in sequence. Snapshots compare new data against previous versions—if columns changed, old rows are marked with end dates. Staging tables clean raw data. Dimensions are built from snapshots. Fact tables use temporal joins to match each transaction to the correct account/customer version based on transaction date.

---

### 6. GitHub Actions CI/CD (Automated Testing & Deployment)

- CI tests code BEFORE merge to main (validates dbt compilation, Python syntax, unit tests)
- CD deploys to production AFTER merge (runs snapshots, staging, facts, data quality tests)
- Feature branch workflow ensures only tested code reaches production

When code is pushed to a feature branch and PR created to main, CI automatically runs tests. Code can only merge if all tests pass. Once merged, CD automatically deploys to production Snowflake with zero manual steps.

---

## Quick Start

```bash
# 1. Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Create dbt profiles
mkdir C:\Users\Tanisha\.dbt
# Edit C:\Users\Tanisha\.dbt\profiles.yml with Snowflake credentials

# 3. Start Docker
docker-compose up -d
docker-compose ps  # Wait for all "Up"

# 4. Load data
cd data-generator && python data_generator.py
cd kafka-debezium && python setup_postgres_connector.py

# 5. Run pipeline
# Open http://localhost:8081 (Airflow UI)
# Trigger: minio_to_snowflake_banking (7-15 min)
# Trigger: SCD2_snapshots (5-13 min)


## Key Features

- Real-time CDC capturing every database change instantly
- SCD Type 2 tracking historical changes with effective dates
- Temporal joins linking transactions to correct dimension versions
- Automated pipelines via Airflow DAGs on schedule
- Data quality validation through dbt tests
- GitHub Actions CI/CD automating testing and deployment
- Scalable architecture built on Snowflake




