# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Eric Chraibi <eric.chraibi@irstea.fr>
# Florian de Boissieu <fdeboiss@gmail.com>
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
from helpers.voxreader import voxel
from helpers.hstools import read_ENVI_hdr, get_hdr_bands, get_bands_files, get_wavelengths, stack_dart_bands
from settings import getsimupath, get_simu_input_path, getdartdir
import pytools4dart.run as run
import helpers.dbtools as dbtools

import pytools4dart as ptd
from pytools4dart.helpers.constants import *

from pytools4dart.core import Core
from pytools4dart.scene import Scene
from pytools4dart.checker import Checker
from pytools4dart.add import Add
from pytools4dart.acquisition import Acquisition
from pytools4dart.source import Source
from pytools4dart.update import Update

class simulation(object):
    """Simulation object corresponding to a DART simulation.
    It allows for storing and editing parameters, and running simulation
    xsd_core: contains objects built according to XSD modules specification, access is given through a key which matches with XSDfile name
                if the simulation whose name can be given as parameter exists, xsdobjs_dic is populated with simulation XML files contents
    properties_dict: dictionnary containing "opt_props" and "thermal_props" DataFrames, "opt_props" provides a DataFrame for each opt property type
    bands: DataFrame containing a list of [wvl, dl] couples
    """
    def __init__(self, name = None):
        """
        :param name: The name of the simulation
        """
        self.name = name

        self.core = Core(self)

        self.scene = Scene(self)

        self.acquisition = Acquisition(self)

        self.source = Source(self)

        self.checker = Checker(self)

        self.run = run.runners(self)

        self.add = Add(self)

        self.update = Update(self)

        self.core.update_simu()

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

    def write(self, name = None, overwrite = False):
        """
        Write XSD objects contents on DART XML input files in simulation input directory
        Warning: if name is None, initial simulation input directory is overwritten
        If new simulation name given as parameter already exists, directory is not overwritten and an Exception is raised
        If module dependencies issues are detected, an Exception is raised
        :param name: name of the new(modified) simulation. If None
        """
        check = self.checker.module_dependencies()

        if not name:
            name = self.name

        if check == True:
            if name != None:
                new_simu_path = pjoin(self.getsimusdir(), name)
                if not os.path.isdir(new_simu_path):
                    os.mkdir(new_simu_path)
                    new_inputsimu_path = pjoin(new_simu_path, "input")
                    os.mkdir(new_inputsimu_path)
                elif overwrite == False:
                    raise Exception("ERROR: requested new simulation already exists, files won't be written!")

            for fname, xsdobj in self.core.xsdobjs.iteritems():
                self.write_xml_file(fname, xsdobj, name)
        else:
            raise Exception("ERROR: please correct dependencies issues, no files written")

    def is_tree_txt_file_considered(self):
        return self.core.xsdobjs["trees"].Trees.Trees_1 != None

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
        return self.core.xsdobjs["plots"].Plots.addExtraPlotsTextFile == 1

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

    def write_xml_file(self, fname, obj, name = None):
        xmlstr = etree.tostring(obj.to_etree(), pretty_print=True)
        if name != None:
            new_simu_path = pjoin(self.getsimusdir(),name)
            new_inputsimu_path = pjoin(new_simu_path, "input")
            xml_file_path = pjoin(new_inputsimu_path, fname + ".xml")
        else:
            xml_file_path = pjoin(self.getinputsimupath(), fname + ".xml")
        xml_file = open(xml_file_path, "w")
        xml_file.write(xmlstr)
        xml_file.close()

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
            self.core.xsdobjs["phase"].Phase.DartInputParameters.SpectralIntervals.add_SpectralIntervalsProperties(sp_int_props)
            sp_irr_value = ptd.phase.create_SpectralIrradianceValue()
            self.core.xsdobjs["phase"].Phase.DartInputParameters.nodeIlluminationMode.SpectralIrradiance.add_SpectralIrradianceValue(sp_irr_value)

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


