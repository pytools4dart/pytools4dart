# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
# Eric Chavanon <eric.chavanon@cesbio.cnes.fr> : contribution for python 3 compatibility
# https://gitlab.com/pytools4dart/pytools4dart
#
# COPYRIGHT:
#
# Copyright 2018-2019 Florian de Boissieu
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
from path import Path
import platform
import subprocess
import zipfile
import pandas as pd
import pytools4dart as ptd
import traceback
import lxml.etree as etree
import sys
from packaging.version import Version

def default_dartdir():
    '''
    Default DART directory
    Returns
    -------
        str : Default DART directory
    '''
    return Path('~').expanduser() / 'DART'


def pytools4dartrc():
    '''
    Path of pytools4dart configuration path
    Returns
    -------
        str: path of .pytools4dartrc
    '''
    return Path('~').expanduser() / '.pytools4dartrc'


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
        if pytools4dartrc().is_file():
            with open(pytools4dartrc()) as f:
                dartdir = Path(f.read())
        else:
            dartdir = default_dartdir()
    else:
        dartdir = Path(dartdir).expanduser()

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
    dartdir = Path(dartdir).expanduser()

    if not checkdartdir(dartdir):
        raise IOError('Please (re)configure pytools4dart with a valid DART directory.')

    if sys.version_info[0] == 2:
        with open(pytools4dartrc(), 'w') as pt4drc:
            pt4drc.write(dartdir)
    else:
        with open(pytools4dartrc(), 'w', encoding='utf-8') as pt4drc:
            pt4drc.write(dartdir)
    print('\n Configures pytools4dart with:\nDART = ' + dartdir)

    try:
        print('\n\tBuilding pytools4dart core...')
        build_core()
        headlessdarttools()
        print('\npytools4dart configured with:\nDART = ' + dartdir + '\nPlease restart python...')
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
    with open(dartdir / 'config.ini') as f:
        dartrcpath = f.read().rstrip()

    # set environmental variables
    if platform.system() == "Windows":
        dartenv = get_dart_env_win(dartrcpath, verbose)
    elif platform.system() == "Linux":
        dartenv = get_dart_env_linux(dartrcpath, verbose)
    else:
        raise ValueError('OS not supported.', 'Supported OS are Linux and Windows')

    return dartenv


def get_dart_env_linux(dartrcpath, verbose=False):
    """
    Linux version of getdartenv, see corresponding doc.
    """
    command = ['/bin/bash', '-c', 'source ' + dartrcpath + ' && env']

    proc = subprocess.Popen(command, stdout=subprocess.PIPE)

    dartenv = {}
    for line in proc.stdout:
        if sys.version_info[0] == 2:
            (key, _, value) = line.rstrip().partition("=")
        else:
            (key, _, value) = line.decode('unicode_escape').rstrip().partition("=")

        if verbose:
            print("{}={}".format(key, value))

        if key in ('DART_HOME', 'DART_LOCAL'):
            value = Path(value)

        dartenv[key] = value

    return {k: dartenv[k] for k in ('DART_HOME', 'DART_LOCAL', 'DART_JAVA_MAX_MEMORY',
                                    'PATH', 'LD_LIBRARY_PATH')}


def get_dart_env_win(dartrcpath, verbose=False):
    """
    Windows version of getdartenv, see corresponding doc.
    """
    SetEnvPattern = re.compile(r"set (\w+)(?:=)(.*)$", re.MULTILINE)
    with open(dartrcpath) as f:
        SetEnvText = f.read()
    SetEnvMatchList = re.findall(SetEnvPattern, SetEnvText)

    dartenv = {}
    for SetEnvMatch in SetEnvMatchList:
        key = SetEnvMatch[0]
        value = SetEnvMatch[1]
        if verbose:
            print("{}={}".format(key, value))
        
        if key in ('DART_HOME', 'DART_LOCAL'):
            value = Path(value)

        dartenv[key] = value

    return dartenv


def checkdartdir(dartdir=None):
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

    if not dartdir.is_dir():
        print('DART directory not found: ' + dartdir)
        return False

    dartconfig = dartdir / 'config.ini'
    if not dartconfig.is_file():
        print('DART configuration file not found: ' + dartconfig)
        return False

    dartversion = getdartversion(dartdir)
    if Version(dartversion['version']) < Version('5.7.1'):
        print('DART version is too old: ' + dartversion['version'])
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

    toolsdir = dartenv['DART_HOME'] / 'tools' / darttools

    darttoolspaths = toolsdir.glob('*.' + bashext)
    dtools = {p.stem.replace('dart-', ''): p for p in darttoolspaths}
    return dtools


