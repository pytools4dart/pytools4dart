# If a previous version of ana/miniconda is already there, remove it.
# Remove the conda section of C:\Users\your_user\Documents\WindowsPowerShell\profile.ps1 if it exists.

$cache = "${env:userprofile}\cache"
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
	python -c "import generateDS; import tinyobj; import gdecomp; import laspy"
}else{
	$env:PATH = "$condadir\condabin;" + $env:PATH
	conda init powershell
	invoke-expression -Command "$env:userprofile\Documents\WindowsPowerShell\profile.ps1"
	conda activate ptdvenv
	conda env list
}

pip install .
python -c "import generateDS; import tinyobj; import gdecomp; import laspy; import pytools4dart"

$dartname = "DART_5-7-6_2020-03-06_v1150_windows64"
$dartzip = "$cache\$dartname.zip"
$dartdir = "$cache\$dartname"
$darturl = "https://dart.omp.eu/membre/downloadDart/contenu/DART/Windows/64bits/$dartname.zip"

if(!(Test-Path $dartdir -PathType Container)) {
    curl.exe -C - $darturl -o $dartzip
    tar -xf $dartzip -C $cache
    python -c "from dart_install_win import install_dart; install_dart(r'$dartdir', r'$dartdir', mode='mv')"
    ls $dartdir
}

python -c "import pytools4dart as ptd;ptd.configure(r'$dartdir')"
python use_case_0.py
python use_case_1.py
python use_case_2.py
python use_case_3.py
python use_case_4.py
python use_case_6.py
python use_case_7.py
python use_case_5.py
