#!/usr/bin/env python3
"""
Quick test script for the MCP AI Agent.
"""

import asyncio
from mcp_agent import create_mcp_agent


async def test_agent():
    """Quick test of the MCP agent."""
    print("=" * 60)
    print("🧪 Testing MCP AI Agent")
    print("=" * 60)

    try:
        # Create agent
        print("\n1️⃣  Creating agent...")
        agent = create_mcp_agent()
        print("   ✓ Agent created successfully")

        # Test 1: Simple query
        print("\n2️⃣  Testing: List topics...")
        response = await agent.chat(
            "List all topics in the financial-data environment"
        )
        print(f"   ✓ Response received: {len(response)} characters")
        print(f"\n   Preview: {response[:200]}...")

        # Test 2: SQL query
        print("\n3️⃣  Testing: Execute SQL query...")
        agent.reset_conversation()
        response = await agent.chat(
            "Get 3 transactions from credit-card-transactions in financial-data"
        )
        print(f"   ✓ Response received: {len(response)} characters")
        print(f"\n   Preview: {response[:200]}...")

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_agent())
    exit(0 if success else 1)
