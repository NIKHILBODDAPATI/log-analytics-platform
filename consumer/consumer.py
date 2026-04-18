"""
Log Analytics Platform - Spark Streaming Consumer
Reads from Kafka, transforms logs, detects anomalies, stores to MongoDB
"""

import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, window, count, avg, sum as spark_sum,
    when, current_timestamp, to_timestamp
)
from pyspark.sql.types import (
    StructType, StructField, StringType,
    DoubleType, BooleanType, IntegerType
)
from pymongo import MongoClient
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────────────────
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "server-logs"
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "log_analytics"
CHECKPOINT_DIR = "/tmp/spark-checkpoints"

# ── Log event schema ──────────────────────────────────────────────────────────
LOG_SCHEMA = StructType([
    StructField("event_id", StringType()),
    StructField("timestamp", StringType()),
    StructField("service", StringType()),
    StructField("endpoint", StringType()),
    StructField("status_code", IntegerType()),
    StructField("level", StringType()),
    StructField("latency_ms", DoubleType()),
    StructField("region", StringType()),
    StructField("is_error", BooleanType()),
    StructField("is_slow", BooleanType()),
])


def create_spark_session() -> SparkSession:
    """Initialize Spark session with Kafka and MongoDB packages."""
    return (
        SparkSession.builder
        .appName("LogAnalyticsPipeline")
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,"
                "org.mongodb.spark:mongo-spark-connector_2.12:10.2.0")
        .config("spark.sql.streaming.checkpointLocation", CHECKPOINT_DIR)
        .getOrCreate()
    )


def write_to_mongodb(batch_df, batch_id: int, collection_name: str):
    """Write a micro-batch DataFrame to MongoDB."""
    if batch_df.count() == 0:
        return

    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[collection_name]

    records = batch_df.toPandas().to_dict(orient="records")
    if records:
        collection.insert_many(records)
        print(f"✅ Batch {batch_id} → {len(records)} records → {collection_name}")
    client.close()


def detect_anomalies(df):
    """Flag anomalies: high error rate or high latency per service."""
    return df.withColumn(
        "anomaly",
        when(
            (col("error_rate") > 0.1) | (col("avg_latency_ms") > 800),
            True
        ).otherwise(False)
    ).withColumn(
        "anomaly_reason",
        when(col("error_rate") > 0.1, "High error rate")
        .when(col("avg_latency_ms") > 800, "High latency")
        .otherwise(None)
    )


def run_consumer():
    """Main streaming pipeline: Kafka → Spark → MongoDB."""
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print("🚀 Starting Spark Streaming consumer...")

    # ── Read from Kafka ───────────────────────────────────────────────────────
    raw_stream = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BROKER)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    # ── Parse JSON ────────────────────────────────────────────────────────────
    parsed = (
        raw_stream
        .select(from_json(col("value").cast("string"), LOG_SCHEMA).alias("data"))
        .select("data.*")
        .withColumn("event_time", to_timestamp(col("timestamp")))
    )

    # ── Raw logs → MongoDB (all events) ──────────────────────────────────────
    raw_query = (
        parsed.writeStream
        .foreachBatch(lambda df, bid: write_to_mongodb(df, bid, "raw_logs"))
        .outputMode("append")
        .option("checkpointLocation", f"{CHECKPOINT_DIR}/raw")
        .start()
    )

    # ── Aggregated metrics per service (1-min window) ─────────────────────────
    aggregated = (
        parsed
        .withWatermark("event_time", "2 minutes")
        .groupBy(
            window(col("event_time"), "1 minute"),
            col("service"),
            col("region")
        )
        .agg(
            count("*").alias("total_requests"),
            spark_sum(col("is_error").cast("int")).alias("error_count"),
            avg("latency_ms").alias("avg_latency_ms"),
            (spark_sum(col("is_error").cast("int")) / count("*")).alias("error_rate"),
        )
        .withColumn("window_start", col("window.start").cast("string"))
        .withColumn("window_end", col("window.end").cast("string"))
        .drop("window")
    )

    # ── Anomaly detection ─────────────────────────────────────────────────────
    with_anomalies = detect_anomalies(aggregated)

    agg_query = (
        with_anomalies.writeStream
        .foreachBatch(lambda df, bid: write_to_mongodb(df, bid, "service_metrics"))
        .outputMode("update")
        .option("checkpointLocation", f"{CHECKPOINT_DIR}/aggregated")
        .start()
    )

    print("✅ Streaming pipeline running. Press Ctrl+C to stop.")
    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    run_consumer()
