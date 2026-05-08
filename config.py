import os

class Config:
    """Base configuration"""
    SQLALCHEMY_DATABASE_URI = 'sqlite:///perfume_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # NCF recommender settings
    NCF_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ncf_model.pt')
    NCF_EMBED_DIM = 64
    NCF_EPOCHS = 20

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'