# RENGLO SYSTEM



## Architecture (Multiple repositories)

Root
│
├── system/                     ← Core System (not to be edited)
│   ├── env_config.py           ← System configuration
│   ├── main.py                 ← Application Point of Entry
│   ├── wsgi.py                 ← Production WSGI entry point
│   ├── lambda_handler.py       ← AWS Lambda handler
│   ├── requirements.txt        ← System dependencies
│   └── README.md
│
|
├── console/                    ← Frontend (React + Vite)
|   ├── package.json            ← Workspace root
|   │   └── workspaces: [".", "../extensions/*/ui"]
|   ├── vite.config.ts          ← Vite configuration
|   ├── tsconfig.json           ← TypeScript config
|   ├── src/
|   │   ├── main.tsx
|   │   ├── router.tsx
|   │   ├── nav.tsx
|   │   ├── components/
|   │   └── contexts/
|   └── public/
|
│
├── extensions/                 ← Pluggable Extensions
│   ├── extension_x/
│   │   ├── README.md
│   │   ├── blueprints/         ← Data declarations for extension_x
│   │   ├── installer/          ← Setup scripts for extension_X
│   │   ├── package/            
│   │   │   ├── setup.py
│   │   │   ├── pyproject.toml
│   │   │   ├── requirements.txt
│   │   │   └── enerclave/
│   │   │       ├── __init__.py
│   │   │       └── handlers/  ← Handlers for extension_x
│   │   └── ui/                
│   │       ├── package.json   ← UI Dependencies for extension_x
│   │       ├── components/    ← Custom components for extension_x
│   │       ├── navigation/    ← Navigation components for extension_x
│   │       ├── onboarding/    ← Onboarding components for extension_x
│   │       └── pages/         ← Subsection components for extension_x
│   │
│   ├── extension_y/            ← Same structure
│   ├── schd/                   ← Same structure
│   └── data/                   ← Same structure
│
└── dev/                       ← Core Libraries (only for development)
   ├── renglo-api/             ← Renglo API (Flask routes)
   │   ├── renglo_api/
   │   │   ├── app.py          ← Flask APP declaration
   │   │   ├── routes/         ← System routes
   │   │   └── config.py       ← Config functions (not a config file)
   │   └── requirements.txt
   │
   └── renglo-lib/             ← Renglo Library (System Logic)
       ├── renglo/
       │   ├── app_auth/       ← Authentication subsystem
       │   ├── app_blueprint/  ← Blueprints subsystem
       │   ├── app_chat/       ← Authentication subsystem
       │   ├── app_data/       ← Data subsystem
       │   ├── app_docs/       ← Docs subsystem
       │   ├── app_schd/       ← Scheduler subsystem
       │   └── app_state/      ← State subsystem
       └── setup.py


Dependencies Flow:
┌─────────────────────────────────────────────────────────────────┐
│ system/ (Backend)                                               │
│   └── imports: renglo_api                                       │
│        └── imports: renglo-lib                                  │
│             └── uses: extensions/*/package/* (handlers)         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ console/ (Frontend)                                             │
│   └── dynamically loads: @extensions/*/ui/*                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘



+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
INSTALLATION
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Setting up a new development environment


Step 0. 

Create a project folder in your computer to hold the project folders.
The name doesn't affect the configuration. You can change it later.
You can move this folder around to different locations in your file system.
```
mkdir <NAME-OF-PROJECT>
cd <NAME-OF-PROJECT>
```

Step 1. 

Clone the system and the console. Install its dependencies

```
git clone https://github.com/renglo/system.git
git clone https://github.com/renglo/console.git

```

Install the system dependencies
```
cd system
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Install the console dependencies
```
cd ..
cd console
npm install
```

Step 2. 

If you are going to modify the core libraries, you'll need to download them locally. 
Create a folder called /dev on the root of the project and clone the core libraries in it.

```
mkdir dev
cd dev
git clone https://github.com/renglo/renglo-lib.git
git clone https://github.com/renglo/renglo-api.git
```

Install the dependencies
```
# located in /dev
pip install -e renglo-lib
pip install -e renglo-api
```



Step 3.

Insert the config files and start the system and console

Place env_config.py in the /system folder
Place .env.development and .env.production in the /console folder


Copy run.sh.TEMPLATE to run.sh
```bash
cp run.sh.TEMPLATE run.sh
```

Fill the PROFILE and REGION env variables in run.sh with your own values
```bash
export AWS_PROFILE=<PROFILE>
export AWS_DEFAULT_REGION=<REGION>

```



Step 4. Setup the System Logo


Create two images. 

A small one (500x500 px, Max 100Kb, name: small_logo.jpg) for the Menu header and 
A large one (1000x1000 px, Max 500kb, name: large_logo.jpg) for the log-in page

Place both images in console/public 



+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
EXTENSIONS
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Up to this point you have the bare bones version of the system.
If you want to use, edit and view the specialized extensions, you need to install them.


Step 5. 

Installing the extensions (locally)

Create a folder called 'extensions' on the root of the project
```
mkdir extensions
cd extensions
```

Clone the extension code
```
git clone https://some-url-where-repository-is-hosted/some-extension.git
```

Install the extension handlers
```
pip install -e extensions/some-extension/package

```

Install the extension ui for the console
```
# Open the console config files (.env.development and .env.production) 
# Add the name of the extension to VITE_BOOTSTRAP_PLUGINS (it is a comma separated string)

```

Repeat Step 5 for each one of the extensions you need to install to the system. 

Notes: 
- Installing an extension in the system doesn't make it immediately available to the user
- Follow the README.md in each extension folder to understand how to activate it.






+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
RUNNING THE SYSTEM
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



Initialize the backEnd (system)
```
cd system
source venv/bin/activate
source run.sh
```

Initialize the console (in another terminal)
```
cd console
npm run dev
```



Alternative ways to run the system:

# Alternative 1: Using Flask CLI
export FLASK_APP=wsgi:app
flask run

# Alternative 2: Using Gunicorn (production-like)
gunicorn wsgi:app -w 4 -b 0.0.0.0:8000
```

The System will be available at `http://localhost:5001` (or 8000 for gunicorn)





+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
DEPLOYMENT
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


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
cp -r ../renglo-lib/renglo deployment/
cp -r ../renglo-api/renglo_api deployment/
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




+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
CONFIGURATION OPTIONS
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


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
from renglo_api import create_app

config = {
    'DYNAMODB_CHAT_TABLE': os.getenv('DYNAMODB_CHAT_TABLE'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'COGNITO_REGION': os.getenv('COGNITO_REGION'),
    # ... etc
}

app = create_app(config=config)
```



+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
AVAILABLE SYSTEM ROUTES
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The system offers a lot of out of the box functionality:

- `/_auth/*` - Authentication endpoints
- `/_data/*` - Data management endpoints
- `/_chat/*` - Chat functionality
- `/_blueprint/*` - Blueprint management
- `/_docs/*` - Document management
- `/_schd/*` - Scheduler endpoints
- `/_state/*` - State management
- `/ping` - Health check
- `/time` - Current time (authenticated)

Visit `http://localhost:5001/ping` to verify the application is running.