import os
from os.path import join
import re
import platform
from shutil import copytree, move
from pathlib import Path

import zipfile

def get_dartrc(dhome):
    jarfile = join(dhome, 'Install.jar')
    os_system = platform.system().lower()
    with zipfile.ZipFile(jarfile, "r") as j:
        dartrc = j.read(r'rsc/{}/dartrcTemplate'.format(os_system)).decode() #'unicode_escape'

    return dartrc

def install_dart(dart_dir, home=None, user_data=None, mode='cp'):

    if home is None:
        home = '~/DART'

    if user_data is None:
        user_data = join(home, 'user_data')

    dart_dir = str(Path(os.path.expanduser(dart_dir)))
    home = str(Path(os.path.expanduser(home)))
    user_data = str(Path(os.path.expanduser(user_data)))
    dart_python = str(Path(join(home, 'bin', 'python')))

    # make raw path for windows so it can be used in re.sub
    # otherwise it is raising an error on escape code \U for paths like C:\Users.
    if platform.system() == 'Windows':
        rhome = home.encode('unicode-escape').decode('raw-unicode-escape')
        ruser_data = user_data.encode('unicode-escape').decode('raw-unicode-escape')
        rdart_python = dart_python.encode('unicode-escape').decode('raw-unicode-escape')
    else:
        rhome = home
        ruser_data = user_data
        rdart_python = dart_python

    dartrc = get_dartrc(dart_dir)

    dartrc = re.sub('DART_HOME=', 'DART_HOME='+rhome, dartrc)
    dartrc = re.sub('DART_LOCAL=', 'DART_LOCAL='+ruser_data, dartrc)
    dartrc = re.sub('DART_PYTHON_PATH=', 'DART_PYTHON_PATH=' + rdart_python, dartrc)


    if os.path.isdir(home):
        raise ValueError('Directory {} already exist.'.format(home))
    else:
        os.mkdir(home)

    if mode is 'mv':
        transfer = move
    elif mode is 'cp':
        transfer = copytree
    elif mode is 'ln':
        transfer = os.symlink
    else:
        raise ValueError('mode {} is not available'.format(mode))

    # copy dart files to home
    if platform.system() == 'Windows':
        # import ctypes
        # kdll = ctypes.windll.LoadLibrary("kernel32.dll")
        for d in ['bin', 'database', 'tools']:
            print('Transfering '+join(dart_dir, 'dart', d))
            print(join(home, d))
            # kdll.CreateSymbolicLinkW(join(dart_dir, 'dart', d), join(home, d), 1)

            transfer(join(dart_dir, 'dart', d), join(home, d))
        # kdll.CreateSymbolicLinkW(join(dart_dir, 'user_data'), user_data, 1)
        transfer(join(dart_dir, 'user_data'), user_data)
    else:
        for d in ['bin', 'database', 'tools']:
            transfer(join(dart_dir, 'dart', d), join(home, d))

        transfer(join(dart_dir, 'user_data'), user_data)



    if platform.system() == 'Windows':
        dartrc_file = 'dartrc_temp.bat'
    else:
        dartrc_file = '.dartrc_temp'

    dartrc_file = join(os.path.expanduser('~'), dartrc_file)

    with open(dartrc_file, 'w', encoding='utf-8') as f:
        f.write(dartrc)

    config_file = join(home, 'config.ini')
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(dartrc_file)


# def download_dart():
