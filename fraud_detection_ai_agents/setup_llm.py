#!/usr/bin/env python3
"""
Setup script for LLM-enhanced fraud detection
This script helps configure the OpenAI API key for enhanced fraud narratives
"""

import os
import sys

def setup_openai_key():
    """
    Setup OpenAI API key for LLM features
    """
    print("🤖 LLM-Enhanced Fraud Detection Setup")
    print("=" * 50)
    
    # Check if API key is already set
    existing_key = os.getenv('OPENAI_API_KEY')
    if existing_key:
        print(f"✅ OpenAI API key already configured: {existing_key[:8]}...")
        return True
    
    print("To enable LLM-enhanced fraud narratives, you need an OpenAI API key.")
    print("\nSteps to get your API key:")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Sign in to your OpenAI account")
    print("3. Click 'Create new secret key'")
    print("4. Copy the API key")
    print("\nThen set it as an environment variable:")
    print("export OPENAI_API_KEY='your-api-key-here'")
    print("\nOr add it to your .env file:")
    print("OPENAI_API_KEY=your-api-key-here")
    
    # Try to get key from user input
    try:
        api_key = input("\nEnter your OpenAI API key (or press Enter to skip): ").strip()
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            print(f"✅ API key set: {api_key[:8]}...")
            return True
        else:
            print("⚠️  Skipping API key setup. LLM features will be disabled.")
            return False
    except KeyboardInterrupt:
        print("\n⚠️  Setup cancelled. LLM features will be disabled.")
        return False

def test_llm_connection():
    """
    Test LLM connection
    """
    try:
        from llm_narrative_agent import LLMNarrativeAgent
        
        print("\n🧪 Testing LLM connection...")
        agent = LLMNarrativeAgent()
        
        if agent.enabled:
            print("✅ LLM Agent initialized successfully!")
            return True
        else:
            print("❌ LLM Agent not enabled. Check your API key.")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LLM connection: {e}")
        return False

def main():
    """
    Main setup function
    """
    print("🚀 Setting up LLM-Enhanced Fraud Detection System")
    print("=" * 60)
    
    # Setup API key
    if setup_openai_key():
        # Test connection
        if test_llm_connection():
            print("\n🎉 Setup complete! LLM features are enabled.")
            print("Run 'python run_fraud_detection.py' to start the enhanced demo.")
        else:
            print("\n⚠️  Setup incomplete. LLM features will be disabled.")
    else:
        print("\n⚠️  LLM features will be disabled. You can still run the demo with basic fraud detection.")
    
    print("\n" + "=" * 60)
    print("📚 For more information, see the README.md file")

if __name__ == "__main__":
    main()
