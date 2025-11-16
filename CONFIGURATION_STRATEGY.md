# Configuration Strategy

## Overview

The application uses **different configuration strategies** for local development vs production (Lambda):

```
Local Development  → env_config.py file
AWS Lambda        → Environment Variables (set by Zappa)
```

## How Configuration Loading Works

### For Flask App (`create_app()`)

Located in `renglo-api/app.py`:

```python
def create_app(config=None, config_path=None):
    # 1. Load defaults
    app.config.from_object('renglo.default_config')
    
    # 2. Load from env_config.py or provided config
    if config is None:
        env_config = load_env_config(config_path)  # Looks for env_config.py
        app.config.update(env_config)
    else:
        app.config.update(config)  # Use provided config
    
    # 3. Store for controllers
    app.renglo_config = dict(app.config)
```

**In Flask context:**
- Local: Uses `system/env_config.py`
- Lambda: Gets config from Zappa's environment variables (passed to `create_app()`)

### For Handlers (`load_config()`)

Located in `renglo-lib/renglo/common.py`:

```python
def load_config():
    # 1. Try to load from env_config.py file
    config = {}
    if env_config_file_exists:
        config = load_from_file()
    
    # 2. Load from environment variables (overwrites file values)
    for key in env_var_keys:
        if key in os.environ:
            config[key] = os.environ[key]
    
    # 3. Validate critical keys exist
    if missing_critical_keys:
        raise RuntimeError("Missing config")
    
    return config
```

**Loading Priority:**
1. Try `system/env_config.py` first (local dev)
2. Load environment variables (production)
3. **Environment variables take precedence** over file

## Configuration by Environment

### Local Development

**Source:** `system/env_config.py` file

```python
# system/env_config.py
DYNAMODB_RINGDATA_TABLE = 'noma_data'
OPENAI_API_KEY = 'sk-...'
```

**How it works:**
- `load_config()` finds and loads `env_config.py`
- All config comes from this file
- Can commit non-secret values
- Secrets should be in `.gitignore`d file or env vars

### AWS Lambda (Production)

**Source:** Environment variables set by Zappa

**`zappa_settings.json`:**
```json
{
    "production": {
        "app_function": "wsgi.app",
        "environment_variables": {
            "DYNAMODB_RINGDATA_TABLE": "noma_data",
            "OPENAI_API_KEY": "sk-..."
        },
        "exclude": ["env_config.py"]  // Don't deploy the file
    }
}
```

**How it works:**
1. Zappa sets environment variables in Lambda
2. `env_config.py` is NOT deployed (excluded)
3. `load_config()` uses environment variables
4. No hardcoded secrets in deployment package

## Best Practices

### ✅ DO: Use Environment Variables in Lambda

**Why:**
- ✅ Secrets not in code/deployment package
- ✅ Different configs for staging/production
- ✅ Can update without redeploying
- ✅ Integrates with AWS Secrets Manager
- ✅ Follows 12-factor app principles

**How:**
```json
// zappa_settings.json
{
    "production": {
        "environment_variables": {
            "DYNAMODB_RINGDATA_TABLE": "noma_data",
            "OPENAI_API_KEY": "{{AWS_SECRET}}"  // Can reference AWS Secrets
        },
        "exclude": ["env_config.py"]
    }
}
```

### ✅ DO: Use env_config.py for Local Development

**Why:**
- ✅ Easy to set up
- ✅ One file for all config
- ✅ Can be shared with team (non-secrets)

**How:**
```python
# system/env_config.py
WL_NAME = 'Noma'
DYNAMODB_RINGDATA_TABLE = 'noma_data'
# Don't commit secrets - use environment variables:
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
```

### ❌ DON'T: Deploy env_config.py to Lambda

**Why NOT:**
- ❌ Secrets in deployment package
- ❌ Can't change config without redeploying
- ❌ Same config for all environments
- ❌ Larger deployment package

**How to prevent:**
```json
"exclude": ["env_config.py", "env_config.py.TEMPLATE"]
```

