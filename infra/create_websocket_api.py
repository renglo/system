import boto3
import argparse
import os
import configparser
import json
import sys
from typing import Dict, Optional


'''

Main Functions

api_exists(): Checks if a WebSocket API already exists
create_websocket_api(): Creates the main WebSocket API
create_route(): Creates a route for the API
create_integration(): Creates an HTTP integration
create_stage(): Creates a stage for deployment


Command Line Interface: 

Takes the following arguments:
environment: The environment name (which becomes the API name)
route: The route key for the WebSocket API
integration_target: The HTTP endpoint URL for integration
stage_name: The stage name (e.g., prod, dev)
--aws-profile: Optional AWS profile (defaults to "default")
--region: Optional AWS region (defaults to "us-east-1")

Usage:
python tank/installer/create_websocket_api.py <api_name> "<route>" "<endpoint>" <environment> --aws-profile <profile>


'''

def log(message: str) -> None:
    """Write human-readable logs to stderr to keep stdout machine-readable."""
    print(message, file=sys.stderr)

def get_available_aws_profiles():
    """Retrieve available AWS profiles from ~/.aws/credentials and ~/.aws/config."""
    profiles = []
    aws_credentials_path = os.path.expanduser("~/.aws/credentials")
    aws_config_path = os.path.expanduser("~/.aws/config")

    if os.path.exists(aws_credentials_path):
        config = configparser.ConfigParser()
        config.read(aws_credentials_path)
        profiles.extend(config.sections())

    if os.path.exists(aws_config_path):
        config = configparser.ConfigParser()
        config.read(aws_config_path)
        for section in config.sections():
            if section.startswith("profile "):
                profile_name = section.replace("profile ", "")
                if profile_name not in profiles:
                    profiles.append(profile_name)

    return profiles if profiles else ["default"]

def api_exists(apigw, api_name: str) -> str:
    """Check if a WebSocket API exists and return its ID if found."""
    try:
        response = apigw.get_apis()
        for api in response.get('Items', []):
            if api['Name'] == api_name and api['ProtocolType'] == 'WEBSOCKET':
                return api['ApiId']
        return ""
    except Exception as e:
        log(f"Error checking API existence: {e}")
        return ""

def find_route(apigw, api_id: str, route_key: str) -> Optional[Dict]:
    """Find a route by key."""
    try:
        response = apigw.get_routes(ApiId=api_id)
        for route in response.get("Items", []):
            if route.get("RouteKey") == route_key:
                return route
    except Exception as e:
        log(f"Error finding route '{route_key}': {e}")
    return None

def find_stage(apigw, api_id: str, stage_name: str) -> Optional[Dict]:
    """Find stage by name."""
    try:
        response = apigw.get_stages(ApiId=api_id)
        for stage in response.get("Items", []):
            if stage.get("StageName") == stage_name:
                return stage
    except Exception as e:
        log(f"Error finding stage '{stage_name}': {e}")
    return None

def create_or_replace_integration(apigw, api_id: str, route_key: str, integration_uri: str, old_integration_id: Optional[str] = None) -> Dict:
    """Always create a fresh integration, then optionally delete the previous one."""
    integration = create_integration(apigw, api_id, route_key, integration_uri)
    if old_integration_id:
        try:
            apigw.delete_integration(ApiId=api_id, IntegrationId=old_integration_id)
        except Exception:
            # Non-fatal: old integration can remain if API Gateway refuses deletion.
            pass
    return integration

def upsert_route_with_integration(apigw, api_id: str, route_key: str, integration_target: str) -> None:
    """Create/update route and point it to a fresh integration."""
    existing_route = find_route(apigw, api_id, route_key)
    old_integration_id = None
    if existing_route:
        target = existing_route.get("Target", "")
        if target.startswith("integrations/"):
            old_integration_id = target.split("/", 1)[1]
        route_id = existing_route["RouteId"]
    else:
        route_response = create_route(apigw, api_id, route_key)
        route_id = route_response["RouteId"]

    integration_response = create_or_replace_integration(
        apigw, api_id, route_key, integration_target, old_integration_id
    )
    integration_id = integration_response["IntegrationId"]
    update_route(apigw, api_id, route_id, route_key, integration_id)

