# Healthy Lifestyle Cities – Health vs Cost Index (AWS Serverless Data Lake + Python Dashboard)

## Project Overview

This project builds a **serverless data lake on AWS** to analyze health and lifestyle metrics across 44 global cities, then delivers a **modern interactive Python dashboard** to visualize:

* Health vs Cost positioning
* Quadrant value analysis
* Top 10 healthiest cities
* Best value cities (health_score / cost_proxy)

The project demonstrates:

* Data lake architecture design
* Data cleaning & transformation in Athena
* Analytical modeling (weighted scoring + normalization)
* Gold layer curation
* Dashboard delivery independent of AWS infrastructure

---

# 1. Architecture Overview

## Cloud Provider

AWS

## Region

af-south-1 (Cape Town)

## Services Used

* Amazon S3 (raw, processed, gold zones)
* AWS Glue Data Catalog
* Amazon Athena
* IAM
* Parquet (SNAPPY compression)

This architecture is fully serverless and free-tier conscious.

---

# 2. Data Source

Dataset: **Healthy Lifestyle Cities Report 2021**
Format: CSV
Rows: 44 cities

Fields include:

* Life expectancy
* Pollution index
* Obesity %
* Sunshine hours
* Happiness score
* Cost of bottled water
* Cost of gym membership
* Outdoor activities
* Takeout places
* Annual working hours

---

# 3. Data Lake Structure

S3 Bucket:

```
healthy-cities-data-lake-caleb-okkers-2026
```

Structure:

```
raw/
  healthy_lifestyle_2021/
    healthy_lifestyle_city_2021.csv

processed/
  healthy_lifestyle_2021_parquet_v4/

gold/
  healthy_lifestyle_2021/

athena-results/
```

Zones follow medallion architecture principles:

* **Raw** → untouched CSV
* **Processed** → cleaned & typed
* **Gold** → analytical-ready dataset

---

# 4. Data Processing Workflow (Cloud Side)

## Step 1 — Raw Ingestion

The CSV was uploaded to:

```
s3://.../raw/healthy_lifestyle_2021/
```

Athena external table created using OpenCSVSerde.
All columns initially treated as STRING.

---

## Step 2 — Data Cleaning (CTAS to Processed Layer)

Using Athena CTAS:

* Removed currency symbols (£)
* Removed percentage signs (%)
* Converted numeric fields to DOUBLE
* Replaced "-" values with NULL
* Trimmed quoted city names
* Ensured consistent typing

Output:

* Parquet format
* SNAPPY compression
* Fully numeric schema
* 44 valid rows

Table:

```
healthy_cities_db.healthy_cities_processed
```

---

## Step 3 — Analytical Model (View Layer)

Created analytical view:

```
healthy_cities_db.vw_healthy_cities_index
```

### Health Score (0–100 scale)

Weighted min–max normalization:

| Metric          | Weight | Direction |
| --------------- | ------ | --------- |
| Life expectancy | 30%    | Positive  |
| Pollution       | 20%    | Inverse   |
| Obesity         | 15%    | Inverse   |
| Sunshine        | 15%    | Positive  |
| Happiness       | 20%    | Positive  |

NULL values (Fukuoka, Geneva) handled via mean imputation using COALESCE.

---

### Cost Proxy

```
cost_proxy = cost_monthly_gym_membership_city
           + cost_bottle_water_city
```

---

## Step 4 — Gold Layer Creation

Final curated dataset created via CTAS:

```
healthy_cities_db.healthy_cities_gold
```

Characteristics:

* Joined processed + analytical view
* All base metrics included
* health_score
* cost_proxy
* Parquet + SNAPPY
* 44 rows

Export query used for dashboard:

```sql
SELECT *
FROM healthy_cities_db.healthy_cities_gold
ORDER BY health_score DESC;
```

Result downloaded as:

```
data/final.csv
```

At this stage, AWS resources can safely be deleted.

---

