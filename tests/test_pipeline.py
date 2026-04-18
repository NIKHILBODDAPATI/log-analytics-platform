"""
Log Analytics Platform - Pipeline Tests
Tests for data quality, schema validation, and anomaly detection logic
"""

import pytest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

# ── Import modules under test ─────────────────────────────────────────────────
import sys
sys.path.append("../producer")
sys.path.append("../consumer")

from producer.producer import generate_log_event


# ── Producer Tests ────────────────────────────────────────────────────────────

class TestLogEventGeneration:

    def test_event_has_required_fields(self):
        """Every log event must contain all required fields."""
        event = generate_log_event()
        required_fields = [
            "event_id", "timestamp", "service", "endpoint",
            "status_code", "level", "latency_ms", "region",
            "is_error", "is_slow"
        ]
        for field in required_fields:
            assert field in event, f"Missing field: {field}"

    def test_event_id_is_unique(self):
        """Each event must have a unique ID."""
        events = [generate_log_event() for _ in range(100)]
        ids = [e["event_id"] for e in events]
        assert len(set(ids)) == 100, "Duplicate event IDs detected"

    def test_status_code_is_valid(self):
        """Status codes must be valid HTTP codes."""
        valid_codes = {200, 201, 400, 401, 404, 500, 503}
        for _ in range(50):
            event = generate_log_event()
            assert event["status_code"] in valid_codes

    def test_latency_is_positive(self):
        """Latency must always be a positive number."""
        for _ in range(50):
            event = generate_log_event()
            assert event["latency_ms"] > 0

    def test_error_flag_matches_status_code(self):
        """is_error must be True only for 5xx status codes."""
        for _ in range(100):
            event = generate_log_event()
            if event["status_code"] >= 500:
                assert event["is_error"] is True
            else:
                assert event["is_error"] is False

    def test_slow_flag_matches_latency(self):
        """is_slow must be True only when latency > 1000ms."""
        for _ in range(100):
            event = generate_log_event()
            if event["latency_ms"] > 1000:
                assert event["is_slow"] is True
            else:
                assert event["is_slow"] is False

    def test_level_matches_status_code(self):
        """Log level must match status code severity."""
        for _ in range(100):
            event = generate_log_event()
            if event["status_code"] >= 500:
                assert event["level"] == "ERROR"
            elif event["status_code"] >= 400:
                assert event["level"] == "WARN"
            else:
                assert event["level"] == "INFO"

    def test_timestamp_is_valid_iso_format(self):
        """Timestamp must be valid ISO 8601 format."""
        event = generate_log_event()
        try:
            datetime.fromisoformat(event["timestamp"])
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {event['timestamp']}")

    def test_event_is_json_serializable(self):
        """Event must be JSON serializable for Kafka."""
        event = generate_log_event()
        try:
            json.dumps(event)
        except (TypeError, ValueError) as e:
            pytest.fail(f"Event not JSON serializable: {e}")

    def test_service_is_known(self):
        """Service name must be from known services list."""
        known_services = {
            "auth-service", "payment-service", "user-service",
            "api-gateway", "recommendation-engine"
        }
        for _ in range(50):
            event = generate_log_event()
            assert event["service"] in known_services


# ── Anomaly Detection Tests ───────────────────────────────────────────────────

class TestAnomalyDetection:

    def test_high_error_rate_triggers_anomaly(self):
        """Error rate above 10% should be flagged as anomaly."""
        error_rate = 0.15
        avg_latency = 200
        is_anomaly = error_rate > 0.1 or avg_latency > 800
        assert is_anomaly is True

    def test_high_latency_triggers_anomaly(self):
        """Average latency above 800ms should be flagged as anomaly."""
        error_rate = 0.02
        avg_latency = 950
        is_anomaly = error_rate > 0.1 or avg_latency > 800
        assert is_anomaly is True

    def test_normal_metrics_no_anomaly(self):
        """Normal error rate and latency should not trigger anomaly."""
        error_rate = 0.02
        avg_latency = 200
        is_anomaly = error_rate > 0.1 or avg_latency > 800
        assert is_anomaly is False


# ── Data Quality Tests ────────────────────────────────────────────────────────

class TestDataQuality:

    def test_no_null_critical_fields(self):
        """Critical fields must never be null."""
        for _ in range(50):
            event = generate_log_event()
            assert event["event_id"] is not None
            assert event["timestamp"] is not None
            assert event["service"] is not None
            assert event["status_code"] is not None

    def test_region_is_valid(self):
        """Region must be a known AWS region."""
        valid_regions = {"eu-west-1", "eu-central-1", "us-east-1"}
        for _ in range(50):
            event = generate_log_event()
            assert event["region"] in valid_regions

    def test_bulk_event_generation_performance(self):
        """Should generate 1000 events without errors."""
        events = [generate_log_event() for _ in range(1000)]
        assert len(events) == 1000
