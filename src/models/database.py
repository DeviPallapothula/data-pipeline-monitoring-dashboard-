"""
Database models for pipeline monitoring metrics.

This module defines the database schema using SQLAlchemy ORM.
It creates tables to store pipeline execution metrics, data quality scores,
and error logs.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Base class for all models
Base = declarative_base()


class PipelineExecution(Base):
    """
    Model to store pipeline execution records.
    
    Attributes:
        id: Primary key
        pipeline_name: Name of the pipeline
        status: Execution status (success, failed, running)
        start_time: When the pipeline started
        end_time: When the pipeline finished
        duration_seconds: How long it took to run
        records_processed: Number of records processed
        error_message: Error details if failed
    """
    __tablename__ = 'pipeline_executions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_name = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # success, failed, running
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    records_processed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DataQualityMetric(Base):
    """
    Model to store data quality metrics.
    
    Attributes:
        id: Primary key
        pipeline_name: Name of the pipeline
        metric_name: Type of quality metric (completeness, accuracy, etc.)
        metric_value: The actual metric score (0-1)
        threshold: Expected threshold for this metric
        passed: Whether the metric passed the threshold
        timestamp: When this metric was recorded
    """
    __tablename__ = 'data_quality_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_name = Column(String(100), nullable=False, index=True)
    metric_name = Column(String(50), nullable=False)  # completeness, accuracy, validity, etc.
    metric_value = Column(Float, nullable=False)  # 0.0 to 1.0
    threshold = Column(Float, default=0.95)
    passed = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class SystemMetric(Base):
    """
    Model to store system-level metrics.
    
    Attributes:
        id: Primary key
        metric_type: Type of system metric (cpu, memory, disk, etc.)
        metric_value: The actual value
        unit: Unit of measurement (%, MB, GB, etc.)
        timestamp: When this metric was recorded
    """
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_type = Column(String(50), nullable=False, index=True)  # cpu, memory, disk
    metric_value = Column(Float, nullable=False)
    unit = Column(String(20), default='%')
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


def get_database_url():
    """
    Get database URL from environment or config.
    Returns SQLite database path by default.
    """
    db_url = os.getenv('DATABASE_URL', 'sqlite:///data/pipeline_metrics.db')
    # Ensure directory exists for SQLite
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_url


def init_database():
    """
    Initialize the database by creating all tables.
    This function creates the database file and all table structures.
    """
    db_url = get_database_url()
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """
    Create a database session for querying.
    Returns a session object that can be used to interact with the database.
    """
    db_url = get_database_url()
    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    return Session()
