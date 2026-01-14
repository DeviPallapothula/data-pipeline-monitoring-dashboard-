# Data Pipeline Monitoring Dashboard

A comprehensive monitoring dashboard for data pipeline health, performance metrics, and data quality tracking. This project provides real-time visibility into your data engineering pipelines with beautiful visualizations and detailed metrics.

## 🎯 Features

- **Pipeline Execution Monitoring**: Track success/failure rates, execution times, and historical trends
- **Data Quality Metrics**: Monitor data quality scores (completeness, accuracy, validity)
- **System Resource Monitoring**: Track CPU, memory, and disk usage
- **Real-time Dashboard**: Beautiful web interface with interactive charts
- **RESTful API**: Complete API for programmatic access to metrics
- **Robust Error Handling**: Comprehensive error handling throughout the application
- **Automated Setup**: One-command setup script for easy installation
- **Docker Support**: Easy deployment with Docker containers

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git
- (Optional) Docker for containerized deployment

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

We provide setup scripts that automate the entire setup process:

**For macOS/Linux:**
```bash
git clone https://github.com/DeviPallapothula/data-pipeline-monitoring-dashboard-.git
cd data-pipeline-monitoring-dashboard-
chmod +x setup.sh
./setup.sh
```

**For Windows:**
```bash
git clone https://github.com/DeviPallapothula/data-pipeline-monitoring-dashboard-.git
cd data-pipeline-monitoring-dashboard-
setup.bat
```

**What the setup script does:**
- ✅ Checks Python and pip installation
- ✅ Creates virtual environment
- ✅ Installs all dependencies
- ✅ Creates necessary directories
- ✅ Initializes the database
- ✅ Sets up environment variables

After running the setup script:
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the application
python app.py
```

### Option 2: Manual Setup

If you prefer to set up manually:

#### 1. Clone the Repository

```bash
git clone https://github.com/DeviPallapothula/data-pipeline-monitoring-dashboard-.git
cd data-pipeline-monitoring-dashboard-
```

**Explanation**: 
- `git clone` downloads the repository from GitHub to your local machine
- `cd` changes your current directory to the project folder

#### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Explanation**:
- `python3 -m venv venv` creates an isolated Python environment
- This prevents conflicts with other projects' dependencies
- `source venv/bin/activate` activates the virtual environment

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Explanation**:
- `pip install` installs Python packages
- `-r requirements.txt` reads the file and installs all listed packages
- This ensures you have all necessary libraries (Flask, SQLAlchemy, etc.)

#### 4. Initialize Database

```bash
python -c "from src.models.database import init_database; init_database()"
```

**Explanation**:
- This Python one-liner imports the database initialization function
- `init_database()` creates the SQLite database and all required tables
- The database file will be created in `data/pipeline_metrics.db`

#### 5. Run the Application

```bash
python app.py
```

**Explanation**:
- Starts the Flask web server
- The application will be available at `http://localhost:5000`
- Open this URL in your browser to see the dashboard

#### 6. (Optional) Add Sample Data

To see the dashboard with sample data, run:

```bash
python scripts/add_sample_data.py
```

**Explanation**:
- This script adds sample pipeline executions, data quality metrics, and system metrics
- Helps you see the dashboard in action with real data
- You can run this anytime to populate the dashboard with test data

## 📖 User Guide

### Accessing the Dashboard

Once the Flask server is running, open your web browser and navigate to:

```
http://localhost:5000
```

You should see the **Data Pipeline Monitoring Dashboard** homepage.

**Note**: If you see "Error Code: -102" or "Connection refused", make sure:
1. The Flask server is running (`python app.py`)
2. No other application is using port 5000
3. You're using `http://` not `https://`

### Dashboard Overview

The dashboard consists of several sections:

#### 1. **Header Section**
- **Title**: "Data Pipeline Monitoring Dashboard"
- **Status Indicator**: Shows connection status
  - 🟢 **Green dot**: Connected and healthy
  - 🔴 **Red dot**: Disconnected or error

#### 2. **Summary Cards** (Top Row)
Four key metrics displayed as cards:

- **Total Executions**: Total number of pipeline runs in the selected time period
- **Success Rate**: Percentage of successful pipeline executions
- **Avg Duration**: Average time taken for pipeline executions
- **Active Pipelines**: Number of unique pipelines being monitored

**What to expect**: Initially, these will show `-` or `0` until you add pipeline data.

#### 3. **Pipeline Status Table**
A detailed table showing:

| Column | Description |
|--------|-------------|
| **Pipeline Name** | Name of the data pipeline |
| **Status** | Latest execution status (Success/Failed/Running) |
| **Last Execution** | Timestamp of the most recent run |
| **Total Runs** | Number of executions in the time period |
| **Success Rate** | Percentage of successful runs |
| **Avg Duration** | Average execution time |
| **Actions** | "View Details" button to see execution history |

