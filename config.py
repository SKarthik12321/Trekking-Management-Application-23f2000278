import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-trekking-key-123456'
    
    # Put database inside the project workspace directory 'instance' folder
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'trekking.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
