# System - Agnostic Backend

This is the agnostic backend system that can be configured for any deployment. The system itself contains no business logic - all specialization comes from:
1. Configuration (`env_config.py`)
2. Installed extensions (handlers)

## Architecture

```
system/                  ← Agnostic Backend (this directory)
├── env_config.py        ← Configuration (NOT versioned, unique per deployment)
├── main.py              ← Flask development server
├── wsgi.py              ← Production WSGI entry point
├── lambda_handler.py    ← AWS Lambda handler
├── requirements.txt     ← System dependencies
└── README.md            ← This file

Dependencies:
├── tank-api/            ← Framework library (no config)
│   └── uses: tank-lib/  ← Core library (no config)
├── extension handlers   ← Installed from /extensions or registries
```

## Key Principle: Configuration-Driven

**The system is completely agnostic.** What makes each deployment unique is:

1. **Configuration File (`env_config.py`)**
   - Database connections (DynamoDB tables, etc.)
   - Authentication settings (Cognito, etc.)
   - API keys (OpenAI, etc.)
   - Extension-specific settings
   - **This file is NOT versioned** - each deployment has its own

2. **Installed Extensions**
   - Extensions provide business logic via handlers
   - Installed as Python packages (locally or from PyPI)
   - System dynamically loads handlers from installed extensions

## Setup

### 0. Prerequisites

- Python 3.12+
- AWS credentials (for DynamoDB, Cognito, etc.)
- Virtual environment

### 1. Install Core Dependencies

```bash
cd system

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Option A: Install from registries (normal deployment)
pip install tank-lib tank-api

# Option B: Install from local /dev (core library development)
pip install -e ../dev/tank-lib
pip install -e ../dev/tank-api

# Install system dependencies
pip install -r requirements.txt
```

### 2. Install Extensions

Install the handlers from extensions you want to use:

```bash
# Option A: From local /extensions (development)
pip install -e ../extensions/extension-name/handlers

# Option B: From PyPI (production)
pip install extension-name-handlers

# Example: Installing multiple extensions
pip install -e ../extensions/enerclave/handlers
pip install -e ../extensions/noma/handlers
```

### 3. Configure System

Create your configuration file:

```bash
# Copy the template
cp env_config.py.TEMPLATE env_config.py

# Edit with your actual values
nano env_config.py  # or vim, code, etc.
```

**Important:** `env_config.py` contains secrets and should NEVER be committed to version control.

Example configuration:

```python
# DynamoDB Tables
DYNAMODB_ENTITY_TABLE = 'prod-entities'
DYNAMODB_REL_TABLE = 'prod-relations'
DYNAMODB_RINGDATA_TABLE = 'prod-ringdata'
DYNAMODB_CHAT_TABLE = 'prod-chat'

# Cognito Authentication
COGNITO_USERPOOL_ID = 'us-east-1_xxxxxxx'
COGNITO_APP_CLIENT_ID = 'xxxxxxxxxxxx'
COGNITO_REGION = 'us-east-1'

# API Keys
OPENAI_API_KEY = 'sk-xxxxxxxxxxxxxxxx'

# AWS Configuration
AWS_REGION = 'us-east-1'
AWS_BUCKET_NAME = 'my-deployment-bucket'
```

### 4. Configure AWS Credentials

Set up AWS credentials for local development:

```bash
# Copy the run script template
cp run.sh.TEMPLATE run.sh

# Edit with your AWS profile and region
nano run.sh
```

Example `run.sh`:

```bash
#!/bin/bash
export AWS_PROFILE=my-profile
export AWS_DEFAULT_REGION=us-east-1

python main.py
```

## Running the System

### Local Development

```bash
# Option 1: Using the run script
source run.sh

# Option 2: Using Flask CLI
export FLASK_APP=wsgi:app
flask run

# Option 3: Using Python directly
python main.py

# Option 4: Using Gunicorn (production-like)
gunicorn wsgi:app -w 4 -b 0.0.0.0:8000
```

The system will be available at `http://localhost:5000` (Flask) or `http://localhost:8000` (Gunicorn)

### Testing Lambda Handler Locally

```bash
python lambda_handler.py
```

## Configuration Options

The application supports three ways to load configuration:

### 1. From env_config.py (Development)
```python
# wsgi.py or main.py
app = create_app()  # Loads from ./env_config.py
```

### 2. Pass Config Dict (Production)
```python
import os
from tank_api import create_app

config = {
    'DYNAMODB_CHAT_TABLE': os.getenv('DYNAMODB_CHAT_TABLE'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    # ... other config
}
app = create_app(config=config)
```

### 3. From Custom Path
```python
app = create_app(config_path='/etc/myapp/config.py')
```

## Available Routes

The system provides all tank-api routes:

- `/_auth/*` - Authentication endpoints
- `/_data/*` - Data management endpoints
- `/_chat/*` - Chat functionality
- `/_blueprint/*` - Blueprint management
- `/_docs/*` - Document management
- `/_schd/*` - Scheduler endpoints (calls extension handlers)
- `/_state/*` - State management
- `/ping` - Health check
- `/time` - Current time (authenticated)

Visit `http://localhost:5000/ping` to verify the system is running.

## Extension Handlers

The system can dynamically call extension handlers via the scheduler endpoint:

```bash
# Call an extension handler
POST /_schd/{portfolio}/{org}/call/{extension}/{handler}
```

Example:
```bash
POST /_schd/my-portfolio/my-org/call/enerclave/geocoding_handler
Content-Type: application/json

{
  "address": "123 Main St, City, State"
}
```

