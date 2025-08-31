from setuptools import setup, find_packages

setup(
    name="visual-product-matcher",
    version="1.0.0",
    description="Visual Product Matcher API",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "gunicorn==21.2.0"
    ]
)
