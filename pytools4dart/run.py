
from settings import darttools, getdartdir, getdartenv
import subprocess
import os

def rundart(path, tool, options = [], dartdir = None):
    '''

    Parameters
    ----------
    path : str
        Simulation name or path expected to be in 'user_data/simulations' directory
    tool: str
        dart tools: either 'full', 'direction', 'phase', 'maket',
        'only', 'sequence', 'vegetation', 'colorComposite',
        'colorCompositeBands'
    options: list
        DART module options. See batch scripts in DART_HOME/tools/os.
    dartdir: str
        DART home directory, default is taken from pytools4dart configuration
        (see pytools4dart.configure).

    Returns
    -------
        True if good
    '''

    dtools = darttools(dartdir)
    if tool not in dtools.keys():
        raise ValueError('DART tool not found.')

    # simulationName = re.findall(re.compile("^" + ))
    tooldir,toolname = os.path.split(dtools[tool])
    cdir = os.getcwd()
    os.chdir(tooldir)
    command = [dtools[tool], path] + options
    ok = subprocess.call(command)
    os.chdir(cdir)
    if ok != 0:
        raise Exception("Erreur DART run " + str(ok))

    return True



def full(simu_name, dartdir=None):
    '''
    Run full DART simulation, i.e. successively direction, phase, maket and only
    Parameters
    ----------
    simuName: str
        Simulation name or path relative 'user_data/simulations' directory
    dartdir: str
        DART home directory, default is taken from :fun:`~pytools4dart.configuration`
        (see pytools4dart.configure).

    Returns
    -------

    '''
    return rundart(simu_name, 'full', dartdir=dartdir)

def direction(simu_name, dartdir=None):
    '''
    Run DART direction module.
    Parameters
    ----------
    simuName: str
        Simulation name or path relative 'user_data/simulations' directory
    dartdir: str
        DART home directory, default is taken from :fun:`~pytools4dart.configuration`
        (see pytools4dart.configure).

    Returns
    -------
        True if good
    '''
    return rundart(simu_name, 'direction', dartdir=dartdir)

def phase(simu_name, dartdir=None):
    '''
    Run the DART phase module.
    Parameters
    ----------
    simuName: str
        Simulation name or path relative 'user_data/simulations' directory
    dartdir: str
        DART home directory, default is taken from :fun:`~pytools4dart.configuration`
        (see pytools4dart.configure).

    Returns
    -------

    '''
    rundart(simu_name, 'phase', dartdir=dartdir)

def dart(simu_name, dartdir=None):
    '''
    Run only DART radiative transfer module,
    with direction, phase and maket computed separately.
    Parameters
    ----------
    simuName: str
        Simulation name or path relative 'user_data/simulations' directory
    dartdir: str
        DART home directory, default is taken from :fun:`~pytools4dart.configuration`
        (see pytools4dart.configure).

    Returns
    -------
        True if good
    '''
    return rundart(simu_name, 'only', dartdir=dartdir)

def sequence(sequenceFile, option='-start', dartdir=None):
    '''

    Parameters
    ----------
    sequenceFile: str
        Full path of the sequence file
    option: str
        Either:
            * '-start' to start from the begining
            * '-continue' to continue an interupted run
    dartdir: str
        DART home directory, default is taken from :fun:`~pytools4dart.configuration`
        (see pytools4dart.configure).

    Returns
    -------
        True if good
    '''
    return rundart(sequenceFile, 'sequence', [option], dartdir=dartdir)

def colorComposite(simu_name, red, green, blue, pngfile, dartdir=None):
    '''
    Build color composite image

    Parameters
    ----------
    simuName: str
        Simulation name or path relative 'user_data/simulations' directory
    red: int
        Red spectral band number (integer).
    green: int
        Green spectral band number (integer).
    blue: int
        Blue spectral band number (integer).
    pngfile: str
        PNG image file name for output
    dartdir: str
        DART home directory, default is taken from :fun:`~pytools4dart.configuration`
        (see pytools4dart.configure).

    Returns
    -------
        True if good
    '''
    return rundart(simu_name, 'colorComposite', [red, green, blue, pngfile], dartdir=dartdir)

def colorCompositeBands(simu_name, red, green, blue, iteration, outdir, dartdir=None):
    '''
    Build color composite of iteration N

    Parameters
    ----------
    simuName: str
        Simulation name or path expected to be in 'user_data/simulations' directory
    red: int
        Band number.
    green: int
        Band number.
    blue: int
        Band number.
    iteration: int
        Iteration nmuber in [0, 1, 2, ..., X]
    outdir: str
        Folder path for output inside the simulation 'output' folder (created if not exists)
    dartdir: str
        DART home directory, default is taken from :fun:`~pytools4dart.configuration`
        (see pytools4dart.configure).


    Returns
    -------
        True if good
    '''
    return rundart(simu_name, 'colorCompositeBands', [red, green, blue, iteration, outdir], dartdir=dartdir)