The system will:
1. Look for the extension package (e.g., `enerclave`)
2. Load the handler dynamically
3. Execute with the provided payload
4. Return the result

## Deployment Options

### Option 1: Traditional Server (EC2, VPS)

```bash
# Install all dependencies
pip install tank-lib tank-api
pip install extension1-handlers extension2-handlers
pip install -r requirements.txt

# Run with Gunicorn
gunicorn wsgi:app -w 4 -b 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --timeout 300
```

**For systemd:**

```ini
# /etc/systemd/system/platform-backend.service
[Unit]
Description=Platform Backend Service
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/platform/system
Environment="PATH=/opt/platform/system/venv/bin"
ExecStart=/opt/platform/system/venv/bin/gunicorn wsgi:app -w 4 -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Option 2: AWS Lambda

1. **Package the system:**

```bash
mkdir deployment
cd deployment

# Copy core files
cp ../lambda_handler.py .
cp ../env_config.py .

# Install dependencies
pip install tank-lib tank-api extension-handlers -t .

# Create deployment package
zip -r ../lambda-deployment.zip .
```

2. **Deploy to Lambda:**
   - Upload `lambda-deployment.zip`
   - Set handler to: `lambda_handler.lambda_handler`
   - Configure environment variables (instead of env_config.py)
   - Set timeout to 300 seconds
   - Configure VPC if accessing DynamoDB via VPC endpoints

3. **Use with API Gateway:**
   - Create REST API or HTTP API
   - Set up proxy integration to Lambda
   - Enable CORS if needed

### Option 3: Docker

```bash
# Build the image
docker build -t platform-backend .

# Run the container
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY_ID=xxx \
  -e AWS_SECRET_ACCESS_KEY=xxx \
  -e AWS_DEFAULT_REGION=us-east-1 \
  platform-backend

# Or use Docker Compose
docker compose up -d
```

**Docker Compose example:**

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
    volumes:
      - ./env_config.py:/app/env_config.py:ro
```

### Option 4: Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: platform-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: platform-backend
  template:
    metadata:
      labels:
        app: platform-backend
    spec:
      containers:
      - name: backend
        image: platform-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: AWS_REGION
          valueFrom:
            configMapKeyRef:
              name: platform-config
              key: aws_region
        # Use Secrets for sensitive data
        envFrom:
        - secretRef:
            name: platform-secrets
```

## Environment Variables (Production)

For production deployments, use environment variables instead of `env_config.py`:

```bash
# Set these in your deployment environment
export DYNAMODB_ENTITY_TABLE=prod-entities
export DYNAMODB_REL_TABLE=prod-relations
export COGNITO_USERPOOL_ID=us-east-1_xxxxxxx
export OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
# ... etc
```

Then load them in your WSGI file:

```python
import os
from tank_api import create_app

config = {
    'DYNAMODB_ENTITY_TABLE': os.getenv('DYNAMODB_ENTITY_TABLE'),
    'DYNAMODB_REL_TABLE': os.getenv('DYNAMODB_REL_TABLE'),
    'COGNITO_USERPOOL_ID': os.getenv('COGNITO_USERPOOL_ID'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    # ... etc
}

app = create_app(config=config)
```

## Troubleshooting

### Warning: env_config.py not found

**Solution:** Make sure you're running from the `system/` directory or pass config explicitly:

```python
from tank_api import create_app
app = create_app(config_path='./env_config.py')
```

### Import errors for tank-lib or tank-api

**Solution:** Verify they're installed:

```bash
pip list | grep tank
```

Install if missing:

```bash
pip install tank-lib tank-api
# or for development:
pip install -e ../dev/tank-lib ../dev/tank-api
```

### AWS Credentials errors

**Solution:** Configure AWS credentials:

```bash
# Option 1: Use AWS CLI
aws configure

# Option 2: Set environment variables
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
export AWS_DEFAULT_REGION=us-east-1

# Option 3: Use IAM role (EC2, Lambda, ECS)
# No configuration needed - role is automatically assumed
```

### Extension handler not found

**Solution:** Make sure the extension handlers are installed:

```bash
# Check installed packages
pip list | grep extension-name

# Install if missing
pip install -e ../extensions/extension-name/handlers
```

### Port already in use

**Solution:** Change the port or kill the process:

```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use a different port
export FLASK_RUN_PORT=5001
flask run
```

## Security Considerations

1. **Never commit `env_config.py`** - It contains secrets
2. **Use environment variables in production** - More secure than config files
3. **Rotate API keys regularly** - Especially OpenAI, AWS keys
4. **Use IAM roles when possible** - Better than access keys
5. **Enable CloudWatch logging** - For audit trails
6. **Use HTTPS in production** - Behind ALB, CloudFront, or similar
7. **Implement rate limiting** - Protect against abuse
8. **Validate all inputs** - Especially from extension handlers

## Monitoring

### Health Check

```bash
curl http://localhost:5000/ping
# Should return: pong
```

### Logs

```bash
# Development: logs to console
python main.py

# Production: configure logging
# See tank-api documentation for logging configuration
```

### Metrics

Consider setting up:
- CloudWatch metrics (if on AWS)
- Application Performance Monitoring (APM) tools
- Custom metrics for extension handler execution

## Support

For issues with:
- **System configuration**: Check this README
- **Core libraries**: See tank-lib and tank-api documentation
- **Extensions**: See extension-specific documentation
- **Platform architecture**: See root README.md

---

**Remember:** This system is completely agnostic. All business logic comes from configuration and installed extensions.
