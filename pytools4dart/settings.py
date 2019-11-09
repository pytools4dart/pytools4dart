# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
# Eric Chavanon <eric.chavanon@cesbio.cnes.fr> : contribution for python 3 compatibility
# https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
#
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
"""
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
import shutil
import zipfile
import pandas as pd
import pytools4dart as ptd
import traceback
import lxml.etree as etree
import sys

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

def configure(dartdir=None):
    """
    Configure path to DART directory

    Parameters
    ----------
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\\Users\\username\\DART'

    Returns
    -------

    """

    if not dartdir:
        dartdir = default_dartdir()

    dartdir = expanduser(dartdir)
    if checkdartdir(dartdir):
        with open(pytools4dartrc(), 'w') as pt4drc:
            pt4drc.write(dartdir)

        print('\n pytools4dart configured with:\nDART = ' + dartdir)
    else:
        print('Please (re)configure.')

    try:
        print('\n\tBuilding pytools4dart core...')
        build_core()
        print('\npytools4dart configured: please restart python.')
    except:
        print(traceback.format_exc())
        raise ValueError('\nCould not manage to configure pytools4dart. Please contact support.')



def getdartenv(dartdir=None, verbose=False):
    """
    Get DART environment variables from the .dartrc corresponding to
    input DART version.
    Parameters
    ----------
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\\Users\\username\\DART'
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
        dartrcpath = f.read().rstrip()

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
        if sys.version_info[0] == 2 :
            (key, _, value) = line.rstrip().partition("=")
        else:
            (key, _, value) = line.decode('unicode_escape').rstrip().partition("=")

        if verbose:
          print("{}={}".format(key, value))

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
            print("{}={}".format(VarName,VarValue))
        dartenv[VarName] = VarValue

    return dartenv

def checkdartdir(dartdir = None):
    """
    Configuration checker

    Parameters
    ----------
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\\Users\\username\\DART'


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

    dartversion = getdartversion(dartdir)
    if dartversion['version'] < '5.7.1':
        print('DART version is too old: '+dartversion['version'])
        return False

    return True


def darttools(dartdir=None):
    """
    Get DART tools batch paths
    Parameters
    ----------
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\\Users\\username\\DART'

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

    darttoolspaths = glob.glob(pjoin(toolsdir, '*.' + bashext))
    dtools = {os.path.splitext(os.path.basename(p))[0].replace('dart-', ''):p for p in darttoolspaths}

    return dtools


def getsimupath(simu_name, dartdir=None):
    """
    Get path of simulation directory
    Parameters
    ----------
    simu_name: str
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\\Users\\username\\DART'

    Returns
    -------
        str: full path of simulation directory
    """
    if not simu_name:
        return None
    return pjoin(getdartenv(dartdir)['DART_LOCAL'], 'simulations', simu_name)


def get_simu_input_path(simu_name, dartdir=None):
    """
    Get path of simulation input directory
    Parameters
    ----------
    simu_name: str
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\\Users\\username\\DART'

    Returns
    -------
        str: full path of simulation input dircetory
    """

    if not simu_name:
        return None

    return pjoin(getdartenv(dartdir)['DART_LOCAL'], 'simulations', simu_name, 'input')


def get_simu_output_path(simu_name, dartdir=None):
    """
    Get path of simulation output directory
    Parameters
    ----------
    simu_name: str
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\\Users\\username\\DART'

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
        e.g. '/home/username/DART' or 'C:\\Users\\username\\DART'

    Returns
    -------
        list: with version, release date and build
    """
    dartdir = getdartdir(dartdir)

    versionfile = pjoin(dartdir, 'bin', 'version')

    with open(versionfile)as f:
        versionstr = f.readlines()[0]

    version, releasedate, build = versionstr.rstrip().split('_')
    version = version.replace('-','.')

    return {'version':version, 'build':build, 'releasedate':releasedate}

def get_xmlfile_version(xmlfile):
    """
    Get DART version and build with which the file was created.
    Parameters
    ----------
    xmlfile: str
        File path to the XML file

    Returns
    -------
        dict

    """
    tree = etree.parse(xmlfile)
    root = tree.getroot()
    if any([a not in root.attrib for a in ['version', 'build']]):
        raise Exception('version or build not found.\n{} might not be DART xml file.'.format(xmlfile))

    return root.attrib

def check_xmlfile_version(xmlfile, dartdir = None):
    """
    Check if version is the same as the
    Parameters
    ----------
    xmlfile
    dartdir

    Returns
    -------

    """
    fversion = get_xmlfile_version(xmlfile)
    dversion = getdartversion(dartdir)
    build_int = int(dversion['build'].replace('v',''))
    fbuild_int = int(fversion['build'].replace('v', ''))

    if dversion['version'] > fversion['version'] : # or build_int > fbuild_int
        raise Exception('Input file created with DART: {fversion} {fbuild}.\n'
                        'Current DART is: {version} {build}.\n'
                        'Upgrade simulation with pytools3dart.run.upgrade before use.'.format(
            fversion = fversion['version'], fbuild = fversion['build'],
            version=dversion['version'], build=dversion['build']
        ))
    elif dversion['version'] < fversion['version'] : # or build_int < fbuild_int
        raise Exception('Input file created with DART: {fversion} {fbuild}.\n'
                        'Current DART is: {version} {build}.\n'
                        'Upgrade DART before continuing.'.format(
            fversion=fversion['version'], fbuild=fversion['build'],
            version=dversion['version'], build=dversion['build']
        ))



