# 🔍 Log Analytics Platform

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Kafka](https://img.shields.io/badge/Apache%20Kafka-7.4-black?logo=apachekafka)
![Spark](https://img.shields.io/badge/Apache%20Spark-3.4-orange?logo=apachespark)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![CI](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-green?logo=githubactions)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> **Real-time server log ingestion and analytics platform** — processes **1M+ events/day** using Apache Kafka, Spark Streaming, MongoDB, and Docker. Features anomaly detection, data quality monitoring, and automated CI/CD via GitHub Actions.

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     LOG ANALYTICS PIPELINE                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Simulated Server Logs                                      │
│          │                                                   │
│          ▼                                                   │
│   ┌─────────────┐     Python · 10 events/sec                │
│   │   Producer   │ ──────────────────────────────────────   │
│   └──────┬──────┘                                           │
│          │                                                   │
│          ▼                                                   │
│   ┌─────────────┐     Topic: server-logs                    │
│   │    Kafka     │ ──────────────────────────────────────   │
│   └──────┬──────┘     Partitioned by service                │
│          │                                                   │
│          ▼                                                   │
│   ┌──────────────────────────┐                              │
│   │   Spark Streaming         │  Micro-batch · 30s window   │
│   │   ✓ Schema validation     │                              │
│   │   ✓ Anomaly detection     │  Error rate > 10% → ALERT  │
│   │   ✓ Metric aggregation    │  Latency  > 800ms → ALERT  │
│   └──────┬───────────────────┘                              │
│          │                                                   │
│    ┌─────┴──────┐                                           │
│    ▼            ▼                                           │
│  ┌──────┐  ┌─────────┐                                     │
│  │  S3   │  │ MongoDB │  raw_logs + service_metrics         │
│  └──────┘  └────┬────┘                                     │
│                 │                                            │
│                 ▼                                            │
│          ┌──────────┐                                       │
│          │ Power BI  │  Live dashboard · 5+ services        │
│          └──────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Key Features

| Feature | Detail |
|---|---|
| **Throughput** | 1M+ log events/day (10 events/sec) |
| **Anomaly Detection** | Flags services with >10% error rate or >800ms latency |
| **Data Quality** | Schema validation on every event before processing |
| **Observability** | Real-time Power BI dashboard across 5+ services |
| **CI/CD** | GitHub Actions runs pytest on every push |
| **Containerized** | Full local setup with single `docker-compose up` |

---

## 🛠️ Tech Stack

```
Language      → Python 3.10
Ingestion     → Apache Kafka 7.4
Processing    → Apache Spark 3.4 (PySpark)
Storage       → MongoDB 6.0 + AWS S3
Orchestration → Docker Compose
Testing       → pytest (15 tests)
CI/CD         → GitHub Actions
Visualization → Power BI
```

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/NIKHILBODDAPATI/log-analytics-platform.git
cd log-analytics-platform

# 2. Start infrastructure (Kafka + MongoDB + Kafka UI)
docker-compose up -d

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start producer (Terminal 1)
python producer/producer.py

# 5. Start Spark consumer (Terminal 2)
python consumer/consumer.py

# 6. Monitor → http://localhost:8080 (Kafka UI)
```

---

## 🧪 Tests

```bash
pytest tests/ -v
# 15 tests · schema · anomaly detection · data quality · performance
```

---

## 📁 Structure

```
log-analytics-platform/
├── producer/producer.py        # Kafka producer — 10 events/sec
├── consumer/consumer.py        # Spark Streaming — transform + store
├── tests/test_pipeline.py      # 15 pytest tests
├── .github/workflows/ci.yml    # GitHub Actions CI/CD
├── docker-compose.yml          # Kafka + MongoDB + Kafka UI
└── requirements.txt
```

---

## 📊 Sample Anomaly Output

```json
{
  "service": "payment-service",
  "region": "eu-central-1",
  "total_requests": 612,
  "error_count": 74,
  "avg_latency_ms": 843.2,
  "error_rate": 0.121,
  "anomaly": true,
  "anomaly_reason": "High error rate"
}
```

---

**👤 Nikhil Boddapati** · [LinkedIn](https://linkedin.com/in/nikhil-boddapati) · [GitHub](https://github.com/NIKHILBODDAPATI)
