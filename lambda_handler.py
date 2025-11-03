"""
AWS Lambda Handler Example

This demonstrates how to use tank-api and tank-lib in AWS Lambda.
Config can come from environment variables or a deployed env_config.py file.
"""

from tank_api import create_app
from tank_api.config import get_config_for_lambda
import json

# Create app instance at module level for Lambda reuse
config = get_config_for_lambda()
app = create_app(config=config)


def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    Args:
        event: Lambda event data
        context: Lambda context object
        
    Returns:
        dict: API Gateway response format
    """
    
    # Example: Handle API Gateway proxy request
    with app.app_context():
        try:
            # Parse request
            http_method = event.get('httpMethod', 'GET')
            path = event.get('path', '/')
            body = event.get('body', '{}')
            
            app.logger.info(f"Processing {http_method} request to {path}")
            
            # Process request using Flask test client or handle directly
            # This is a simplified example
            
            # Your business logic here
            # You can access tank-lib controllers via tank-api routes
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'Success',
                    'path': path,
                    'method': http_method
                })
            }
            
        except Exception as e:
            app.logger.error(f"Error processing request: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': str(e)})
            }


# For testing locally
if __name__ == '__main__':
    # Simulate a Lambda event
    test_event = {
        'httpMethod': 'GET',
        'path': '/ping',
        'body': '{}'
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))

