# setup.py
from setuptools import setup, find_packages

setup(
    name="dynamic-etl-pipeline",
    version="1.0.0",
    description="Dynamic ETL Pipeline for Unstructured Data",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "etl-server=app.main:app",
        ],
    },
)