**Status Badges**:
- 🟢 **Green (Success)**: Pipeline completed successfully
- 🔴 **Red (Failed)**: Pipeline execution failed
- 🟠 **Orange (Running)**: Pipeline is currently executing

**How to use**:
- Click **"View Details"** to see detailed execution history for a specific pipeline
- The table automatically refreshes every 30 seconds

#### 4. **Charts Section**

Two interactive charts:

**a) Execution Trends Chart**
- Shows pipeline execution trends over the last 7 days
- Displays successful vs failed executions
- Hover over data points to see exact values
- Helps identify patterns and anomalies

**b) System Metrics Chart**
- Displays system resource usage (CPU, Memory, Disk)
- Shows trends over the last 24 hours
- Color-coded lines for each metric type
- Useful for monitoring infrastructure health

### Adding Sample Data

To see the dashboard in action with real data, you can add sample pipeline executions:

#### Option 1: Using the Provided Script (Recommended)

We've included a ready-to-use script that adds comprehensive sample data:

```bash
python scripts/add_sample_data.py
```

This script will:
- Add 30 pipeline executions over the last 7 days
- Add 50 data quality metrics
- Add 24 hours of system metrics

**What you'll see**: The script creates realistic sample data with:
- Multiple pipeline types (ETL, data quality, warehouse load, API sync)
- Mix of successful and failed executions (85% success rate)
- Various data quality scores
- System resource metrics

Then refresh your browser to see the data appear on the dashboard.

#### Option 2: Manual Python Script

You can also create your own script:

```python
from src.collectors.metrics_collector import MetricsCollector
from datetime import datetime, timedelta

collector = MetricsCollector()

# Add a sample pipeline execution
collector.record_pipeline_execution(
    pipeline_name="etl_pipeline",
    status="success",
    start_time=datetime.utcnow() - timedelta(hours=1),
    end_time=datetime.utcnow() - timedelta(minutes=55),
    records_processed=10000
)

# Add data quality metric
collector.record_data_quality_metric(
    pipeline_name="etl_pipeline",
    metric_name="completeness",
    metric_value=0.98,
    threshold=0.95
)

collector.close()
print("Sample data added!")
```

Run it:
```bash
python your_script.py
```

#### Option 2: Using the API

You can also add data via the REST API:

```bash
curl -X POST http://localhost:5000/api/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline_name": "etl_pipeline",
    "status": "success",
    "start_time": "2024-01-14T10:00:00Z",
    "end_time": "2024-01-14T10:05:00Z",
    "records_processed": 10000
  }'
```

### Understanding the Data

#### Pipeline Executions
- **Success**: Pipeline completed without errors
- **Failed**: Pipeline encountered an error (check error_message)
- **Running**: Pipeline is currently executing

#### Data Quality Metrics
- **Completeness**: Percentage of non-null values
- **Accuracy**: How correct the data is
- **Validity**: Data conforms to expected format
- **Consistency**: Data is consistent across sources
- **Timeliness**: Data is up-to-date

**Threshold**: If a metric value is below the threshold, it's marked as "Failed"

#### System Metrics
- **CPU**: Processor usage percentage
- **Memory**: RAM usage percentage  
- **Disk**: Storage usage percentage

**Normal ranges**:
- CPU: < 80% is healthy
- Memory: < 85% is healthy
- Disk: < 90% is healthy

### Dashboard Features

#### Auto-Refresh
- The dashboard automatically refreshes every 30 seconds
- Summary cards and pipeline table update automatically
- No need to manually refresh the page

#### Interactive Charts
- **Hover**: Move your mouse over chart elements to see detailed values
- **Zoom**: Click and drag on charts to zoom into specific time periods
- **Legend**: Click legend items to show/hide data series

#### Pipeline Details Modal
- Click **"View Details"** on any pipeline row
- See recent execution history
- View execution status, duration, and records processed
- Close the modal by clicking the X or clicking outside

### Troubleshooting

#### Dashboard shows "No pipelines found"
**Solution**: Add some pipeline execution data using the methods above.

#### Charts are empty
**Solution**: 
- Ensure you have pipeline executions recorded
- Check that system metrics are being collected
- Verify the time range (charts show last 7 days/24 hours)

#### Status shows "Disconnected"
**Solution**:
- Check if Flask server is running
- Verify the API endpoint: `http://localhost:5000/api/health`
- Check browser console for JavaScript errors

#### Data not updating
**Solution**:
- Wait 30 seconds (auto-refresh interval)
- Manually refresh the browser (F5 or Cmd+R)
- Check server logs for errors

### Best Practices

