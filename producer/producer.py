"""
Log Analytics Platform - Kafka Producer
Simulates real-time server log events (HTTP requests, errors, latency)
"""

import json
import random
import time
import uuid
from datetime import datetime
from kafka import KafkaProducer

# ── Config ──────────────────────────────────────────────────────────────────
KAFKA_BROKER = "localhost:9092"
TOPIC = "server-logs"
EVENTS_PER_SECOND = 10

# ── Simulated data pools ─────────────────────────────────────────────────────
SERVICES = ["auth-service", "payment-service", "user-service", "api-gateway", "recommendation-engine"]
ENDPOINTS = ["/login", "/checkout", "/profile", "/search", "/recommend", "/health", "/api/v1/orders"]
STATUS_CODES = [200, 200, 200, 200, 201, 400, 401, 404, 500, 503]  # weighted toward 200
LEVELS = ["INFO", "INFO", "INFO", "WARN", "ERROR"]  # weighted toward INFO
REGIONS = ["eu-west-1", "eu-central-1", "us-east-1"]


def generate_log_event() -> dict:
    """Generate a single simulated server log event."""
    status = random.choice(STATUS_CODES)
    level = "ERROR" if status >= 500 else ("WARN" if status >= 400 else "INFO")
    latency = round(random.uniform(10, 2000), 2)  # ms

    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "service": random.choice(SERVICES),
        "endpoint": random.choice(ENDPOINTS),
        "status_code": status,
        "level": level,
        "latency_ms": latency,
        "region": random.choice(REGIONS),
        "is_error": status >= 500,
        "is_slow": latency > 1000,
    }


def create_producer() -> KafkaProducer:
    """Create and return a Kafka producer."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8"),
    )


def run_producer():
    """Continuously produce log events to Kafka."""
    producer = create_producer()
    print(f"🚀 Starting log producer → topic: {TOPIC}")
    print(f"📊 Rate: {EVENTS_PER_SECOND} events/second\n")

    total_sent = 0
    try:
        while True:
            for _ in range(EVENTS_PER_SECOND):
                event = generate_log_event()
                producer.send(
                    topic=TOPIC,
                    key=event["service"],
                    value=event,
                )
                total_sent += 1

            producer.flush()
            print(f"✅ Sent {total_sent} events | Last: {event['service']} {event['status_code']} {event['latency_ms']}ms")
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n🛑 Producer stopped. Total events sent: {total_sent}")
    finally:
        producer.close()


if __name__ == "__main__":
    run_producer()
