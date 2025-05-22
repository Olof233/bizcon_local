#!/usr/bin/env python3
"""
Test script to validate the bizCon framework with real API models.
This script tests the framework with actual API calls (requires API keys).
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for importing
sys.path.insert(0, str(Path(__file__).resolve().parent))

def test_with_real_models():
    """Test the framework with real API models."""
    print("Testing bizCon Framework with Real Models...")
    
    # Check for API keys
    api_keys = {
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
        "MISTRAL_API_KEY": os.environ.get("MISTRAL_API_KEY")
    }
    
    available_providers = []
    for key, value in api_keys.items():
        if value:
            provider = key.replace("_API_KEY", "").lower()
            available_providers.append(provider)
            print(f"✓ {provider.title()} API key found")
        else:
            provider = key.replace("_API_KEY", "").lower()
            print(f"✗ {provider.title()} API key not found")
    
    if not available_providers:
        print("\nNo API keys found. Please set at least one of:")
        print("- OPENAI_API_KEY")
        print("- ANTHROPIC_API_KEY")
        print("- MISTRAL_API_KEY")
        print("\nExample:")
        print("export OPENAI_API_KEY='your-key-here'")
        print("python test_with_real_models.py")
        return False
    
    print(f"\nRunning tests with {len(available_providers)} provider(s): {', '.join(available_providers)}")
    
    try:
        # Import after setting up paths
        from run import run_benchmark
        
        # Create a minimal config for testing
        config_path = "config/models.yaml"
        
        # Run a simple benchmark with one scenario
        results = run_benchmark(
            config_path=config_path,
            output_dir="test_output_real",
            scenario_ids=["product_inquiry_001"],
            parallel=False,
            verbose=True
        )
        
        if results:
            print("\n🎉 Real model test completed successfully!")
            print("Check test_output_real/ directory for detailed results.")
            return True
        else:
            print("\n❌ Real model test failed.")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running real model test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_with_real_models()
    sys.exit(0 if success else 1)