
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
    if len(options):
        options = [str(s) for s in options]
    command = [dtools[tool], path] + options
    ok = subprocess.call(command)
    os.chdir(cdir)
    if ok != 0:
        raise Exception('Error in ' + tool + ' : ' + str(ok))

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
    return rundart(simu_name, 'directions', dartdir=dartdir)

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

def maket(simu_name, dartdir=None):
    '''
    Run the DART maket module.
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
    rundart(simu_name, 'maket', dartdir=dartdir)

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

def sequence(simu_name, sequence_name, option='-start', dartdir=None):
    '''

    Parameters
    ----------
    sequenceFile: str
        Path of the sequence file relative to 'user_data/simulations', i.e. 'simu_name/sequence_name.xml'
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
    return rundart(os.path.join(simu_name, sequence_name+'.xml'), 'sequence', [option], dartdir=dartdir)

def colorComposite(simu_name, red, green, blue, pngfile, dartdir=None):
    '''
    Build color composite image

    Parameters
    ----------
    simuName: str
        Simulation name or path relative 'user_data/simulations' directory
    red: str
        Red image file name (full path).
    green: str
        Green image file name (full path).
    blue: str
        Blue image file name (full path).
    pngfile: str
        PNG image file name for output.
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
    iteration: int or str
        Iteration number in [0, 1, 2, ..., X]
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


class runners(object):

    def __init__(self, simu):
        self.simu = simu

    def full(self, dartdir=None):
        full(self.simu.name, dartdir)

    def direction(self, dartdir=None):
        direction(self.simu.name, dartdir)

    def phase(self, dartdir=None):
        phase(self.simu.name, dartdir)

    def maket(self, dartdir=None):
        maket(self.simu.name, dartdir)

    def dart(self, dartdir=None):
        dart(self.simu.name, dartdir)

    def sequence(self, sequence_name, option='-start', dartdir=None):
        sequence(self.simu.name, sequence_name, option, dartdir)

    def colorCompositeBands(self, red, green, blue, iteration, outdir, dartdir=None):
        colorCompositeBands(self.simu.name, red, green, blue, iteration, outdir, dartdir=None)