def create_websocket_api(apigw, api_name: str, route_selection_expr: str) -> Dict:
    """Create a WebSocket API."""
    log(f"🛠️  Creating WebSocket API: {api_name}...")
    
    try:
        response = apigw.create_api(
            Name=api_name,
            ProtocolType='WEBSOCKET',
            RouteSelectionExpression=route_selection_expr
        )
        log(f"✅ WebSocket API '{api_name}' created successfully.")
        return response
    except Exception as e:
        log(f"❌ Error creating WebSocket API: {e}")
        raise

def create_route(apigw, api_id: str, route_key: str) -> Dict:
    """Create a route for the WebSocket API."""
    log(f"🛠️  Creating route: {route_key}...")
    
    try:
        response = apigw.create_route(
            ApiId=api_id,
            RouteKey=route_key
        )
        log(f"✅ Route '{route_key}' created successfully.")
        return response
    except Exception as e:
        log(f"❌ Error creating route: {e}")
        raise

def update_route(apigw, api_id: str, route_id: str, route_key: str, integration_id: str) -> Dict:
    """Update a route to point to an integration."""
    log(f"🛠️  Updating route target for: {route_key}...")
    
    try:
        response = apigw.update_route(
            ApiId=api_id,
            RouteId=route_id,
            RouteKey=route_key,
            Target=f'integrations/{integration_id}'
        )
        log(f"✅ Route target updated successfully.")
        return response
    except Exception as e:
        log(f"❌ Error updating route target: {e}")
        raise

def create_integration(apigw, api_id: str, route_key: str, integration_uri: str) -> Dict:
    """Create an HTTP integration for the WebSocket API."""
    log(f"🛠️  Creating integration for route: {route_key}...")
    
    try:
        # Remove @ symbol if present at the start of the integration URI
        cleaned_uri = integration_uri.lstrip('@')
        
        # Define the request template
        request_template = '''#set($inputRoot = $input.path('$'))
            {
            "handler": "$inputRoot.handler",
            "portfolio": "$inputRoot.portfolio",
            "org": "$inputRoot.org",
            "entity_type": "$inputRoot.entity_type",
            "entity_id": "$inputRoot.entity_id",
            "thread": "$inputRoot.thread",
            "connectionId": "$context.connectionId"
            }'''

        response = apigw.create_integration(
            ApiId=api_id,
            IntegrationType='HTTP',
            IntegrationMethod='POST',
            IntegrationUri=cleaned_uri,
            PassthroughBehavior='WHEN_NO_MATCH',
            RequestTemplates={
                'application/json': request_template
            }
        )
        log(f"✅ Integration for route '{route_key}' created successfully.")
        return response
    except Exception as e:
        log(f"❌ Error creating integration: {e}")
        raise

def create_stage(apigw, api_id: str, stage_name: str) -> Dict:
    """Create a stage for the WebSocket API."""
    log(f"🛠️  Creating stage: {stage_name}...")
    
    try:
        response = apigw.create_stage(
            ApiId=api_id,
            StageName=stage_name,
            AutoDeploy=True
        )
        log(f"✅ Stage '{stage_name}' created successfully.")
        return response
    except Exception as e:
        log(f"❌ Error creating stage: {e}")
        raise

def ensure_stage(apigw, api_id: str, stage_name: str) -> Dict:
    """Create stage if missing; otherwise keep existing stage."""
    existing_stage = find_stage(apigw, api_id, stage_name)
    if existing_stage:
        log(f"✅ Stage '{stage_name}' already exists.")
        return existing_stage
    return create_stage(apigw, api_id, stage_name)

