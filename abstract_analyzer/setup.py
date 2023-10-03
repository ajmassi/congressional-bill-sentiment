from setuptools import find_packages, setup

setup(
    name="abstract_analyzer",
    version="0.1.0",
    packages=find_packages(include=["abstract_analyzer", "abstract_analyzer.*"]),
    install_requires=["kafka-python", "pydantic", "pydantic_settings"],
)
