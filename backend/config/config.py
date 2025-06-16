import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///timevis.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis configuration for Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    
    # Model configurations
    MAX_SEQUENCE_LENGTH = 512
    QWEN_MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
    QWEN_LOCAL_PATH = "./models/qwen"
    
    # Training configurations
    BATCH_SIZE = 8
    LEARNING_RATE = 5e-5
    NUM_EPOCHS = 10
    GRADIENT_ACCUMULATION_STEPS = 4
    
    # File upload configurations
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'json'}
    
    # Prediction tasks
    SUPPORTED_TASKS = ['weather', 'electricity', 'traffic']
    SUPPORTED_MODELS = ['qwen', 'lstm']

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
