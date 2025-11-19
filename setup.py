"""Setup configuration for KalcEngine."""
from setuptools import setup, find_packages

setup(
    name="kalc-engine",
    version="1.0.0",
    description="Lightweight multi-mode calculator with zero dependencies",
    author="Khaled",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "kalc=kalc_engine.__main__:main",
        ],
    },
)
