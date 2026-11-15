import os

class Config:
    """Application configuration settings."""
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Secret Keys
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tma-mad2-secure-secret-key-23f2000278')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'tma-jwt-secret-key-23f2000278')
    JWT_ACCESS_TOKEN_EXPIRES_HOURS = 24

    # SQLite Database Configuration (strictly SQLite as mandated)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'trekking.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis Configuration for Caching
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_CACHE_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes cache expiry

    # Celery Configuration for Batch Jobs
    CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
    CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/2"

    # Export & Report Output Directories
    EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')
    REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

    # Student Details
    STUDENT_ROLL_NO = '23f2000278'
    PROJECT_NAME = 'Trekking Management Application - V2'
