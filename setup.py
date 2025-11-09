"""
Setup configuration for MCP Workshop
"""

from setuptools import setup, find_packages

setup(
    name="mcp_workshop",
    version="0.1.0",
    description="Star Wars API MCP Server Workshop",
    author="Workshop",
    packages=find_packages(),
    package_dir={"": "."},
    install_requires=[
        "fastmcp",
        "requests",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "pytest-mock",
            "responses",
        ]
    },
    python_requires=">=3.12",
)
