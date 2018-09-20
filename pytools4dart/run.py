# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <florian.deboissieu@irstea.fr>
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
Module of DART runners, i.e. functions for subprocess calls to DART tools to run
DART simulation, sequence or make color composites image.
See DART_HOME/bin/tools/linux/*.sh or DART_HOME\\bin\\windows\\*.bat for details.
"""
from settings import darttools, getdartdir, getdartenv
import subprocess
import os


def rundart(path, tool, options = []):
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

    Returns
    -------
        True if good
    '''

    dtools = darttools()
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

def full(simu_name):
    '''
    Run full DART simulation, i.e. successively direction, phase, maket and only
    Parameters
    ----------
    simuName: str
        Simulation name or path relative 'user_data/simulations' directory

    Returns
    -------

    '''
    return rundart(simu_name, 'full')

def direction(simu_name):
    '''
    Run DART direction module.
    Parameters
    ----------
    simuName: str
        Simulation name or path relative 'user_data/simulations' directory

    Returns
    -------
        True if good
    '''
    return rundart(simu_name, 'directions')

def phase(simu_name):
    '''
    Run the DART phase module.
    Parameters
    ----------
    simuName: str
        Simulation name or path relative 'user_data/simulations' directory

    Returns
    -------

    '''
    rundart(simu_name, 'phase')

def maket(simu_name):
    '''
    Run the DART maket module.
    Parameters
    ----------
    simuName: str
        Simulation name or path relative 'user_data/simulations' directory

    Returns
    -------

    '''
    rundart(simu_name, 'maket')

def dart(simu_name):
    '''
    Run only DART radiative transfer module,
    with direction, phase and maket computed separately.
    Parameters
    ----------
    simuName: str
        Simulation name or path relative 'user_data/simulations' directory

    Returns
    -------
        True if good
    '''
    return rundart(simu_name, 'only')

def sequence(simu_name, sequence_name, option='-start'):
    '''

    Parameters
    ----------
    sequenceFile: str
        Path of the sequence file relative to 'user_data/simulations', i.e. 'simu_name/sequence_name.xml'
    option: str
        Either:
            * '-start' to start from the begining
            * '-continue' to continue an interupted run

    Returns
    -------
        True if good
    '''
    return rundart(os.path.join(simu_name, sequence_name+'.xml'), 'sequence', [option])

def colorComposite(simu_name, red, green, blue, pngfile):
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

    Returns
    -------
        True if good
    '''
    return rundart(simu_name, 'colorComposite', [red, green, blue, pngfile])

def colorCompositeBands(simu_name, red, green, blue, iteration, outdir):
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


    Returns
    -------
        True if good
    '''
    return rundart(simu_name, 'colorCompositeBands', [red, green, blue, iteration, outdir])


class runners(object):

    def __init__(self, simu):
        self.simu = simu

    def full(self):
        full(self.simu.name)

    def direction(self):
        direction(self.simu.name)

    def phase(self):
        phase(self.simu.name)

    def maket(self):
        maket(self.simu.name)

    def dart(self):
        dart(self.simu.name)

    def sequence(self, sequence_name, option='-start'):
        sequence(self.simu.name, sequence_name, option)

    def colorCompositeBands(self, red, green, blue, iteration, outdir):
        colorCompositeBands(self.simu.name, red, green, blue, iteration, outdir)


