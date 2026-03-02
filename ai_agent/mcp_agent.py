"""
AI Agent that uses MCP tools from lenses_mcp to interact with Kafka/Lenses.

This agent uses OpenAI's function calling to intelligently use MCP tools.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add src to path to import lenses_mcp modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "lenses_mcp"))

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from clients.websocket_client import LensesWebSocketClient
    from clients.http_client import api_client
except ImportError as e:
    print(f"Error importing lenses_mcp clients: {e}")
    LensesWebSocketClient = None
    api_client = None

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
import os

load_dotenv()


class MCPAgent:
    """
    AI Agent that can use MCP tools to query and manage Kafka/Lenses.
    """

    def __init__(self, openai_api_key: str, lenses_base_url: str, lenses_api_key: str):
        """
        Initialize the MCP Agent.

        Args:
            openai_api_key: OpenAI API key
            lenses_base_url: Lenses WebSocket base URL (e.g., ws://54.195.167.195:8080)
            lenses_api_key: Lenses API key for authentication
        """
        if OpenAI is None:
            raise ImportError("OpenAI library not installed. Run: pip install openai")

        self.openai = OpenAI(api_key=openai_api_key)
        self.lenses_client = LensesWebSocketClient(lenses_base_url, lenses_api_key)
        self.conversation_history = []

        # Define available MCP tools for OpenAI function calling
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "execute_sql",
                    "description": "Execute SQL queries on Kafka topics using Lenses SQL. Use this to query, filter, and analyze data in Kafka topics.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "environment": {
                                "type": "string",
                                "description": "The Lenses environment name (e.g., 'financial-data')",
                            },
                            "sql": {
                                "type": "string",
                                "description": "The SQL query to execute (e.g., 'SELECT * FROM `credit-card-transactions` LIMIT 10')",
                            },
                        },
                        "required": ["environment", "sql"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_topics",
                    "description": "List all Kafka topics in an environment. Use this to discover available topics.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "environment": {
                                "type": "string",
                                "description": "The Lenses environment name",
                            }
                        },
                        "required": ["environment"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_topic_info",
                    "description": "Get detailed information about a specific Kafka topic including partitions, config, and metadata.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "environment": {
                                "type": "string",
                                "description": "The Lenses environment name",
                            },
                            "topic_name": {
                                "type": "string",
                                "description": "The name of the topic",
                            },
                        },
                        "required": ["environment", "topic_name"],
                    },
                },
            },
        ]

    async def execute_sql(self, environment: str, sql: str) -> Dict[str, Any]:
        """Execute SQL query using Lenses WebSocket client."""
        try:
            endpoint = f"/api/v1/environments/{environment}/proxy/api/ws/v2/sql/execute"
            result = await self.lenses_client._make_request(endpoint=endpoint, sql=sql)
            return {
                "success": True,
                "records": result,
                "count": len(result) if result else 0,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def list_topics(self, environment: str) -> Dict[str, Any]:
        """List all topics in an environment."""
        try:
            endpoint = f"/api/v1/environments/{environment}/proxy/api/topics"
            result = await api_client._make_request("GET", endpoint)
            topics = [topic.get("topicName") for topic in result if "topicName" in topic]
            return {"success": True, "topics": topics, "count": len(topics)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_topic_info(self, environment: str, topic_name: str) -> Dict[str, Any]:
        """Get information about a specific topic."""
        try:
            endpoint = f"/api/v1/environments/{environment}/proxy/api/topics/{topic_name}"
            result = await api_client._make_request("GET", endpoint)
            return {"success": True, "topic_info": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a specific MCP tool and return the result."""
        print(f"  🔧 Executing tool: {tool_name}")
        print(f"     Arguments: {json.dumps(arguments, indent=2)}")

        if tool_name == "execute_sql":
            result = await self.execute_sql(
                arguments["environment"], arguments["sql"]
            )
        elif tool_name == "list_topics":
            result = await self.list_topics(arguments["environment"])
        elif tool_name == "get_topic_info":
            result = await self.get_topic_info(
                arguments["environment"], arguments["topic_name"]
            )
        else:
            result = {"success": False, "error": f"Unknown tool: {tool_name}"}

        print(f"  ✓ Tool result: {result.get('success', False)}")
        return json.dumps(result, indent=2)

    async def chat(self, user_message: str, max_iterations: int = 5) -> str:
        """
        Have a conversation with the AI agent. The agent can use MCP tools as needed.

        Args:
            user_message: The user's message/question
            max_iterations: Maximum number of tool calls to allow

        Returns:
            The agent's response
        """
        print(f"\n{'='*60}")
        print(f"🤖 AI Agent Processing: {user_message}")
        print(f"{'='*60}\n")

        # Add user message to conversation
        self.conversation_history.append({"role": "user", "content": user_message})

        iterations = 0
        while iterations < max_iterations:
            iterations += 1

            # Call OpenAI with conversation history and available tools
            response = self.openai.chat.completions.create(
                model="gpt-4",
                messages=self.conversation_history,
                tools=self.tools,
                tool_choice="auto",
            )

            message = response.choices[0].message

            # Check if the agent wants to use a tool
            if message.tool_calls:
                # Add assistant's response to history
                self.conversation_history.append(message)

                # Execute each tool call
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Execute the tool
                    tool_result = await self.execute_tool(
                        function_name, function_args
                    )

                    # Add tool result to conversation
                    self.conversation_history.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result,
                        }
                    )

                # Continue the loop to get the agent's response after using tools
                continue
            else:
                # No more tool calls, return the final response
                final_response = message.content
                self.conversation_history.append(
                    {"role": "assistant", "content": final_response}
                )
                return final_response

        return "Maximum iterations reached. The agent couldn't complete the task."

    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []


def create_mcp_agent() -> MCPAgent:
    """Create an MCP agent with configuration from environment variables."""
    openai_key = os.getenv("OPENAI_API_KEY")
    lenses_url = os.getenv("LENSES_API_WEBSOCKET_URL", "ws://localhost")
    lenses_port = os.getenv("LENSES_API_WEBSOCKET_PORT", "8080")
    lenses_key = os.getenv("LENSES_API_KEY")

    if not openai_key:
        raise ValueError("OPENAI_API_KEY not set in environment")
    if not lenses_key:
        raise ValueError("LENSES_API_KEY not set in environment")

    lenses_base_url = f"{lenses_url}:{lenses_port}"

    return MCPAgent(
        openai_api_key=openai_key,
        lenses_base_url=lenses_base_url,
        lenses_api_key=lenses_key,
    )
