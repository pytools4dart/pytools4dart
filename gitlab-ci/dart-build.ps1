#### install DART ####
$prefix = $env:cachedir
echo "cache directory: $prefix"

$dartname = "DART_5-7-6_2020-03-06_v1150_windows64"
$dartzip = "$prefix\$dartname.zip"
$dartdir = "$prefix\$dartname"
$darturl = "https://dart.omp.eu/membre/downloadDart/contenu/DART/Windows/64bits/$dartname.zip"

if(!(Test-Path $dartdir -PathType Container)) {
    curl.exe -C - $darturl -o $dartzip
    # tar.exe -xf $dartzip -C $prefix
    # python -c "from dart_install_win import install_dart; install_dart(r'$dartdir', r'$dartdir', mode='mv')"
    # ls $dartdir
}



