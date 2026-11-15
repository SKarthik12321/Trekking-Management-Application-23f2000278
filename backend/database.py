"""
Database initialization module using Flask-SQLAlchemy.
All models are defined programmatically and bound to this SQLAlchemy instance.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
