import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="dataviper",
    version="0.1.5",
    author="Hiromu Ochiai",
    author_email="otiai10@gmail.com",
    description="A simple Data Quality Assessment Tool based on SQL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/otiai10/dataviper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=requirements,
)
