# -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import setup
import os
import subprocess

import nobel

here = os.path.abspath(os.path.dirname(__file__))

def pandoc(source, from_format, to_format):
    # http://osiux.com/html-to-restructured-text-in-python-using-pandoc
    # raises OSError if pandoc is not found!
    p = subprocess.Popen(
        ['pandoc', '--from=' + from_format, '--to=' + to_format],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    return p.communicate(source)[0]

description = "A simple pythonic wrapper for the Nobel Prize API."
try:
    md = open('README.md').read()

    long_description = pandoc(md, 'markdown', 'rst')
except (IOError, OSError):
    print('check that you have installed pandoc properly and that README.md '
          'exists!')
    long_description = description

setup(
    name='nobel',
    version=nobel.__version__,
    url='https://github.com/vibragiel/nobel',
    license='Apache Software License',
    author='Gabriel Rodríguez Alberich',
    tests_require=[],
    install_requires=['requests>=0.13.3'],
    cmdclass={},
    author_email='gabi@gabi.is',
    description=description,
    long_description=long_description,
    packages=['nobel'],
    include_package_data=True,
    platforms='any',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    extras_require={}
)
