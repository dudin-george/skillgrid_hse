import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

class Settings(BaseModel):
    APP_NAME: str = "SkillGrid API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Backend API for SkillGrid application"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/skillgrid")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "skillgrid")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

# Create settings instance
settings = Settings() 