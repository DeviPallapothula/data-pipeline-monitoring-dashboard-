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
        
        Raises:
            ValueError: If input validation fails
            DatabaseError: If database operation fails
        """
        # Input validation
        if not pipeline_name or not pipeline_name.strip():
            raise ValueError("Pipeline name cannot be empty")
        
        if status not in ['success', 'failed', 'running']:
            raise ValueError(f"Invalid status: {status}. Must be 'success', 'failed', or 'running'")
        
        if not isinstance(start_time, datetime):
            raise ValueError("start_time must be a datetime object")
        
        if end_time is not None and not isinstance(end_time, datetime):
            raise ValueError("end_time must be a datetime object or None")
        
        if end_time and start_time and end_time < start_time:
            raise ValueError("end_time cannot be before start_time")
        
        if not isinstance(records_processed, int) or records_processed < 0:
            raise ValueError("records_processed must be a non-negative integer")
        
        try:
            # Calculate duration if end_time is provided
            duration_seconds = None
            if end_time and start_time:
                duration_seconds = (end_time - start_time).total_seconds()
                if duration_seconds < 0:
                    raise ValueError("Calculated duration cannot be negative")
            
            execution = PipelineExecution(
                pipeline_name=pipeline_name.strip(),
                status=status,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration_seconds,
                records_processed=records_processed,
                error_message=error_message[:1000] if error_message else None  # Limit error message length
            )
            
            self.session.add(execution)
            self.session.commit()
            logger.info(f"Recorded pipeline execution: {pipeline_name} - {status}")
            return execution
        except ValueError:
            self.session.rollback()
            raise
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error recording pipeline execution: {e}", exc_info=True)
            from src.utils.error_handler import DatabaseError
            raise DatabaseError(f"Failed to record pipeline execution: {str(e)}") from e
    
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
        
        Raises:
            ValueError: If input validation fails
            DatabaseError: If database operation fails
        """
        # Input validation
        if not pipeline_name or not pipeline_name.strip():
            raise ValueError("Pipeline name cannot be empty")
        
        if not metric_name or not metric_name.strip():
            raise ValueError("Metric name cannot be empty")
        
        if not isinstance(metric_value, (int, float)) or metric_value < 0 or metric_value > 1:
            raise ValueError("metric_value must be a number between 0.0 and 1.0")
        
        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
            raise ValueError("threshold must be a number between 0.0 and 1.0")
        
        try:
            passed = metric_value >= threshold
            
            metric = DataQualityMetric(
                pipeline_name=pipeline_name.strip(),
                metric_name=metric_name.strip(),
                metric_value=float(metric_value),
                threshold=float(threshold),
                passed=passed
            )
            
            self.session.add(metric)
            self.session.commit()
            logger.info(f"Recorded data quality metric: {pipeline_name} - {metric_name} = {metric_value}")
            return metric
        except ValueError:
            self.session.rollback()
            raise
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error recording data quality metric: {e}", exc_info=True)
            from src.utils.error_handler import DatabaseError
            raise DatabaseError(f"Failed to record data quality metric: {str(e)}") from e
    
    def collect_system_metrics(self):
        """
        Collect current system resource metrics (CPU, Memory, Disk).
        
        Returns:
            Dictionary with system metrics
        
        Raises:
            RuntimeError: If system metrics cannot be collected
            DatabaseError: If database operation fails
        """
        try:
            # Get CPU usage with error handling
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                if cpu_percent < 0 or cpu_percent > 100:
                    raise ValueError(f"Invalid CPU percentage: {cpu_percent}")
            except Exception as e:
                logger.warning(f"Failed to get CPU metrics: {e}")
                cpu_percent = 0.0
            
            # Get memory usage with error handling
            try:
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                if memory_percent < 0 or memory_percent > 100:
                    raise ValueError(f"Invalid memory percentage: {memory_percent}")
            except Exception as e:
                logger.warning(f"Failed to get memory metrics: {e}")
                memory_percent = 0.0
            
            # Get disk usage with error handling
            try:
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                if disk_percent < 0 or disk_percent > 100:
                    raise ValueError(f"Invalid disk percentage: {disk_percent}")
            except Exception as e:
                logger.warning(f"Failed to get disk metrics: {e}")
                disk_percent = 0.0
            
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
            logger.error(f"Error collecting system metrics: {e}", exc_info=True)
            from src.utils.error_handler import DatabaseError
            raise DatabaseError(f"Failed to collect system metrics: {str(e)}") from e
    
    def close(self):
        """Close the database session."""
        self.session.close()
