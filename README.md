<div align="center">

# ⚡ FlagSplainer

### Real-Time Fraud Detection & Explainability with Multi-Agent AI

[![Hackathon](https://img.shields.io/badge/🏆_Hackathon-2nd_Place-silver?style=for-the-badge)](https://lenses.io)
[![Event](https://img.shields.io/badge/Lenses.io_×_AWS_×_Ness-Real--Time_Data_%26_AI-blue?style=for-the-badge)](https://lenses.io)
[![Venue](https://img.shields.io/badge/📍_One_World_Trade_Center-NYC-black?style=for-the-badge)](#)

> *Financial systems flag countless transactions as suspicious — but rarely explain why. FlagSplainer changes that.*

</div>

---

## 🧠 What is FlagSplainer?

**FlagSplainer** is a multi-agent reasoning system that not only detects suspicious activity in real-time Kafka streams, but **explains why each transaction is flagged** — making fraud analysis transparent, interpretable, and human-readable.

Built in a few intense hours at the **Real-Time Data & AI Hackathon** hosted by [Lenses.io](https://lenses.io), [Amazon Web Services](https://aws.amazon.com/), and [Ness Digital Engineering](https://www.ness.com/) at **One World Trade Center, NYC** — and took home 🥈 **2nd Place**.

---

## 🎯 The Problem

Financial systems process **massive streams** of credit card and PayPal transactions every second. Countless are flagged as potentially fraudulent — yet the reasoning behind those flags often stays opaque.

**The gap between detection and understanding costs trust, time, and money.**

FlagSplainer bridges that gap.

---

## ⚙️ How It Works

```
Apache Kafka (AWS MSK)
  └─ Credit Card Transactions
  └─ PayPal Transactions
          │
          ▼
  Lenses MCP Server  ◄──── Real-time streaming via Lenses SQL
          │
          ▼
  ┌───────────────────────────────────────┐
  │       LangChain Multi-Agent Pipeline  │
  │                                       │
  │  🚩 Flagging Agent                    │
  │     └─ Spots anomalies in live data   │
  │            │                          │
  │            ▼                          │
  │  🔍 Reasoning Agent                   │
  │     └─ Evaluates behavioral &         │
  │        rule-based patterns            │
  │            │                          │
  │            ▼                          │
  │  💬 Explainer Agent                   │
  │     └─ Delivers real-time,            │
  │        human-readable explanations    │
  └───────────────────────────────────────┘
          │
          ▼
  Fraud Alerts + Plain-English Explanations
```

### The Three Agents

| Agent | Role |
|-------|------|
| 🚩 **Flagging Agent** | Monitors live Kafka streams, detects anomalies using rule-based patterns |
| 🔍 **Reasoning Agent** | Evaluates behavioral context, cross-platform signals, and risk scoring |
| 💬 **Explainer Agent** | Generates real-time, human-readable explanations for every flag |

### Fraud Detection Patterns

- Foreign PayPal + Domestic CC activity → account takeover indicator
- Merchant category mismatch → merchant fraud detection
- High-amount foreign transactions → suspicious large transfers
- Multiple failed transactions → card testing attacks
- Duplicate amounts across platforms → double-charging detection
- AI-powered velocity and behavioral analysis via **AWS Bedrock / OpenAI GPT-4**

---

## 🏗️ Architecture

**Hybrid Rule + LLM** design ensures both speed and interpretability:

- **Rule-based layer** catches known fraud patterns instantly
- **LLM layer** handles novel, context-dependent patterns and generates natural language explanations
- **Multi-agent coordination** via LangChain ensures clean separation of detection, reasoning, and explanation

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Streaming Data** | Apache Kafka via AWS MSK |
| **MCP Server** | [Lenses.io MCP](https://lenses.io) + FastMCP |
| **Agent Framework** | LangChain multi-agent pipeline |
| **LLM** | AWS Bedrock / OpenAI GPT-4 |
| **Transport** | WebSocket + HTTP (Lenses SQL) |
| **Language** | Python 3.12 |
| **Dependency Management** | `uv` |

---

## 📁 Project Structure

```
FlagSplainer/
├── src/lenses_mcp/              # Core Lenses MCP server
│   ├── server.py                # FastMCP server entrypoint
│   ├── config.py                # Configuration management
│   ├── clients/
│   │   ├── http_client.py       # Lenses HTTP API client
│   │   └── websocket_client.py  # Lenses WebSocket client (SQL)
│   └── tools/
│       ├── sql.py               # Execute SQL on Kafka topics
│       ├── topics.py            # Topic management tools
│       ├── environments.py      # Environment discovery
│       └── kafka_consumer_groups.py
│
├── fraud_detection_ai_agents/   # Multi-agent orchestration
│   ├── agent_coordinator.py     # LangChain agent pipeline
│   ├── anomaly_detection_agent.py
│   ├── data_analysis_agent.py
│   ├── llm_narrative_agent.py   # Explainer agent
│   ├── mcp_tool_agent.py
│   └── real_live_consumer.py
│
├── hackathon/                   # 2-agent fraud detection system
│   ├── run_fraud_detection.py   # Main entrypoint
│   ├── fraud_detection/
│   │   ├── scanner_direct.py    # Scanner agent (Kafka → data)
│   │   ├── analyzer.py          # Analyzer agent (AI + rules)
│   │   └── graph.py             # Agent workflow graph
│   └── config.py
│
└── ai_agent/                    # Natural language Kafka agent
    ├── mcp_agent.py             # GPT-4 + MCP tool agent
    └── example_usage.py
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) for dependency management
- A Lenses.io instance (or [Community Edition](https://lenses.io/community-edition/))
- OpenAI API key or AWS Bedrock access

### 1. Clone & Install

```bash
git clone https://github.com/Jkanishkha0305/FlagSplainer.git
cd FlagSplainer
uv sync
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Lenses.io
LENSES_API_KEY=your-lenses-api-key
LENSES_API_HTTP_URL=http://your-lenses-host
LENSES_API_HTTP_PORT=9991
LENSES_API_WEBSOCKET_URL=ws://your-lenses-host
LENSES_API_WEBSOCKET_PORT=9991
LENSES_ENVIRONMENT=dev

# OpenAI / AWS Bedrock
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4
```

### 3. Run the MCP Server

```bash
uv run src/lenses_mcp/server.py
```

Or as a remote server:

```bash
uv run fastmcp run src/lenses_mcp/server.py --transport=http --port=8000
```

### 4. Run FlagSplainer (Fraud Detection)

```bash
cd hackathon
python run_fraud_detection.py
```

### 5. Run the Multi-Agent Pipeline

```bash
cd fraud_detection_ai_agents
python agent_coordinator.py
```

---

## 🔌 MCP Client Configuration

To use with Claude Desktop, Cursor, Gemini CLI, etc.:

```json
{
  "mcpServers": {
    "FlagSplainer": {
      "command": "uv",
      "args": [
        "run",
        "--project", "<ABSOLUTE_PATH_TO_THIS_REPO>",
        "--with", "fastmcp",
        "fastmcp",
        "run",
        "<ABSOLUTE_PATH_TO_THIS_REPO>/src/lenses_mcp/server.py"
      ],
      "env": {
        "LENSES_API_KEY": "<YOUR_LENSES_API_KEY>"
      },
      "transport": "stdio"
    }
  }
}
```

---

## 📊 Sample Output

```
============================================================
⚡ FLAGSPLAINER - Real-Time Fraud Detection
============================================================

🔍 SCANNER AGENT - Fetching live transactions via MCP...
  ✓ 20 credit card transactions from Kafka
  ✓ 20 PayPal transactions from Kafka

🚩 FLAGGING AGENT - Detecting anomalies...
  🚨 CUST-001933 — Foreign PayPal + Domestic CC activity
  🚨 CUST-004721 — Duplicate amounts across platforms ($847.50)
  🚨 CUST-009812 — Multiple failed transactions (card testing)

🔬 REASONING AGENT - Evaluating patterns...
  Risk Level: HIGH | Confidence: 87%

💬 EXPLAINER AGENT - Generating explanations...
  → CUST-001933: "This customer made a $1,240 PayPal payment
    routed through a foreign account minutes after a domestic
    credit card purchase. This pattern is consistent with
    account takeover — recommend immediate MFA challenge."

📊 SUMMARY: 8 alerts | 3 Critical | 3 High | 2 Medium
============================================================
```

---

## 👥 Team

Built with 💪 by:

- **[Kanishkha J](https://github.com/Jkanishkha0305)**
- **Nirbhaya Reddy G**
- **Vijay Gottipati**

---

## 🙏 Acknowledgements

Huge thanks to **[Lenses.io](https://lenses.io)**, **[Amazon Web Services](https://aws.amazon.com/)**, and **[Ness Digital Engineering](https://www.ness.com/)** for an incredible event — and to the judges, mentors, and organizers:

*Tun Shwe, Andrew Oetzel, Samit Kumbhani, Bilge Zeren Aksu, Nicholas Ivory, Guillaume Aymé, Germain Cassis*

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

**⚡ Built live. Streamed live. Explained live.**

*Real-Time Data & AI Hackathon · One World Trade Center, NYC · 🥈 2nd Place*

</div>
