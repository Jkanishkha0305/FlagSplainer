#!/usr/bin/env python3
"""
Example usage of the MCP AI Agent.

This demonstrates how to use the AI agent to interact with Kafka/Lenses
using natural language.
"""

import asyncio
from mcp_agent import create_mcp_agent


async def main():
    """Run example conversations with the MCP agent."""

    print("=" * 70)
    print("🤖 MCP AI Agent - Example Usage")
    print("=" * 70)
    print()
    print("This agent can use MCP tools to:")
    print("  • Query Kafka topics with SQL")
    print("  • List available topics")
    print("  • Get topic information")
    print("=" * 70)
    print()

    # Create the agent
    try:
        agent = create_mcp_agent()
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        print("\nMake sure your .env file has:")
        print("  - OPENAI_API_KEY")
        print("  - LENSES_API_KEY")
        print("  - LENSES_API_WEBSOCKET_URL")
        print("  - LENSES_API_WEBSOCKET_PORT")
        return

    # Example 1: List topics
    print("\n" + "=" * 70)
    print("Example 1: List all topics")
    print("=" * 70)

    response = await agent.chat(
        "Can you list all the Kafka topics in the financial-data environment?"
    )
    print(f"\n🤖 Agent Response:\n{response}\n")

    # Example 2: Query specific topic
    print("\n" + "=" * 70)
    print("Example 2: Query credit card transactions")
    print("=" * 70)

    agent.reset_conversation()  # Start fresh conversation
    response = await agent.chat(
        "Show me the latest 5 credit card transactions from the credit-card-transactions topic in the financial-data environment. Include transaction ID, merchant, amount, and customer ID."
    )
    print(f"\n🤖 Agent Response:\n{response}\n")

    # Example 3: Analyze data
    print("\n" + "=" * 70)
    print("Example 3: Find high-value transactions")
    print("=" * 70)

    agent.reset_conversation()
    response = await agent.chat(
        "Find all credit card transactions over $500 from the credit-card-transactions topic in financial-data environment. Show the merchant, amount, and location."
    )
    print(f"\n🤖 Agent Response:\n{response}\n")

    # Example 4: Multi-step analysis
    print("\n" + "=" * 70)
    print("Example 4: Multi-step analysis")
    print("=" * 70)

    agent.reset_conversation()
    response = await agent.chat(
        "First, tell me what topics are available in the financial-data environment. Then query the paypal-transactions topic and show me the last 3 transactions."
    )
    print(f"\n🤖 Agent Response:\n{response}\n")

    # Example 5: Get topic info
    print("\n" + "=" * 70)
    print("Example 5: Get topic information")
    print("=" * 70)

    agent.reset_conversation()
    response = await agent.chat(
        "Tell me about the credit-card-transactions topic in the financial-data environment. How many partitions does it have?"
    )
    print(f"\n🤖 Agent Response:\n{response}\n")

    print("=" * 70)
    print("✅ Examples complete!")
    print("=" * 70)


async def interactive_mode():
    """Run the agent in interactive mode."""
    print("=" * 70)
    print("🤖 MCP AI Agent - Interactive Mode")
    print("=" * 70)
    print()
    print("Ask me anything about your Kafka topics!")
    print("Type 'quit' or 'exit' to stop.")
    print("Type 'reset' to start a new conversation.")
    print("=" * 70)
    print()

    try:
        agent = create_mcp_agent()
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return

    while True:
        try:
            user_input = input("\n👤 You: ").strip()

            if user_input.lower() in ["quit", "exit"]:
                print("\n👋 Goodbye!")
                break

            if user_input.lower() == "reset":
                agent.reset_conversation()
                print("🔄 Conversation reset!")
                continue

            if not user_input:
                continue

            response = await agent.chat(user_input)
            print(f"\n🤖 Agent: {response}")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # Run in interactive mode
        asyncio.run(interactive_mode())
    else:
        # Run examples
        asyncio.run(main())
