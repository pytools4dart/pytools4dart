gitlab-ci\activate-env.ps1
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