### ❌ DON'T: Hardcode Secrets

**Bad:**
```python
# env_config.py
OPENAI_API_KEY = 'sk-hardcoded-key'  # ❌ Will be in git
```

**Good:**
```python
# env_config.py
import os
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')  # ✅ From env var
```

## Configuration Flow Diagrams

### Local Development

```
Handler.__init__()
    ↓
load_config()
    ↓
Find system/env_config.py ✓
    ↓
Load all uppercase vars
    ↓
Check environment variables (optional)
    ↓
Return config dict
```

### AWS Lambda

```
Lambda Cold Start
    ↓
Zappa sets environment variables
    ↓
Handler.__init__()
    ↓
load_config()
    ↓
Try to find env_config.py (not found)
    ↓
Load from environment variables ✓
    ↓
Validate critical keys
    ↓
Return config dict
```

## Critical Configuration Keys

These **must** be present (file or env vars):

```python
critical_keys = [
    'DYNAMODB_RINGDATA_TABLE',  # Required by DataModel
    'DYNAMODB_ENTITY_TABLE'      # Required by AuthModel
]
```

If missing, `load_config()` raises `RuntimeError`.

## Environment Variable Names

All config uses **UPPERCASE** names:

```python
env_var_keys = [
    'WL_NAME',
    'BASE_URL',
    'DYNAMODB_ENTITY_TABLE',
    'DYNAMODB_RINGDATA_TABLE',
    'DYNAMODB_CHAT_TABLE',
    'OPENAI_API_KEY',
    'COGNITO_USERPOOL_ID',
    # ... etc
]
```

## Example Configurations

### Local Development Setup

```bash
# In your shell profile (~/.zshrc or ~/.bashrc)
export OPENAI_API_KEY="sk-your-key"
export AWS_PROFILE="noma-dev"

# Run the app
cd system
python main.py
```

### Lambda Deployment Setup

```json
// zappa_settings.json
{
    "production": {
        "environment_variables": {
            "DYNAMODB_RINGDATA_TABLE": "noma_data",
            "DYNAMODB_ENTITY_TABLE": "noma_entities",
            "OPENAI_API_KEY": "sk-production-key",
            "SYS_ENV": "production"
        }
    },
    "staging": {
        "extends": "production",
        "environment_variables": {
            "DYNAMODB_RINGDATA_TABLE": "noma_staging_data",
            "SYS_ENV": "staging"
        }
    }
}
```

## Troubleshooting

### Error: "Critical configuration missing"

**Cause:** Neither env_config.py nor environment variables provide required keys

**Solutions:**
1. **Local:** Create `system/env_config.py` with required keys
2. **Lambda:** Set environment variables in `zappa_settings.json`

### Warning: "Config file not found, using environment variables"

**Expected in Lambda** - This is normal and correct behavior

**Unexpected locally** - Create `system/env_config.py`

### Config values not updating in Lambda

**Cause:** Using deployed env_config.py instead of environment variables

**Solution:** 
1. Add `"env_config.py"` to `exclude` in zappa_settings.json
2. Redeploy: `zappa update production`

## Migration Guide

### If you were deploying env_config.py before:

1. **Extract all values** from env_config.py
2. **Add to zappa_settings.json** as environment_variables
3. **Exclude env_config.py** from deployment
4. **Redeploy**: `zappa update production`

```json
{
    "production": {
        "exclude": ["env_config.py"],
        "environment_variables": {
            // Add all your config here
        }
    }
}
```

## Summary

| Aspect | Local Development | AWS Lambda |
|--------|------------------|------------|
| **Config Source** | `env_config.py` | Environment Variables |
| **Secrets** | Env vars or file | Environment Variables |
| **Deployment** | N/A | Excluded from package |
| **Updates** | Edit file | Update Zappa settings |
| **Priority** | File → Env vars | Env vars only |

This strategy gives you the best of both worlds:
- **Easy local development** with env_config.py
- **Secure production** with environment variables

