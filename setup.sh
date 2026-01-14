#!/bin/bash

# Setup Script for Data Pipeline Monitoring Dashboard
# This script automates the setup process for the project

set -e  # Exit on any error

echo "🚀 Setting up Data Pipeline Monitoring Dashboard..."
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python 3 is installed
echo "📋 Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
print_success "Python $PYTHON_VERSION found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    print_error "pip is not installed. Please install pip."
    exit 1
fi
print_success "pip found"

echo ""
echo "📦 Setting up virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet
print_success "pip upgraded"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Create necessary directories
echo ""
echo "📁 Creating necessary directories..."
mkdir -p data logs config
print_success "Directories created"

# Initialize database
echo ""
echo "🗄️  Initializing database..."
if python3 -c "from src.models.database import init_database; init_database()" 2>/dev/null; then
    print_success "Database initialized"
else
    print_error "Failed to initialize database"
    exit 1
fi

# Create .env file if it doesn't exist
echo ""
echo "⚙️  Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f "config/.env.example" ]; then
        cp config/.env.example .env
        print_success ".env file created from template"
        print_warning "Please edit .env file with your configuration"
    else
        print_warning ".env.example not found, skipping .env creation"
    fi
else
    print_warning ".env file already exists, skipping"
fi

# Check if database file exists
if [ -f "data/pipeline_metrics.db" ]; then
    print_success "Database file created: data/pipeline_metrics.db"
fi

echo ""
echo "=================================================="
print_success "Setup completed successfully!"
echo ""
echo "📝 Next steps:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. (Optional) Edit .env file with your settings"
echo "   3. Run the application: python app.py"
echo "   4. Open browser: http://localhost:5000"
echo "   5. (Optional) Add sample data: python scripts/add_sample_data.py"
echo ""
echo "💡 Tip: You can run this script again safely - it won't overwrite existing files"
