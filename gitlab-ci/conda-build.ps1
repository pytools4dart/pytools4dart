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

$prefix = $env:userprofile
echo "Installing Miniconda in: $prefix"
$condaurl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
$condaexe = "$prefix\Miniconda3-latest-Windows-x86_64.exe"
$condadir = "$prefix\miniconda3"
$env:condadir = $condadir

# if(!(Test-Path $prefix -PathType Container)) {
#	mkdir $prefix
# }

# install conda if not already installed
# and activate environment
if(!(Test-Path $condadir -PathType Container)) {
	curl.exe -C - $condaurl -o $condaexe
	Start-Process $condaexe -Args "/InstallationType=JustMe /RegisterPython=0 /S /D=$condadir" -wait
	$env:PATH = "$condadir\condabin;" + $env:PATH
	conda init powershell
	invoke-expression -Command "$env:userprofile\Documents\WindowsPowerShell\profile.ps1"
	conda install -y conda-build
	conda create -y -n ptdvenv -c conda-forge python=3.7
	conda activate ptdvenv
	conda env list
	Write-Host "conda directory size: "
	(gci $condadir | measure Length -s).sum / 1Mb
}else{
	$env:PATH = "$condadir\condabin;" + $env:PATH
	conda init powershell
	invoke-expression -Command "$env:userprofile\Documents\WindowsPowerShell\profile.ps1"
	conda activate ptdvenv
	conda env list
}


