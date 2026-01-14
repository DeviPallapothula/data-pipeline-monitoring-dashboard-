"""
Unit Tests for Metrics Collector

This module contains tests for the metrics collection functionality.
"""

import pytest
from datetime import datetime
from src.collectors.metrics_collector import MetricsCollector
from src.models.database import init_database, get_session, PipelineExecution
import os

# Use a test database
TEST_DB = 'data/test_metrics.db'


@pytest.fixture
def setup_test_db():
    """Set up a test database before each test."""
    # Set test database URL
    os.environ['DATABASE_URL'] = f'sqlite:///{TEST_DB}'
    
    # Initialize database
    init_database()
    
    yield
    
    # Cleanup: remove test database
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_record_pipeline_execution(setup_test_db):
    """Test recording a pipeline execution."""
    collector = MetricsCollector()
    
    start_time = datetime.utcnow()
    end_time = datetime.utcnow()
    
    execution = collector.record_pipeline_execution(
        pipeline_name="test_pipeline",
        status="success",
        start_time=start_time,
        end_time=end_time,
        records_processed=1000
    )
    
    assert execution.id is not None
    assert execution.pipeline_name == "test_pipeline"
    assert execution.status == "success"
    assert execution.records_processed == 1000
    
    collector.close()


def test_record_data_quality_metric(setup_test_db):
    """Test recording a data quality metric."""
    collector = MetricsCollector()
    
    metric = collector.record_data_quality_metric(
        pipeline_name="test_pipeline",
        metric_name="completeness",
        metric_value=0.95,
        threshold=0.90
    )
    
    assert metric.id is not None
    assert metric.pipeline_name == "test_pipeline"
    assert metric.metric_name == "completeness"
    assert metric.metric_value == 0.95
    assert metric.passed == True  # 0.95 >= 0.90
    
    collector.close()
