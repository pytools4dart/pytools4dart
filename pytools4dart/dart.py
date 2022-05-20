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

import tempfile
import os
import re
import platform
from shutil import unpack_archive
# see https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
from distutils.dir_util import copy_tree
from path import Path
import subprocess
from .settings import getdartenv
from .settings import configure as ptdconfig

import zipfile


def _get_install_files(dhome):
    """
    Extracts and returns the content of the DART files necessary for DART installation.
    Parameters
    ----------
    dhome: str
        Path to the unzipped directory of DART archive.

    Returns
    -------
    tuple
        (dartrc, dartLauncher), i.e. the dartrc template and the DART launcher.

    """

    jarfile = dhome / 'Install.jar'

    if platform.system() == 'Windows':
        system = 'windows'
    else:
        system = 'linux'

    with zipfile.ZipFile(jarfile, "r") as j:
        dartrc = j.read(r'rsc/{}/dartrcTemplate'.format(system)).decode()  # 'unicode_escape'
        dartLauncher = j.read(r'rsc/{}/dartLauncher'.format(system)).decode()  # 'unicode_escape'

    return dartrc, dartLauncher


def install(dart_zip, dart_home='~/DART', user_data=None, overwrite=False,
            configure=True, verbose=True):
    """
    Install DART from url or zip/tar.gz archive.
    Parameters
    ----------
    x: str
        URL or path to the downloaded DART archive, e.g. r'~/Downloads/DART_5-7-6_2020-03-06_v1150_linux64.tar.gz'.
    dart_home: str
        Directory where DART will be installed, e.g. r'~/DART'.
    user_data: str
        Path to the directory where user_data will be installed, e.g. '~/user_data'.
        If None, user_data = dart_home / 'user_data'.
    overwrite: bool
        If True, overwrites existing
    verbose: bool

    Notes
    -----
    Use a dart_zip file adapted to your platform, example:
    - for 64bits Linux: 'DART_5-7-6_2020-03-06_v1150_linux64.tar.gz',
    - for 64bits Windows: 'DART_5-7-6_2020-03-06_v1150_windows64.zip'

    The successive operations of installation are the following:
        - create dart_home if it does not exist
        - unpack `dart_zip` archive to `dart_home/dart_unzip`
        - move `dart_home/dart_unzip/dart/*` to `dart_home/`, see below for details.
        - copy `dart_home/dart_unzip/user_data` into `dart_home/user_data`, see below for details.
        - generate DART launcher and DART configuration files
        - remove `dart_home/dart_unzip`

    If the dart_home directory already exists and overwrite=True,
    it will overwrite the directories bin, database, tools, changeLog.html,
    README.txt and uninstall scripts with te new ones.

    If user_data already exists, it will merge new user_data in it,
    i.e. keeping the simulations and databases already there.

    Returns
    -------
    str
        Full path of DART home directory, that can be used in `ptd.configure'.
    """
    # TODO:
    #   - add tempdir for extraction
    #   - see TODO below
    #   - add examples in doc

    # Unwanted cases


    if dart_zip.startswith('https://'):
        with tempfile.TemporaryDirectory(prefix='dart_') as tmpdir:
            dart_zip = _download(dart_zip, tmpdir)
            output = install(dart_zip, dart_home, user_data, overwrite, configure, verbose)
            return output


    #### Paths of files ####
    dart_zip = Path(dart_zip).expanduser()
    dart_home = Path(dart_home).expanduser()

    if user_data is None:
        user_data = dart_home / 'user_data'


    user_data = Path(user_data).expanduser()
    dart_python = dart_home / 'bin/python'

    if verbose:
        print('Installing DART:')
        print('\tsource: ' + dart_zip)
        print('\tDART directory: ' + dart_home)
        print('\tuser_data directory: ' + user_data)

    # create DART directory if does not exist
    if dart_home.exists():
        if not overwrite:
            raise ValueError('Directory {} already exists.\n'
                             'Set overwrite=True to overwrite.'.format(dart_home))
        if dart_home.isfile():
            raise ValueError('{} is a file.\n'
                             'Remove it before trying again.'.format(dart_home))
    else:
        if verbose:
            print('Create directory: {}'.format(dart_home))
        dart_home.mkdir()

    # create user_data directory if does not exist
    if user_data.isdir():
        if not overwrite:
            raise ValueError('Directory {} already exist.\n'
                             'Set overwrite=True to merge new in old.'.format(user_data))
    else:
        if verbose:
            print('Create directory: {}'.format(user_data))
        user_data.mkdir()

    # ### extract DART archive ###
    # if extract_dir is None:
    extract_dir = dart_home

    dart_unzip, version = _extract(dart_zip, extract_dir, verbose)
    # starting from DART v1177, content is compressed in dart_unzip/data.7zv
    data7z = dart_unzip / 'data.7z'
    if data7z.isfile():
        if platform.system() == 'Windows':
            bin7z = dart_unzip / '7za.exe'
        else:
            bin7z = dart_unzip / '7za'
        outdir7z = dart_unzip
        command = [bin7z, 'x', '-o' + outdir7z, data7z]
        if verbose:
            print('Extracting DART files...')
        subprocess.run(' '.join(command), shell=True)

    if platform.system() == 'Windows':
        dart_launcher_file = dart_home / 'dart.bat'
        # TODO: check if underscore in file name
        dartrc_file = 'dartrc_' + version + '.bat'
    else:
        dart_launcher_file = dart_home / 'dart'
        dartrc_file = '.dartrc' + version

    dartrc_file = Path('~').expanduser() / dartrc_file
    config_file = dart_home / 'config.ini'
    if dartrc_file.exists() and not overwrite:
        raise Exception('This DART version is already installed. Set overwrite=True to override.')

    # make raw path for windows so it can be used in re.sub
    # otherwise it is raising an error on escape code \U for paths like C:\Users.
    if platform.system() == 'Windows':
        rdart_home = dart_home.encode('unicode-escape').decode('raw-unicode-escape')
        ruser_data = user_data.encode('unicode-escape').decode('raw-unicode-escape')
        rdart_python = dart_python.encode('unicode-escape').decode('raw-unicode-escape')
    else:
        rdart_home = dart_home
        ruser_data = user_data
        rdart_python = dart_python

    dartrc, dart_launcher = _get_install_files(dart_unzip)
    dartrc = re.sub('DART_HOME=', 'DART_HOME=' + rdart_home, dartrc)
    dartrc = re.sub('DART_LOCAL=', 'DART_LOCAL=' + ruser_data, dartrc)
    dartrc = re.sub('DART_PYTHON_PATH=', 'DART_PYTHON_PATH=' + rdart_python, dartrc)

    ###### move dart files to dart_home ######
    move_files = [dart_unzip / 'dart' / f for f in (dart_unzip / 'dart').listdir()]  # ['bin', 'database', 'tools', 'changeLog.html]
    move_files.append(dart_unzip / 'README.txt')
    if platform.system() == 'Windows':
        move_files.append(dart_unzip / 'uninstall.bat')
    else:
        move_files.append(dart_unzip / 'uninstall.sh')
        move_files.append(dart_unzip / 'uninstall-text.sh')

    for src in move_files:
        dst = dart_home / src.name
        if verbose:
            print(src + '  >  ' + dst)
        if dst.isdir() and overwrite:
            dst.rmtree()
        src.move(dst)

    ##### merge user_data with existing ######
    if verbose and user_data.isdir():
        print('merge ' + (dart_unzip / 'user_data') + '  in  ' + user_data)

    # TODO: try when existing user_data is symlink
    (dart_unzip / 'user_data').copytree(user_data, dirs_exist_ok=True)


    #### Generate configuration files ####
    if verbose:
        print('Generate DART launcher & configuration files:'
              '\n {}\n {}\n {}'.format(dart_launcher_file, dartrc_file, config_file))

    with open(dart_launcher_file, 'w', encoding='utf-8') as f:
        f.write(dart_launcher)
    if platform.system() == 'Windows':
        dart_launcher_file.chmod(0o744)  # set as executable for user

    with open(dartrc_file, 'w', encoding='utf-8') as f:
        f.write(dartrc)

    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(dartrc_file)

    if verbose:
        print('Remove extracted archive: {}'.format(dart_unzip))
    dart_unzip.rmtree()

    if configure:
        ptdconfig(dart_home)

    return dart_home

