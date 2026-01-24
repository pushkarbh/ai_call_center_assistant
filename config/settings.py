import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""

    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # LangSmith (Observability - https://smith.langchain.com)
    # Note: Variable is LANGCHAIN_API_KEY but it's for LangSmith service
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")  # LangSmith API key
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "call-center-assistant")

    # App Settings
    MAX_AUDIO_DURATION_SECONDS: int = 3600  # 1 hour
    MIN_AUDIO_DURATION_SECONDS: int = 10
    MAX_REVISION_COUNT: int = 3

    @classmethod
    def validate(cls) -> dict:
        """Check which settings are configured"""
        return {
            "openai": bool(cls.OPENAI_API_KEY),
            "anthropic": bool(cls.ANTHROPIC_API_KEY),
            "langsmith": bool(cls.LANGCHAIN_API_KEY),  # LangSmith observability
        }

settings = Settings()
