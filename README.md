# 🔍 Log Analytics Platform

A real-time log ingestion and analytics platform built with Apache Kafka, Apache Spark Streaming, MongoDB, Docker, and Power BI. Processes 1M+ server log events/day with anomaly detection and live dashboarding.

---

## 🏗️ Architecture

```
Simulated Server Logs
        │
        ▼
┌─────────────────┐
│  Kafka Producer  │  ← Python · generates 10 events/sec
│  (server-logs)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Apache Kafka    │  ← Message broker · topic: server-logs
│  + Zookeeper     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│   Spark Streaming Consumer   │  ← PySpark · 1-min micro-batches
│   • Schema validation        │
│   • Anomaly detection        │
│   • Metric aggregation       │
└────────┬────────────────────┘
         │
         ├──────────────────────┐
         ▼                      ▼
┌──────────────┐     ┌──────────────────┐
│   MongoDB     │     │    AWS S3         │
│  raw_logs     │     │  (data lake)      │
│  service_     │     │  Parquet format   │
│  metrics      │     └──────────────────┘
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Power BI    │  ← Live dashboard · error rates · latency · anomalies
└──────────────┘
```

---

## 📊 Key Features

- **Real-time ingestion** — 10+ events/second via Kafka
- **Spark Streaming** — 1-minute micro-batch aggregations per service & region
- **Anomaly detection** — flags services with >10% error rate or >800ms avg latency
- **Data quality checks** — schema validation on every event
- **CI/CD** — GitHub Actions runs pytest on every push
- **Dockerized** — full local setup with one command

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Ingestion | Apache Kafka 7.4 |
| Processing | Apache Spark 3.4 (PySpark) |
| Storage | MongoDB 6.0 |
| Orchestration | Docker Compose |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Visualization | Power BI |
| Cloud | AWS S3 |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Java 11 (for Spark)

### 1. Clone the repo
```bash
git clone https://github.com/NIKHILBODDAPATI/log-analytics-platform.git
cd log-analytics-platform
```

### 2. Start infrastructure
```bash
docker-compose up -d
```
This starts: Kafka, Zookeeper, MongoDB, Kafka UI

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Kafka producer
```bash
python producer/producer.py
```

### 5. Start the Spark consumer (new terminal)
```bash
python consumer/consumer.py
```

### 6. Monitor Kafka UI
Open http://localhost:8080 to see live events flowing through Kafka

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_pipeline.py::TestLogEventGeneration::test_event_has_required_fields PASSED
tests/test_pipeline.py::TestLogEventGeneration::test_event_id_is_unique PASSED
tests/test_pipeline.py::TestLogEventGeneration::test_status_code_is_valid PASSED
...
15 passed in 0.42s
```

---

## 📁 Project Structure

```
log-analytics-platform/
├── producer/
│   └── producer.py          # Kafka producer — simulates server logs
├── consumer/
│   └── consumer.py          # Spark Streaming — transforms + stores
├── tests/
│   └── test_pipeline.py     # pytest — 15 pipeline tests
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI/CD
├── docker-compose.yml       # Kafka + MongoDB + Kafka UI
├── requirements.txt
└── README.md
```

---

## 📈 Sample Metrics (MongoDB Output)

```json
{
  "service": "payment-service",
  "region": "eu-central-1",
  "window_start": "2025-09-01T10:00:00",
  "window_end": "2025-09-01T10:01:00",
  "total_requests": 612,
  "error_count": 74,
  "avg_latency_ms": 843.2,
  "error_rate": 0.121,
  "anomaly": true,
  "anomaly_reason": "High error rate"
}
```

---

## 🔮 Future Improvements

- Add AWS S3 sink for long-term storage
- Grafana dashboard for real-time monitoring
- Kubernetes deployment for production scale
- dbt models for analytical transformations

---

## 👤 Author

**Nikhil Boddapati**
- LinkedIn: [linkedin.com/in/nikhil-boddapati](https://linkedin.com/in/nikhil-boddapati)
- GitHub: [github.com/NIKHILBODDAPATI](https://github.com/NIKHILBODDAPATI)
