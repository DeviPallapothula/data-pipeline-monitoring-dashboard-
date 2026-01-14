# Data Pipeline Monitoring Dashboard

A comprehensive monitoring dashboard for data pipeline health, performance metrics, and data quality tracking. This project provides real-time visibility into your data engineering pipelines with beautiful visualizations and detailed metrics.

## 🎯 Features

- **Pipeline Execution Monitoring**: Track success/failure rates, execution times, and historical trends
- **Data Quality Metrics**: Monitor data quality scores (completeness, accuracy, validity)
- **System Resource Monitoring**: Track CPU, memory, and disk usage
- **Real-time Dashboard**: Beautiful web interface with interactive charts
- **RESTful API**: Complete API for programmatic access to metrics
- **Docker Support**: Easy deployment with Docker containers

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git
- (Optional) Docker for containerized deployment

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/DeviPallapothula/data-pipeline-monitoring-dashboard-.git
cd data-pipeline-monitoring-dashboard-
```

**Explanation**: 
- `git clone` downloads the repository from GitHub to your local machine
- `cd` changes your current directory to the project folder

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Explanation**:
- `python3 -m venv venv` creates an isolated Python environment
- This prevents conflicts with other projects' dependencies
- `source venv/bin/activate` activates the virtual environment

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Explanation**:
- `pip install` installs Python packages
- `-r requirements.txt` reads the file and installs all listed packages
- This ensures you have all necessary libraries (Flask, SQLAlchemy, etc.)

### 4. Initialize Database

```bash
python -c "from src.models.database import init_database; init_database()"
```

**Explanation**:
- This Python one-liner imports the database initialization function
- `init_database()` creates the SQLite database and all required tables
- The database file will be created in `data/pipeline_metrics.db`

### 5. Run the Application

```bash
python app.py
```

**Explanation**:
- Starts the Flask web server
- The application will be available at `http://localhost:5000`
- Open this URL in your browser to see the dashboard

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
