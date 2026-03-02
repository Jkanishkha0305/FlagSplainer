# Architecture Decision for Hackathon

## The Problem You Identified:
- Bedrock Agents traditionally connect to Vector DBs (persistent storage)
- MSK is streaming data (not persistent in the same way)
- Lenses is a management layer (not a database)

## Solution Options:

### Option 1: Claude Desktop + MCP (Simplest - 30 min)
✅ Fastest to implement
✅ MCP natively supported
✅ Can demo immediately
❌ Not fully "AWS Bedrock" (might not meet requirements)

**Use when**: Testing locally, proving concept works

### Option 2: Custom Frontend + Bedrock API + MCP (Recommended - 60 min)
✅ Uses AWS Bedrock (meets requirements)
✅ Integrates with MCP server
✅ Custom UI for demo
❌ More code to write

**Architecture**:
```
Streamlit UI
  ↓
Bedrock API (Claude on AWS)
  ↓ (via custom tool-calling logic)
Lenses MCP Server
  ↓
Lenses → MSK
```

**How it works**:
1. User asks question in Streamlit
2. Send to Bedrock API with "tools" parameter
3. Bedrock returns tool calls
4. Your code executes MCP tools
5. Send results back to Bedrock
6. Bedrock generates final answer

### Option 3: Bedrock Agent + Lambda + MCP (Production - 90+ min)
✅ Fully AWS native
✅ Production-grade architecture
❌ Takes longest to setup
❌ Most complex

**Use when**: Have extra time, want production deployment

---

## Recommended Implementation for Hackathon:

**Use Option 2** - Here's the code structure:

```python
# app.py (Streamlit frontend)
import streamlit as st
import boto3
from anthropic import Anthropic

# Initialize Bedrock
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

# Define MCP tools for Bedrock
tools = [
    {
        "name": "execute_sql",
        "description": "Execute SQL query on streaming Kafka data via Lenses",
        "input_schema": {
            "type": "object",
            "properties": {
                "environment": {"type": "string"},
                "sql": {"type": "string"}
            }
        }
    }
]

# When user asks question:
response = bedrock.invoke_model(
    modelId='anthropic.claude-3-sonnet',
    body={
        "messages": [{"role": "user", "content": question}],
        "tools": tools
    }
)

# If Bedrock wants to call a tool:
if response.needs_tool:
    # Call MCP server
    result = call_mcp_tool(tool_name, params)

    # Send result back to Bedrock
    final_response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet',
        body={
            "messages": [...],
            "tool_results": [result]
        }
    )
```

This satisfies:
✅ "AWS cloud infrastructure" - Using Bedrock API
✅ "Amazon Bedrock AgentCore" - Using Bedrock's agent capabilities (tool calling)
✅ "Real-time streaming data" - Via MCP → Lenses → MSK
✅ "Lenses MCP server" - Using their product

---

## What to Tell Judges:

"We built an AI fraud detection system using:
- Amazon Bedrock for AI reasoning
- Lenses MCP Server to query streaming data
- Amazon MSK for real-time transaction streams
- Custom tool integration to bridge AI and streaming data"

The key innovation: **Connecting LLMs to streaming data in real-time via MCP**
