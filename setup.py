#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

test_requirements = ['pytest>=3', ]

setup(
    author="Miaoqi Chu",
    author_email='mqichu@anl.gov',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    entry_points={
        'console_scripts': [
            'xpcs_webplot=xpcs_webplot.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='xpcs_webplot',
    name='xpcs_webplot',
    packages=find_packages(include=['xpcs_webplot', 'xpcs_webplot.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/AZjk/xpcs_webplot',
    version='0.0.1',
    zip_safe=False,
)
