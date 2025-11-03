#!/usr/bin/env python3
"""
Test script to verify the application is configured correctly.

Run this to check that tank-lib and tank-api are working properly
with your configuration.
"""

import sys
from tank_api import create_app
from tank_api.config import load_env_config


def test_configuration():
    """Test that configuration loads correctly."""
    print("=" * 60)
    print("Testing Application Configuration")
    print("=" * 60)
    
    config = load_env_config()
    
    print(f"\n✓ Loaded {len(config)} configuration values")
    
    # Check required configs
    required_configs = [
        'DYNAMODB_ENTITY_TABLE',
        'DYNAMODB_CHAT_TABLE',
        'COGNITO_REGION',
        'COGNITO_USERPOOL_ID',
        'OPENAI_API_KEY',
        'TANK_BASE_URL'
    ]
    
    missing = []
    for key in required_configs:
        if key in config and config[key] and config[key] != 'your-secret-key-here':
            print(f"  ✓ {key}: {config[key][:20]}{'...' if len(str(config[key])) > 20 else ''}")
        else:
            print(f"  ✗ {key}: NOT SET")
            missing.append(key)
    
    if missing:
        print(f"\n⚠️  Warning: {len(missing)} required config(s) not properly set")
        print("   Update env_config.py with real values for production use")
    else:
        print(f"\n✓ All required configurations are set")
    
    return len(missing) == 0


def test_app_creation():
    """Test that Flask app can be created."""
    print("\n" + "=" * 60)
    print("Testing Flask App Creation")
    print("=" * 60)
    
    try:
        app = create_app()
        print(f"\n✓ Flask app created successfully")
        print(f"  - Environment: {'Lambda' if app.config.get('IS_LAMBDA') else 'Local'}")
        print(f"  - Debug mode: {app.debug}")
        print(f"  - Config loaded: {len(app.config)} keys")
        return True
    except Exception as e:
        print(f"\n✗ Failed to create Flask app: {e}")
        return False


def test_routes():
    """Test that routes are registered."""
    print("\n" + "=" * 60)
    print("Testing Route Registration")
    print("=" * 60)
    
    try:
        app = create_app()
        
        # Get all registered routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.endpoint}: {rule.rule}")
        
        print(f"\n✓ {len(routes)} routes registered")
        
        # Check for key blueprints
        blueprints = ['auth', 'data', 'chat', 'blueprint', 'docs', 'schd', 'state']
        found_blueprints = set()
        
        for route in routes:
            for bp in blueprints:
                if bp in route.lower():
                    found_blueprints.add(bp)
        
        print(f"  - Blueprints found: {', '.join(sorted(found_blueprints))}")
        
        # Show some example routes
        print("\n  Sample routes:")
        for route in sorted(routes)[:10]:
            print(f"    {route}")
        
        return True
    except Exception as e:
        print(f"\n✗ Failed to test routes: {e}")
        return False


def test_controllers():
    """Test that controllers can be instantiated."""
    print("\n" + "=" * 60)
    print("Testing Controller Initialization")
    print("=" * 60)
    
    try:
        from tank.app_chat.chat_controller import ChatController
        from tank.app_data.data_controller import DataController
        from tank.app_auth.auth_controller import AuthController
        
        config = load_env_config()
        
        # Test instantiation
        chat_ctrl = ChatController(config=config)
        data_ctrl = DataController(config=config)
        auth_ctrl = AuthController(config=config)
        
        print("\n✓ All controllers instantiated successfully")
        print("  ✓ ChatController")
        print("  ✓ DataController")
        print("  ✓ AuthController")
        
        return True
    except Exception as e:
        print(f"\n✗ Failed to instantiate controllers: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_health_endpoint():
    """Test the health check endpoint."""
    print("\n" + "=" * 60)
    print("Testing Health Check Endpoint")
    print("=" * 60)
    
    try:
        app = create_app()
        client = app.test_client()
        
        response = client.get('/ping')
        
        if response.status_code == 200:
            print(f"\n✓ Health check endpoint working")
            print(f"  - Status: {response.status_code}")
            print(f"  - Response: {response.get_json()}")
            return True
        else:
            print(f"\n✗ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"\n✗ Failed to test health endpoint: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "🚀 " * 20)
    print("TANK APPLICATION TEST SUITE")
    print("🚀 " * 20 + "\n")
    
    results = {
        'Configuration': test_configuration(),
        'App Creation': test_app_creation(),
        'Routes': test_routes(),
        'Controllers': test_controllers(),
        'Health Check': test_health_endpoint()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your application is ready to run.")
        print("\nNext steps:")
        print("  1. Update env_config.py with your actual AWS credentials")
        print("  2. Run the application: python main.py")
        print("  3. Visit http://localhost:5000/ping to verify")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == '__main__':
    main()

