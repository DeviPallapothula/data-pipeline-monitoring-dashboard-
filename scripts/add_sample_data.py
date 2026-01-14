"""
Script to add sample data to the monitoring dashboard.

This script creates sample pipeline executions, data quality metrics,
and system metrics so you can see the dashboard in action.

Usage:
    python scripts/add_sample_data.py
"""

from src.collectors.metrics_collector import MetricsCollector
from datetime import datetime, timedelta
import random

def add_sample_data():
    """Add sample data to the database."""
    print("🚀 Adding sample data to the monitoring dashboard...")
    print("-" * 50)
    
    collector = MetricsCollector()
    
    # Sample pipeline names
    pipelines = ["etl_pipeline", "data_quality_check", "data_warehouse_load", "api_data_sync"]
    
    # Add pipeline executions for the last 7 days
    print("📊 Adding pipeline executions...")
    execution_count = 0
    for i in range(30):  # 30 executions over 7 days
        pipeline_name = random.choice(pipelines)
        days_ago = random.randint(0, 7)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        start_time = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        duration = random.randint(30, 600)  # 30 seconds to 10 minutes
        end_time = start_time + timedelta(seconds=duration)
        
        # 85% success rate
        status = "success" if random.random() > 0.15 else "failed"
        records_processed = random.randint(1000, 50000) if status == "success" else random.randint(0, 5000)
        error_message = None if status == "success" else random.choice([
            "Connection timeout error",
            "Data validation failed",
            "Memory limit exceeded",
            "Invalid data format"
        ])
        
        collector.record_pipeline_execution(
            pipeline_name=pipeline_name,
            status=status,
            start_time=start_time,
            end_time=end_time,
            records_processed=records_processed,
            error_message=error_message
        )
        execution_count += 1
    
    print(f"   ✅ Added {execution_count} pipeline executions")
    
    # Add data quality metrics
    print("📈 Adding data quality metrics...")
    quality_metrics = ["completeness", "accuracy", "validity", "consistency", "timeliness"]
    quality_count = 0
    
    for i in range(50):
        pipeline_name = random.choice(pipelines)
        metric_name = random.choice(quality_metrics)
        # Quality scores between 0.85 and 1.0
        metric_value = round(random.uniform(0.85, 1.0), 3)
        threshold = 0.95
        
        collector.record_data_quality_metric(
            pipeline_name=pipeline_name,
            metric_name=metric_name,
            metric_value=metric_value,
            threshold=threshold
        )
        quality_count += 1
    
    print(f"   ✅ Added {quality_count} data quality metrics")
    
    # Add system metrics for the last 24 hours
    print("💻 Adding system metrics...")
    system_count = 0
    
    for i in range(24):  # One per hour for last 24 hours
        # Collect current system metrics
        collector.collect_system_metrics()
        system_count += 1
    
    print(f"   ✅ Added {system_count} system metric collections")
    
    collector.close()
    
    print("-" * 50)
    print("✅ Sample data added successfully!")
    print("\n📱 Next steps:")
    print("   1. Open your browser and go to: http://localhost:5000")
    print("   2. Refresh the page to see the new data")
    print("   3. Explore the dashboard with real metrics!")
    print("\n💡 Tip: The dashboard auto-refreshes every 30 seconds")

if __name__ == "__main__":
    try:
        add_sample_data()
    except Exception as e:
        print(f"\n❌ Error adding sample data: {e}")
        print("Make sure the database is initialized and the server is not running.")
        print("Run: python -c 'from src.models.database import init_database; init_database()'")
