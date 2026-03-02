#!/usr/bin/env python3
"""
Quick setup verification script for fraud detection system.
"""

import sys


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n🔍 Checking Dependencies...")

    missing = []

    try:
        import openai
        print("  ✓ openai")
    except ImportError:
        print("  ✗ openai (missing)")
        missing.append("openai")

    try:
        import mcp
        print("  ✓ mcp")
    except ImportError:
        print("  ✗ mcp (missing)")
        missing.append("mcp")

    try:
        from dotenv import load_dotenv
        print("  ✓ python-dotenv")
    except ImportError:
        print("  ✗ python-dotenv (missing)")
        missing.append("python-dotenv")

    try:
        import langgraph
        print("  ✓ langgraph")
    except ImportError:
        print("  ⚠️  langgraph (optional - will use fallback)")

    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("   Install with: pip install -r requirements.txt")
        return False

    print("\n✅ All required dependencies installed!")
    return True


def check_config():
    """Check if configuration is properly set."""
    print("\n🔍 Checking Configuration...")

    from .config import Config

    Config.print_config()

    issues = []

    if not Config.OPENAI_API_KEY:
        issues.append("OPENAI_API_KEY not set")
        print("  ✗ OpenAI API Key not configured")
    else:
        print("  ✓ OpenAI API Key configured")

    if not Config.LENSES_TOKEN:
        print("  ⚠️  LENSES_TOKEN not set (may be required)")

    if issues:
        print(f"\n⚠️  Configuration issues: {', '.join(issues)}")
        print("   Set environment variables or create a .env file")
        return False

    print("\n✅ Configuration looks good!")
    return True


def check_mcp_connection():
    """Test MCP server connectivity."""
    print("\n🔍 Checking MCP Server...")

    try:
        # Basic import check
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        print("  ✓ MCP client modules available")
        print("  ℹ️  To test actual connection, run the fraud detection system")
        return True

    except Exception as exc:
        print(f"  ✗ MCP check failed: {exc}")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("🚨 Fraud Detection System - Setup Verification")
    print("=" * 60)

    checks = [
        check_dependencies(),
        check_config(),
        check_mcp_connection(),
    ]

    print("\n" + "=" * 60)

    if all(checks):
        print("✅ All checks passed! Ready to run fraud detection.")
        print("\nRun with: python run_fraud_detection.py")
        print("=" * 60)
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
