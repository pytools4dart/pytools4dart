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
# This powershell script installs miniconda3 in C:\Users\your_name\miniconda3 and creates a ptdvenv with python 3.7
# If a previous version of ana/miniconda is already there, remove/uninstall it before executing the script.
# Remove also the conda section of C:\Users\your_user\Documents\WindowsPowerShell\profile.ps1 if it exists.

# In Windows 10, there is a problem reported to activate a conda environment from a powershell session.
# It s duee to execution permission, see https://github.com/conda/conda/issues/8428.
# It can be resolved opening a new powershell session bypassing the execution permission:
# > powershell –ExecutionPolicy Bypass

# Tried to cache in gitlab-ci but to long to download and unpack (5min...), while download of installer and install is ~100s

# For further environment activation in powershell use the following code.
## If the powershell profile is not loaded correctly (i.e. error at powershell start):
# powershell -ExecutionPolicy Bypass
# $env:PATH = "$condadir\condabin;" + $env:PATH  # add conda command to path
### This block is not necessary if powershell profile is already loaded
# conda init powershell  # writes the conda in the profile, not necessary if already done
# invoke-expression -Command "$env:userprofile\Documents\WindowsPowerShell\profile.ps1"  # load the powershell profile
###
# conda activate ptdvenv  # activate ptdvenv
# conda env list  # check that ptdvenv is activated

# change condaexe and condadir
$condaurl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
# Path where miniconda installer will be downloaded
$condaexe = "${env:userprofile}\Miniconda3-latest-Windows-x86_64.exe"
# Path where miniconda will be installed
$condadir = "${env:userprofile}\miniconda3"

echo "Installing Miniconda in: $condadir"
# download miniconda installer
curl.exe -C - $condaurl -o $condaexe
# install miniconda
Start-Process $condaexe -Args "/InstallationType=JustMe /RegisterPython=0 /S /D=$condadir" -wait
# add condabin to path to have `conda` command available
$env:PATH = "$condadir\condabin;" + $env:PATH
# initialize conda: it creates the powershell profile script
conda init powershell
# load the profile for current session: it activates (base) environment
invoke-expression -Command "$env:userprofile\Documents\WindowsPowerShell\profile.ps1"
# create new environment
conda create -y -n ptdvenv -c conda-forge python=3.7 gdal rasterio
# activate the newly created environment
conda activate ptdvenv
# check that it is really activated
conda env list
Write-Host "Which python:"
Get-Command python | fl *
Write-Host "conda directory size: "
Write-Host "Try gdal:"
# python3 -c 'import gdal; print(gdal.VersionInfo())'
python -c 'from osgeo import gdal; print(gdal.VersionInfo())'
Write-Host "gdal works"
(gci $condadir | measure Length -s).sum / 1Mb

# This part takes around 7-8min on gitlab.com windows runner
# Tried to cache in gitlab-ci, re-compressing directory miniconda3 with tar.gz but it takes more than 10min
# Using conda env create -f environment.yml leads to out of memory error...
conda install -y -c conda-forge cython gdal geopandas git ipython libspatialindex lxml matplotlib
conda install -y -c conda-forge lmfit plyfile pybind11 pyjnius pytest
conda install -y -c conda-forge rasterio rtree scipy laspy
Write-Host "Try gdal again:"
# python3 -c 'import gdal; print(gdal.VersionInfo())'
python -c 'from osgeo import gdal; print(gdal.VersionInfo())'
Write-Host "gdal works"
pip install git+https://gitlab.com/pytools4dart/generateds.git
pip install tinyobjloader==2.0.0rc5
pip install git+https://gitlab.com/pytools4dart/gdecomp.git
pip install git+https://github.com/jgomezdans/prosail.git

# install pytools4dart
pip install .

$env:PATH = "$condadir\pkgs\openjdk-11.0.1-1018\Library\bin\server;" + $env:PATH

