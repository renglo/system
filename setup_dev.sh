#!/bin/bash
# Development environment setup script

set -e

echo "🚀 Setting up development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher required. Found: $python_version"
    exit 1
fi

echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install tank libraries in development mode
echo "Installing tank-lib..."
pip install -e ../tank-lib

echo "Installing tank-api..."
pip install -e ../tank-api

# Install application dependencies
echo "Installing application dependencies..."
pip install -r requirements.txt

# Check if env_config.py exists
if [ ! -f "env_config.py" ]; then
    echo "⚠️  env_config.py not found"
    echo "   It already exists with example values."
    echo "   Update it with your actual AWS credentials before running."
fi

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the environment: source venv/bin/activate"
echo "  2. Update env_config.py with your actual values"
echo "  3. Run tests: python test_app.py"
echo "  4. Start the app: python main.py"
echo ""