# 5. Dashboard Architecture (Local Layer)

Stack:

* Python
* Streamlit
* Plotly
* Pandas

Structure:

```
healthy-cities/
  app.py
  requirements.txt
  data/final.csv
  src/
    charts.py
    metrics.py
```

The dashboard uses the exported gold dataset and is fully independent of AWS.

---

# 6. Dashboard Walkthrough

## Header

Displays project title and notes that data was built using an AWS serverless data lake.

---

## KPI Section

Four key summary metrics:

* Total Cities
* Average Health Score
* Average Cost Proxy
* Best Value City (health_score / cost_proxy)

---

## Main Visualization — Health vs Cost Scatter

X-axis: Cost Proxy
Y-axis: Health Score

Features:

* Interactive hover tooltips
* Median-based quadrant split
* Clean modern layout
* Full metric breakdown in tooltip:

  * Rank
  * Health score
  * Cost proxy
  * Value score
  * Life expectancy
  * Pollution
  * Obesity
  * Happiness
  * Sunshine
  * Annual working hours
  * Gym cost
  * Water cost
  * Outdoor activities
  * Takeout places

### Quadrant Interpretation

| Quadrant                | Meaning                    |
| ----------------------- | -------------------------- |
| High Health / Low Cost  | Best value cities          |
| High Health / High Cost | Premium healthy cities     |
| Low Health / Low Cost   | Budget but weaker outcomes |
| Low Health / High Cost  | Poor value                 |

---

## Rankings Section

### Top 10 Healthiest Cities

Sorted by health_score descending.

### Top 10 Best Value Cities

Sorted by:

```
health_score / cost_proxy
```

Highlights cities delivering strong health outcomes at lower cost.

---

## Data Table

Sortable full dataset including:

* All base metrics
* health_score
* cost_proxy
* value_score

Allows exploratory inspection.

---

# 7. Key Observations

* European cities dominate the upper-right and upper-left quadrants.
* Zurich and Geneva show high health but high cost.
* Fukuoka and Helsinki demonstrate strong value positioning.
* Lower-ranked cities cluster in high pollution + lower life expectancy zones.

---

# 8. Design Decisions

* Serverless architecture to minimize cost.
* Parquet + SNAPPY for optimized storage.
* Medallion-style zone separation.
* Analytical logic separated into view layer.
* Gold dataset created for reproducibility.
* Dashboard decoupled from AWS for portability.

---

# 9. Cost Management Strategy

After project submission:

* Athena results deleted
* Gold S3 objects deleted
* Processed layer optionally deleted
* Glue catalog removed
* Bucket emptied

Local dashboard remains fully functional using exported dataset.

---

# 10. How to Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open:

```
http://localhost:8501
```

---

# 11. Skills Demonstrated

Cloud:

* AWS S3 data lake design
* Athena CTAS transformations
* Data cleaning & schema typing
* Analytical SQL modeling
* Weighted normalization logic

Data Engineering:

* Zone separation (raw → processed → gold)
* Parquet optimization
* Join integrity handling
* NULL imputation strategy

Analytics:

* Multi-factor index design
* Cost proxy modeling
* Value ratio computation

Frontend:

* Interactive dashboard design
* Plotly visualization
* KPI summaries
* Quadrant analysis

---

Security & Access (Implemented)

Private S3 bucket (block public access enabled)

Least-privilege IAM policy scoped to the project bucket/prefixes

Athena/Glue permissions limited to required actions

---

Governance & Monitoring (Not in scope)

Lake Formation not used (single-user portfolio project; would be used for fine-grained table/column permissions in multi-user environments)

CloudWatch not used (no scheduled Glue/Lambda pipelines); would be used for alarms/logging if automation is added

---

# Conclusion

This project demonstrates a complete end-to-end workflow:

Raw dataset → Cloud data lake → Analytical model → Gold dataset → Modern interactive dashboard

It combines data engineering, analytics, and presentation into a portfolio-ready deliverable.
