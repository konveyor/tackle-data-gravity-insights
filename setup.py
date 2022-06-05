from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tackle-dgi',
    version='0.1.0',
    url="https://github.com/konveyor/tackle-data-gravity-insights",
    author="IBM",
    description="Konveyor Tackle Data Gravity Insights",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
        'Click>=8.0.4',
        'neomodel>=4.0.8',
        'simple-ddl-parser==0.25.0',
        'PyYAML>=6.0',
        'ipdb>=0.13.9',
        'pandas>=1.4.1',
        'tqdm>=4.63.0'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    extras_require = {
        "dev": [
            "nose==1.3.7",
            "pinocchio==0.4.3",
            "coverage==6.3.2",
            "pylint==2.13",
            "py2neo==2021.2.3",
            "flake8==4.0.1",
            "black==22.3.0",
            "tox==3.24.5"
        ],
    },
    entry_points={
        'console_scripts': [
            'dgi = dgi.cli:cli'
        ],
    },
)
