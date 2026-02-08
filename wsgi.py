# wsgi.py
"""WSGI entry point for production deployment."""
from smart_farming_advisory.app import create_app

app = create_app()
