# Credit Card Fraud Detection - 2-Agent System

A sophisticated fraud detection system using a 2-agent architecture with OpenAI LLM and MCP (Model Context Protocol) integration.

## Architecture

### Agent 1: Scanner Agent
- **Purpose**: Fetch transaction data from Kafka topics via MCP
- **Technology**: MCP client, Lenses SQL
- **Data Sources**:
  - `credit-card-transactions` topic
  - `paypal-transactions` topic
- **Output**: Normalized transaction data

### Agent 2: Analyzer Agent
- **Purpose**: Detect fraud patterns using rule-based + AI analysis
- **Technology**: OpenAI GPT-4, Pattern matching algorithms
- **Features**:
  - 5 rule-based fraud patterns
  - AI-powered intelligent analysis
  - Risk scoring and recommendations

## Fraud Detection Patterns

### Rule-Based Detection:
1. **Foreign PayPal + Domestic CC** - Account takeover indicator
2. **Category Mismatch** - Merchant fraud detection
3. **High Amount Foreign Transactions** - Suspicious large transfers
4. **Multiple Failed Transactions** - Card testing attacks
5. **Duplicate Amounts Across Platforms** - Double-charging detection

### AI-Powered Detection:
- Velocity attack detection
- Sophisticated pattern recognition
- Contextual risk assessment
- Actionable recommendations

## Setup

### 1. Install Dependencies

```bash
cd hackathon
pip install -r requirements.txt
```

### 2. Configure Environment

**Option A: Use the root `.env` file (Recommended)**

If you already have a `.env` file in the project root with Lenses configuration, just add your OpenAI key:

```bash
# Add to /Users/j_kanishkha/lenses-mcp/.env
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4
```

**Option B: Create a separate hackathon `.env` file**

```bash
cd hackathon
cp .env.example .env
```

Edit `hackathon/.env` and set:
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `OPENAI_MODEL` - Model to use (default: gpt-4)
- `LENSES_API_HTTP_URL` - Lenses HTTP URL (default: http://localhost)
- `LENSES_API_HTTP_PORT` - Lenses HTTP port (default: 9991)
- `LENSES_API_WEBSOCKET_URL` - Lenses WebSocket URL (default: ws://localhost)
- `LENSES_API_WEBSOCKET_PORT` - Lenses WebSocket port (default: 9991)
- `LENSES_ENVIRONMENT` - Your Lenses environment name (default: dev)
- `LENSES_TOKEN` - Your Lenses API token

**Note**: The config automatically checks both `hackathon/.env` and the root `.env` file.

### 3. Verify Setup

Run the setup verification script:

```bash
python check_setup.py
```

This will check:
- All required dependencies are installed
- Configuration is properly set
- MCP client modules are available

### 4. Ensure MCP Server is Running

The scanner agent connects to your MCP server to fetch data:

```bash
# From the root directory
python -m lenses_mcp.server
```

### 5. Run the Fraud Detection System

```bash
python run_fraud_detection.py
```

## How It Works

```
┌─────────────────────┐
│  Scanner Agent      │
│  (Data Fetcher)     │
│                     │
│  - Connect to MCP   │
│  - Query Kafka      │
│  - Normalize data   │
└──────────┬──────────┘
           │
           │ Transaction Data
           ▼
┌─────────────────────┐
│  Analyzer Agent     │
│  (Fraud Detector)   │
│                     │
│  - Rule matching    │
│  - AI analysis      │
│  - Risk scoring     │
└──────────┬──────────┘
           │
           │ Fraud Alerts
           ▼
┌─────────────────────┐
│  Results            │
│                     │
│  - Alert summary    │
│  - Risk levels      │
│  - Recommendations  │
└─────────────────────┘
```

## MCP Integration

The system uses MCP to communicate with your Lenses platform:

1. **Scanner Agent** calls `execute_sql` tool via MCP
2. Queries Kafka topics using Lenses SQL
3. Receives transaction data in real-time
4. Passes to Analyzer Agent for fraud detection

## OpenAI Integration

The Analyzer Agent uses OpenAI for:
- Advanced pattern recognition beyond rules
- Risk level assessment (LOW, MEDIUM, HIGH, CRITICAL)
- Contextual analysis of transaction behaviors
- Actionable fraud prevention recommendations

## Sample Output

```
============================================================
🚨 2-AGENT FRAUD DETECTION SYSTEM
============================================================
Data Sources: Credit Card + PayPal Transactions
============================================================

============================================================
🔍 SCANNER AGENT - Fetching Transactions via MCP
============================================================
→ Connecting to MCP server for environment 'dev'...
→ Fetching from topic 'credit-card-transactions'...
→ Fetching from topic 'paypal-transactions'...
✓ Found 20 credit card transactions
✓ Found 20 PayPal transactions

============================================================
🔬 ANALYZER AGENT - Detecting Fraud Patterns
============================================================

Analyzing 20 CC + 20 PayPal transactions...

→ Pattern 1: Foreign PayPal + Domestic CC...
  🚨 Alert: CUST-001933 - Foreign account activity

→ Running AI-powered analysis with OpenAI...

✓ Analysis complete: 8 rule-based alerts generated
✓ AI analysis complete: Risk level HIGH

============================================================
📊 FINAL RESULTS
============================================================

FRAUD DETECTION SUMMARY
========================
Total Alerts: 8
  - Critical (8-10): 3
  - High (6-7): 3
  - Medium (1-5): 2

🤖 AI-POWERED ANALYSIS
========================
Risk Level: HIGH
Confidence: 85%

Insights:
The transaction patterns indicate potential account takeover
attacks and card testing activities. Recommend immediate review
of flagged customers.

Recommendations:
  - Implement multi-factor authentication for high-risk accounts
  - Monitor velocity patterns for flagged customers
  - Review merchant categorization accuracy
```

## Configuration Options

Edit `hackathon/config.py` to customize:
- Fetch limits (default: 20 transactions)
- Topic names
- OpenAI model (default: gpt-4)
- Environment settings

## Fallback Mode

If MCP or OpenAI are unavailable, the system gracefully falls back:
- **Scanner**: Uses sample transaction data
- **Analyzer**: Uses rule-based detection only

## Dependencies

- `openai>=1.12.0` - OpenAI API client
- `mcp>=0.9.0` - Model Context Protocol client
- `langgraph>=0.0.20` - Agent workflow orchestration (optional)
- `python-dotenv>=1.0.0` - Environment variable management

## Troubleshooting

### MCP Connection Issues
- Ensure MCP server is running: `python -m lenses_mcp.server`
- Check `LENSES_ENVIRONMENT` is correctly set
- Verify Lenses credentials in `.env`

### OpenAI Errors
- Verify `OPENAI_API_KEY` is valid
- Check API quota/rate limits
- Ensure network connectivity

### No Transactions Found
- Verify Kafka topics exist and have data
- Check topic names in `config.py`
- Review Lenses SQL permissions

## License

MIT
