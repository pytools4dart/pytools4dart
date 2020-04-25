# If a previous version of ana/miniconda is already there, remove it.
# Remove the conda section of C:\Users\your_user\Documents\WindowsPowerShell\profile.ps1 if it exists.

# Tried in gitlab-ci cache directory but to long to download and unpack (5min...), while install is ~2min

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

# test pytools4dart dependencies
# $env:PATH = "$condadir\pkgs\openjdk-11.0.1-1018\Library\bin\server;" + $env:PATH
# python -c "import generateDS; import tinyobj; import gdecomp; import laspy; print('ptdvenv setup done...')"


