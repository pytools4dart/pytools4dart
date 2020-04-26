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
# This powershell script downloads DART and installs it
# The install script is in python, thus it is necessary

# Takes around 180s (3min)
$cache = $env:cachedir # only for dart.zip
echo "Cache directory: $cache"
$prefix = $env:userprofile

$dartname = "DART_5-7-6_2020-03-06_v1150_windows64"

$dartzip = "$cache\$dartname.zip"
$dartdir = "$prefix\$dartname"
$env:dartdir = $dartdir
echo "Dart install directory: $dartdir"
$darturl = "https://dart.omp.eu/membre/downloadDart/contenu/DART/Windows/64bits/$dartname.zip"

if(!(Test-Path $cache -PathType Container)) {
    mkdir $cache
}

if(!(Test-Path $prefix -PathType Container)) {
    mkdir $prefix
}

# Remove-Item "$env:cachedir\$dartname" -Recurse

if(!(Test-Path $dartdir -PathType Container)) {
    curl.exe -C - $darturl -o $dartzip # 8min to download from gitlab.com, <1min to pack/upload cache...
    tar.exe -xf $dartzip -C $prefix # 155s=2min35 to unzip, about the same time to pack/upload cache, 4 min to download/unpack cache
    python -c "from dart_install_win import install_dart; install_dart(r'$dartdir', mode='mv')"
    Write-Host "Cache content:"
    ls $prefix
    Write-Host "dart content:"
    ls $dartdir
}



