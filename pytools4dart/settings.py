#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <florian.deboissieu@irstea.fr>
# https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
#
# Copyright 2018 Eric Chraibi
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
===============================================================================
This module contains settings functions and others related to dart path such as simulation
absolute paths.
"""
import re
from os.path import join as pjoin
from os.path import expanduser
import os
import platform
import subprocess
import glob
import zipfile

def default_dartdir():
    '''
    Default DART directory
    Returns
    -------
        str : Default DART directory
    '''
    return pjoin(expanduser('~'), 'DART')


def pytools4dartrc():
    '''
    Path of pytools4dart configuration path
    Returns
    -------
        str: path of .pytools4dartrc
    '''
    home = expanduser('~')
    return pjoin(home, '.pytools4dartrc')

def getdartdir(dartdir=None):
    '''
    Get DART default directory or expand and normalize input DART directory
    Parameters
    ----------
    dartdir: str
        path to DART directory, e.g. /home/username/DART

    Returns
    -------
        str: full path to DART directory
    '''
    if not dartdir:
        if os.path.isfile(pytools4dartrc()):
            with open(pytools4dartrc()) as f:
                dartdir = f.read()
        else:
            dartdir = default_dartdir()
    else:
        dartdir = os.path.expanduser(dartdir)

    return dartdir

def configure(dartdir = None):
    '''Configure path to DART directory

    Parameters
    ----------
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\Users\username\DART'

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


def getdartenv(dartdir=None, verbose=False):
    """
    Get DART environment variables from the .dartrc corresponding to
    input DART version.
    Parameters
    ----------
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\Users\username\DART'
    verbose : bool
        Print dictionary

    Returns
    -------
        dict: DART environment variables

    """
    dartdir = getdartdir(dartdir)

    if not checkdartdir(dartdir):
        raise ValueError('Please (re)configure pytools4dart before use.',
                         'Use pytools4dart.configure(dartdir)')

    # Look for config.ini
    with open(pjoin(dartdir, 'config.ini')) as f:
        dartrcpath = f.read()

    # set environmental variables
    if platform.system() == "Windows":
        dartenv = get_dart_env_win(dartrcpath, verbose)
    elif platform.system() == "Linux":
        dartenv = get_dart_env_linux(dartrcpath, verbose)
    else:
        raise ValueError('OS not supported.', 'Supported OS are Linux and Windows')

    return dartenv


def get_dart_env_linux(dartrcpath, verbose = False):
    """
    Linux version of getdartenv, see corresponding doc.
    """
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


def get_dart_env_win(dartrcpath, verbose = False):
    """
    Windows version of getdartenv, see corresponding doc.
    """
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

    return dartenv

def checkdartdir(dartdir = None):
    """
    Configuration checker

    Parameters
    ----------
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\Users\username\DART'


    Returns
    -------
        bool: True if dartdir exist and if config.ini found in directory
    """

    dartdir = getdartdir(dartdir)

    if not os.path.isdir(dartdir):
        print('DART directory not found: ' + dartdir)
        return False

    dartconfig = pjoin(dartdir, 'config.ini')
    if not os.path.isfile(dartconfig):
        print('DART configuration file not found: ' + pjoin(dartconfig))
        return False

    version,_,build = getdartversion(dartdir)
    if version < '5-7-1':
        print('DART version is too old: '+version)
        return False

    return True


def darttools(dartdir=None):
    """
    Get DART tools batch paths
    Parameters
    ----------
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\Users\username\DART'

    Returns
    -------
        dict: path of the different tools
    """
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


def getsimupath(simu_name, dartdir = None):
    """
    Get path of simulation directory
    Parameters
    ----------
    simu_name: str
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\Users\username\DART'

    Returns
    -------
        str: full path of simulation directory
    """
    if not simu_name:
        return None
    return pjoin(getdartenv(dartdir)['DART_LOCAL'], 'simulations', simu_name)


def get_simu_input_path(simu_name, dartdir = None):
    """
    Get path of simulation input directory
    Parameters
    ----------
    simu_name: str
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\Users\username\DART'

    Returns
    -------
        str: full path of simulation input dircetory
    """

    if not simu_name:
        return None

    return pjoin(getdartenv(dartdir)['DART_LOCAL'], 'simulations', simu_name, 'input')


def get_simu_output_path(simu_name, dartdir = None):
    """
    Get path of simulation output directory
    Parameters
    ----------
    simu_name: str
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\Users\username\DART'

    Returns
    -------
        str: full path of simulation input dircetory
    """

    if not simu_name:
        return None

    return pjoin(getdartenv(dartdir)['DART_LOCAL'], 'simulations', simu_name, 'output')


def getdartversion(dartdir=None):
    """
    Get DART version
    Parameters
    ----------
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\Users\username\DART'

    Returns
    -------
        list: with version, release date and build
    """
    dartdir = getdartdir(dartdir)

    versionfile = pjoin(dartdir, 'bin', 'version')

    with open(versionfile)as f:
        versionstr = f.readlines()[0]

    version, releasedate, build = versionstr.rstrip().split('_')

    return version, releasedate, build