def update(dart_zip, dart_home=None, verbose=True):
    """
    Update existing DART version

    Parameters
    ----------
    x: str
        URL or path to the downloaded DART archive, e.g. '~/Downloads/DART_5-7-6_2020-03-06_v1150_linux64.tar.gz'.
        See https://dart.omp.eu/index.php#/download .

    dart_home: str
        DART directory to be updated. If None, pytools4dart.getdartenv is used.

    verbose: bool

    Returns
    -------
    str
        Full path of DART home directory, that can be used in `ptd.configure'.

    Notes
    -----
    This function uses `install` with option overwrite=True and getting DART_HOME path from pytools4dart configuration file if not specified.

    Update will overwrite dart_home/bin, dart_home/database and dart_home/tools with those of the new version.

    """
    ## TODO: check version should be made before overwriting, because DART updater only works for upgrade (no downgrade).

    dartenv = getdartenv(dart_home, verbose)

    # DART HOME
    if dart_home is None:
        if verbose:
            print('Getting DART_HOME path from pytools4dart current configuration.')
        if not os.path.isdir(dartenv["DART_HOME"]):
            raise FileNotFoundError('DART_HOME directory no found: '+dartenv["DART_HOME"])
        dart_home = dartenv["DART_HOME"]

    # User data
    if verbose:
        print('Getting DART_LOCAL from DART configuration in {}.'.format(dart_home))

    if not os.path.isdir(dartenv["DART_LOCAL"]):
        raise FileNotFoundError('DART_LOCAL directory (e.g. user_data) no found: '+dartenv["DART_LOCAL"])

    user_data = dartenv["DART_LOCAL"]
    dart_home = install(dart_zip, dart_home, user_data=user_data, overwrite=True, verbose=verbose)
    return dart_home

