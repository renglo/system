"""
AWS Lambda container entrypoint.

API Gateway (REST/Lambda proxy) -> WSGI via apig-wsgi. Same Flask app as Zappa
(`application.app`); see `application.py`.
"""

from apig_wsgi import make_lambda_handler

from application import app

lambda_handler = make_lambda_handler(app)
