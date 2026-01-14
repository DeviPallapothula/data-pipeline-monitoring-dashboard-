"""
API Routes Module

This module defines all the REST API endpoints for the monitoring dashboard.
It provides endpoints to retrieve metrics, pipeline status, and system health.
"""

from flask import Blueprint, jsonify, request
from src.models.database import get_session, PipelineExecution, DataQualityMetric, SystemMetric
from src.collectors.metrics_collector import MetricsCollector
from src.utils.error_handler import (
    handle_error, 
    validate_request_data, 
    safe_database_operation,
    DatabaseError,
    ValidationError
)
from datetime import datetime, timedelta
from sqlalchemy import func, desc, Integer
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

# Create a Blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    Returns the status of the API and database connection.
    
    Returns:
        JSON response with health status
    """
    try:
        def check_database():
            session = get_session()
            try:
                # Try a simple query to check database connection
                session.query(PipelineExecution).limit(1).all()
                return True
            finally:
                session.close()
        
        # Use safe database operation wrapper
        safe_database_operation(check_database, "Database health check failed")
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        }), 200
    except DatabaseError as e:
        return handle_error(e, status_code=503, message="Database connection failed")
    except Exception as e:
        return handle_error(e, status_code=500, message="Health check failed")


@api_bp.route('/pipelines', methods=['GET'])
def get_pipelines():
    """
    Get list of all pipelines with their latest execution status.
    
    Query Parameters:
        days: Number of days to look back (default: 7)
    
    Returns:
        JSON response with pipeline summary
    """
    try:
        # Validate and parse query parameters
        try:
            days = int(request.args.get('days', 7))
            if days < 1 or days > 365:
                raise ValidationError("Days parameter must be between 1 and 365")
        except ValueError:
            raise ValidationError("Invalid 'days' parameter. Must be a number.")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        def query_pipelines():
            session = get_session()
            try:
                # Get unique pipeline names
                pipelines = session.query(PipelineExecution.pipeline_name).distinct().all()
                pipeline_list = []
                
                for (pipeline_name,) in pipelines:
                    # Get latest execution
                    latest = session.query(PipelineExecution).filter(
                        PipelineExecution.pipeline_name == pipeline_name
                    ).order_by(desc(PipelineExecution.start_time)).first()
                    
                    # Get statistics
                    stats = session.query(
                        func.count(PipelineExecution.id).label('total_runs'),
                        func.sum(func.cast(PipelineExecution.status == 'success', Integer)).label('success_count'),
                        func.avg(PipelineExecution.duration_seconds).label('avg_duration')
                    ).filter(
                        PipelineExecution.pipeline_name == pipeline_name,
                        PipelineExecution.start_time >= cutoff_date
                    ).first()
                    
                    pipeline_list.append({
                        'name': pipeline_name,
                        'latest_status': latest.status if latest else 'unknown',
                        'latest_execution_time': latest.start_time.isoformat() if latest else None,
                        'total_runs': stats.total_runs or 0,
                        'success_count': stats.success_count or 0,
                        'success_rate': (stats.success_count / stats.total_runs * 100) if stats.total_runs > 0 else 0,
                        'avg_duration_seconds': float(stats.avg_duration) if stats.avg_duration else None
                    })
                
                return pipeline_list
            finally:
                session.close()
        
        pipeline_list = safe_database_operation(query_pipelines, "Failed to query pipelines")
        
        return jsonify({
            'pipelines': pipeline_list,
            'count': len(pipeline_list)
        }), 200
        
    except ValidationError as e:
        return handle_error(e, status_code=400)
    except DatabaseError as e:
        return handle_error(e, status_code=503)
    except Exception as e:
        return handle_error(e, status_code=500)


@api_bp.route('/pipelines/<pipeline_name>/executions', methods=['GET'])
def get_pipeline_executions(pipeline_name):
    """
    Get execution history for a specific pipeline.
    
    Query Parameters:
        limit: Maximum number of records to return (default: 100)
        days: Number of days to look back (default: 30)
    
    Returns:
        JSON response with execution history
    """
    try:
        # Validate pipeline name
        if not pipeline_name or not pipeline_name.strip():
            raise ValidationError("Pipeline name is required")
        
        # Validate and parse query parameters
        try:
            limit = int(request.args.get('limit', 100))
            if limit < 1 or limit > 1000:
                raise ValidationError("Limit must be between 1 and 1000")
            days = int(request.args.get('days', 30))
            if days < 1 or days > 365:
                raise ValidationError("Days must be between 1 and 365")
        except ValueError:
            raise ValidationError("Invalid query parameters. 'limit' and 'days' must be numbers.")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        def query_executions():
            session = get_session()
            try:
                executions = session.query(PipelineExecution).filter(
                    PipelineExecution.pipeline_name == pipeline_name,
                    PipelineExecution.start_time >= cutoff_date
                ).order_by(desc(PipelineExecution.start_time)).limit(limit).all()
                
                return [{
                    'id': ex.id,
                    'status': ex.status,
                    'start_time': ex.start_time.isoformat(),
                    'end_time': ex.end_time.isoformat() if ex.end_time else None,
                    'duration_seconds': ex.duration_seconds,
                    'records_processed': ex.records_processed,
                    'error_message': ex.error_message
                } for ex in executions]
            finally:
                session.close()
        
        execution_list = safe_database_operation(query_executions, "Failed to query pipeline executions")
        
        return jsonify({
            'pipeline_name': pipeline_name,
            'executions': execution_list,
            'count': len(execution_list)
        }), 200
        
    except ValidationError as e:
        return handle_error(e, status_code=400)
    except DatabaseError as e:
        return handle_error(e, status_code=503)
    except Exception as e:
        return handle_error(e, status_code=500)


@api_bp.route('/pipelines/<pipeline_name>/quality', methods=['GET'])
def get_pipeline_quality(pipeline_name):
    """
    Get data quality metrics for a specific pipeline.
    
    Query Parameters:
        days: Number of days to look back (default: 7)
    
    Returns:
        JSON response with quality metrics
    """
    try:
        if not pipeline_name or not pipeline_name.strip():
            raise ValidationError("Pipeline name is required")
        
        try:
            days = int(request.args.get('days', 7))
            if days < 1 or days > 365:
                raise ValidationError("Days must be between 1 and 365")
        except ValueError:
            raise ValidationError("Invalid 'days' parameter. Must be a number.")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        def query_quality_metrics():
            session = get_session()
            try:
                metrics = session.query(DataQualityMetric).filter(
                    DataQualityMetric.pipeline_name == pipeline_name,
                    DataQualityMetric.timestamp >= cutoff_date
                ).order_by(desc(DataQualityMetric.timestamp)).all()
                
                # Group by metric name
                quality_data = {}
                for metric in metrics:
                    if metric.metric_name not in quality_data:
                        quality_data[metric.metric_name] = []
                    
                    quality_data[metric.metric_name].append({
                        'value': metric.metric_value,
                        'threshold': metric.threshold,
                        'passed': metric.passed,
                        'timestamp': metric.timestamp.isoformat()
                    })
                
                return quality_data
            finally:
                session.close()
        
        quality_data = safe_database_operation(query_quality_metrics, "Failed to query quality metrics")
        
        return jsonify({
            'pipeline_name': pipeline_name,
            'quality_metrics': quality_data
        }), 200
        
    except ValidationError as e:
        return handle_error(e, status_code=400)
    except DatabaseError as e:
        return handle_error(e, status_code=503)
    except Exception as e:
        return handle_error(e, status_code=500)


@api_bp.route('/system/metrics', methods=['GET'])
def get_system_metrics():
    """
    Get recent system metrics (CPU, Memory, Disk).
    
    Query Parameters:
        hours: Number of hours to look back (default: 24)
    
    Returns:
        JSON response with system metrics
    """
    try:
        try:
            hours = int(request.args.get('hours', 24))
            if hours < 1 or hours > 168:  # Max 1 week
                raise ValidationError("Hours must be between 1 and 168")
        except ValueError:
            raise ValidationError("Invalid 'hours' parameter. Must be a number.")
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        def query_system_metrics():
            session = get_session()
            try:
                metrics = session.query(SystemMetric).filter(
                    SystemMetric.timestamp >= cutoff_time
                ).order_by(SystemMetric.timestamp).all()
                
                # Group by metric type
                system_data = {
                    'cpu': [],
                    'memory': [],
                    'disk': []
                }
                
                for metric in metrics:
                    if metric.metric_type in system_data:
                        system_data[metric.metric_type].append({
                            'value': metric.metric_value,
                            'unit': metric.unit,
                            'timestamp': metric.timestamp.isoformat()
                        })
                
                return system_data
            finally:
                session.close()
        
        system_data = safe_database_operation(query_system_metrics, "Failed to query system metrics")
        
        return jsonify({
            'system_metrics': system_data,
            'period_hours': hours
        }), 200
        
    except ValidationError as e:
        return handle_error(e, status_code=400)
    except DatabaseError as e:
        return handle_error(e, status_code=503)
    except Exception as e:
        return handle_error(e, status_code=500)


@api_bp.route('/metrics/summary', methods=['GET'])
def get_metrics_summary():
    """
    Get overall metrics summary for the dashboard.
    
    Returns:
        JSON response with summary statistics
    """
    try:
        try:
            days = int(request.args.get('days', 7))
            if days < 1 or days > 365:
                raise ValidationError("Days must be between 1 and 365")
        except ValueError:
            raise ValidationError("Invalid 'days' parameter. Must be a number.")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        def query_summary():
            session = get_session()
            try:
                # Total executions
                total_executions = session.query(func.count(PipelineExecution.id)).filter(
                    PipelineExecution.start_time >= cutoff_date
                ).scalar() or 0
                
                # Success rate
                success_count = session.query(func.count(PipelineExecution.id)).filter(
                    PipelineExecution.start_time >= cutoff_date,
                    PipelineExecution.status == 'success'
                ).scalar() or 0
                
                success_rate = (success_count / total_executions * 100) if total_executions > 0 else 0
                
                # Average execution time
                avg_duration = session.query(func.avg(PipelineExecution.duration_seconds)).filter(
                    PipelineExecution.start_time >= cutoff_date,
                    PipelineExecution.status == 'success'
                ).scalar()
                
                # Total pipelines
                pipeline_count = session.query(func.count(func.distinct(PipelineExecution.pipeline_name))).scalar() or 0
                
                return {
                    'total_executions': total_executions,
                    'success_count': success_count,
                    'success_rate': round(success_rate, 2),
                    'avg_duration_seconds': float(avg_duration) if avg_duration else None,
                    'pipeline_count': pipeline_count,
                    'period_days': days
                }
            finally:
                session.close()
        
        summary = safe_database_operation(query_summary, "Failed to query metrics summary")
        
        return jsonify({
            'summary': summary,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except ValidationError as e:
        return handle_error(e, status_code=400)
    except DatabaseError as e:
        return handle_error(e, status_code=503)
    except Exception as e:
        return handle_error(e, status_code=500)


@api_bp.route('/pipelines', methods=['POST'])
def record_pipeline_execution():
    """
    Record a new pipeline execution.
    
    Request Body (JSON):
        pipeline_name: Name of the pipeline
        status: Execution status (success, failed, running)
        start_time: Start time (ISO format)
        end_time: End time (ISO format, optional)
        records_processed: Number of records processed
        error_message: Error message if failed
    
    Returns:
        JSON response with created execution record
    """
    try:
        # Validate request has JSON data
        if not request.is_json:
            raise ValidationError("Request must be JSON")
        
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is empty")
        
        # Validate required fields
        validate_request_data(data, ['pipeline_name', 'status', 'start_time'])
        
        # Validate pipeline name
        pipeline_name = data['pipeline_name'].strip()
        if not pipeline_name:
            raise ValidationError("Pipeline name cannot be empty")
        
        # Validate status
        valid_statuses = ['success', 'failed', 'running']
        if data['status'] not in valid_statuses:
            raise ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        # Parse and validate timestamps
        try:
            start_time_str = data['start_time'].replace('Z', '+00:00')
            start_time = datetime.fromisoformat(start_time_str)
        except (ValueError, AttributeError) as e:
            raise ValidationError(f"Invalid start_time format: {str(e)}")
        
        end_time = None
        if data.get('end_time'):
            try:
                end_time_str = data['end_time'].replace('Z', '+00:00')
                end_time = datetime.fromisoformat(end_time_str)
                if end_time < start_time:
                    raise ValidationError("end_time must be after start_time")
            except (ValueError, AttributeError) as e:
                raise ValidationError(f"Invalid end_time format: {str(e)}")
        
        # Validate records_processed
        records_processed = data.get('records_processed', 0)
        if not isinstance(records_processed, int) or records_processed < 0:
            raise ValidationError("records_processed must be a non-negative integer")
        
        # Record the execution
        collector = MetricsCollector()
        try:
            execution = collector.record_pipeline_execution(
                pipeline_name=pipeline_name,
                status=data['status'],
                start_time=start_time,
                end_time=end_time,
                records_processed=records_processed,
                error_message=data.get('error_message')
            )
        finally:
            collector.close()
        
        return jsonify({
            'message': 'Pipeline execution recorded successfully',
            'execution_id': execution.id
        }), 201
        
    except ValidationError as e:
        return handle_error(e, status_code=400)
    except DatabaseError as e:
        return handle_error(e, status_code=503)
    except Exception as e:
        return handle_error(e, status_code=500)
