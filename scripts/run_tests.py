# scripts/run_tests.py
"""Run the test suite"""
import subprocess
import sys


def main():
    print("Running Dynamic ETL Pipeline tests...")
    
    result = subprocess.run(
        ["pytest", "tests/", "-v", "--cov=app", "--cov-report=html"],
        cwd="."
    )
    
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