def _download(url, outdir=None, verbose=False):
    """
    Download DART zip/tar.gz file, see Notes for license.
    Parameters
    ----------
    url: str
        Path to a DART archive (see https://dart.omp.eu/index.php#/getDart)
    outdir: str
        Path to directory.
    system: str
        System platform, i.e. 'Windows' or 'Linux'.
        If None, it is deduced from platform.system().
    nbits: int
        64 or 32 bits in function of OS.
    verbose: bool

    Notes
    -----

    **DART is distributed by Paul Sabatier University.
    It is freely available for research with public funding.
    In order to get a license, you need to register and complete the form at
    https://dart.omp.eu/index.php#/getDart.**


    Returns
    -------
    str
        Path of the downloaded file
    """
    url = Path(url)

    if platform.system() == 'Windows':
        curl = 'curl.exe'
    else:
        curl = 'curl'

    # url_start = 'https://dart.omp.eu/membre/downloadDart/contenu/DART'

    outdir = Path(outdir).expanduser()
    if outdir.isdir():
        output = outdir / url.name

    command = '{curl} -o {output} {url}'.format(curl=curl, output=output, url=url)
    if verbose:
        print(command)

    # If the file is completely downloaded '-C -' will avoiding re-downloading.
    # Otherwise (i.e. partially downloaded) DART server does not support byte range,
    # thus '-C -' leads to an error. Therefore, download will start from beginning (overwriting partial download).
    try:
        if output.isfile() and verbose:
            print('Try to resume downloading on existing file.')
        subprocess.check_call(command + '-C -', shell=True)
    except:
        print('Resuming download went wrong. Restarts download from the beginning.')
        subprocess.check_call(command, shell=True)

    if output.isfile():
        output = output
    else:
        raise Exception('Downloaded file not found: {}'
                        'an error may have occured.'.format(output))

    return output


def _extract(dart_zip, extract_dir=None, verbose=False):
    """
    Extract DART archive in directory extract_dir.
    Parameters
    ----------
    dart_zip: str
        Path to DART archive.
    extract_dir: str
        Path where the archive will be unpacked.
    verbose: bool

    Returns
    -------
    (Path, str)
        (dart_unzip, version): unpacked DART directory and DART version

    """
    if extract_dir is None:
        extract_dir = dart_zip.parent

    if platform.system() == 'Windows':
        import zipfile
        with zipfile.ZipFile(dart_zip, "r") as j:
            outname = j.namelist()[0].replace('/', '')
    else:
        import tarfile
        with tarfile.open(dart_zip, "r") as j:
            outname = j.next().path

    dart_unzip = extract_dir / outname

    if dart_unzip.exists():
        raise Exception('Directory already exist: {}'
                        'Remove it before trying again.'.format(dart_unzip))

    pat = r'^DART_\d+-\d+-\d+_\d+-\d+-\d+_(v\d+)_(?:linux|windows)(?:32|64)$'
    m = re.match(pat, outname)
    if m:
        version = m.groups()[0]
    else:
        raise Exception('Root directory of DART archive does not have the expected format:\n {}\n {}'.format(pat, outname))

    if verbose:
        print('Extracting {} to {}'.format(dart_zip, dart_unzip))

    # if platform.system() == 'Windows': # tar.exe only available since Windows 10 build 17063
    #     cmd = 'tar.exe -xf {dart_zip} -C {dart_unzip}'.format(dart_zip=dart_zip, dart_unzip=dart_unzip)
    # else:
    #     cmd = 'tar -xzf {dart_zip} -C {dart_unzip}'.format(dart_zip=dart_zip, dart_unzip=dart_unzip)
    #
    # ok = subprocess.call(cmd)

    unpack_archive(dart_zip, extract_dir)

    return dart_unzip, version
