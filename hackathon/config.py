"""
Configuration for fraud detection system.
"""

import os
from pathlib import Path
from typing import Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Try to load from hackathon/.env first, then fall back to root .env
    hackathon_env = Path(__file__).parent / ".env"
    root_env = Path(__file__).parent.parent / ".env"

    if hackathon_env.exists():
        load_dotenv(hackathon_env, override=True)
    elif root_env.exists():
        load_dotenv(root_env, override=True)
except ImportError:
    pass  # dotenv not installed, rely on system environment variables


class Config:
    """Configuration for OpenAI and MCP integration."""

    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")

    # Lenses API Configuration (used by MCP server)
    LENSES_API_HTTP_URL: str = os.getenv("LENSES_API_HTTP_URL", "http://54.195.167.195")
    LENSES_API_HTTP_PORT: str = os.getenv("LENSES_API_HTTP_PORT", "8080")
    LENSES_API_WEBSOCKET_URL: str = os.getenv("LENSES_API_WEBSOCKET_URL", "ws://54.195.167.195")
    LENSES_API_WEBSOCKET_PORT: str = os.getenv("LENSES_API_WEBSOCKET_PORT", "8080")
    LENSES_API_KEY: Optional[str] = os.getenv("LENSES_API_KEY")  # Alias for websocket client
    LENSES_TOKEN: Optional[str] = os.getenv("LENSES_TOKEN") or os.getenv("LENSES_API_KEY")

    # MCP/Lenses Environment
    LENSES_ENVIRONMENT: str = os.getenv("LENSES_ENVIRONMENT", "dev")

    # Kafka Topics
    CC_TOPIC: str = "credit-card-transactions"
    PAYPAL_TOPIC: str = "paypal-transactions"

    # Query Limits
    FETCH_LIMIT: int = 20

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Set it with: export OPENAI_API_KEY='your-key-here'"
            )

    @classmethod
    def is_mcp_available(cls) -> bool:
        """Check if MCP configuration is available."""
        return bool(cls.LENSES_API_HTTP_URL and cls.LENSES_ENVIRONMENT)

    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (for debugging)."""
        print("\n📋 Current Configuration:")
        print(f"  OpenAI Model: {cls.OPENAI_MODEL}")
        print(f"  OpenAI API Key: {'✓ Set' if cls.OPENAI_API_KEY else '✗ Not Set'}")
        print(f"  Lenses HTTP: {cls.LENSES_API_HTTP_URL}:{cls.LENSES_API_HTTP_PORT}")
        print(f"  Lenses WebSocket: {cls.LENSES_API_WEBSOCKET_URL}:{cls.LENSES_API_WEBSOCKET_PORT}")
        print(f"  Lenses Token: {'✓ Set' if cls.LENSES_TOKEN else '✗ Not Set'}")
        print(f"  Lenses Environment: {cls.LENSES_ENVIRONMENT}")
        print(f"  CC Topic: {cls.CC_TOPIC}")
        print(f"  PayPal Topic: {cls.PAYPAL_TOPIC}")
        print(f"  Fetch Limit: {cls.FETCH_LIMIT}\n")
