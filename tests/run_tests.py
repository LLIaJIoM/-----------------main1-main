import sys
import os
import pytest

def main():
    print("Running all tests with coverage...")
    
    # Add project root to sys.path so tests can import server.py
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Run pytest with coverage options
    args = [
        "tests",
        "--cov=.",
        "--cov-report=term-missing",
        "-v"
    ]
    sys.exit(pytest.main(args))

if __name__ == "__main__":
    main()
