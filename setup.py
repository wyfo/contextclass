from setuptools import find_packages, setup

with open("README.md") as f:
    README = f.read()

setup(
    name="contextclass",
    url="https://github.com/wyfo/contextclass",
    author="Joseph Perez",
    author_email="joperez@hotmail.fr",
    description="Typed class wrapper for context variables",
    long_description=README,
    long_description_content_type="text/markdown",
    version="0.2",
    packages=find_packages(include=["contextclasses"]),
    classifiers=[
        "Programming Language :: Python :: 3.7",
    ],
)
