"""
Metrics Collector Module

This module collects and stores pipeline execution metrics.
It provides functions to record pipeline runs, data quality metrics,
and system metrics.
"""

from src.models.database import (
    PipelineExecution, 
    DataQualityMetric, 
    SystemMetric,
    get_session
)
from datetime import datetime
import psutil
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Class to collect and store various types of metrics.
    
    This collector handles:
    - Pipeline execution records
    - Data quality metrics
    - System resource metrics
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.session = get_session()
    
    def record_pipeline_execution(
        self,
        pipeline_name: str,
        status: str,
        start_time: datetime,
        end_time: datetime = None,
        records_processed: int = 0,
        error_message: str = None
    ):
        """
        Record a pipeline execution in the database.
        
        Args:
            pipeline_name: Name of the pipeline
            status: 'success', 'failed', or 'running'
            start_time: When the pipeline started
            end_time: When the pipeline finished (None if still running)
            records_processed: Number of records processed
            error_message: Error details if failed
        
        Returns:
            The created PipelineExecution object
        """
        try:
            # Calculate duration if end_time is provided
            duration_seconds = None
            if end_time and start_time:
                duration_seconds = (end_time - start_time).total_seconds()
            
            execution = PipelineExecution(
                pipeline_name=pipeline_name,
                status=status,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration_seconds,
                records_processed=records_processed,
                error_message=error_message
            )
            
            self.session.add(execution)
            self.session.commit()
            logger.info(f"Recorded pipeline execution: {pipeline_name} - {status}")
            return execution
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error recording pipeline execution: {e}")
            raise
    
    def record_data_quality_metric(
        self,
        pipeline_name: str,
        metric_name: str,
        metric_value: float,
        threshold: float = 0.95
    ):
        """
        Record a data quality metric.
        
        Args:
            pipeline_name: Name of the pipeline
            metric_name: Type of metric (completeness, accuracy, validity, etc.)
            metric_value: The metric score (0.0 to 1.0)
            threshold: Expected threshold for this metric
        
        Returns:
            The created DataQualityMetric object
        """
        try:
            passed = metric_value >= threshold
            
            metric = DataQualityMetric(
                pipeline_name=pipeline_name,
                metric_name=metric_name,
                metric_value=metric_value,
                threshold=threshold,
                passed=passed
            )
            
            self.session.add(metric)
            self.session.commit()
            logger.info(f"Recorded data quality metric: {pipeline_name} - {metric_name} = {metric_value}")
            return metric
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error recording data quality metric: {e}")
            raise
    
    def collect_system_metrics(self):
        """
        Collect current system resource metrics (CPU, Memory, Disk).
        
        Returns:
            Dictionary with system metrics
        """
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Get disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Store metrics in database
            metrics = [
                SystemMetric(metric_type='cpu', metric_value=cpu_percent, unit='%'),
                SystemMetric(metric_type='memory', metric_value=memory_percent, unit='%'),
                SystemMetric(metric_type='disk', metric_value=disk_percent, unit='%')
            ]
            
            for metric in metrics:
                self.session.add(metric)
            
            self.session.commit()
            
            logger.info(f"Collected system metrics: CPU={cpu_percent}%, Memory={memory_percent}%, Disk={disk_percent}%")
            
            return {
                'cpu': cpu_percent,
                'memory': memory_percent,
                'disk': disk_percent,
                'timestamp': datetime.utcnow()
            }
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error collecting system metrics: {e}")
            raise
    
    def close(self):
        """Close the database session."""
        self.session.close()
