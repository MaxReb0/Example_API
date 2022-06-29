from setuptools import find_packages, setup

DEV_REQUIRES = [
    "pytest",
    "pytest-cov",
    "pytest-mock",
    "python-dotenv",
    "requests-mock",
]

setup(
    name="example-api",
    version="0.1.0",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "flask",
        "flask-sqlalchemy",
        "flask-migrate",
        "pydantic"
    ],
    python_requires=">=3.7",
    extras_require={
        "dev": DEV_REQUIRES,
    },
)