# 🤖 MCP AI Agent

An intelligent AI agent that uses MCP tools from `lenses_mcp` to interact with Kafka/Lenses using natural language.

## 🎯 What It Does

This AI agent can:
- **Query Kafka topics** using SQL through natural language
- **List and discover** available topics in your Lenses environment
- **Get detailed information** about specific topics
- **Use OpenAI's function calling** to intelligently decide when to use MCP tools

## 🏗️ Architecture

```
User Query (Natural Language)
        ↓
   OpenAI GPT-4 (Function Calling)
        ↓
    MCP Tools Decision
        ↓
├─ execute_sql → LensesWebSocketClient → Kafka
├─ list_topics → LensesHttpClient → Lenses API
└─ get_topic_info → LensesHttpClient → Lenses API
        ↓
   AI-Generated Response
```

## 📁 Files

- **`mcp_agent.py`** - Main AI agent class with MCP tool integration
- **`example_usage.py`** - Example conversations and use cases
- **`test_agent.py`** - Quick test script
- **`README.md`** - This file

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install openai
```

### 2. Configure Environment

Make sure your `.env` file has:

```bash
OPENAI_API_KEY=your-openai-key
LENSES_API_KEY=your-lenses-key
LENSES_API_WEBSOCKET_URL=ws://54.195.167.195
LENSES_API_WEBSOCKET_PORT=8080
```

### 3. Run Test

```bash
cd /Users/j_kanishkha/lenses-mcp/ai_agent
python test_agent.py
```

### 4. Run Examples

```bash
python example_usage.py
```

### 5. Interactive Mode

```bash
python example_usage.py --interactive
```

## 💡 Example Usage

### Python API

```python
import asyncio
from mcp_agent import create_mcp_agent

async def main():
    # Create agent
    agent = create_mcp_agent()

    # Ask questions in natural language
    response = await agent.chat(
        "Show me the last 10 credit card transactions over $500"
    )
    print(response)

    # Multi-step conversations
    response = await agent.chat(
        "First list all topics, then query the paypal-transactions topic"
    )
    print(response)

asyncio.run(main())
```

### Command Line

```bash
# Run examples
python example_usage.py

# Interactive mode
python example_usage.py --interactive
```

## 🛠️ Available MCP Tools

The agent has access to these MCP tools:

### 1. `execute_sql`
Execute SQL queries on Kafka topics using Lenses SQL.

**Example prompts:**
- "Query the credit-card-transactions topic and show me the last 5 transactions"
- "Find all transactions over $1000 in the paypal-transactions topic"
- "Show me transactions from customer CUST-123456"

### 2. `list_topics`
List all available Kafka topics in an environment.

**Example prompts:**
- "What topics are available in the financial-data environment?"
- "List all Kafka topics"
- "Show me all the topics"

### 3. `get_topic_info`
Get detailed information about a specific topic.

**Example prompts:**
- "Tell me about the credit-card-transactions topic"
- "How many partitions does the paypal-transactions topic have?"
- "What's the configuration of the auto-loan-payments topic?"

## 📊 Example Conversations

### Example 1: Query Transactions

**You:** "Show me the last 5 credit card transactions with amounts over $100"

**Agent:**
- Uses `execute_sql` with SQL: `SELECT * FROM credit-card-transactions WHERE amount > 100 LIMIT 5`
- Returns formatted results with transaction details

### Example 2: Topic Discovery

**You:** "What topics do we have, and can you query one of them?"

**Agent:**
- Uses `list_topics` to discover available topics
- Uses `execute_sql` to query one of the found topics
- Returns comprehensive response

### Example 3: Topic Analysis

**You:** "Tell me about the paypal-transactions topic and show me a sample record"

**Agent:**
- Uses `get_topic_info` to get topic metadata
- Uses `execute_sql` to fetch a sample record
- Combines information in a detailed response

## 🔧 How It Works

### 1. Function Calling
The agent uses OpenAI's function calling feature to:
- Understand user intent from natural language
- Decide which MCP tools to use
- Extract parameters from the conversation
- Execute tools in the right order

### 2. MCP Integration
The agent directly uses clients from `src/lenses_mcp`:
- `LensesWebSocketClient` for SQL queries
- `api_client` for HTTP API calls
- Inherits authentication and connection handling

### 3. Conversational Context
The agent maintains conversation history:
- Remembers previous questions and answers
- Can handle follow-up questions
- Builds multi-step workflows

## 🎨 Customization

### Add New Tools

Edit `mcp_agent.py` and add to the `self.tools` list:

```python
{
    "type": "function",
    "function": {
        "name": "your_tool_name",
        "description": "What your tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Description of param1"
                }
            },
            "required": ["param1"]
        }
    }
}
```

Then implement the tool method:

```python
async def your_tool_name(self, param1: str) -> Dict[str, Any]:
    """Implementation of your tool."""
    # Your code here
    pass
```

### Change AI Model

In `mcp_agent.py`, change the model:

```python
response = self.openai.chat.completions.create(
    model="gpt-4-turbo",  # or "gpt-3.5-turbo"
    ...
)
```

## 🐛 Troubleshooting

### ImportError: No module named 'lenses_mcp'
Make sure you're running from the right directory and the path setup is correct.

### Authentication Errors
Check your `.env` file has the correct `LENSES_API_KEY`.

### Connection Errors
Verify `LENSES_API_WEBSOCKET_URL` and `LENSES_API_WEBSOCKET_PORT` are correct.

### OpenAI API Errors
Check your `OPENAI_API_KEY` is valid and you have quota available.

## 📝 Notes

- The agent uses **OpenAI GPT-4** by default (you can change to gpt-3.5-turbo)
- It makes real API calls to your Lenses instance
- Conversation history is maintained per agent instance
- Use `agent.reset_conversation()` to start fresh

## 🚀 Next Steps

1. ✅ Test with `python test_agent.py`
2. ✅ Try examples with `python example_usage.py`
3. ✅ Interactive mode with `python example_usage.py --interactive`
4. 🔧 Customize tools for your use case
5. 🎯 Integrate into your own applications

## 📚 Related

- Lenses MCP Server: `/Users/j_kanishkha/lenses-mcp/src/lenses_mcp/`
- Fraud Detection System: `/Users/j_kanishkha/lenses-mcp/hackathon/`
- Main README: `/Users/j_kanishkha/lenses-mcp/README.md`
