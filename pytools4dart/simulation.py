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
import xmlwriters as dxml
from tools.voxreader import voxel
from tools.hstools import read_ENVI_hdr, get_hdr_bands, get_bands_files, get_wavelengths, stack_dart_bands
from settings import getsimupath, get_simu_input_path, getdartdir
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

        self.core = Core(self, type, empty)

        self.scene = Scene(self)

        self.sensor = Sensor(self)

        self.source = Source(self)

        self.run = run.Run(self)

        self.add = Add(self)

        self.sequences = []

        self.core.update_simu()

    def __repr__(self):

        description ='\n'.join(
            ["\nSimulation '{}'".format(self.name),
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

    def getsimusdir(self):
        return pjoin(getdartdir(),"user_data","simulations")

    def get_database_dir(self):
        return pjoin(getdartdir(),"database")

    def write(self, overwrite = False):
        """
        Write XSD objects contents on DART XML input files in simulation input directory
        Warning: if name is None, initial simulation input directory is overwritten
        If new simulation name given as parameter already exists, directory is not overwritten and an Exception is raised
        If module dependencies issues are detected, an Exception is raised
        :param name: name of the new(modified) simulation. If None
        """
        # check = self.checker.module_dependencies()
        self.core.update()

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
                # thus this option was further investigated
                shutil.rmtree(inputDpath)
            else:
                raise Exception('Simulation already exists.')

        os.mkdir(inputDpath)

        # write inputs
        modules = self.core.get_modules_names()
        for module in modules:
            file = pjoin(inputDpath, module + '.xml')
            obj = getattr(self.core, module)
            with open(file, 'w') as f:
                obj.export(f, level=0)

        # write sequence
        for s in self.sequences:
            s.write(overwrite=overwrite)

    def stack_bands(self, zenith=0, azimuth=0):
        """Stack bands into an ENVI .bil file

        Parameters
        ----------
        zenith: float
            Zenith viewing angle
        azimuth: float
            Azimuth viewing angle

        Returns
        -------
            str: output file path
        """

        simu_input_dir = self.getinputsimupath()
        simu_output_dir = pjoin(self.getsimupath(), 'output')

        bands = get_bands_files(simu_output_dir, band_sub_dir=pjoin('BRF', 'ITERX', 'IMAGES_DART'))

        band_files=bands.path[(bands.zenith==0) & (bands.azimuth==0)]

        wvl = get_wavelengths(simu_input_dir)

        outputfile = pjoin(simu_output_dir, os.path.basename(band_files.iloc[0]).replace('.mpr','.bil'))

        stack_dart_bands(band_files, outputfile, wavelengths=wvl.wavelength.values, fwhm=wvl.fwhm.values, verbose=True)

        return outputfile

    def is_tree_txt_file_considered(self):
        return self.core.trees.Trees.Trees_1 != None

    def read_dart_txt_file_with_header(self, file_path, sep_str):
        """
        read a dart txt file like with header mark "*"
        :param file_path: file path
        :return: a data frame with file contents and columns matching file header
        """
        if not "/" in file_path:
            file_path = pjoin(self.get_database_dir(),file_path)

        list = []
        f = open(file_path, 'r')
        l = f.readline()
        while l[0] == "*": #skip file comments
            l = f.readline()
        header = l.split("\n")[0]
        for line in f:
            if line != '\n':
                list.append(line.split('\n')[0].split(sep_str))
        f.close()
        return pd.DataFrame.from_records(list, columns=header.split(sep_str))

    def is_plots_txt_file_considered(self):
        return self.core.plots.Plots.addExtraPlotsTextFile == 1

    # def get_multfacts_xmlpaths_dict(self):
    #     """
    #     get multiplicative factors xml nodes paths according to opt property types
    #     :return:dictionnary containing xml paths for each opt property type
    #     """
    #     multfacts_xmlpaths_dict = {}
    #     multfacts_xmlpaths_dict["vegetation"] = "understoryNodeMultiplicativeFactorForLUT.understoryMultiplicativeFactorForLUT"
    #     multfacts_xmlpaths_dict["fluid"] = "AirFunctionNodeMultiplicativeFactorForLut.AirFunctionMultiplicativeFactorForLut"
    #     multfacts_xmlpaths_dict["lambertian"] = "lambertianNodeMultiplicativeFactorForLUT.lambertianMultiplicativeFactorForLUT"
    #     multfacts_xmlpaths_dict["hapke"] = "hapkeNodeMultiplicativeFactorForLUT.hapkeMultiplicativeFactorForLUT"
    #     multfacts_xmlpaths_dict["rpv"] = "RPVNodeMultiplicativeFactorForLUT.RPVMultiplicativeFactorForLUT"
    #     return multfacts_xmlpaths_dict

    def get_opt_props_xmlpaths_dict(self):
        """
        get optical properties lists xml nodes paths according to opt property types
        :return: dictionnary containing xml paths for each opt property type
        """
        opt_props_xmlpaths_dict = {}
        opt_props_xmlpaths_dict["vegetation"] = "UnderstoryMultiFunctions.UnderstoryMulti"
        opt_props_xmlpaths_dict["fluid"] = "AirMultiFunctions.AirFunction"
        opt_props_xmlpaths_dict["lambertian"] = "LambertianMultiFunctions.LambertianMulti"
        opt_props_xmlpaths_dict["hapke"] = "HapkeSpecularMultiFunctions.HapkeSpecularMulti"
        opt_props_xmlpaths_dict["rpv"] = "RPVMultiFunctions.RPVMulti"
        return opt_props_xmlpaths_dict

    def add_sp_bands(self, spbands_list):
        """
        add spectral intervals defined by (mean_lambda, fwhm)
        no check of sp_bands unicity is made (as in DART interface)
        :param spbands_list:
        :return:
        """
        #phase module modification
        for sp_band in spbands_list:
            sp_int_props = ptd.phase.create_SpectralIntervalsProperties(meanLambda=sp_band[0], deltaLambda=sp_band[1])
            self.core.phase.Phase.DartInputParameters.SpectralIntervals.add_SpectralIntervalsProperties(sp_int_props)
            sp_irr_value = ptd.phase.create_SpectralIrradianceValue()
            self.core.phase.Phase.DartInputParameters.nodeIlluminationMode.SpectralIrradiance.add_SpectralIrradianceValue(sp_irr_value)

    def get_default_opt_prop(self, opt_prop_type):
        """
        get default optical property (with default attributes) for the opt_prop_type given
        :param opt_prop_type:
        :return:
        """
        opt_prop = None

        opt_props_list = self.get_opt_props_xmlpaths_dict()
        opt_prop_types = opt_props_list.keys()
        if not (opt_prop_type in opt_prop_types):
            raise Exception("optical property type not valid")

        opt_prop = eval('ptd.coeff_diff.create_{}()'.format( opt_props_list[opt_prop_type].split(".")[1] ))

        return opt_prop

    def get_default_th_prop(self):
        return(ptd.coeff_diff.create_ThermalFunction())

    def get_opt_prop_index(self, type, name):
        """
        gets index of optical property given as parameter, using opt_props DataFrame
        :param type: optical proprety type in ["vegetation", "fluid", "lambertian", "hapke", "rpv"]
        :param name: optical property name
        :return: index on DataFrame corresponding to the type, None if property does not exist
        """
        self.core.update_properties_dict()
        index = None
        opt_prop_list = self.scene.properties["opt_props"][type.lower()]
        # For future ue of simu.core.get_optical_properties()
        # df = self.scene.properties["opt_props"]
        # opt_prop_list = df[df.type.str.contains(type, case=False) & (df.ident==name)]


        if opt_prop_list.shape[0] > 0:
            if len(opt_prop_list[opt_prop_list["prop_name"] == name]) > 0: #property exists
                index = opt_prop_list[opt_prop_list["prop_name"] == name].index.tolist()[0]
        return index

    def get_thermal_prop_index(self, th_prop_name):
        """
        gets index of thermal property given as parameter, using thermal_props DataFrame
        :param th_prop_name: thermal property name
        :return: index on th_props DataFrame, None if property does not exist
        """
        self.core.update_properties_dict()
        index = None
        th_prop_list = self.scene.properties["thermal_props"]
        if th_prop_list.shape[0] > 0:
            if len(th_prop_list[th_prop_list["prop_name"] == th_prop_name]) > 0: #property exists
                index = th_prop_list[th_prop_list["prop_name"] == th_prop_name].index.tolist()[0]
        return index

    #ToDo
    #refreshObjFromTables(auto=True) : aimed to be launched automatically after each Table Modification, or manually
    #add_sequence()


