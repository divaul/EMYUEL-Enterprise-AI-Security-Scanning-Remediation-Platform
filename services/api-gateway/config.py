"""
Configuration Management for API Gateway

Uses pydantic-settings for type-safe configuration from environment variables
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_GATEWAY_HOST: str = "0.0.0.0"
    API_GATEWAY_PORT: int = 8000
    API_VERSION: str = "v1"
    
    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "emyuel"
    POSTGRES_USER: str = "emyuel_user"
    POSTGRES_PASSWORD: str = "changeme"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Security
    JWT_SECRET_KEY: str = "change-this-to-a-very-long-random-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = "change-this-to-32-byte-key-___"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # LLM Configuration
    LLM_PRIMARY_PROVIDER: str = "openai"  # openai, gemini, claude
    LLM_FALLBACK_ENABLED: bool = True
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.1
    
    # Gemini
    GOOGLE_AI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GEMINI_MAX_TOKENS: int = 4096
    GEMINI_TEMPERATURE: float = 0.1
    
    # Claude
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-3-opus-20240229"
    CLAUDE_MAX_TOKENS: int = 4096
    CLAUDE_TEMPERATURE: float = 0.1
    
    # Scanner
    DEFAULT_SCAN_PROFILE: str = "standard"
    MAX_CONCURRENT_SCANS: int = 5
    SCAN_TIMEOUT: int = 3600
    DYNAMIC_ANALYSIS_ENABLED: bool = False
    
    # Celery
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""
    CELERY_WORKER_CONCURRENCY: int = 4
    
    # Integrations
    JIRA_ENABLED: bool = False
    JIRA_URL: str = ""
    JIRA_EMAIL: str = ""
    JIRA_API_TOKEN: str = ""
    JIRA_PROJECT_KEY: str = ""
    
    SLACK_ENABLED: bool = False
    SLACK_WEBHOOK_URL: str = ""
    SLACK_CHANNEL: str = ""
    
    LINEAR_ENABLED: bool = False
    LINEAR_API_KEY: str = ""
    LINEAR_TEAM_ID: str = ""
    
    SERVICENOW_ENABLED: bool = False
    SERVICENOW_INSTANCE: str = ""
    SERVICENOW_USERNAME: str = ""
    SERVICENOW_PASSWORD: str = ""
    
    # SSO
    SSO_ENABLED: bool = False
    SAML_ENTITY_ID: str = ""
    SAML_ACS_URL: str = ""
    SAML_IDP_METADATA_URL: str = ""
    OIDC_CLIENT_ID: str = ""
    OIDC_CLIENT_SECRET: str = ""
    OIDC_DISCOVERY_URL: str = ""
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    OTEL_TRACING_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Storage
    STORAGE_TYPE: str = "local"  # local, s3, gcs, azure
    STORAGE_PATH: str = "/var/lib/emyuel/storage"
    S3_BUCKET_NAME: str = ""
    S3_REGION: str = "us-east-1"
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    
    # Email
    SMTP_ENABLED: bool = False
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "EMYUEL Platform"
    
    # Compliance
    AUDIT_LOG_RETENTION_DAYS: int = 365
    COMPLIANCE_REPORTS_ENABLED: bool = True
    COMPLIANCE_OWASP_ENABLED: bool = True
    COMPLIANCE_PCI_DSS_ENABLED: bool = False
    COMPLIANCE_SOC2_ENABLED: bool = False
    
    # Feature Flags
    FEATURE_WEBHOOKS_ENABLED: bool = True
    FEATURE_API_GRAPHQL_ENABLED: bool = True
    FEATURE_MULTI_TENANCY_ENABLED: bool = False
    FEATURE_CUSTOM_DETECTORS_ENABLED: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
