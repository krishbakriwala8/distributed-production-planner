"""Configuration management"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///production.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Simulation
    DEFAULT_NUM_PLANTS = 2
    DEFAULT_NUM_JOBS = 10
    DEFAULT_SIMULATION_STEPS = 100
    MAX_TIME = 10000

    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def to_dict(cls) -> dict:
        """Convert config to dictionary"""
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('_')}