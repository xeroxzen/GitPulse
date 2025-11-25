from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gitpulse",
    version="0.1.0",
    author="Andile Jaden Mbele",
    author_email="andilembele020@gmail.com",
    description="A tool for analyzing Git repositories and measuring contributions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xeroxzen/GitPulse",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "gitpython>=3.1.40",
        "pygit2>=1.15.0",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "pygments>=2.17.2",
        "click>=8.1.7",
        "rich>=13.7.0",
        "pydantic>=2.6.0",
        "sqlalchemy>=2.0.25",
        "alembic>=1.13.1",
    ],
    entry_points={
        "console_scripts": [
            "gitpulse=gitpulse.cli.main:cli",
        ],
    },
) 