def create_default_routes(apigw, api_id: str, integration_target: str) -> None:
    """Create default WebSocket routes ($connect, $disconnect)."""
    default_routes = ['$connect', '$disconnect']
    
    for route_key in default_routes:
        log(f"🛠️  Creating default route: {route_key}...")
        try:
            upsert_route_with_integration(apigw, api_id, route_key, integration_target)
            log(f"✅ Default route '{route_key}' created successfully.")
        except Exception as e:
            log(f"❌ Error creating default route {route_key}: {e}")
            raise

def run(environment: str, route: str, integration_target: str, stage_name: str, 
        aws_profile: Optional[str] = None, region: str = "us-east-1") -> Dict[str, str]:
    """Programmatic entry point that returns structured data"""
    # Initialize Boto3 Session with selected profile when provided.
    # In CI, credentials are usually injected via environment (OIDC).
    if aws_profile:
        boto3.setup_default_session(profile_name=aws_profile, region_name=region)
        log(f"🔄 Using AWS Profile: {aws_profile} in region {region}")
    else:
        boto3.setup_default_session(region_name=region)
        log(f"🔄 Using environment credentials in region {region}")
    apigw = boto3.client('apigatewayv2', region_name=region)

    api_name = environment
    route_selection_expr = "$request.body.action"
    
    # Check if API already exists
    existing_api_id = api_exists(apigw, api_name)
    if existing_api_id:
        log(f"✅ WebSocket API '{api_name}' already exists with ID: {existing_api_id}")
        api = apigw.get_api(ApiId=existing_api_id)
        api_id = existing_api_id
    else:
        # Create the WebSocket API
        api = create_websocket_api(apigw, api_name, route_selection_expr)
        api_id = api['ApiId']

    # Ensure default and custom routes always point to current integration target.
    create_default_routes(apigw, api_id, integration_target)
    upsert_route_with_integration(apigw, api_id, route, integration_target)

    # Ensure stage exists.
    ensure_stage(apigw, api_id, stage_name)
    api_endpoint = api.get('ApiEndpoint', '')
    stage_url = f"{api_endpoint}/{stage_name}"
    websocket_url = stage_url.replace("https://", "wss://")

    return {
        "api_id": api_id,
        "api_endpoint": api_endpoint,
        "stage_url": stage_url,
        "websocket_url": websocket_url,
        "connections_url": stage_url,
    }

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Create WebSocket API for a given environment.")
    parser.add_argument("environment", type=str, help="The environment name (e.g., dev, prod, test).")
    parser.add_argument("route", type=str, help="The route key for the WebSocket API.")
    parser.add_argument("integration_target", type=str, help="The integration target URL.")
    parser.add_argument("stage_name", type=str, help="The stage name (e.g., prod, dev).")
    
    available_profiles = get_available_aws_profiles()
    parser.add_argument(
        "--aws-profile",
        type=str,
        choices=available_profiles + [""],
        default="",
        help=f"AWS profile to use (empty = environment credentials). Available: {', '.join(available_profiles)}"
    )
    parser.add_argument(
        "--region",
        type=str,
        default="us-east-1",
        help="AWS region to create the API in (default: us-east-1)"
    )

    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Print machine-readable JSON only."
    )

    args = parser.parse_args()
    
    # Run the deployment
    result = run(args.environment, args.route, args.integration_target,
                 args.stage_name, args.aws_profile or None, args.region)
    
    # Print results
    if args.json_output:
        print(json.dumps(result))
    else:
        print("\n✅ WebSocket API Created/Updated Successfully!\n")
        print(f"API ID: {result['api_id']}")
        print(f"API Endpoint: {result['api_endpoint']}")
        print(f"Stage URL: {result['stage_url']}")
        print(f"WebSocket URL: {result['websocket_url']}")
        print(f"Connections URL: {result['connections_url']}\n")

if __name__ == "__main__":
    main() 