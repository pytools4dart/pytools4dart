# If a previous version of ana/miniconda is already there, remove it.
# Remove the conda section of C:\Users\your_user\Documents\WindowsPowerShell\profile.ps1 if it exists.

$projectdir = pwd
echo "$projectdir"
$cache = "$projectdir\cache"
echo "$cache"
$condaurl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
$condaexe = "$cache\Miniconda3-latest-Windows-x86_64.exe"
$condadir = "$cache\miniconda3"

if(!(Test-Path $cache -PathType Container)) {
	mkdir $cache
}

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
	conda install -y -c conda-forge cython gdal geopandas git ipython libspatialindex lxml matplotlib
	conda install -y -c conda-forge lmfit plyfile pybind11 pyjnius pytest
	conda install -y -c conda-forge rasterio rtree scipy
	pip install git+https://gitlab.com/pytools4dart/generateds.git
	pip install git+https://gitlab.com/pytools4dart/tinyobj.git
	pip install git+https://gitlab.com/pytools4dart/gdecomp.git
	pip install git+https://github.com/floriandeboissieu/laspy.git@patch-1
	pip install git+https://github.com/jgomezdans/prosail.git
}else{
	$env:PATH = "$condadir\condabin;" + $env:PATH
	conda init powershell
	invoke-expression -Command "$env:userprofile\Documents\WindowsPowerShell\profile.ps1"
	conda activate ptdvenv
	conda env list
}

# test pytools4dart dependencies
$env:PATH = "$condadir\pkgs\openjdk-11.0.1-1018\Library\bin\server;" + $env:PATH
python -c "import generateDS; import tinyobj; import gdecomp; import laspy; print('ptdvenv setup done...')"


