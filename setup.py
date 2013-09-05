# -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from pkg_resources import normalize_path
import os
import subprocess
import sys
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
    md = open('README.md').read().encode('utf8')

    long_description = pandoc(md, 'markdown', 'rst').decode('utf8')
except (IOError, OSError):
    print('check that you have installed pandoc properly and that README.md '
          'exists!')
    long_description = description

# if we are running on python 3, enable 2to3 and
# let it use the custom fixers from the custom_fixers
# package.
extra = {}
if sys.version_info >= (3, 0):
    extra.update(
        use_2to3=True,
        use_2to3_fixers=['custom_fixers']
    )


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['nobel/test']
        self.test_suite = True

    def run_tests(self):
        import pytest

        # Purge modules under test from sys.modules. The test loader will
        # re-import them from the build location. Required when 2to3 is used
        # with namespace packages.
        if sys.version_info >= (3,) and \
                getattr(self.distribution, 'use_2to3', False):
            sys.modules.__delitem__('nobel')
            sys.modules.__delitem__('nobel.api')

            ## Run on the build directory for 2to3-built code.
            ei_cmd = self.get_finalized_command("egg_info")
            self.test_args = [normalize_path(ei_cmd.egg_base)]

        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name='nobel',
    version=nobel.__version__,
    url='https://github.com/vibragiel/nobel',
    license='Apache Software License',
    author='Gabriel Rodríguez Alberich',
    tests_require=['pytest', 'mock'],
    test_suite='test',
    cmdclass={'test': PyTest},
    install_requires=['requests>=0.13.3'],
    author_email='gabi@gabi.is',
    description=description,
    long_description=long_description,
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Development Status :: 2 - Pre-Alpha',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    extras_require={},
    **extra
)
