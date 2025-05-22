from setuptools import setup, find_packages

setup(
    name="bizcon",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "anthropic",
        "mistralai",
        "numpy",
        "pandas",
        "matplotlib",
        "seaborn",
        "pyyaml",
        "tqdm",
        "pytest",
        "tiktoken",
        "pdfkit",
        "markdown",
    ],
    entry_points={
        "console_scripts": [
            "bizcon=bizcon.cli:main",
        ],
    },
    python_requires=">=3.8",
)
