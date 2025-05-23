#!/usr/bin/env python3
"""
Demo script for the Advanced Visualization Dashboard.

This example shows how to launch the advanced dashboard with interactive features.
"""
import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import bizcon modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from visualization.advanced_dashboard import launch_advanced_dashboard
    from visualization.analysis_utils import BenchmarkAnalyzer, FilterManager
    from visualization import _ADVANCED_FEATURES_AVAILABLE
except ImportError:
    print("❌ Advanced dashboard features require additional dependencies.")
    print("Install with: pip install -e \".[advanced]\"")
    print("(Note: Use quotes to prevent shell glob expansion)")
    sys.exit(1)


def main():
    """Launch the advanced dashboard demo."""
    # Check if advanced features are available
    if not _ADVANCED_FEATURES_AVAILABLE:
        print("❌ Advanced dashboard features are not available.")
        print("Install dependencies with: pip install -e \".[advanced]\"")
        print("(Note: Use quotes to prevent shell glob expansion)")
        return 1
    
    parser = argparse.ArgumentParser(description='Launch bizCon Advanced Dashboard Demo')
    parser.add_argument('--results-dir', '-r', 
                       default='output/',
                       help='Directory containing benchmark results (default: output/)')
    parser.add_argument('--host', 
                       default='127.0.0.1',
                       help='Host to run dashboard on (default: 127.0.0.1)')
    parser.add_argument('--port', '-p',
                       type=int,
                       default=5001,
                       help='Port to run dashboard on (default: 5001)')
    parser.add_argument('--no-auto-refresh',
                       action='store_true',
                       help='Disable automatic data refresh')
    parser.add_argument('--refresh-interval',
                       type=int,
                       default=30,
                       help='Auto-refresh interval in seconds (default: 30)')
    
    args = parser.parse_args()
    
    # Check if results directory exists
    results_path = Path(args.results_dir)
    if not results_path.exists():
        print(f"❌ Results directory '{results_path}' does not exist.")
        print("Please run some benchmarks first or specify a different directory with --results-dir")
        return 1
    
    # Check if there are any JSON result files
    json_files = list(results_path.glob('*.json'))
    if not json_files:
        print(f"❌ No JSON result files found in '{results_path}'.")
        print("Please run some benchmarks first to generate result files.")
        return 1
    
    print("🚀 bizCon Advanced Dashboard Demo")
    print("=" * 50)
    print(f"📁 Results directory: {results_path.absolute()}")
    print(f"📊 Found {len(json_files)} result files")
    print(f"🌐 Dashboard URL: http://{args.host}:{args.port}")
    print()
    
    # Display features
    print("✨ Advanced Features Available:")
    print("  • Interactive Plotly charts (radar, 3D scatter, heatmap, etc.)")
    print("  • Real-time filtering by models and scenarios")
    print("  • Model comparison and analysis tools")
    print("  • Data export (JSON, CSV)")
    print("  • Auto-refresh" if not args.no_auto_refresh else "  • Manual refresh only")
    print("  • Statistical analysis and insights")
    print()
    
    # Quick analysis preview
    try:
        import json
        print("📈 Quick Analysis Preview:")
        print("-" * 30)
        
        # Load one result file for preview
        with open(json_files[0], 'r') as f:
            sample_result = json.load(f)
        
        model_name = sample_result.get('model_name', 'Unknown')
        overall_score = sample_result.get('overall', {}).get('overall_score', 0)
        run_count = len(sample_result.get('runs', []))
        
        print(f"Sample model: {model_name}")
        print(f"Overall score: {overall_score:.2f}/10")
        print(f"Runs completed: {run_count}")
        print()
        
    except Exception as e:
        print(f"⚠️  Could not load sample data: {e}")
        print()
    
    # Launch instructions
    print("🎯 Dashboard Controls:")
    print("  • Use the filter panel to narrow down results")
    print("  • Select different chart types from the dropdown")
    print("  • Compare two models using the comparison tool")
    print("  • Export data using the export buttons")
    print("  • Charts are fully interactive (zoom, pan, hover)")
    print()
    
    print("🔧 To stop the dashboard, press Ctrl+C")
    print()
    
    try:
        # Launch the advanced dashboard
        launch_advanced_dashboard(
            results_dir=str(results_path),
            host=args.host,
            port=args.port,
            auto_refresh=not args.no_auto_refresh,
            refresh_interval=args.refresh_interval
        )
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())