def build_core(directory=None):
    if not directory:
        directory = os.path.abspath(ptd.__path__[0])

    templatesDpath = os.path.join(directory,'templates')
    xsdDpath = os.path.join(directory, 'xsdschemas')
    labelsDpath = os.path.join(directory, 'labels')

    # remove templates and xsdschemas directory
    if os.path.exists(templatesDpath):
        print("deleting '{}'".format(templatesDpath))
        for s in os.listdir(templatesDpath):
            os.remove(os.path.join(templatesDpath, s))
        os.rmdir(templatesDpath)

    if os.path.exists(xsdDpath):
        print("deleting '{}'".format(xsdDpath))
        for s in os.listdir(xsdDpath):
            os.remove(os.path.join(xsdDpath, s))
        os.rmdir(xsdDpath)

    if os.path.exists(labelsDpath):
        print("deleting '{}'".format(labelsDpath))
        for s in os.listdir(labelsDpath):
            os.remove(os.path.join(labelsDpath, s))
        os.rmdir(labelsDpath)


    try:
        os.mkdir(templatesDpath)
    except:
        print("Directory ", templatesDpath, " already exists")

    try:
        os.mkdir(xsdDpath)
    except:
        print("Directory ", xsdDpath, " already exists")

    try:
        os.mkdir(labelsDpath)
    except:
        print("Directory ", xsdDpath, " already exists")


    write_templates(templatesDpath)
    write_schemas(xsdDpath)
    write_labels(labelsDpath)
    shutil.copyfile(os.path.join(directory,'sequence.xsd'),os.path.join(xsdDpath, 'sequence.xsd'))
    shutil.copyfile(os.path.join(directory, 'sequence.xml'), os.path.join(templatesDpath, 'sequence.xml'))
    xsdnames = [s.split('.xsd')[0] for s in os.listdir(xsdDpath) if s.endswith('.xsd')]
    
    # change to pytools4dart site-package directory: necessary for user_methods
    cwd = os.getcwd()
    os.chdir(directory)
    ### Commented because not working with windows+conda
    # if platform.system().lower() == 'windows':
    #     generateDS='generateDS.exe' # shebang line not working on certain windows platform...
    # else:
    generateDS = 'generateDS.py'

    for xsdname in xsdnames:
        cmd = ' '.join([sys.executable, generateDS, '-m -f --always-export-default --export="write literal etree"',
                        '-u "{user_methods}"',
                        '-p "create" --post-attrib-setter="update_node(self,self.troot,\'{xsdname}\')"',
                        '--pre-ctor="self.troot=get_gs_troot(\'{xsdname}\',\'{{classname}}\')"',
                        '--post-ctor="update_node(self,self.troot,\'{xsdname}\')"',
                        '--imports="from pytools4dart.core_ui.utils import get_gs_troot, update_node, get_path, findpaths, subpaths, set_nodes"',
                        '-o "{pypath}"',
                        '{xsdpath}']).format(user_methods = 'core_ui.user_methods',
                                                xsdname = xsdname,
                                                 pypath = os.path.join(directory, "core_ui", xsdname+'.py'),
                                                 xsdpath = os.path.join(directory, "xsdschemas", xsdname+'.xsd'))
        print('\n'+cmd+'\n')
        subprocess.run(cmd, shell=True)

    os.chdir(cwd) # get back to original directory

def get_input_file_path(simu_name, filename, dartdir=None):
    """
    Get the absolute file path if exists.
    Parameters
    ----------
    simu_name
    filename
    dartdir

    Returns
    -------
        str

    Notes
    -----
    Below is the order in which DART will search file:
      - filename if absolute path
      - otherwise, first that exists in the following list:
         - input/filename starting from $DART_HOME/user_data/simulations and getting down until root
         - $DART_HOME/user_data/database
         - $DART_HOME/database
    If none of these file is found, first path of the list is returned, i.e. absolute path if it is the case,
    $DART_HOME/user_data/simulations/input/filename otherwise
    """
    if filename is None:
        return

    if os.path.abspath(filename) == filename:
        return filename

    ### DO NOT SEE ORIGINAL OJECTIVE OF THIS BLOCK ###
    # if os.path.basename(filename)==filename:
    #     filelist = []
    # else:
    #     filelist = [filename]
    filelist = []

    # input directories
    # check in input directory recursively until reaches DART simulations directory
    if simu_name is not None:
        base_dir = pjoin(getdartenv(dartdir)['DART_LOCAL'], 'simulations')
        spath = simu_name.split(os.path.sep)
        mainpath = [base_dir] + spath + ['input', filename]
        filelist.append(os.path.sep.join(mainpath))
        for i in range(1, len(spath)):
            ppieces = [base_dir] + spath[:-i] + ['input', filename]
            filelist.append(os.path.sep.join(ppieces))

    # database
    filelist.append(pjoin(getdartdir(dartdir), 'user_data', 'database', filename))
    filelist.append(pjoin(getdartdir(dartdir), 'database', filename))

    for f in filelist:
        if os.path.isfile(f):
            return f

    # if none exists default is first
    return filelist[0]




