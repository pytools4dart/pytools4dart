# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
# https://gitlab.com/pytools4dart/pytools4dart
#
# COPYRIGHT:
#
# Copyright 2018-2020 Florian de Boissieu
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


# This script takes around 7-8min on gitlab.com windows runner
# Tried to cache in gitlab-ci, re-compressing directory miniconda3 with tar.gz but it takes more than 10min
# Using conda env create -f environment.yml leads to out of memory error...
conda install -y -c conda-forge cython gdal geopandas git ipython libspatialindex lxml matplotlib
conda install -y -c conda-forge lmfit plyfile pybind11 pyjnius pytest
conda install -y -c conda-forge rasterio rtree scipy
pip install git+https://gitlab.com/pytools4dart/generateds.git
pip install git+https://gitlab.com/pytools4dart/tinyobj.git
pip install git+https://gitlab.com/pytools4dart/gdecomp.git
pip install git+https://github.com/floriandeboissieu/laspy.git@patch-1
pip install git+https://github.com/jgomezdans/prosail.git

# install pytools4dart
pip install .

#### configure DART ####
cd pytools4dart\examples
$env:PATH = "${env:condadir}\pkgs\openjdk-11.0.1-1018\Library\bin\server;" + $env:PATH
python -c "import pytools4dart as ptd; ptd.configure(r'${env:dartdir}')"
cd $env:projectdir
