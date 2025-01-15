from setuptools import setup, find_packages

setup(

    name = "code-review-assistant",
    packages = find_packages(),
    install_requires=[
        "fastapi>=0.68.1",
        "uvicorn>=0.15.0",
        "python-gitlab>=2.10.1",
        "tensorflow>=2.7.0",
        "transformers>=4.11.3",
        "redis>=4.0.2",
    ]


)