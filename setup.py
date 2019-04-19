#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Set up module for utils
In case time is come to publish, do `python setup.py sdist upload`
"""

import os.path
from setuptools import setup, find_packages

CWD = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(CWD, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

import utils

packages = find_packages(exclude=['contrib', 'docs', 'tests'])  # py module name
package_data = {
    "utils": [
        'web/download_img.js',
        'web/get_elements.js',
        'web/get_everything.js',
        'web/get_xpath.js',
    ]
}
requires = [
    "pipe",
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Topic :: Software Development",
    "Topic :: Software Development :: Libraries :: Python Modules"
]

setup(
    name = 'utils',
    description = 'Generic tools for Python projects',
    version = utils.__version__,

    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = utils.__author__,
    author_email = utils.__author_email__,

    # Look for package directories automatically
    packages = packages,
    package_data = package_data,

    # runtime dependencies
    install_requires = requires,
    url = "https://github.com/righthandabacus",
    license = "BSD",
    classifiers = classifiers,
)
