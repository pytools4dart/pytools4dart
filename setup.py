# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
# 
# Florian de Boissieu <florian.deboissieu@irstea.fr>
# Eric Chraibi <eric.chraibi@irstea.fr>
# https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
#
#
# This file is part of the pytools4dart package.
#
# pytools4dart is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
#
# ===============================================================================

from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
import os.path

here = os.path.abspath(os.path.dirname(__file__))

NAME = 'pytools4dart'

# Read the version from the relevant file
# with open(os.path.join(here, 'VERSION'), encoding='utf-8') as f:
#     version = f.readline()
# version = version.rstrip('\n')
about = {}
with open(os.path.join(here, NAME, '_version.py')) as f:
    exec(f.read(), about)

setup(
    name=NAME,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=about['__version__'],

    description="Python API for [DART radiative transfer simulator](http://www.cesbio.ups-tlse.fr/dart/index.php#/)",
    long_description='Python API for [DART radiative transfer simulator](http://www.cesbio.ups-tlse.fr/dart/index.php#/)',

    # Project's main homepage.
    url='https://gitlab.irstea.fr/florian.deboissieu/pytools4dartMTD',

    # Author details
    author='Florian de Boissieu, Eric Chraibi, Dav Ebengo, Claudia Lavalley, Yinjie Wang, Jean-Baptiste Féret',
    author_email='florian.deboissieu@irstea.fr',

    # License
    license='GPLv3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # Project maturity:
        #   2 - Pre-Alpha
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 2 - Pre-Alpha',

        # Execution environment
        'Environment :: Console',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Information Analysis',

        # License
        'License :: OSI Approved :: '
        'GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='DART radiative transfer API',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    # find_packages(exclude=['doc', 'tests', 'scripts', 'examples']),
    packages=find_packages(exclude=['doc', 'tests', 'scripts', 'examples']),

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[],

    # List additional groups of dependencies here (e.g. dev dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    extras_require={},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={}, #'pytools4dart/templates':'templates/plots.xml'
    include_package_data=True,

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[], # ('templates', ['templates/plots.xml'])

    # Where to find tests
    test_suite="tests",

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={},
)
