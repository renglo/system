# Example System

This is a complete example system demonstrating how to use `tank-lib` and `tank-api` as libraries with externalized configuration.

## Architecture

```
example-sys/               ← Your System (config lives here)
├── env_config.py          ← System configuration
├── main.py                ← Flask development server
├── wsgi.py                ← Production WSGI entry point
├── lambda_handler.py      ← AWS Lambda handler
├── requirements.txt       ← System dependencies
└── README.md              ← This file

Dependencies:
├── tank-api/               ← Library (no config)
│   └── uses: tank-lib/     ← Library (no config)
├── {OTHER}-module/       ← Optional: Custom handlers
```

## Setup

### 1. Install Dependencies

```bash
cd example-sys

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install tank libraries from local paths (for development)
pip install -e ../tank-lib
pip install -e ../tank-api

# (Optional) Install extension modules
pip install -e ../{OTHER}-mod

# Install system dependencies
pip install -r requirements.txt
```

### 2. Configure System

Edit `env_config.py` with your actual values:

```python
# Update these with your AWS resources
DYNAMODB_ENTITY_TABLE = 'your_entities_table'
COGNITO_USERPOOL_ID = 'your_pool_id'
OPENAI_API_KEY = 'your_api_key'
# ... etc
```

## Running the System

### Local Development

```bash
# Option 1: Using main.py
python main.py

# Option 2: Using Flask CLI
export FLASK_APP=wsgi:app
flask run

# Option 3: Using Gunicorn (production-like)
gunicorn wsgi:app -w 4 -b 0.0.0.0:8000
```

The System will be available at `http://localhost:5000` (or 8000 for gunicorn)

### Testing Lambda Handler Locally

```bash
python lambda_handler.py
```

## Deployment Options

### Option 1: Traditional Server (EC2, VPS)

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn wsgi:app -w 4 -b 0.0.0.0:8000 --access-logfile - --error-logfile -
```

### Option 2: AWS Lambda

1. Package your system:
```bash
# Create deployment package
mkdir deployment
cp -r ../tank-lib/tank deployment/
cp -r ../tank-api/tank_api deployment/
cp lambda_handler.py deployment/
cp env_config.py deployment/
cd deployment
pip install -r ../requirements.txt -t .
zip -r ../lambda-deployment.zip .
```

2. Upload to Lambda and set handler to: `lambda_handler.lambda_handler`

### Option 3: Docker (Optional)

**Prerequisites:** Install Docker Desktop from https://www.docker.com/products/docker-desktop/

```bash
# Build and run with Docker Compose
docker compose up -d

# Or build manually
docker build -t example-sys .
docker run -p 8000:8000 example-sys
```

**Note:** Docker is optional for local development. Use Python directly for faster iteration.

## Configuration Options

The application supports three ways to load configuration:

### 1. From env_config.py (Development)
```python
app = create_app()  # Loads from ./env_config.py
```

### 2. Pass Config Dict (Production)
```python
config = {
    'DYNAMODB_CHAT_TABLE': 'prod_chat',
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    # ...
}
app = create_app(config=config)
```

### 3. From Custom Path
```python
app = create_app(config_path='/etc/myapp/config.py')
```

## Environment Variables

For production, you can load config from environment variables:

```python
import os
from tank_api import create_app

config = {
    'DYNAMODB_CHAT_TABLE': os.getenv('DYNAMODB_CHAT_TABLE'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'COGNITO_REGION': os.getenv('COGNITO_REGION'),
    # ... etc
}

app = create_app(config=config)
```

## Available Routes

The application includes all tank-api routes:

- `/_auth/*` - Authentication endpoints
- `/_data/*` - Data management endpoints
- `/_chat/*` - Chat functionality
- `/_blueprint/*` - Blueprint management
- `/_docs/*` - Document management
- `/_schd/*` - Scheduler endpoints
- `/_state/*` - State management
- `/ping` - Health check
- `/time` - Current time (authenticated)

Visit `http://localhost:5000/ping` to verify the application is running.


## Troubleshooting

**Warning about env_config.py not found:**
- This is expected if you run from a different directory
- Make sure to run from the `app/` directory or pass config explicitly

**Import errors:**
- Make sure tank-lib and tank-api are installed: `pip list | grep tank`
- For development: `pip install -e ../tank-lib ../tank-api`

**AWS Credentials:**
- Ensure AWS credentials are configured for DynamoDB and Cognito
- Use `aws configure` or set environment variables

