# -*- coding: utf-8 -*-
import re
from os.path import join as pjoin
from os.path import expanduser
import os
import platform
import subprocess
import glob


def default_dartdir():
    '''
    Default DART directory
    Returns
    -------
        str : Default DART directory
    '''
    return pjoin(expanduser('~'), 'DART')


def pytools4dartrc():
    home = expanduser('~')
    return pjoin(home, '.pytools4dartrc')

def getdartdir():
    with open(pytools4dartrc()) as f:
        dartdir = f.read()
    return dartdir

def configure(dartdir = None):
    '''Configure path to DART directory

    Parameters
    ----------
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or '\Users\username\DART'

    Returns
    -------
        None
    '''

    if not dartdir:
        dartdir = default_dartdir()

    dartdir = expanduser(dartdir)
    if checkdartdir(dartdir):
        with open(pytools4dartrc(), 'w') as pt4drc:
            pt4drc.write(dartdir)

        print('\n pytools4dart configured with:\nDART = ' + dartdir)
    else:
        print('Please (re)configure.')


class dartconfig(object):

    def __init__(self):

        self.pt4drc = pytools4dartrc()

        if not os.path.isfile(self.pt4drc):
            raise ValueError('Please (re)configure pytools4dart before use.',
                             'Use pytools4dart.configure(dartdir)')

        self.dartenv = getdartenv()

def getdartenv(dartdir = None):

    if not dartdir:
        dartdir = getdartdir()

    if not checkdartdir(dartdir):
        raise ValueError('Please (re)configure pytools4dart before use.',
                         'Use pytools4dart.configure(dartdir)')

    # Look for config.ini
    with open(pjoin(dartdir, 'config.ini')) as f:
        dartrcpath = f.read()

    # set environmental variables
    if platform.system() == "Windows":
        dartenv = getDartEnvWin(dartrcpath)
    elif platform.system() == "Linux":
        dartenv = getDartEnvLinux(dartrcpath)
    else:
        raise ValueError('OS not supported.', 'Supported OS are Linux and Windows')

    return dartenv

def getDartEnvLinux(dartrcpath, verbose = False):

    command = ['bash', '-c', 'source ' + dartrcpath + ' && env']

    proc = subprocess.Popen(command, stdout = subprocess.PIPE)

    dartenv = {}
    for line in proc.stdout:
      (key, _, value) = line.rstrip().partition("=")
      if verbose:
            print "%s=%s"%(key, value)
      dartenv[key] = value

    return {k: dartenv[k] for k in ('DART_HOME', 'DART_LOCAL', 'DART_JAVA_MAX_MEMORY',
                    'PATH', 'LD_LIBRARY_PATH')}


def getDartEnvWin(dartrcpath, verbose = False):
    SetEnvPattern = re.compile("set (\w+)(?:=)(.*)$", re.MULTILINE)
    with open(dartrcpath) as f:
        SetEnvText = f.read()
    SetEnvMatchList = re.findall(SetEnvPattern, SetEnvText)

    dartenv = {}
    for SetEnvMatch in SetEnvMatchList:
        VarName=SetEnvMatch[0]
        VarValue=SetEnvMatch[1]
        if verbose:
            print "%s=%s"%(VarName,VarValue)
        dartenv[VarName] = VarValue

def checkdartdir(dartdir = None):

    if not dartdir:
        dartdir = default_dartdir()

    if not os.path.isdir(dartdir):
        print('DART directory not found: ' + dartdir)
        return False

    dartconfig = pjoin(dartdir, 'config.ini')
    if not os.path.isfile(dartconfig):
        print('DART configuration file not found: ' + pjoin(dartconfig))
        return False

    return True

def darttools(dartdir = None):
    if not dartdir:
        dartdir = getdartdir()

    dartenv = getdartenv(dartdir)
    currentplatform = platform.system().lower()
    if currentplatform == 'windows':
        darttools = 'windows'
        bashext = 'bat'
    else:
        darttools = 'linux'
        bashext = 'sh'

    toolsdir = pjoin(dartenv['DART_HOME'], 'tools', darttools)

    darttoolspaths = glob.glob(pjoin(toolsdir, 'dart-*.' + bashext))

    darttoolspattern = re.compile("dart-(.*?)." + bashext, re.MULTILINE)
    dtools = {re.findall(darttoolspattern, p)[0] : p
                          for p in darttoolspaths}

    return dtools

def getsimupath(simuName, dartdir = None):

    if not simuName:
        return None

    if not dartdir:
        dartdir = getdartdir()

    return pjoin(getdartenv()['DART_LOCAL'], 'simulations', simuName)

def getdartversion(dartdir=None):

    if not dartdir:
        dartdir = getdartdir()

    versionfile = pjoin(dartdir, 'bin', 'version')

    with open(versionfile)as f:
        versionstr = f.readlines()[0]

    version, releasedate, build = versionstr.rstrip().split('_')

    return version, releasedate, build