"""
WSGI Entry Point for Production

Use this with production WSGI servers like Gunicorn or uWSGI.

Example usage:
    gunicorn wsgi:app -w 4 -b 0.0.0.0:8000
"""

from tank_api import create_app

# Create application instance
# Config will be loaded from env_config.py in this directory
app = create_app()

if __name__ == '__main__':
    # This is only for testing; use gunicorn/uwsgi in production
    app.run(host='0.0.0.0', port=8000)