1. **Regular Monitoring**: Check the dashboard daily to catch issues early
2. **Set Thresholds**: Configure appropriate quality thresholds in `config/config.yaml`
3. **Review Failures**: Click "View Details" on failed pipelines to investigate
4. **Track Trends**: Use charts to identify performance degradation over time
5. **System Health**: Monitor system metrics to ensure adequate resources

### Next Steps

1. **Integrate with Your Pipelines**: Modify your existing ETL pipelines to record executions
2. **Customize Alerts**: Set up alerts based on failure rates or quality thresholds
3. **Add More Metrics**: Extend the dashboard with custom metrics specific to your use case
4. **Deploy to Production**: Use Docker or cloud deployment for production use

## 📁 Project Structure

```
data-pipeline-monitoring-dashboard-/
├── app.py                 # Main Flask application entry point
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container configuration
├── .gitignore            # Files to ignore in Git
├── README.md             # This file
├── config/
│   ├── config.yaml       # Application configuration
│   └── .env.example      # Environment variables template
├── src/
│   ├── api/
│   │   └── routes.py     # API endpoints
│   ├── models/
│   │   └── database.py   # Database models and setup
│   ├── collectors/
│   │   └── metrics_collector.py  # Metrics collection logic
│   └── utils/
│       ├── config_loader.py      # Configuration management
│       └── logger_setup.py       # Logging configuration
├── templates/
│   └── dashboard.html    # Main dashboard HTML
├── static/
│   ├── css/
│   │   └── dashboard.css # Dashboard styles
│   └── js/
│       └── dashboard.js  # Dashboard JavaScript
├── tests/                # Unit tests
├── scripts/              # Utility scripts
│   └── add_sample_data.py  # Script to add sample data
├── setup.sh              # Automated setup script (macOS/Linux)
├── setup.bat             # Automated setup script (Windows)
├── data/                 # Database and data files
└── logs/                 # Application logs
```

## 🔧 Configuration

### Environment Variables

Copy the example environment file and update it:

```bash
cp config/.env.example .env
```

Edit `.env` with your settings:
- `DATABASE_URL`: Database connection string
- `FLASK_ENV`: Development or production mode
- `SECRET_KEY`: Secret key for Flask sessions

### Configuration File

Edit `config/config.yaml` to customize:
- Server host and port
- Logging settings
- Monitoring thresholds
- Pipeline configurations

## 📊 API Endpoints

### Health Check
```
GET /api/health
```
Returns API and database health status.

### Get All Pipelines
```
GET /api/pipelines?days=7
```
Returns list of all pipelines with summary statistics.

### Get Pipeline Executions
```
GET /api/pipelines/{pipeline_name}/executions?limit=100&days=30
```
Returns execution history for a specific pipeline.

### Get Data Quality Metrics
```
GET /api/pipelines/{pipeline_name}/quality?days=7
```
Returns data quality metrics for a pipeline.

### Get System Metrics
```
GET /api/system/metrics?hours=24
```
Returns system resource usage metrics.

### Record Pipeline Execution
```
POST /api/pipelines
Content-Type: application/json

{
  "pipeline_name": "etl_pipeline",
  "status": "success",
  "start_time": "2024-01-14T10:00:00Z",
  "end_time": "2024-01-14T10:05:00Z",
  "records_processed": 10000,
  "error_message": null
}
```

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t pipeline-monitoring-dashboard .
```

**Explanation**:
- `docker build` creates a Docker image from the Dockerfile
- `-t pipeline-monitoring-dashboard` tags the image with a name
- `.` means use the current directory as the build context

### Run Docker Container

```bash
docker run -d -p 5000:5000 --name monitoring-dashboard pipeline-monitoring-dashboard
```

**Explanation**:
- `docker run` starts a container from the image
- `-d` runs in detached mode (background)
- `-p 5000:5000` maps port 5000 from container to host
- `--name` gives the container a friendly name

## 🧪 Testing

Run tests with pytest:

```bash
pytest tests/
```

## 📝 Usage Example

### Recording a Pipeline Execution

```python
from src.collectors.metrics_collector import MetricsCollector
from datetime import datetime

collector = MetricsCollector()

# Record a successful pipeline run
collector.record_pipeline_execution(
    pipeline_name="etl_pipeline",
    status="success",
    start_time=datetime.utcnow(),
    end_time=datetime.utcnow(),
    records_processed=10000
)

# Record a data quality metric
collector.record_data_quality_metric(
    pipeline_name="etl_pipeline",
    metric_name="completeness",
    metric_value=0.98,
    threshold=0.95
)

collector.close()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

**Devi Pallapothula**

- GitHub: [@DeviPallapothula](https://github.com/DeviPallapothula)

## 🙏 Acknowledgments

- Flask community for the excellent web framework
- SQLAlchemy for robust database ORM
- Plotly for beautiful visualizations
