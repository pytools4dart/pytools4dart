#### install DART ####
$prefix = $env:cachedir
echo "cache directory: $prefix"

$dartname = "DART_5-7-6_2020-03-06_v1150_windows64"
$dartzip = "$prefix\$dartname.zip"
$dartdir = "$prefix\$dartname"
$darturl = "https://dart.omp.eu/membre/downloadDart/contenu/DART/Windows/64bits/$dartname.zip"

if(!(Test-Path $prefix -PathType Container)) {
    mkdir $prefix
}


if(!(Test-Path $dartdir -PathType Container)) {
    curl.exe -C - $darturl -o $dartzip # 8min to download from gitlab.com, <1min to pack/upload cache...
    tar.exe -xf $dartzip -C $prefix
    # python -c "from dart_install_win import install_dart; install_dart(r'$dartdir', r'$dartdir', mode='mv')"
    Write-Host "Cache content:"
    ls $prefix
    Write-Host "dart content:"
    ls $dartdir
}



