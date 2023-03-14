from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="tackle-dgi",
    version="1.0.0",
    url="https://github.com/konveyor/tackle-data-gravity-insights",
    author="IBM",
    description="Konveyor Tackle Data Gravity Insights",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
        "Click==8.1.3",
        "neomodel==4.0.10",
        "simple-ddl-parser==0.25.0",
        "PyYAML==6.0",
        "ipdb==0.13.11",
        "pandas==1.5.3",
        "tqdm==4.65.0",
        "rich==13.3.2",
        "rich-click==1.6.1",
        "py2neo==2021.2.3",
        "minerva-cargo==1.1.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    extras_require={
        "dev": [
            "nose==1.3.7",
            "pinocchio==0.4.3",
            "coverage==7.1.0",
            "pylint==2.16.2",
            "py2neo==2021.2.3",
            "flake8==6.0.0",
            "black==23.1.0",
            "tox==3.24.5",
        ],
    },
    entry_points={
        "console_scripts": ["dgi = dgi.cli:cli"],
    },
)
