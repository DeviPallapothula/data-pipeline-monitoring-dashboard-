"""
Main Application Entry Point

This is the Flask application that serves the monitoring dashboard.
It initializes the database, sets up routes, and serves the web interface.
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
from src.api.routes import api_bp
from src.models.database import init_database
from src.utils.config_loader import load_config
from src.utils.logger_setup import setup_logger
import os

# Load configuration
config = load_config()

# Setup logging
logger = setup_logger(
    name='monitoring',
    log_file=config.get('logging', {}).get('file', 'logs/monitoring.log'),
    level=config.get('logging', {}).get('level', 'INFO')
)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Enable CORS for API endpoints
CORS(app)

# Register API blueprint
app.register_blueprint(api_bp)


@app.route('/')
def index():
    """
    Main dashboard page.
    Serves the HTML dashboard interface.
    """
    return render_template('dashboard.html')


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


def create_app():
    """
    Application factory function.
    Initializes the database and returns the Flask app.
    """
    # Initialize database
    logger.info("Initializing database...")
    init_database()
    logger.info("Database initialized successfully")
    
    return app


if __name__ == '__main__':
    # Create app and initialize
    app = create_app()
    
    # Get server configuration
    host = config.get('server', {}).get('host', '0.0.0.0')
    port = config.get('server', {}).get('port', 5000)
    debug = config.get('server', {}).get('debug', False)
    
    logger.info(f"Starting monitoring dashboard on {host}:{port}")
    
    # Run the application
    app.run(host=host, port=port, debug=debug)
