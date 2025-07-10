from setuptools import setup, find_packages

setup(
    name="bizcon",
    version="0.4.0",
    author="Akram Hasan Sharkar",
    author_email="akram@olib.ai",
    description="Business Conversation Evaluation Framework for LLMs with Advanced Visualization Dashboards",
    url="https://github.com/Olib-AI/bizcon",
    packages=find_packages(),
    py_modules=['cli'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
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
    extras_require={
        "advanced": [
            "plotly>=5.0.0",
            "flask>=2.0.0",
            "jinja2",
            "scipy",
        ],
        "all": [
            "plotly>=5.0.0", 
            "flask>=2.0.0",
            "jinja2",
            "scipy",
        ]
    },
    entry_points={
        "console_scripts": [
            "bizcon=cli:main",
        ],
    },
    python_requires=">=3.8",
)
