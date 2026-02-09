"""
Application configuration management using Pydantic Settings.

This module loads and validates environment variables for the application.
"""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database Configuration
    database_url: str = Field(
        ...,
        description="PostgreSQL database connection URL",
        examples=["postgresql://user:password@localhost:5432/todo_chatbot"],
    )

    # Google Gemini API Configuration
    gemini_api_key: str = Field(
        ...,
        description="Google Gemini API key for AI agent",
    )

    # JWT Configuration
    jwt_secret_key: str = Field(
        ...,
        description="Secret key for JWT token signing",
        min_length=32,
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm",
    )
    jwt_expiration_minutes: int = Field(
        default=1440,
        description="JWT token expiration time in minutes (default: 24 hours)",
        gt=0,
    )

    # Application Configuration
    environment: str = Field(
        default="development",
        description="Application environment (development, staging, production)",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )

    # MCP Server Configuration
    mcp_server_name: str = Field(
        default="Todo MCP Server",
        description="MCP server name",
    )
    mcp_server_version: str = Field(
        default="0.1.0",
        description="MCP server version",
    )

    # Agent Configuration
    agent_session_db_path: str = Field(
        default="./data/agent_sessions.db",
        description="Path to SQLite database for agent sessions",
    )
    agent_session_max_messages: int = Field(
        default=200,
        description="Maximum messages per session",
        gt=0,
    )
    agent_session_retention_days: int = Field(
        default=7,
        description="Days to retain inactive sessions",
        gt=0,
    )
    agent_session_cleanup_hour: int = Field(
        default=2,
        description="Hour (UTC) to run daily cleanup job",
        ge=0,
        le=23,
    )
    conversation_retention_days: int = Field(
        default=30,
        description="Number of days to retain conversation history",
        gt=0,
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"log_level must be one of {allowed_levels}")
        return v_upper

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the allowed values."""
        allowed_envs = ["development", "staging", "production"]
        v_lower = v.lower()
        if v_lower not in allowed_envs:
            raise ValueError(f"environment must be one of {allowed_envs}")
        return v_lower

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


# Global settings instance
settings = Settings()
