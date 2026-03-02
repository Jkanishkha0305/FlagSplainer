#!/usr/bin/env python3
"""
Test Lenses WebSocket connection.
"""

import asyncio

from .config import Config
from .fraud_detection.lenses_client import create_lenses_client


async def test_connection():
    """Test Lenses WebSocket connection."""
    print("=" * 60)
    print("Testing Lenses WebSocket Connection")
    print("=" * 60)

    print(f"\nConfiguration:")
    Config.print_config()

    client = create_lenses_client()

    if client is None:
        print("\n❌ Failed to create Lenses client")
        print("   Check your LENSES_API_KEY is set in .env")
        return False

    print(f"\n→ Testing connection to {client.base_url}...")

    try:
        # Try a simple SQL query
        sql = "SELECT * FROM `credit-card-transactions` LIMIT 1"
        print(f"→ Executing SQL: {sql}")

        result = await client.execute_sql(
            environment=Config.LENSES_ENVIRONMENT,
            sql=sql
        )

        print(f"\n✅ Connection successful!")
        print(f"   Retrieved {len(result)} records")

        if result:
            print(f"\n   Sample record:")
            print(f"   {result[0]}")

        return True

    except Exception as exc:
        print(f"\n❌ Connection failed: {exc}")
        print(f"\nTroubleshooting:")
        print(f"  1. Check if Lenses is running at {Config.LENSES_API_WEBSOCKET_URL}:{Config.LENSES_API_WEBSOCKET_PORT}")
        print(f"  2. Verify your LENSES_API_KEY is valid")
        print(f"  3. Confirm the environment name '{Config.LENSES_ENVIRONMENT}' exists")
        print(f"  4. Check if the topic 'credit-card-transactions' exists")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
