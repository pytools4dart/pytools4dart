# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
# Eric Chraibi <eric.chraibi@irstea.fr>
# Claudia Lavalley <claudia.lavalley@cirad.fr>
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
This module contains the class "simulation".
This class corresponds to the python object version of DART configuration XML files contents, according to XSDs schemes provided

The aim of this module is to provide
* simulations reader (from XML files) and writer (to XML files)
* "user friendly" simulation modification methods matching behaviour templates provided by DART team
some summary dataframes (such as plots, lambda, optprops, etc) are associated to each simulation
they are not produced initially, but can be retrieved or modified using getters and setters
the correspondance between those summary dataframes and object modules contents is ensured by method refresh(source)
"""

import os
import glob
from io import StringIO
from os.path import join as pjoin
import pandas as pd
import lxml.etree as etree
import subprocess
import pprint
import numpy as np
import shutil
import warnings
#warnings.warn("deprecated", DeprecationWarning)

# local imports
from tools.voxreader import voxel
from tools.hstools import read_ENVI_hdr, get_hdr_bands, get_bands_files, get_wavelengths, stack_dart_bands
from settings import getsimupath, get_simu_input_path, getdartdir, get_input_file_path
import pytools4dart.run as run
import tools.dbtools as dbtools

import pytools4dart as ptd
from pytools4dart.tools.constants import *

from pytools4dart.core import Core
from pytools4dart.scene import Scene
from pytools4dart.add import Add
from pytools4dart.sensor import Sensor
from pytools4dart.source import Source

class simulation(object):
    """
    Simulation object corresponding to a DART simulation.
    It allows for storing and editing parameters, and running simulation.
    Memebers are:

        - core: objects built according to DART XML files (coeff_diff, directions, phase, ...) each corresponding to a part of DART GUI.
        As in DART GUI, changes propagates automatically to subnodes.
        All available parameters are listed in pytools4dart.core_ui.utils.get_labels() or in the file labels/labels.tab of the package.

        - scene: summary and fast access to the main elements of the mockup scene : size, resolution,
        properties (optical, thermal), plots, object_3d, trees.

        - sensor: summary and fast access to the main element of acquisition: bands, sensors, etc.

        - source: summary and fast access to the main elements of the source definition.

        - sequences: the list of sequences that have been added. Each contains its own core, and adders to add groups and items.

        - add: list of user friendly adders to add elements to scene, acquisition, source and sequence.

        - run: list of available runners, full, step by step, composites, sequences.

    """
    def __init__(self, name=None, method=0, empty=False):
        """

        Parameters
        ----------
        name: str
            simulation name.

            If empty is False and if simulation already exists in DART simulation directory,
            the sismulation is automatically loaded.

        method: int
            simulation methods are:

                - 0: Flux Tracking
                - 1: Monte-Carlo
                - 2: LIDAR

        empty: bool
            New simulation in DART usually comes with a default spectral band.
            If `empty` is True, this band is removed.
        """

        self.name = name

        self.core = Core(self, method, empty)

        self.scene = Scene(self)

        self.sensor = Sensor(self)

        self.source = Source(self)

        self.run = run.Run(self)

        self.add = Add(self)

        self.sequences = []

    def __repr__(self):

        description ='\n'.join(
            ["\nSimulation '{}': {}".format(self.name, self.method),
             '__________________________________',
             'Sensor\n========',
             '{}\n'.format(self.sensor),
             # 'Source\n========',
             # '{}\n'.format(self.source),
             'Scene\n========',
             '{}\n'.format(self.scene),
             'Sequences',
             '=========',
             'number of sequences: {}\n'.format(len(self.sequences)),
             '__________________________________\n'])

        return description

    @property
    def method(self):
        return SIMU_TYPE.type_str[SIMU_TYPE.type_int == self.core.phase.Phase.calculatorMethod].iloc[0]

    def getsimupath(self):
        """
        Get simulation directory path

        Returns
        -------
            str: Simulation full path

        """
        return getsimupath(self.name)

    def getinputsimupath(self):
        """
        Get simulation directory path

        Returns
        -------
            str: Simulation full path

        """
        return get_simu_input_path(self.name)

    def get_input_file_path(self, filename):
        return get_input_file_path(self.name, filename)

    def get_database_dir(self):
        return pjoin(getdartdir(),"database")

    def write(self, overwrite=False, verbose=True):
        """
        Write XSD objects contents on DART XML input files in simulation input directory
        Warning: if name is None, initial simulation input directory is overwritten
        If new simulation name given as parameter already exists, directory is not overwritten and an Exception is raised
        If module dependencies issues are detected, an Exception is raised
        :param name: name of the new(modified) simulation. If None
        """
        # check = self.checker.module_dependencies()
        self.core.update(verbose)

        if self.name is None:
            raise Exception('Simulation name not defined.')

        # create directories
        simuDpath = self.getsimupath()
        # keep all that is in simuDpath
        if not os.path.isdir(simuDpath):
            os.mkdir(simuDpath)

        inputDpath = self.getinputsimupath()
        if os.path.isdir(inputDpath):
            if overwrite: # remove file
                # tempfile was considered however the plots.xml can be large if lots of plots,
                # thus this option wasn't further investigated
                for f in glob.glob(os.path.join(self.getinputsimupath(), '*.xml')):
                    os.remove(f)
            else:
                raise Exception('Simulation already exists.')
        else:
            os.mkdir(inputDpath)

        # write inputs
        modules = self.core.get_modules_names()
        for module in modules:
            file = pjoin(inputDpath, module + '.xml')
            obj = getattr(self.core, module)
            with open(file, 'w') as f:
                obj.export(f, level=0)

        self.scene.plot_file.write(overwrite=overwrite)
        self.scene.tree_file.write(overwrite=overwrite)

        # write sequence
        for s in self.sequences:
            s.write(overwrite=overwrite)


