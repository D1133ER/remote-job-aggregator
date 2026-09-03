import secrets
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from typing import Optional, List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "RemoteJobHub"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/remotejobs"
    REDIS_URL: str = "redis://localhost:6379/0"
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    # Security
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # External APIs
    OPENAI_API_KEY: Optional[str] = None

    # Scraping Settings
    SCRAPING_INTERVAL_HOURS: int = 1
    MAX_CONCURRENT_SCRAPES: int = 5
    REQUEST_TIMEOUT: int = 30
    GREENHOUSE_COMPANY_TOKENS: str = (
        "stripe,gitlab,airbnb,discord,figma,vercel,"
        "coinbase,reddit,instacart,datadog,duolingo,airtable,chime,upwork"
    )
    # Lever-based companies that expose their public job board (verified slugs)
    LEVER_COMPANY_TOKENS: str = "linkedin,spotify"
    # Workable accounts (apply.workable.com/api/v1/widget/accounts/{slug}/jobs).
    # Set to a comma-separated list of your target company slugs to enable.
    WORKABLE_COMPANY_TOKENS: str = ""

    # Email (for notifications)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or v == "your-secret-key-change-in-production":
            if v == "your-secret-key-change-in-production":
                import logging
                logging.warning(
                    "SECRET_KEY is using the default insecure value. "
                    "Generating a random key for this session. "
                    "Set SECRET_KEY in .env for production."
                )
            return secrets.token_hex(32)
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()