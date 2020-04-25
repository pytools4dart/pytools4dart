$condadir = "${env:cachedir}\miniconda3"
$env:PATH = "$condadir\condabin;" + $env:PATH
conda init powershell
invoke-expression -Command "$env:userprofile\Documents\WindowsPowerShell\profile.ps1"
conda activate ptdvenv
conda env list
