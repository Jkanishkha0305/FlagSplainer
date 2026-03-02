#!/usr/bin/env python3
"""
Quick test to verify Lenses MCP server can connect to Lenses API
"""
import asyncio
import sys
sys.path.insert(0, 'src/lenses_mcp')

from clients.http_client import api_client

async def test_connection():
    try:
        print("🔄 Testing connection to Lenses API...")
        print(f"   URL: {api_client.base_url}")

        # Try to list environments
        result = await api_client._make_request("GET", "/api/v1/environments")

        print("✅ SUCCESS! Connected to Lenses!")
        print(f"📊 Found {len(result)} environment(s):")

        for env in result:
            print(f"   - {env.get('name', 'Unknown')}")

        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Is Lenses running? Check: http://localhost:9991")
        print("   2. Is the API key correct in .env file?")
        print("   3. Check Lenses logs for errors")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
