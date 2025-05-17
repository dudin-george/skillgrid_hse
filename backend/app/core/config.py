import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "SkillGrid API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Backend API for SkillGrid application"
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "True").lower() in ("true", "1", "t"))
    
    # Database settings
    POSTGRES_HOST: str = Field(default="postgres", env="POSTGRES_HOST")
    POSTGRES_PORT: str = Field(default="5432", env="POSTGRES_PORT")
    POSTGRES_USER: str = Field(default="postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(default="skillgrid", env="POSTGRES_DB")
    
    # API settings
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    
    # CORS settings
    CORS_ORIGINS: list = ["*", "https://skillgrid.tech", "https://www.skillgrid.tech", "https://api.skillgrid.tech"]
    
    # Computed properties
    @property
    def DATABASE_URL(self) -> str:
        """Constructs database URL from components"""
        return os.getenv(
            "DATABASE_URL", 
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def SQLALCHEMY_URL(self) -> str:
        """Alias for DATABASE_URL for Alembic"""
        return self.DATABASE_URL
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create a global instance of the settings
settings = Settings() 