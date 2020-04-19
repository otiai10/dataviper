import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

# with open('requirements.txt') as f:
#     requirements = f.read().splitlines()

setuptools.setup(
    name="dataviper",
    version="0.1.7",
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
    install_requires=[
        'pandas==1.0.3',
        'openpyxl==3.0.3',
        'pymysql==0.9.3',
        'pypyodbc==1.3.4.3',
        'matplotlib-venn==0.11.5',
    ],
    extras_require={
        'tests': [
            'pytest',
            'pytest-cov',
            'flake8',
        ],
        'release': [
            'twine',
        ],
    },
)
