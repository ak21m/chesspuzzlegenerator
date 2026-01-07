"""
Setup script for chess puzzle generator
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chess-puzzle-generator",
    version="1.0.0",
    author="Aniket Shingote",
    description="Console-based chess puzzle trainer using Lichess database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "chess>=1.11.2",
        "cairosvg>=2.7.1",
        "zstandard>=0.22.0",
        "python-dotenv>=1.0.0",
        "pillow>=10.1.0",
        "tqdm>=4.66.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "mypy>=1.7.1",
        ]
    },
    entry_points={
        "console_scripts": [
            "chess-puzzle=main:main",
        ],
    },
)