def headlessdarttools(dartdir=None):
    """
    Add flag -Djava.awt.headless=true to DART/tools/linux/*.sh for headless servers
    Parameters
    ----------
    dartdir : str
        Path of the DART directory containing dart executable
        e.g. '/home/username/DART' or 'C:\\Users\\username\\DART'

    Notes
    -----
    All platforms different of windows are considered linux
    """
    currentplatform = platform.system().lower()
    if currentplatform != "windows":
        currentplatform = 'linux'

    dartenv = getdartenv(dartdir)
    toolsdir = dartenv['DART_HOME'] / 'tools' / currentplatform

    ## Headless seems to bring an error in TriangleProcessor at dart-maket.bat execution, leaving scene without OBJ...
    # if currentplatform == 'windows' and os.path.isdir(toolsdir):
    #     toolspath = pjoin(toolsdir, '*.bat')
    #     toolslist = glob.glob(toolspath)
    #     # add -Djava.awt.headless=true, if not already there, to DART/tools/windows/*.bat for headless servers
    #     print('Add flag -Djava.awt.headless=true to {} for headless servers compatibility'.format(
    #         toolspath))
    #     for file in toolslist:
    #         with open(file) as f:
    #             fcont = f.read()
    #         # add -Djava.awt.headless=true if not already there
    #         fcont = re.sub('java.exe"(?!\s+-Djava.awt.headless=true)', 'java.exe" -Djava.awt.headless=true ', fcont)
    #         # remove pause command as it will wait for a key to be pressed
    #         fcont = re.sub('\npause\n', '\n', fcont)
    #         with open(file, 'w') as f:
    #             f.write(fcont)

    if currentplatform == 'linux' and toolsdir.is_dir():
        toolspath = toolsdir / '*.sh'
        # add -Djava.awt.headless=true, if not already there, to DART/tools/linux/*.sh for headless servers
        print('Add flag -Djava.awt.headless=true to {} for headless servers compatibility'.format(
            toolspath))
        cmd = "sed -i '/-Djava.awt.headless=true/! s#$DART_HOME/bin/jre/bin/java#$DART_HOME/bin/jre/bin/java -Djava.awt.headless=true#g' {}".format(
            toolspath)
        subprocess.run(cmd, shell=True)


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
    return getdartenv(dartdir)['DART_LOCAL'] / 'simulations' / simu_name


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

    return getsimupath(simu_name, dartdir) / 'input'


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

    return getsimupath(simu_name, dartdir) / 'output'


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

    versionfile = dartdir / 'bin' / 'version'

    with open(versionfile) as f:
        versionstr = f.readlines()[0]

    version, releasedate, build = versionstr.rstrip().split('_')
    version = version.replace('-', '.')

    return {'version': version, 'build': build, 'releasedate': releasedate}


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


def check_xmlfile_version(xmlfile, dartdir=None):
    """
    Check if the simulation input xml file was created with the same DART version than the one in use.
    Parameters
    ----------
    xmlfile: str
        Simulation input xml file path.
    dartdir: str
        Path to DART root directory. If None, the DART directory configured in pytools4dart is used.

    Returns
    -------

    """
    fversion = get_xmlfile_version(xmlfile)
    dversion = getdartversion(dartdir)
    build_int = int(dversion['build'].replace('v', ''))
    fbuild_int = int(fversion['build'].replace('v', ''))

    if dversion['version'] != fversion['version']:  # or build_int > fbuild_int
        raise Exception('Input file created with DART: {fversion} ({fbuild}).\n'
                        'Current DART is: {version} ({build}).\n\n'
                        'Upgrade simulation to current DART version with "pytools4dart.run.upgrade".'.format(
            fversion=fversion['version'], fbuild=fversion['build'],
            version=dversion['version'], build=dversion['build']
        ))
    elif dversion['version'] < fversion['version']:  # or build_int < fbuild_int
        raise Exception('Input file created with DART: {fversion} {fbuild}.\n'
                        'Current DART is: {version} {build}.\n'
                        'Upgrade DART before continuing.'.format(
            fversion=fversion['version'], fbuild=fversion['build'],
            version=dversion['version'], build=dversion['build']
        ))


