# End-to-End Healthcare Insurance Analytics Data Pipeline

A production-grade data pipeline that simulates real healthcare insurance operations, captures changes in near real-time, stages data in a data lake, and transforms it into analytics-ready tables with historical tracking (SCD Type 2) and temporal joins.

---

## Project Overview

This project demonstrates a modern **payer-style analytics architecture** used by healthcare insurance organizations. It ingests synthetic healthcare insurance data from a PostgreSQL OLTP system, streams changes using Kafka, stages Parquet data in an object store, and transforms it in Snowflake using dbt with **SCD Type 2 dimensional modeling**. The entire workflow is orchestrated with Airflow and deployed through automated CI/CD using GitHub Actions.

**Use Case:**  
Track **member enrollment, policy coverage changes, and claims activity over time**, while ensuring fact tables always join to the **correct historical version** of member and policy dimensions.

---

## Tech Stack

| Component | Technology | Purpose |
|---------|-----------|---------|
| **Source** | PostgreSQL | OLTP database for members, policies, and claims |
| **Streaming / CDC** | Kafka | Event-driven ingestion of data changes |
| **Data Lake** | MinIO | S3-compatible storage for Parquet staging |
| **Orchestration** | Apache Airflow | Pipeline scheduling and dependency management |
| **Cloud DW** | Snowflake | Scalable analytics warehouse |
| **Transformation** | dbt | SCD Type 2 modeling and temporal joins |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Query Tool** | DBeaver | Data validation and exploration |
| **Language** | Python | Data generation, ingestion, and DAGs |

---

## Implementation Overview

### 1. Data Simulation (Faker + PostgreSQL)

- 1,000 synthetic insurance members  
- 1,000+ insurance policies (HMO, PPO, Medicare, Medicaid)  
- 5,000+ insurance claims with realistic statuses and dates  

A Python-based generator creates **synthetic but rule-driven healthcare insurance data** and inserts it into PostgreSQL. Data simulates real-world payer workflows including policy lifecycles and claim processing states. DBeaver is used to validate data across PostgreSQL and Snowflake.

---

### 2. Event-Driven Ingestion (Kafka)

- Near-real-time ingestion of member, policy, and claim events  
- Topic-level separation by entity  
- Replayable event streams  

Changes in PostgreSQL are streamed into Kafka topics, enabling downstream systems to process updates incrementally instead of relying on batch reloads. This mirrors how modern healthcare analytics platforms ingest operational data.

---

### 3. MinIO Data Lake (Parquet Staging)

- Entity-partitioned Parquet files  
- Columnar compression (70–80% storage savings)  
- Historical files retained for backfills and recovery  
- S3-compatible storage  

Kafka consumers convert streaming events into Parquet files and store them in MinIO. This layer decouples ingestion from warehouse loading and enables reliable reprocessing.

---

### 4. Airflow Orchestration (Warehouse Loading)

- Scheduled daily DAGs  
- Automated Parquet-to-Snowflake ingestion  
- Schema validation and row-count checks  
- Retry and failure handling  

Airflow orchestrates ingestion from MinIO into Snowflake using staged COPY operations. Each run validates schema consistency and record counts before downstream transformations.

---

### 5. dbt Transformations (SCD Type 2 + Temporal Joins)

- Snapshots track historical changes to members and policies  
- Staging models standardize raw fields  
- Dimension tables preserve history with effective date ranges  
- Fact tables use temporal joins to resolve correct dimension versions  
- dbt tests enforce data quality and referential integrity  

Snapshots capture attribute changes over time. Dimension tables expose historical views. Claims facts are joined to the **correct policy and member version based on service date**, ensuring accurate historical reporting.

---

### 6. GitHub Actions CI/CD (Automated Validation & Deployment)

- CI runs on every push and pull request  
- Validates Python code, dbt compilation, and project structure  
- CD deploys snapshots, models, and tests on merge to main  
- No manual production deployments  

This workflow ensures only validated transformations and pipelines reach production Snowflake environments.

---

## Quick Start

```bash
# 1. Setup environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Configure dbt profile
mkdir C:\Users\Tanisha\.dbt
# Edit profiles.yml with Snowflake credentials

# 3. Start infrastructure
docker-compose up -d
docker-compose ps

# 4. Generate data
cd data-generator
python data_generator.py

# 5. Run pipeline
# Open Airflow UI
# Trigger: minio_to_snowflake_healthcare
# Trigger: scd2_snapshots



## Key Features

- **API-driven synthetic data generation**  
  Generates realistic healthcare insurance data (members, policies, claims) using rule-based logic to simulate real payer workflows without using sensitive data.

- **Near-real-time ingestion**  
  Event-driven ingestion using Kafka enables incremental processing of member enrollments, policy updates, and claim events instead of full batch reloads.

- **Lakehouse-style architecture**  
  Decouples ingestion and analytics using Parquet files staged in MinIO before loading into Snowflake, improving reliability and reprocessing capability.

- **SCD Type 2 historical tracking**  
  Tracks full history of member and policy attribute changes using dbt snapshots with effective start and end dates.

- **Temporal joins for facts**  
  Ensures each claim is joined to the **correct historical version** of the member and policy based on service date, enabling accurate point-in-time reporting.

- **Analytics-ready dimensional models**  
  Builds clean staging, dimension, and fact tables optimized for BI tools and downstream analytics.

- **Automated orchestration**  
  Apache Airflow schedules and manages ingestion, transformation, validation, and retries with full observability.

- **Built-in data quality checks**  
  dbt tests enforce not-null constraints, referential integrity, accepted values, and snapshot consistency.

- **CI/CD-driven deployments**  
  GitHub Actions automates validation, compilation, testing, and production deployments with zero manual intervention.

- **Enterprise-aligned design**  
  Architecture and modeling patterns align with real-world healthcare insurance and payer analytics platforms.
