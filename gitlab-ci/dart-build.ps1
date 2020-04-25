#### install DART ####
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

Remove-Item "$env:cachedir\$dartname" -Recurse

if(!(Test-Path $dartdir -PathType Container)) {
    curl.exe -C - $darturl -o $dartzip # 8min to download from gitlab.com, <1min to pack/upload cache...
    tar.exe -xf $dartzip -C $prefix # 155s=2min35 to unzip, about the same time to pack/upload cache, 4 min to download/unpack cache
    python -c "from dart_install_win import install_dart; install_dart(r'$dartdir', mode='mv')"
    Write-Host "Cache content:"
    ls $prefix
    Write-Host "dart content:"
    ls $dartdir
}