def build_core(directory=None):
    if not directory:
        directory = ptd.__path__[0]
    directory = Path(directory)

    templatesDpath = directory / 'templates'
    xsdDpath = directory / 'xsdschemas'
    labelsDpath = directory / 'labels'

    # remove templates and xsdschemas directory
    if templatesDpath.exists():
        print("deleting '{}'".format(templatesDpath))
        templatesDpath.rmtree()

    if xsdDpath.exists():
        print("deleting '{}'".format(xsdDpath))
        xsdDpath.rmtree()

    if labelsDpath.exists():
        print("deleting '{}'".format(labelsDpath))
        labelsDpath.rmtree()

    try:
        templatesDpath.mkdir()
        print('extracting templates to ', templatesDpath)
    except:
        print("Directory ", templatesDpath, " already exists")

    write_templates(templatesDpath)

    try:
        xsdDpath.mkdir()
        print('extracting schemas to ', xsdDpath)
    except:
        print("Directory ", xsdDpath, " already exists")

    write_schemas(xsdDpath)

    try:
        labelsDpath.mkdir()
        print('extracting labels to ', labelsDpath)
    except:
        print("Directory ", labelsDpath, " already exists")

    write_labels(labelsDpath)

    (directory / 'sequence.xsd').copy(xsdDpath)
    (directory / 'sequence.xml').copy(templatesDpath)
    xsdnames = [s.stem for s in xsdDpath.glob('*.xsd')]


    #### Temporary fix for issue #39: load urban simulation ####
    urban_file = xsdDpath / "urban.xsd"
    x = etree.parse(urban_file)
    # fromstring(urban_schema.encode('utf-8'))
    elements = x.xpath(
        '//xsd:element[@name="OpticalPropertyLink" and @minOccurs="4" and @maxOccurs="4"]',
        namespaces={"xsd":"http://www.w3.org/2001/XMLSchema"}
               ) + x.xpath(
        '//xsd:element[@name="ThermalPropertyLink" and @minOccurs="4" and @maxOccurs="4"]',
        namespaces={"xsd":"http://www.w3.org/2001/XMLSchema"}
               )
    
    for e in elements:
        e.attrib['minOccurs'] = '1'
        e.attrib['maxOccurs'] = '5'

    x.write(urban_file, encoding='utf-8', xml_declaration=True, pretty_print=True)
    ###########################################################

    # change to pytools4dart site-package directory: necessary for user_methods
    cwd = Path.cwd()
    directory.chdir()
    ### Commented because not working with windows+conda
    # if platform.system().lower() == 'windows':
    #     generateDS='generateDS.exe' # shebang line not working on certain windows platform...
    # else:
    if platform.system() == "Windows":
        import generateDS
        generateDS_script = ' '.join([sys.executable, generateDS.__file__])  # 'generateDS.py'
    else:
        generateDS_script = 'generateDS.py'

    for xsdname in xsdnames:
        cmd = ' '.join([generateDS_script, '-m -f --always-export-default --export="write literal etree"',
                        '-u "{user_methods}"',
                        '-p "create" --post-attrib-setter="update_node(self,self.troot,\'{xsdname}\')"',
                        '--pre-ctor="self.troot=get_gs_troot(\'{xsdname}\',\'{{classname}}\')"',
                        '--post-ctor="update_node(self,self.troot,\'{xsdname}\')"',
                        '--imports="from pytools4dart.core_ui.utils import get_gs_troot, update_node, get_path, findpaths, subpaths, set_nodes"',
                        '-o "{pypath}"',
                        '{xsdpath}']).format(user_methods=directory / "core_ui" / 'user_methods.py',
                                             xsdname=xsdname,
                                             pypath=directory / "core_ui" / xsdname + '.py',
                                             xsdpath=directory / "xsdschemas" / xsdname + '.xsd')
        # print('\n'+cmd+'\n')
        if sys.version_info[0] == 2:
            subprocess.call(cmd, shell=True)
        else:
            subprocess.run(cmd, shell=True)

    Path.chdir(cwd)  # get back to original directory


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

    Examples
    --------
    >>> import pytools4dart as ptd
    >>> simu = ptd.simulation('test_simu', empty=True)
    >>> simu.get_input_file_path('test.txt')
    >>> simu.get_input_file_path('plots.txt')
    """
    if filename is None:
        return
    filename = Path(filename)
    if filename.absolute() == filename:
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
        base_dir = getdartenv(dartdir)['DART_LOCAL'] / 'simulations'
        spath = Path(simu_name).splitall()
        mainpath = [base_dir] + spath + ['input', filename]
        filelist.append(Path.joinpath(*mainpath))
        for i in range(1, len(spath)):
            ppieces = [base_dir] + spath[:-i] + ['input', filename]
            filelist.append(Path.joinpath(*ppieces))

    # database
    filelist.append(getdartdir(dartdir) / 'user_data' / 'database' / filename)
    filelist.append(getdartdir(dartdir) / 'database' / filename)

    for f in filelist:
        if f.is_file():
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
    jarfile = dartenv['DART_HOME'] / 'bin' / 'DARTDocument.jar'

    with zipfile.ZipFile(jarfile, "r") as j:
        if sys.version_info[0] == 2:
            templates = {s.split('/')[3]: j.read(s) for s in j.namelist()
                         if re.match(r'cesbio/dart/documents/.*/ressources/Template.xml', s)}
        else:
            templates = {s.split('/')[3]: j.read(s).decode('unicode_escape') for s in j.namelist()
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
    jarfile = dartenv['DART_HOME'] / 'bin' / 'DARTEnv.jar'

    with zipfile.ZipFile(jarfile, "r") as j:
        if sys.version_info[0] == 2:
            schemas = {Path(s).stem: clean_documentation(j.read(s)) for s in j.namelist()
                       if re.match(r'schemaXml/.*\.xsd', s)}
        else:
            schemas = {Path(s).stem: clean_documentation(j.read(s).decode('unicode_escape')) for s in j.namelist()
                       if re.match(r'schemaXml/.*\.xsd', s)}


    return schemas

def clean_documentation(content):
    # Use a regular expression to find the content between the <xsd:documentation> and </xsd:documentation> tags.
    pattern = re.compile(r'(<xsd:documentation.*?>)(.*?)(</xsd:documentation>)', re.DOTALL)

    # Function to replace \ in the content between tags
    def replace_backslashes(match):
        start_tag = match.group(1)
        content = match.group(2).replace('\\', '')
        end_tag = match.group(3)
        return f"{start_tag}{content}{end_tag}"

    # Apply the replace function to all occurrences
    return pattern.sub(replace_backslashes, content)

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
    jarfile = dartenv['DART_HOME'] / 'bin' / 'DARTIHMSimulationEditor.jar'
    labelsfile = 'cesbio/dart/ihm/DartSimulationEditor/ressources/DartIhmSimulationLabel_en.properties'
    with zipfile.ZipFile(jarfile, "r") as j:
        labels = j.read(labelsfile).decode('unicode_escape')

    labels = labels.split('\n')

    rx = re.compile(r'^(.+?)\s*=\s*(.*?)\s*$', re.M | re.I)

    labelsdf = pd.DataFrame(
        [rx.findall(line)[0] for line in labels if len(rx.findall(line))],
        columns=['dartnode', 'label'])

    if pat is not None:
        labelsdf = labelsdf[labelsdf[column].str.contains(pat, case, regex=regex)]

    labelsdf['label'] = labelsdf['label'].str.replace(r'\\', '', regex=True)
    labelsdf = labelsdf[['label', 'dartnode']]

    return labelsdf


def write_templates(directory):
    directory = Path(directory)
    xml_templates = get_templates()
    for k, v in xml_templates.items():
        filename = directory.absolute() / k + '.xml'
        if sys.version_info[0] == 2:
            with open(filename, 'w') as f:
                f.write(v)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(v)


def write_schemas(directory):
    """
    Extract DART xsd files and writes them in input directory

    Parameters
    ----------
    directory: str
        Path to write pytools4dart core directory (typically 'pytools4dart/xsdschemas')
    """
    directory = Path(directory)
    xmlschemas = get_schemas()
    for k, v in xmlschemas.items():
        if k not in ['LUT']:  # patch for DART <= v1141
            filename = directory.absolute() / k + '.xsd'
            if sys.version_info[0] == 2:
                with open(filename, 'w') as f:
                    f.write(v)
            else:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(v)


def write_labels(directory):
    """
    Extract DART xsd files and writes them in input directory

    Parameters
    ----------
    directory: str
        Path to write pytools4dart core directory (typically 'pytools4dart/xsdschemas')
    """
    directory = Path(directory)
    labels = get_labels()
    labels.to_csv(directory / 'labels.tab', sep='\t', index=False, encoding='utf-8')