def get_templates():
    """
    Extract DART xml templates from DARTDocument.jar

    Returns
    -------
        dict

    """
    dartenv = getdartenv()
    jarfile = pjoin(dartenv['DART_HOME'], 'bin',  'DARTDocument.jar')

    with zipfile.ZipFile(jarfile, "r") as j:
        if sys.version_info[0] == 2:
            templates = {s.split('/')[3] : j.read(s) for s in j.namelist()
                              if re.match(r'cesbio/dart/documents/.*/ressources/Template.xml', s)}
        else:
            templates = {s.split('/')[3] : j.read(s).decode('unicode_escape') for s in j.namelist()
                              if re.match(r'cesbio/dart/documents/.*/ressources/Template.xml', s)}

    return templates

def get_schemas():
    """
    Extracts DART xsd schemas from DARTEnv.jar

    Returns
    -------
        dict

    """
    dartenv = getdartenv()
    jarfile = pjoin(dartenv['DART_HOME'], 'bin',  'DARTEnv.jar')

    with zipfile.ZipFile(jarfile, "r") as j:
        if sys.version_info[0] == 2:
            schemas = {os.path.basename(s).replace('.xsd', '') : j.read(s) for s in j.namelist()
                              if re.match(r'schemaXml/.*\.xsd', s)}
        else:
            schemas = {os.path.basename(s).replace('.xsd', ''): j.read(s).decode('unicode_escape') for s in j.namelist()
                       if re.match(r'schemaXml/.*\.xsd', s)}

    return schemas

def get_labels(pat=None, case=False, regex=True, column='dartnode'):
    """
    Extract DART labels and corresponding DART node from DARTIHMSimulationEditor.jar.
    Prefer to use ptd.core_ui.utils.get_labels for rapidty.
    Parameters
    ----------

    pat: str
        Character sequence or regular expression.

        See pandas.Series.str.contains.

    case: bool
        If True, case sensitive.

        See pandas.Series.str.contains.

    regex: bool
        If True, assumes the pat is a regular expression.

        If False, treats the pat as a literal string.

        See pandas.Series.str.contains.

    column: str
        Column name to apply pattern filtering: 'label' or 'dartnode'.

    Returns
    -------
        DataFrame

    Examples
    --------
    # get all nodes finishing with OpticalPropertyLink
    import pytools4dart as ptd
    ptd.core_ui.utils.get_labels('OpticalPropertyLink$')
    """

    dartenv = getdartenv()
    jarfile = pjoin(dartenv['DART_HOME'], 'bin',  'DARTIHMSimulationEditor.jar')
    labelsfile = 'cesbio/dart/ihm/DartSimulationEditor/ressources/DartIhmSimulationLabel_en.properties'
    with zipfile.ZipFile(jarfile, "r") as j:
            labels = j.read(labelsfile).decode('unicode_escape')

    labels = labels.split('\n')

    rx = re.compile(r'^(.+?)\s*=\s*(.*?)\s*$', re.M | re.I)

    labelsdf = pd.DataFrame(
        [rx.findall(line)[0] for line in labels if len(rx.findall(line))],
    columns = ['dartnode', 'label'])

    if pat is not None:
        labelsdf = labelsdf[labelsdf[column].str.contains(pat, case, regex=regex)]

    labelsdf = labelsdf[['label', 'dartnode']]


    return labelsdf

def write_templates(directory):
    xml_templates = get_templates()
    for k, v in xml_templates.items():
        filename=pjoin(os.path.abspath(directory), k+'.xml')
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(v)

def write_schemas(directory):
    """
    Extract DART xsd files and writes them in input directory

    Parameters
    ----------
    directory: str
        Path to write pytools4dart core directory (typically 'pytools4dart/xsdschemas')
    """
    xmlschemas = get_schemas()
    for k, v in xmlschemas.items():
        filename=pjoin(os.path.abspath(directory), k+'.xsd')
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(v)

def write_labels(directory):
    """
    Extract DART xsd files and writes them in input directory

    Parameters
    ----------
    directory: str
        Path to write pytools4dart core directory (typically 'pytools4dart/xsdschemas')
    """
    labels = get_labels()
    labels.to_csv(os.path.join(directory, 'labels.tab'), sep='\t', index=False, encoding='utf-8')

