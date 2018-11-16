# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Eric Chraibi <eric.chraibi@irstea.fr>, Florian de Boissieu <florian.deboissieu@irstea.fr>, Claudia Lavalley <claudia.lavalley@cirad.fr>
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
This module contains the class "simulationXSD".
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

# local imports
import xmlwriters as dxml
from helpers.voxreader import voxel
from helpers.hstools import read_ENVI_hdr, get_hdr_bands, get_bands_files, get_wavelengths, stack_dart_bands
from settings import getsimupath, get_simu_input_path, getdartdir
import pytools4dart.run as run
import helpers.dbtools as dbtools

import pytools4dart as ptd

from pytools4dart.xsdschema.plots import createDartFile
from pytools4dart.xsdschema.phase import createDartFile
from pytools4dart.xsdschema.atmosphere import createDartFile
from pytools4dart.xsdschema.coeff_diff import createDartFile
from pytools4dart.xsdschema.directions import createDartFile
from pytools4dart.xsdschema.object_3d import createDartFile
from pytools4dart.xsdschema.maket import createDartFile
from pytools4dart.xsdschema.inversion import createDartFile
from pytools4dart.xsdschema.LUT import createDartFile
from pytools4dart.xsdschema.lut import createDartFile
from pytools4dart.xsdschema.trees import createDartFile
from pytools4dart.xsdschema.triangleFile import createDartFile
from pytools4dart.xsdschema.water import createDartFile
from pytools4dart.xsdschema.urban import createDartFile


spbands_fields = ['wvl', 'fwhm']
opt_props_fields = ['type', 'op_name', 'db_name', 'op_name_in_db', 'specular']
plot_fields = ['x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 'y4',
               'zmin', 'dz', 'density',
               'densitydef', 'op_name']
opt_prop_types = ["vegetation","fluid","lambertian","hapke","rpv"]

class simulation(object):
    """Simulation object corresponding to a DART simulation.
    It allows for storing and editing parameters, and running simulation
    xsdobjs_dict: contains objects built according to XSD modules specification, access is given through a key which matches with XSDfile name
                if the simulation whose name can be given as parameter exists, xsdobjs_dic is populated with simulation XML files contents
    properties_dict: dictionnary containing "opt_props" and "thermal_props" DataFrames, "opt_props" provides a DataFrame for each opt property type
    spbands_table: DataFrame containing a list of [wvl, dl] couples
    """
    #def __init__(self, name = "test_newSimu_IHM"):
    def __init__(self, name = None):
        """
        :param name: The name of the simulation
        """
        self.name = name

        self.xsdobjs_dict = {} #xsdobjs_dict contains objects built according to XSD modules specification
        modulenames_list = self.get_xmlfile_names(pjoin(os.path.dirname(os.path.realpath(__file__)), "templates"))#["plots", "phase", "atmosphere", "coeff_diff", "directions", "object_3d","maket","inversion","trees","water","urban"]
        for modname in modulenames_list:
            self.xsdobjs_dict[modname] = eval('ptd.xsdschema.{}.createDartFile()'.format(modname))
        for xsdobj in self.xsdobjs_dict.values():
            xsdobj.factory()

        #if the simulation exists, populate xsdobjs_dict with simulation XML files contents
        if name != None and os.path.isdir(self.getsimupath()): # if name != None and dir doesnt exist, create Dir?
            self.read_from_xmls()

        # summary tables:
        self.properties_dict = self.extract_properties_dict() # dictionnary containing "opt_props" and "thermal_props" DataFrames

        self.spbands_table = self.extract_sp_bands_table() # DataFrame containing a list of [wvl, dl] couples

        self.plots_full_table = self.extract_plots_full_table() # DataFrame containing Plots fields according to DART Plot.txt header

        #runners:
        self.runners = run.runners(self)

    def get_xmlfile_names(self, dir_path):
        """
        Provide file names (without xml extension) contained in the directory whose path is given in parameter
        :param dir_path: directory paty
        :return: list of file names
        """
        xml_files_paths_list = glob.glob(pjoin(dir_path,"*.xml"))
        fnames = []
        for xml_file_path in xml_files_paths_list:
            fname = (xml_file_path.split('/')[len(xml_file_path.split('/')) - 1]).split('.xml')[0]
            fnames.append(fname)
        return fnames

    def read_from_xmls(self):
        """
        Populate XSD Objects contained in xsdobjs_dict according to DART XML input files contents
        Update properties, sp_bands and plots tables after population of xsdobjs
        """
        xml_files_paths_list = glob.glob(self.getinputsimupath() + "/*.xml")
        xml_files_paths_dict = {}
        self.xml_root_nodes_dict = {}
        for xml_file_path in xml_files_paths_list:
            fname = (xml_file_path.split('/')[len(xml_file_path.split('/')) - 1]).split('.xml')[0]
            if fname != "triangleFile" and fname != "log": #triangleFile ane log files are created by runners, it is not a normal input DART file, no template exists for this file
                xml_files_paths_dict[fname] = xml_file_path
                with open(xml_file_path, 'r') as f:
                    xml_string = f.read()
                    input_xm_lroot_node = etree.fromstring(xml_string)
                    self.xml_root_nodes_dict[fname] = input_xm_lroot_node

        for fname, xsdobj in self.xsdobjs_dict.iteritems():
            xsdobj.build(self.xml_root_nodes_dict[fname])

        #Following files are not to be read as input files, they are created when running a sequence or by maket DART module

        # if "LUT" in self.xml_root_nodes_dict.keys():
        #     self.xsdobjs_dict["LUT"] = LUTRoot()
        #     self.xsdobjs_dict["LUT"].factory()
        #     self.xsdobjs_dict["LUT"].build(self.xml_root_nodes_dict["LUT"])
        #
        # if "lut" in self.xml_root_nodes_dict.keys():
        #     self.xsdobjs_dict["lut"] = lutRoot()
        #     self.xsdobjs_dict["lut"].factory()
        #     self.xsdobjs_dict["lut"].build(self.xml_root_nodes_dict["lut"])
        #
        # if "triangleFile" in self.xml_root_nodes_dict.keys():
        #     self.xsdobjs_dict["triangleFile"] = TriangleFileRoot()
        #     self.xsdobjs_dict["triangleFile"].factory()
        #     self.xsdobjs_dict["triangleFile"].build(self.xml_root_nodes_dict["triangleFile"])

        self.update_tables_from_objs()
        self.update_properties_dict()

    def update_tables_from_objs(self):
        """
        Updates self.plots_full_table and self.spbands_table variables
        """
        self.plots_full_table = self.extract_plots_full_table()
        self.spbands_table = self.extract_sp_bands_table()

    def extract_sp_bands_table(self):
        """
        Build a DataFrame contaning a list of [wvl,dl] pairs corresponding to spectral bands contained in Phase XSD Object
        :return: DataFrame contaning a list of [wvl,dl] pairs
        """
        spbands_list = self.xsdobjs_dict["phase"].Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties

        rows_to_add = []
        for sp_interval in spbands_list:
            wvl, dl = sp_interval.meanLambda, sp_interval.deltaLambda
            rows_to_add.append([wvl, dl])

        return pd.DataFrame(rows_to_add, columns = spbands_fields)


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

    def writeToXMLFromObj(self, modified_simu_name = None):
        """
        Write XSD objects contents on DART XML input files in simulation input directory
        Warning: if modified_simu_name is None, initial simulation input directory is overwritten
        If new simulation name given as parameter already exists, directory id not overwritten and an ERROR message is printed
        :param modified_simu_name: name of the new(modified) simulation
        """
        check = self.check_module_dependencies()

        if check == True:
            if modified_simu_name != None:
                new_simu_path = pjoin(self.getsimusdir(), modified_simu_name)
                if not os.path.isdir(new_simu_path):
                    os.mkdir(new_simu_path)
                    new_inputsimu_path = pjoin(new_simu_path, "input")
                    os.mkdir(new_inputsimu_path)
                else:
                    print("requested new simulation already exists, files won't be written!")
                    return

            for fname, xsdobj in self.xsdobjs_dict.iteritems():
                self.write_xml_file(fname, xsdobj, modified_simu_name)
        else:
            print("ERROR: please correct dependencies issues, no files written")

    def check_properties_indexes_through_tables(self):
        """
        Cross check properties of every mockup element (plots, scene, object3d, trees) with properties DataFrames.
        Only plots cross check has been implemented, others are coming (Todo cross_check_plots_txt, cross_check_scene_props, cross_check_object3d_props, cross_check_trees_props)
        Att: In the case of plots.txt et trees.txt, we can only check if the given property index does exist
        :return:
        """
        self.update_tables_from_objs()
        check_plots = self.cross_check_plots_props()
        # check_scene = self.cross_check_scene_props(self.properties_dict)
        # check_object3d = self.cross_check_object3d_props(self.properties_dict)
        # check_trees = self.cross_check_trees_props(self.properties_dict) # only if trees.txt is referenced
        return check_plots
        # return check_plots and check_scene and check_object3d and check_trees

    def get_plots_dfs_by_opt_prop_type(self):
        """
        build a dictionnary of dataframes containing plots by optical property type:
            vegetation: PLT_TYPE = vegetation or veg+ground (1,2)
            fluid: PLT_TYPE = fluid (3)
            lambertian: PLT_TYPE = ground or veg+ground (0,2) AND GRD_TYPE = lambertian(GRD_OPT_TYPE = 0)
            hapke: PLT_TYPE = ground or veg+ground (0,2) AND GRD_TYPE = hapke(GRD_OPT_TYPE = 2)
            rpv: PLT_TYPE = ground or veg+ground (0,2) AND GRD_TYPE = rpv(GRD_OPT_TYPE = 4)
        :return: dictionnary containing a dataframe for each optical property type (key)
        """
        plots_full_table = self.plots_full_table

        plots_by_opt_prop_type = {}  # dictionnary of full plot data frames splitted according to opt_prop_type (vegetation, turbid, lamb, hapke, rpv)
        plots_by_opt_prop_type["vegetation"] = plots_full_table[
            plots_full_table['PLT_TYPE'].isin([1, 2])]  # plot type = vegetation or vegetation+ground
        plots_by_opt_prop_type["fluid"] = plots_full_table[plots_full_table['PLT_TYPE'] == 3]  # plot type = fluid
        grd_plots = plots_full_table[
            plots_full_table['PLT_TYPE'].isin([0, 2])]  # plot type = ground or vegetation+ground
        # ground optical property type : 0:lambertian, 1: ??, 2: Hapke, 3: Phase, 4: RPV
        plots_by_opt_prop_type["lambertian"] = grd_plots[
            grd_plots['GRD_OPT_TYPE'] == 0]  # ground optical property type = lambertian
        plots_by_opt_prop_type["hapke"] = grd_plots[
            grd_plots['GRD_OPT_TYPE'] == 2]  # ground optical property type = hapke
        plots_by_opt_prop_type["rpv"] = grd_plots[grd_plots['GRD_OPT_TYPE'] == 4]  # ground optical property type = rpv

        return plots_by_opt_prop_type

    def get_plots_dfs_by_plot_type(self):
        """
        build a dictionnary of dataframes containing plots by plot_type
        2 plot types:
            veg_vegplusground_fluid leading to non empty columns PLT_OPT_NAME, PLT_OPT_NUMB, PLT_THERM_NAME, PLT_THERM_NUMB
            ground leading to non empty columns GRD_OPT_TYPE, GRD_OPT_NAME, GRD_OPT_NUMB, GRD_THERM_NAME, GRD_THERM_NUMB
        :return: dictionnary containing a dataframe for each plot type (key)
        """
        plots_full_table = self.plots_full_table

        plots_by_plot_type = {}  # dictionnary of full plot data frames splitted according to opt_prop_type (vegetation, turbid, lamb, hapke, rpv)
        plots_by_plot_type["veg_vegplusground_fluid"] = plots_full_table[
            plots_full_table['PLT_TYPE'].isin([1, 2, 3])]  # plot type = vegetation or vegetation+ground or fluid
        plots_by_plot_type["ground"] =  plots_full_table[plots_full_table['PLT_TYPE'].isin([0,2])]

        return plots_by_plot_type

    def check_plots_opt_props(self):
        check = True
        opt_props = self.properties_dict["opt_props"]
        plots_dfs_by_opt_prop_type = self.get_plots_dfs_by_opt_prop_type()
        cross_plots_opt_props_dict = {} # join of opt_props_dict and plots/ground optical properties

        #build dictionnary containing joins of opt_props_dict and plots/ground optical properties, for each optical prop type
        for opt_prop_type in opt_props.keys():
            if opt_prop_type in ["vegetation","fluid"]:
                cross_plots_opt_props_dict[opt_prop_type] = pd.merge(opt_props[opt_prop_type], plots_dfs_by_opt_prop_type[opt_prop_type],
                                                                     left_on = ['prop_name'],right_on=['PLT_OPT_NAME'])
            else: #lambertian, hapke, rpv
                cross_plots_opt_props_dict[opt_prop_type] = pd.merge(opt_props[opt_prop_type], plots_dfs_by_opt_prop_type[opt_prop_type],
                                                                     left_on=['prop_name'], right_on=['GRD_OPT_NAME'])

        for opt_prop_type in opt_props.keys():
            plots = plots_dfs_by_opt_prop_type[opt_prop_type]
            cross_props = cross_plots_opt_props_dict[opt_prop_type]

            if len(plots) > len(cross_props): # number of plots is greater than the number of retrieved optical properties (missing plot opt properties)
                check = False
                print("ERROR: missing %d %s optical properties:" % (len(plots) - len(cross_props), opt_prop_type))
                if opt_prop_type in ["vegetation","fluid"]:
                    missing_props = plots[~(plots['PLT_OPT_NAME'].isin(cross_props["prop_name"]))]['PLT_OPT_NAME']
                    for missing_prop in missing_props:
                        print("%s property %s is does not exist, please FIX" % (opt_prop_type,missing_prop))
                else: #opt_prop_type in ["lambertian","hapke","rpv"]
                    missing_props = plots[~(plots['GRD_OPT_NAME'].isin(cross_props["prop_name"]))]['GRD_OPT_NAME']
                    for missing_prop in missing_props:
                        print("%s property %s is does not exist, please FIX" % (opt_prop_type,missing_prop))

            else: # if plots/ground properties DO exist in properties list, check if indexes match
                if opt_prop_type in ["vegetation","fluid"]:
                    eq_serie = cross_props["prop_index"].eq(cross_props["PLT_OPT_NUMB"])
                    if len(eq_serie[eq_serie == False]):
                        print("ERROR: indexes inconsistency, proceed to correction ")# TO Be TESTED!!
                        for i, eq_value in enumerate(eq_serie):
                            if eq_value == False:
                                plot_number = cross_props["PLT_NUMB"]
                                prop_index = cross_props[i]["prop_index"]
                                self.plots_full_table.iloc[plot_number]["PLT_OPT_NUMB"] = prop_index
                                plot = self.xsdobjs_dict["plots"].Plots.Plot[plot_number]
                                if opt_prop_type == "vegetation":
                                    plot.PlotVegetationProperties.VegetationOpticalPropertyLink.indexFctPhase = prop_index
                                else: #if opt_prop_type == "fluid"
                                    plot.PlotAirProperties.AirOpticalProperties[0].AirOpticalPropertyLink.indexFctPhase = prop_index

                else: # opt_prop_type in ["lambertian","hapke","rpv"]
                    eq_serie = cross_props["prop_index"].eq(cross_props["GRD_OPT_NUMB"])
                    if len(eq_serie[eq_serie == False]):
                        print("ERROR: indexes inconsistency, proceed to correction ")# STILL TO Be TESTED!!
                        for i, eq_value in enumerate(eq_serie):
                            if eq_value == False:
                                plot_number = cross_props["PLT_NUMB"]
                                prop_index = cross_props[i]["prop_index"]
                                self.plots_full_table.iloc[plot_number]["GRD_OPT_NUMB"] = prop_index  # correct index in Plots DataFrame
                                #correct index in PlotsObject:
                                plot = self.xsdobjs_dict["plots"].Plots.Plot[plot_number]
                                plot.GroundOpticalPropertyLink.indexFctPhase = prop_index
        return check

    def check_plots_thermal_props(self):

        check = True

        thermal_props = self.properties_dict["thermal_props"]
        cross_plots_therm_props_dict = {}  # jointure of opt_props_dict and plots/ground optical properties

        plot_types = ["veg_vegplusground_fluid","ground"]
        plots_dfs_by_plot_type = self.get_plots_dfs_by_plot_type()

        cross_plots_therm_props_dict["veg_vegplusground_fluid"] = pd.merge(thermal_props, plots_dfs_by_plot_type["veg_vegplusground_fluid"],
                                                               left_on=["prop_name"], right_on=['PLT_THERM_NAME'])
        cross_plots_therm_props_dict["ground"] = pd.merge(thermal_props,plots_dfs_by_plot_type["ground"],
                                                                           left_on=["prop_name"],right_on=['GRD_THERM_NAME'])
        for plot_type in plot_types:
            plots = plots_dfs_by_plot_type[plot_type]
            cross_props = cross_plots_therm_props_dict[plot_type]
            if len(plots) > len(cross_props):
                check = False
                print("ERROR: missing %d %s thermal properties:" % ( len(plots) - len(cross_props), plot_type ) )
                if plot_type == "veg_vegplusground_fluid":
                    missing_props = plots[~(plots['PLT_THERM_NAME'].isin(cross_props["prop_name"]))]['PLT_THERM_NAME']
                    for missing_prop in missing_props:
                        print("%s property %s is does not exist, please FIX" % (plot_type, missing_prop))
                else:  # plot_type == "ground"
                    missing_props = plots[~(plots['GRD_THERM_NAME'].isin(cross_props["prop_name"]))]['GRD_THERM_NAME']
                    for missing_prop in missing_props:
                        print("%s property %s is does not exist, please FIX" % (plot_type, missing_prop))
            else:  # if plots/ground properties do exist in properties list, check if indexes match
                if plot_type == "veg_vegplusground_fluid":
                    eq_serie = cross_props["prop_index"].eq(cross_props["PLT_THERM_NUMB"])
                    if len(eq_serie[eq_serie == False]):
                        print("ERROR: indexes inconsistency, proceed to correction ") # TO Be TESTED!!
                        for i, eq_value in enumerate(eq_serie):
                            if eq_value == False:
                                plot_number = cross_props["PLT_NUMB"]
                                prop_index = cross_props[i]["prop_index"]
                                self.plots_full_table.iloc[plot_number]["PLT_THERM_NUMB"] = prop_index
                                plot = self.xsdobjs_dict["plots"].Plots.Plot[plot_number]
                                plot.PlotVegetationProperties.GroundThermalPropertyLink.indexTemperature = prop_index
                else:  # plot_type == "ground"
                    eq_serie = cross_props["prop_index"].eq(cross_props["GRD_THERM_NUMB"])
                    if len(eq_serie[eq_serie == False]):
                        print("ERROR: indexes inconsistency, proceed to correction ")  # TO Be TESTED!!
                        for i, eq_value in enumerate(eq_serie):
                            if eq_value == False:
                                plot_number = cross_props["PLT_NUMB"]
                                prop_index = cross_props[i]["prop_index"]
                                self.plots_full_table.iloc[plot_number]["GRD_THERM_NUMB"] = prop_index
                                plot = self.xsdobjs_dict["plots"].Plots.Plot[plot_number]
                                plot.GroundThermalPropertyLink.indexTemperature = prop_index
        return check

    def cross_check_plots_props(self):
        """
        Check plots optical/thermal properties consistency
        If property does not exist, an Error message is printed, asking the user to fix
        If property does exist but indexes correspondance is not ensured, this is corrected and a warning message is printed
        ToDo if any plots.txt check if opt/thermal property indexes given in those files are present in properties lists, if not, just Warn the user an let her/him fix
        :return: True if check is ok or if just indexes inconsistency is corrected, False in any other case.
        """
        check_plots_opt_props = self.check_plots_opt_props()
        check_plots_thermal_props = self.check_plots_thermal_props()
        # check plots.txt indexes
        return check_plots_opt_props and check_plots_thermal_props

    def get_thermal_props(self):
        """
        Provides a DataFrame containing thermal properties names and indexes of thermal properties in coeff_diff module
        th_props.id: location of thermal property in the thermal properties list
        :return: DataFrame containing thermal properties names and indexes
        """
        thermal_props_dict = {"prop_index": [], "prop_name": []}
        thermal_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.Temperatures.ThermalFunction
        for i,th_prop in enumerate(thermal_props_list):
            thermal_props_dict["prop_index"].append(i)
            thermal_props_dict["prop_name"].append(th_prop.idTemperature)
        return pd.DataFrame(thermal_props_dict)

    def get_opt_props(self):
        """
        Builds a dictionnary of dataframes, containing optical properties in coeff_diff module, for each opt_property type
        Optical property types are the output dictionnary keys
        Each DataFrame corresponds to each optical property type
        For each optical property, the index and the name in the corresponding opt prop type list are provided
        :return: dictionnary containing, for each optical prop type, a DataFrame containing optical properties names and indexes
        """
        listnodes_paths = []
        opt_props = {}
        opt_props_DF_cols =  ["prop_index", "prop_name"]

        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti) > 0:
            listnodes_paths.append(["vegetation","UnderstoryMultiFunctions.UnderstoryMulti"])
        else:
            opt_props["vegetation"] = pd.DataFrame(columns = opt_props_DF_cols)

        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti) > 0:
            listnodes_paths.append(["lambertian","LambertianMultiFunctions.LambertianMulti"])
        else:
            opt_props["lambertian"] = pd.DataFrame(columns = opt_props_DF_cols)

        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.HapkeSpecularMultiFunctions.HapkeSpecularMulti) > 0:
            listnodes_paths.append(["hapke","HapkeSpecularMultiFunctions.HapkeSpecularMulti"])
        else:
            opt_props["hapke"] = pd.DataFrame(columns=opt_props_DF_cols)

        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.RPVMultiFunctions.RPVMulti) > 0:
            listnodes_paths.append(["rpv","RPVMultiFunctions.RPVMulti"])
        else:
            opt_props["rpv"] = pd.DataFrame(columns=opt_props_DF_cols)

        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.AirMultiFunctions.AirFunction) > 0:
            listnodes_paths.append(["fluid","AirMultiFunctions.AirFunction"])
        else:
            opt_props["fluid"] = pd.DataFrame(columns=opt_props_DF_cols)

        for listnode_path in listnodes_paths:
            props_list = eval('self.xsdobjs_dict["coeff_diff"].Coeff_diff.{}'.format(listnode_path[1]))
            prop_index_list = []
            prop_name_list = []
            for i, prop in enumerate(props_list):
                prop_index_list.append(i)
                prop_name_list.append(prop.ident)
            opt_props[listnode_path[0]] = pd.DataFrame({"prop_index" : prop_index_list, "prop_name" : prop_name_list})

        return opt_props

    def extract_plots_full_table(self):
        """
        extract a DataFrame containing Plots information, directly from plots_obj (self.xdsobjs_dict["plots"])
        for each plot, the fields defined in DART plots.txt file header are provided
        :return: DataFrame containing Plot fields
        """
        #
        # plots_opt_props_dict = {}
        #
        # for field in plots_table_header:
        #     plots_opt_props_dict[field] = []

        rows = []

        plots_list = self.xsdobjs_dict["plots"].Plots.Plot
        for i, plot in enumerate(plots_list):
            plt_btm_hei, plt_hei_mea, plt_std_dev = None, None, None
            veg_density_def, veg_lai, veg_ul = None, None, None

            plt_opt_number, plt_opt_name, plt_therm_number, plt_therm_name = None, None, None, None

            grd_opt_type, grd_opt_number, grd_opt_name, grd_therm_number, grd_therm_name = None, None, None, None, None

            plt_type = plot.type_

            #if plot.form = "corners": else: calculate corners
            points_list = plot.Polygon2D.Point2D
            x1, y1 = points_list[0].x, points_list[0].y
            x2, y2 = points_list[1].x, points_list[1].y
            x3, y3 = points_list[2].x, points_list[2].y
            x4, y4 = points_list[3].x, points_list[3].y

            if plt_type in [1,2,3]:
                opt_prop_node_name = None
                th_prop_node_name = None
                geom_node_name = None

                if plt_type in [1,2]: # vegetation or veg+grd
                    opt_prop_node_name = "PlotVegetationProperties.VegetationOpticalPropertyLink"
                    th_prop_node_name = "PlotVegetationProperties.GroundThermalPropertyLink"
                    geom_node_name = "PlotVegetationProperties.VegetationGeometry"
                elif plt_type == 3:
                    opt_prop_node_name = "PlotAirProperties.AirOpticalProperties[0].AirOpticalPropertyLink"
                    th_prop_node_name = "PlotAirProperties.GroundThermalPropertyLink"
                    geom_node_name = "PlotAirProperties.AirGeometry"

                plt_opt_number = eval('plot.{}.indexFctPhase'.format(opt_prop_node_name))
                plt_opt_name = eval('plot.{}.ident'.format(opt_prop_node_name))
                plt_therm_number = eval('plot.{}.indexTemperature'.format(th_prop_node_name))
                plt_therm_name = eval('plot.{}.idTemperature'.format(th_prop_node_name))

                plt_btm_hei, plt_hei_mea, plt_std_dev = eval('plot.{}.baseheight'.format(geom_node_name)),\
                                                        eval('plot.{}.height'.format(geom_node_name)),\
                                                        eval('plot.{}.stDev'.format(geom_node_name))

            if plt_type in [0, 2]:  # ground or vegetation+ground
                grd_opt_type = plot.GroundOpticalPropertyLink.type_
                grd_opt_number = plot.GroundOpticalPropertyLink.indexFctPhase
                grd_opt_name = plot.GroundOpticalPropertyLink.ident
                grd_therm_number = plot.GroundThermalPropertyLink.indexTemperature
                grd_therm_name = plot.GroundThermalPropertyLink.idTemperature

            row_to_add = [i, plt_type, x1, y1, x2, y2, x3, y3, x4, y4,
                          grd_opt_type, grd_opt_number, grd_opt_name, grd_therm_number, grd_therm_name,
                          plt_opt_number, plt_opt_name, plt_therm_number, plt_therm_name,
                          plt_btm_hei, plt_hei_mea, plt_std_dev, veg_density_def, veg_lai, veg_ul]

            rows.append(row_to_add)


        plots_table_header = ['PLT_NUMBER', 'PLT_TYPE', 'PT_1_X', 'PT_1_Y', 'PT_2_X', 'PT_2_Y', 'PT_3_X', 'PT_3_Y',
                              'PT_4_X',
                              'PT_4_Y',
                              'GRD_OPT_TYPE', 'GRD_OPT_NUMB', 'GRD_OPT_NAME', 'GRD_THERM_NUMB', 'GRD_THERM_NAME',
                              'PLT_OPT_NUMB', 'PLT_OPT_NAME', 'PLT_THERM_NUMB', 'PLT_THERM_NAME',
                              'PLT_BTM_HEI', 'PLT_HEI_MEA', 'PLT_STD_DEV', 'VEG_DENSITY_DEF', 'VEG_LAI', 'VEG_UL']

        return pd.DataFrame(rows, columns=plots_table_header)

    def check_module_dependencies(self):
        """
        Cross check XSD module dependencies:

        * check optical properties names associated to scene objects (plots, soil, object3D, trees(To be done)) exist in optical/thermal properties lists (coeff_diff.xml file) (ToDo: check thermal properties)
        * check if the number of spectral intervals associated to each optical property in coeff_diff
         is equal to the number of spectral bands in phase.xml file

        if optical/thermal property associated to scene object is missing in the optical/thermal property list, a warning is printed, asking the user to fix this inconsistency.

        if spectral band multiplicative factors are missing in coeff_diff.xml file with respect to the number of spectral bands in phase.xml file,
        additional default multiplicative factors are introduced

        :return:    True if every checks are satisfied (even if additional multiplicative factor have been created),
                    False if one or several checks are not satisfied
        """
        print ("checking module dependencies")
        check1 = self.check_and_correct_sp_bands()
        check2 = self.check_properties_indexes_through_tables()
        return (check1 and check2)

    def check_and_correct_sp_bands(self):
        """
        check if the number of number multiplicative factors for each optical property in coeff_diff module
        is equal to the number of spectral bands in phase module

        if spectral band multiplicative factors are missing in coeff_diff module,
        default multiplicative factors are introduced for each missing spectral band

        :return: True if the number of spectral bands in phase XSD module is equal to the number of spectral bandds in each optical property given in coeff_diff XSD module
                      (including if this has been corrected)
                 False otherwise
        """
        phase_spbands_nb = len(self.xsdobjs_dict["phase"].Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties)

        #lambertian opt properties
        min_coeff_spbands_nb = phase_spbands_nb
        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti)>0: # if opt_prop list is non empty
            lamb_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti
            for lamb_prop in lamb_props_list:
                coeff_lamb_spbands = len(lamb_prop.lambertianNodeMultiplicativeFactorForLUT.lambertianMultiplicativeFactorForLUT)
                min_coeff_spbands_nb = min(min_coeff_spbands_nb,coeff_lamb_spbands)

        if min_coeff_spbands_nb < phase_spbands_nb: # if missing multiplicative factors
            print("WARNING: missing multiplicative factor for %s opt prop type" %  "lambertian")
            check_lam =  self.add_lamb_multiplicative_factors_for_lut() #for each property, add missing sp_bands
        else:
            check_lam = True

        #hapke opt properties
        min_coeff_spbands_nb = phase_spbands_nb
        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.HapkeSpecularMultiFunctions.HapkeSpecularMulti)>0:# if opt_prop list is non empty
            hapke_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.HapkeSpecularMultiFunctions.HapkeSpecularMulti
            for hapke_prop in hapke_props_list:
                coeff_hapke_spbands = len(hapke_prop.hapkeNodeMultiplicativeFactorForLUT.hapkeMultiplicativeFactorForLUT)
                min_coeff_spbands_nb = min(min_coeff_spbands_nb, coeff_hapke_spbands)

        if min_coeff_spbands_nb < phase_spbands_nb: # if missing multiplicative factors
            print("WARNING: missing multiplicative factor for %s opt prop type. Correcting..." % "hapke")
            check_hapke = self.add_hapke_multiplicative_factors_for_lut()
        else:
            check_hapke = True

        #rpv opt properties
        min_coeff_spbands_nb = phase_spbands_nb
        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.RPVMultiFunctions.RPVMulti)>0:# if opt_prop list is non empty
            rpv_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.RPVMultiFunctions.RPVMulti
            for rpv_prop in rpv_props_list:
                coeff_rpv_spbands = len(rpv_prop.RPVNodeMultiplicativeFactorForLUT.RPVMultiplicativeFactorForLUT)
                min_coeff_spbands_nb = min(min_coeff_spbands_nb, coeff_rpv_spbands)

        if min_coeff_spbands_nb < phase_spbands_nb: # if missing multiplicative factors
            print("WARNING: missing multiplicative factor for %s opt prop type. Correcting... " % "rpv")
            check_rpv = self.add_rpv_multiplicative_factors_for_lut()
        else:
            check_rpv = True

        #fluid_opt_properties
        min_coeff_spbands_nb = phase_spbands_nb
        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.AirMultiFunctions.AirFunction) > 0:# if opt_prop list is non empty
            air_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.AirMultiFunctions.AirFunction
            for air_prop in air_props_list:
                coeff_air_spbands = len(air_prop.AirFunctionNodeMultiplicativeFactorForLut.AirFunctionMultiplicativeFactorForLut)
                min_coeff_spbands_nb = min(min_coeff_spbands_nb, coeff_air_spbands)

        if min_coeff_spbands_nb < phase_spbands_nb: # if missing multiplicative factors
            print("WARNING: missing multiplicative factor for %s opt prop type. Correcting... " % "air")
            check_air = self.add_air_multiplicative_factors_for_lut()
        else:
            check_air = True

        #understory opt properties
        min_coeff_spbands_nb = phase_spbands_nb
        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti) > 0:# if opt_prop list is non empty
            veg_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti
            for veg_prop in veg_props_list:
                coeff_veg_spbands = len(veg_prop.understoryNodeMultiplicativeFactorForLUT.understoryMultiplicativeFactorForLUT)
                min_coeff_spbands_nb = min(min_coeff_spbands_nb, coeff_veg_spbands)

        if min_coeff_spbands_nb < phase_spbands_nb: # if missing multiplicative factors
            print("WARNING: missing multiplicative factor for %s opt prop type. Correcting... " % "vegetation")
            check_veg = self.add_veg_multiplicative_factors_for_lut()
        else:
            check_veg = True


        #GENERIC try: DOESN'T WORK!! XML object cast problem
        # min_coeff_spbands_nb = {}
        #
        # for opt_prop_type in opt_prop_types:
        #     min_coeff_spbands_nb[opt_prop_type] = phase_spbands_nb
        #
        # listnodes_paths = self.get_list_of_optproplist_nodes()
        # for listnode in listnodes_paths:
        #     prop_list = eval('self.xsdobjs_dict["coeff_diff"].Coeff_diff.{}'.format(listnode[1]))
        #     for prop in prop_list:
        #         coeff_spbands_nb =len(eval('prop.{}'.format(listnode[2])))
        #         min_coeff_spbands_nb[listnode[0]] = min(coeff_spbands_nb , min_coeff_spbands_nb[listnode[0]])
        #
        # listnode_paths_dict_by_optproptype = {}
        # for listnode in listnodes_paths:
        #     listnode_paths_dict_by_optproptype[listnode[0]] = eval('self.xsdobjs_dict["coeff_diff"].Coeff_diff.{}'.format(listnode[1]))
        #
        # for opt_prop_type in opt_prop_types: # this doesn't work!!!
        #     if min_coeff_spbands_nb[opt_prop_type] < phase_spbands_nb:  # if missing multiplicative factors
        #         print("WARNING: %d missing multiplicative factor for %s opt prop type" % (phase_spbands_nb - min_coeff_spbands_nb[opt_prop_type], opt_prop_type) )
        #         for i in range(phase_spbands_nb - min_coeff_spbands_nb[opt_prop_type]):
        #             self.add_optproptype_multiplicative_factor_for_lut(listnode_paths_dict_by_optproptype[opt_prop_type],opt_prop_type)
        #
        # return True


        return check_lam and check_veg and check_air and check_hapke  and check_rpv

    # def add_optproptype_multiplicative_factor_for_lut(self, opt_props_list, opt_prop_type): ### DOESN'T WORK!!!!!
    #     multiplicative_factor_xmlpaths = self.get_multiplicative_factor_xmlpaths_dict()[opt_prop_type]
    #
    #     # add_function_str = '{}.add_{}'.format(multiplicative_factor_xmlpaths.split(".")[0], multiplicative_factor_xmlpaths.split(".")[1])
    #     # create_function_str = '{}.create_{}'.format(multiplicative_factor_xmlpaths.split(".")[0], multiplicative_factor_xmlpaths.split(".")[1])
    #
    #     # lambertianNodeMultiplicativeFactorForLUT.lambertianMultiplicativeFactorForLUT"
    #     for opt_prop in opt_props_list:
    #         eval('opt_prop.{}.add_{}(ptd.coeff_diff.create_{})'.format(multiplicative_factor_xmlpaths.split(".")[0],
    #                                                                    multiplicative_factor_xmlpaths.split(".")[1],
    #                                                                    multiplicative_factor_xmlpaths.split(".")[1]))
    #         # TEST: (ne marche pas non plus)
    #         # opt_prop.lambertianNodeMultiplicativeFactorForLUT.add_lambertianMultiplicativeFactorForLUT(ptd.coeff_diff.create_lambertianMultiplicativeFactorForLUT)

    def add_veg_multiplicative_factors_for_lut(self, phase_spbands_nb):
        """
        add multiplicatif factors for each optical property in coeff_diff module to complete the number of phase sp_bands
        :param phase_spbands_nb: number of spectral bands in phase module
        :return:True if add is ok, False if not
        """
        add_ok = True
        try:
            veg_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti
            for veg_opt_prop in veg_opt_props_list:
                coeff_sp_bands_nb = len(
                    veg_opt_prop.understoryNodeMultiplicativeFactorForLUT.understoryMultiplicativeFactorForLUT)
                if phase_spbands_nb - coeff_sp_bands_nb > 0:
                    print('adding {} multiplicative factors'.format(phase_spbands_nb - coeff_sp_bands_nb))
                    for i in range(phase_spbands_nb - coeff_sp_bands_nb):
                        veg_opt_prop.understoryNodeMultiplicativeFactorForLUT.add_understoryMultiplicativeFactorForLUT(ptd.coeff_diff.create_understoryMultiplicativeFactorForLUT())
        except ValueError:
            print("ERROR: multiplicative factor add failed")
            add_ok = False
        return add_ok

    def add_lamb_multiplicative_factors_for_lut(self):
        """
        add multiplicatif factors for each optical property in coeff_diff module to complete the number of phase sp_bands
        :return: True if add is ok, False if not
        """
        phase_spbands_nb = len(
            self.xsdobjs_dict["phase"].Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties) # nb of sp bands in phase module

        add_ok = True
        try:
            lambertian_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti
            for lamb_opt_prop in lambertian_opt_props_list:
                coeff_sp_bands_nb = len(lamb_opt_prop.lambertianNodeMultiplicativeFactorForLUT.lambertianMultiplicativeFactorForLUT)
                if phase_spbands_nb - coeff_sp_bands_nb > 0:
                    print('adding {} multiplicative factors'.format(phase_spbands_nb - coeff_sp_bands_nb))
                    for i in range(phase_spbands_nb - coeff_sp_bands_nb):
                        lamb_opt_prop.lambertianNodeMultiplicativeFactorForLUT.add_lambertianMultiplicativeFactorForLUT(ptd.coeff_diff.create_lambertianMultiplicativeFactorForLUT())
        except ValueError:
            print("ERROR: multiplicative factor add failed")
            add_ok = False
        return add_ok

    def add_hapke_multiplicative_factors_for_lut(self, phase_spbands_nb):
        """
        add multiplicatif factors for each optical property in coeff_diff module to complete the number of phase sp_bands
        :param phase_spbands_nb: number of spectral bands in phase module
        :return: True if add is ok, False if not
        """
        add_ok = True
        try:
            hapke_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.HapkeSpecularMultiFunctions.HapkeSpecularMulti
            for hapke_opt_prop in hapke_opt_props_list:
                coeff_sp_bands_nb = len(
                    hapke_opt_prop.hapkeNodeMultiplicativeFactorForLUT.hapkeMultiplicativeFactorForLUT)
                if phase_spbands_nb - coeff_sp_bands_nb > 0:
                    print('adding {} multiplicative factors'.format(phase_spbands_nb - coeff_sp_bands_nb))
                    for i in range(phase_spbands_nb - coeff_sp_bands_nb):
                        hapke_opt_prop.hapkeNodeMultiplicativeFactorForLUT.add_hapkeMultiplicativeFactorForLUT(ptd.coeff_diff.create_hapkeMultiplicativeFactorForLUT())
        except ValueError:
            print("ERROR: multiplicative factor add failed")
            add_ok = False
        return add_ok

    def add_rpv_multiplicative_factors_for_lut(self, phase_spbands_nb):
        """
        add multiplicatif factors for each optical property in coeff_diff module to complete the number of phase sp_bands
        :param phase_spbands_nb: number of spectral bands in phase module
        :return: True if add is ok, False if not
        """
        add_ok = True
        try:
            rpv_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.RPVMultiFunctions.RPVMulti
            for rpv_opt_prop in rpv_opt_props_list:
                coeff_sp_bands_nb = len(
                    rpv_opt_prop.RPVNodeMultiplicativeFactorForLUT.RPVMultiplicativeFactorForLUT)
                if phase_spbands_nb - coeff_sp_bands_nb > 0:
                    print('adding {} multiplicative factors'.format(phase_spbands_nb - coeff_sp_bands_nb))
                    for i in range(phase_spbands_nb - coeff_sp_bands_nb):
                        rpv_opt_prop.RPVNodeMultiplicativeFactorForLUT.add_RPVMultiplicativeFactorForLUT(ptd.coeff_diff.create_RPVMultiplicativeFactorForLUT())
        except ValueError:
            print("ERROR: multiplicative factor add failed")
            add_ok = False
        return add_ok

    def add_air_multiplicative_factors_for_lut(self, phase_spbands_nb): # complicate CASE, possible list or AirMultifunctions, ignore for the moment
        """
        add multiplicatif factors for each optical property in coeff_diff module to complete the number of phase sp_bands
        :param phase_spbands_nb: number of spectral bands in phase module
        :return: True if add is ok, False if not
        """
        add_ok = True
        try:
            air_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.AirMultiFunctions.AirFunction
            for air_opt_prop in air_opt_props_list:
                coeff_sp_bands_nb = len(
                    air_opt_prop.AirFunctionNodeMultiplicativeFactorForLut.AirFunctionMultiplicativeFactorForLut)
                if phase_spbands_nb - coeff_sp_bands_nb > 0:
                    print('adding {} multiplicative factors'.format(phase_spbands_nb - coeff_sp_bands_nb))
                    for i in range(phase_spbands_nb - coeff_sp_bands_nb):
                        air_opt_prop.AirFunctionNodeMultiplicativeFactorForLut.add_AirFunctionMultiplicativeFactorForLut(ptd.coeff_diff.create_AirFunctionMultiplicativeFactorForLut())
        except ValueError:
            print("ERROR: multiplicative factor add failed")
            add_ok = False
        return add_ok

    def add_hapke_multiplicative_factor_for_lut(self):
        """
        add one single multiplicatif factor for each hapke optical property in coeff_diff module
        :return: True if add is ok, False if not
        """
        add_ok = True
        try:
            hapke_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.HapkeSpecularMultiFunctions.HapkeSpecularMulti
            for hapke_opt_prop in hapke_opt_props_list:
                hapke_opt_prop.hapkeNodeMultiplicativeFactorForLUT.add_hapkeMultiplicativeFactorForLUT(ptd.coeff_diff.create_hapkeMultiplicativeFactorForLUT())
        except ValueError:
            print("ERROR: multiplicative factor add failed")
            add_ok = False
        return add_ok

    def add_rpv_multiplicative_factor_for_lut(self):
        """
        add one single multiplicatif factor for each rpv optical property in coeff_diff module
        :return: True if add is ok, False if not
        """
        add_ok = True
        try:
            rpv_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.RPVMultiFunctions.RPVMulti
            for rpv_opt_prop in rpv_opt_props_list:
                rpv_opt_prop.RPVNodeMultiplicativeFactorForLUT.add_RPVMultiplicativeFactorForLUT(ptd.coeff_diff.create_RPVMultiplicativeFactorForLUT())
        except ValueError:
            print("ERROR: multiplicative factor add failed")
            add_ok = False
        return add_ok

    def add_air_multiplicative_factor_for_lut(self): # complicate CASE, possible list or AirMultifunctions, ignore for the moment
        """
        add one single multiplicatif factor for each fluid optical property in coeff_diff module
        :return: True if add is ok, False if not
        """
        add_ok = True
        try:
            air_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.AirMultiFunctions.AirFunction
            for air_opt_prop in air_opt_props_list:
                air_opt_prop.AirFunctionNodeMultiplicativeFactorForLut.add_AirFunctionMultiplicativeFactorForLut(ptd.coeff_diff.create_AirFunctionMultiplicativeFactorForLut())
        except ValueError:
            print("ERROR: multiplicative factor add failed")
            add_ok = False
        return add_ok


    def add_lamb_multiplicative_factor_for_lut(self):
        """
        add one single multiplicatif factor for each lambertian optical property in coeff_diff module
        :return: True if add is ok, False if not
        """
        add_ok = True
        try:
            lambertian_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti
            for lamb_opt_prop in lambertian_opt_props_list:
                lamb_opt_prop.lambertianNodeMultiplicativeFactorForLUT.add_lambertianMultiplicativeFactorForLUT(ptd.coeff_diff.create_lambertianMultiplicativeFactorForLUT())
        except ValueError:
            print("ERROR: multiplicative factor add failed")
            add_ok = False
        return add_ok

    def add_veg_multiplicative_factor_for_lut(self):
        """
        add one single multiplicatif factor for each vegetation optical property in coeff_diff module
        :return: True if add is ok, False if not
       """
        add_ok = True
        try:
            veg_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti
            for veg_opt_prop in veg_opt_props_list:
                veg_opt_prop.understoryNodeMultiplicativeFactorForLUT.add_understoryMultiplicativeFactorForLUT(ptd.coeff_diff.create_understoryMultiplicativeFactorForLUT())
        except ValueError:
            print("ERROR: multiplicative factor add failed")
            add_ok = False
        return add_ok

    def check_scene_optical_props(self): # TO BE COMPLETED AND TESTED
        """
        check if optical property associated to soil exist in optical properties list (ToDo: thermal properties, ThermalPropertyLink, idTemperature, indexTemperature)
        :return:True if associated properties are found in properties lists, False if not
        """
        check = True
        lambopt_prop = self.xsdobjs_dict["maket"].Maket.Soil.OpticalPropertyLink
        prop_name = lambopt_prop.ident
        index = self.get_lamboptprop_index(prop_name)
        if index == None:
                print("warning: opt_prop %s does not exist in vegetation Optical Properties List" % prop_name)
                return False
        else:
            if lambopt_prop.indexFctPhase != index:
                print("warning:  opt_prop %s index inconsistency, correcting index" % prop_name)
                lambopt_prop.indexFctPhase = index
        return check

    def check_object_3d_opt_props(self): # TO BE COMPLETED AND TESTED
        """
        check if optical properties associated to all 3d objects groups exist in optical properties list (ToDo: thermal properties)
        search of optical prop names is made through the etree corresponding to object3D XSD module, because the number of levels having an associated optical property is huge
        this means that the index can not be corrected (choice to be done)
        :return: True if every property associated to 3D ojects exist in properties lists
        """
        check = True
        lambopt_props_elements = self.xsdobjs_dict["object_3d"].to_etree().findall(".//OpticalPropertyLink")
        for lambopt_props_element in lambopt_props_elements:
            prop_name = lambopt_props_element.get("ident")
            if (self.get_optprop_index(lambopt_props_element.get("ident")) == None):
                print("warning: opt_prop %s does not exist in vegetation Optical Properties List" % lambopt_props_element.get("ident"))
                return False
        return check


    def write_xml_file(self, fname, obj, modified_simu_name = None):
        xmlstr = etree.tostring(obj.to_etree(), pretty_print=True)
        if modified_simu_name != None:
            new_simu_path = pjoin(self.getsimusdir(),modified_simu_name)
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
            self.xsdobjs_dict["phase"].Phase.DartInputParameters.SpectralIntervals.add_SpectralIntervalsProperties(sp_int_props)
            sp_irr_value = ptd.phase.create_SpectralIrradianceValue()
            self.xsdobjs_dict["phase"].Phase.DartInputParameters.nodeIlluminationMode.SpectralIrradiance.add_SpectralIrradianceValue(sp_irr_value)

    def update_properties_dict(self):
        """
        updates self.properties_dict variable
        """
        self.properties_dict = self.extract_properties_dict()

    def extract_properties_dict(self):
        return {"opt_props": self.get_opt_props(), "thermal_props": self.get_thermal_props()}

    def get_opt_prop_index(self, opt_prop_type, opt_prop_name):
        """
        gets index of optical property given as parameter, using opt_props DataFrame
        :param opt_prop_type: optical proprety type in ["vegetation", "fluid", "lambertian", "hapke", "rpv"]
        :param opt_prop_name: optical property name
        :return: index on DataFrame corresponding to the opt_prop_type, 999 if property does not exist
        """
        self.update_properties_dict()
        index = 999
        opt_prop_list = self.properties_dict["opt_props"][opt_prop_type]

        if opt_prop_list.shape[0] > 0:
            if len(opt_prop_list[opt_prop_list["prop_name"] == opt_prop_name]) > 0: #property exists
                index = opt_prop_list[opt_prop_list["prop_name"] == opt_prop_name].index.tolist()[0]
        return index

    def get_thermal_prop_index(self, th_prop_name):
        """
        gets index of thermal property given as parameter, using thermal_props DataFrame
        :param th_prop_name: thermal property name
        :return: index on th_props DataFrame, 999 if property does not exist
        """
        self.update_properties_dict()
        index = 999
        th_prop_list = self.properties_dict["thermal_props"]
        if th_prop_list.shape[0] > 0:
            if len(th_prop_list[th_prop_list["prop_name"] == th_prop_name]) > 0: #property exists
                index = th_prop_list[th_prop_list["prop_name"] == th_prop_name].index.tolist()[0]
        return index

    def checkandcorrect_opt_prop_exists(self,opt_prop_type, opt_prop_name, createProps = False):
        """
        Check if opt_prop exists
        If it doesn't exist, and createOptProps == True, creates the missing optical property
        If it doesn't exist, and createOptProps == False, prints ERROR Message
        :param opt_prop_type: type of optical property in ["vegetation", "fluid", "lambertian", "hapke", "rpv"]
        :param opt_prop_name: name of optical property to be checked
        :param createOptProps: boolean, if True, a missing optical property will be created
        :return: index in the corresponding list, 999 if missing  : TOBE DONE
        """
        self.update_properties_dict()
        index = 999
        opt_prop_list = self.properties_dict["opt_props"][opt_prop_type]
        if opt_prop_list.shape[0] > 0: # non empty opt_prop_list
            if len(opt_prop_list[opt_prop_list["prop_name"] == opt_prop_name])<1: # if property does not exist
                if createProps == True:
                    print("creating {} optical property named {}".format(opt_prop_type, opt_prop_name))
                    self.add_opt_property(opt_prop_type, opt_prop_name)
                    self.update_properties_dict()
                    opt_prop_list = self.properties_dict["opt_props"][opt_prop_type]
                    index = opt_prop_list[opt_prop_list["prop_name"] == opt_prop_name].index.tolist()[0]# unicity of prop_name
                else:
                    print("ERROR: %s optical property %s does not exist, please FIX or set createOptProps to TRUE" % (
                        opt_prop_type, opt_prop_name))
                    return index
            else: #property exists
                index = opt_prop_list[opt_prop_list["prop_name"] == opt_prop_name].index.tolist()[0]
        else: #empty opt_prop_list
            if createProps == True:
                print("creating {} optical property named {}".format(opt_prop_type, opt_prop_name))
                self.add_opt_property(opt_prop_type, opt_prop_name)
                self.update_properties_dict()
                opt_prop_list = self.properties_dict["opt_props"][opt_prop_type]
                index = opt_prop_list[opt_prop_list["prop_name"] == opt_prop_name].index.tolist()[0]  # unicity of prop_name
        return index

    def checkandcorrect_th_prop_exists(self, th_prop_name, createProps = False):
        """
        Check if thermal_prop exists
        If it doesn't exist, and createOptProps == True, creates the missing optical property
        If it doesn't exist, and createOptProps == False, prints ERROR Message
        :param th_prop_name: thermal property name
        :param createOptProps: boolean, if True, a missing thermal property will be created
        :return:index in the corresponding list, 999 if missing
        """
        self.update_properties_dict()
        index = 999
        th_prop_list = self.properties_dict["thermal_props"]
        if th_prop_list.shape[0] > 0: #non empty prop_list
            if len(th_prop_list[th_prop_list["prop_name"] == th_prop_name])<1:# if property does not exist
                if createProps == True:
                    print("creating thermal property named {}".format(th_prop_name))
                    self.add_th_property(th_prop_name)
                    self.update_properties_dict()
                    th_prop_list = self.properties_dict["thermal_props"]
                    index = th_prop_list[th_prop_list["prop_name"] == th_prop_name].index.tolist()[0]#unicity of th_prop_name
                else:
                    print("ERROR: thermal property %s does not exist, please FIX or set createOptProps to TRUE" % (
                        th_prop_name))
                    return index
            else: # property exists
                index = th_prop_list[th_prop_list["prop_name"] == th_prop_name].index.tolist()[0]
        else: # empty prop list
            if createProps == True:
                print("creating {} thermal property named {}".format(th_prop_name))
                self.add_th_property(th_prop_name)
                self.update_properties_dict()
                th_prop_list = self.properties_dict["thermal_props"]
                index = th_prop_list[th_prop_list["prop_name"] == th_prop_name].index.tolist()[
                    0]  # unicity of th_prop_name

        return index




###################################################
##### USER FRIENDLY FUNCTIONS ###################

    def add_opt_property(self, opt_prop_type, opt_prop_name):
        self.extract_sp_bands_table()
        nb_sp_bands = self.spbands_table.shape[0]
        if self.get_opt_prop_index(opt_prop_type, opt_prop_name) == 999: # if oprtical property does not exist, create
            if opt_prop_type == "vegetation":
                understoryMulti = ptd.coeff_diff.create_UnderstoryMulti(ident = opt_prop_name)
                for i in range(nb_sp_bands):
                    understoryMulti.understoryNodeMultiplicativeFactorForLUT.add_understoryMultiplicativeFactorForLUT(
                        ptd.coeff_diff.create_understoryMultiplicativeFactorForLUT())
                self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.add_UnderstoryMulti(understoryMulti)
            elif opt_prop_type == "fluid":
                airFunction = ptd.coeff_diff.create_AirFunction(ident = opt_prop_name)
                for i in range(nb_sp_bands):
                    airFunction.airFunctionNodeMultiplicativeFactorForLUT.add_airFunctionMultiplicativeFactorForLUT(
                        ptd.coeff_diff.create_AirFunctionMultiplicativeFactorForLut())
                self.xsdobjs_dict["coeff_diff"].Coeff_diff.AirMultiFunctions.add_AirFuntion(airFunction)
            elif opt_prop_type == "lambertian":
                lambertianMulti = ptd.coeff_diff.create_LambertianMulti(ident = opt_prop_name)
                for i in range(nb_sp_bands):
                    lambertianMulti.lambertianNodeMultiplicativeFactorForLUT.add_lambertianMultiplicativeFactorForLUT(
                        ptd.coeff_diff.create_lambertianMultiplicativeFactorForLUT())
                self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.add_LambertianMulti(lambertianMulti)
            elif opt_prop_type == "hapke":
                hapkeSpecMulti = ptd.coeff_diff.create_HapkeSpecularMulti(ident = opt_prop_name)
                for i in range(nb_sp_bands):
                    hapkeSpecMulti.hapkeNodeMultiplicativeFactorForLUT.add_hapkeMultiplicativeFactorForLUT(
                        ptd.coeff_diff.create_hapkeMultiplicativeFactorForLUT())
                self.xsdobjs_dict["coeff_diff"].Coeff_diff.HapkeSpecularMultiFunctions.add_HapkeSpecularMulti(hapkeSpecMulti)
            elif opt_prop_type == "rpv":
                rpvMulti = ptd.coeff_diff.create_RPVMulti(ident = opt_prop_name)
                for i in range(nb_sp_bands):
                    rpvMulti.RPVNodeMultiplicativeFactorForLUT.add_RPVMultiplicativeFactorForLUT(
                        ptd.coeff_diff.create_RPVMultiplicativeFactorForLUT())
                self.xsdobjs_dict["coeff_diff"].Coeff_diff.RPVMultiFunctions.add_RPVMulti(rpvMulti)
            self.update_properties_dict()
        else: # opt_property having name opt_prop_name already exists
            print("ERROR: optical property of type %s named %s already exists, please change name" % (opt_prop_type, opt_prop_name))


    def add_th_property(self, th_prop_name):
        if self.get_thermal_prop_index(th_prop_name) == 999:  # if thermal property does not exist, create
            th_function = ptd.coeff_diff.create_ThermalFunction(idTemperature=th_prop_name)
            self.xsdobjs_dict["coeff_diff"].Coeff_diff.Temperatures.add_ThermalFunction(th_function)
            self.update_properties_dict()
        else: # th_prop having name opt_prop_name already exists
            print("ERROR: thermal property named %s already exists, please change name" % (th_prop_name))


    def add_multiplots(self, plots_list):
        # plots_fields = ["plot_type", "plot_form", "plot_opt_prop_name", "plot_therm_prop_name", "grd_opt_prop_type",
        #                 "grd_opt_prop_name", "grd_therm_prop_name", "createProps"]
        for plot_params in plots_list:
            self.add_plot(plot_type = plot_params[0] , plot_form = plot_params[1],
                     plot_opt_prop_name = plot_params[2], plot_therm_prop_name = plot_params[3],
                     grd_opt_prop_type = plot_params[4], grd_opt_prop_name = plot_params[5],
                     grd_therm_prop_name = plot_params[6], createProps = plot_params[7]
                     )

    def add_plot(self, plot_type = "vegetation", plot_form = "polygon", plot_opt_prop_name = None, plot_therm_prop_name = None, grd_opt_prop_type = None, grd_opt_prop_name = None, grd_therm_prop_name = None, createProps = False):
        """
        Adds a plot in plots_obj (self.xsdsobjs_dict["plots"]), corresponding to the given parameters
        :param plot_type: type of plot in ["ground","vegetation","veg_ground","fluid"]
        :param plot_form: ["polygon", "rectangle"]
        :param plot_opt_prop_name: name of vegetation optical property, can be None (if plot type = ground)
        :param plot_therm_prop_name: name of plot_ground thermal property, can be None (if plot type = ground)
        :param grd_opt_prop_type: ground optical property type in ["lambertian","hapke","rpv"]
        :param grd_opt_prop_name: name of ground optical property name.  Can be None (if plot_type = vegetation or fluid)
        :param grd_therm_prop_name: name of ground thermal property name. Can be None (if plot_type = vegetation or fluid)
        :param createOptProps: optional. If True, missing optical/thermal properties should be created

        either (plot_opt_prop_name and plot_therm_prop_name) or (grd_opt_prop_type and grd_opt_prop_name and grd_therm_prop_name) must be != None
        if they are not given by user, default properties (comming from default DART property links) are taken

        :return True if plot could be added, False if not
        """

        if ( (plot_opt_prop_name == None or plot_therm_prop_name == None) and (grd_opt_prop_type == None or grd_opt_prop_name == None or grd_opt_prop_type == None)): # default case
            default_vegProp = ptd.plots.create_VegetationOpticalPropertyLink()
            default_grd_thProp = ptd.plots.create_GroundThermalPropertyLink()
            plot_type = "vegetation"
            plot_opt_prop_name = default_vegProp.ident
            plot_therm_prop_name = default_grd_thProp.idTemperature

        grd_opt_prop_types_dict = {0: "lambertian", 2: "hapke", 4: "rpv"}
        grd_opt_prop_types_inv_dict = {"lambertian": 0, "hapke": 2, "rpv": 4}
        plot_types_dict = {0: "ground", 1: "vegetation", 2: "veg_ground", 3: "fluid"}
        plot_types_inv_dict = {"ground": 0, "vegetation": 1, "veg_ground": 2, "fluid": 3}
        plot_form_dict = {0: "polygon", 1: "rectangle"}
        plot_form_inv_dict = {"polygon": 0, "rectangle": 1}

        plt_type_num = plot_types_inv_dict[plot_type]
        plt_form_num = plot_form_inv_dict[plot_form]
        if grd_opt_prop_type != None:
            grd_optprop_type_num = grd_opt_prop_types_inv_dict[grd_opt_prop_type]

        plt_vegetation_properties = None
        plt_air_properties = None
        plt_water_proerties = None
        grd_opt_prop = None
        grd_therm_prop = None

        if plt_type_num in [1,2]:
            plot_opt_prop_type = "vegetation"
            plot_opt_prop_index = self.checkandcorrect_opt_prop_exists(plot_opt_prop_type, plot_opt_prop_name, createProps)
            plot_th_prop_index = self.checkandcorrect_th_prop_exists(plot_therm_prop_name, createProps)
            if plot_opt_prop_index!= 999 and plot_th_prop_index != 999:
                plt_opt_prop = ptd.plots.create_VegetationOpticalPropertyLink(ident=plot_opt_prop_name, indexFctPhase=plot_opt_prop_index)
                plt_therm_prop = ptd.plots.create_GroundThermalPropertyLink(idTemperature=plot_therm_prop_name, indexTemperature=plot_th_prop_index)
                plt_vegetation_properties = ptd.plots.create_PlotVegetationProperties(
                    VegetationOpticalPropertyLink=plt_opt_prop, GroundThermalPropertyLink=plt_therm_prop)
            else: #either opt_prop or th_prop does not exist
                print("ERROR opt_prop or thermal prop does not exist, please FIX or set createProps = True")
                return False
        elif plt_type_num == 3:
            plot_opt_prop_type = "fluid"
            opt_prop_exists = self.checkandcorrect_opt_prop_exists(plot_opt_prop_type, plot_opt_prop_name,
                                                                   createProps)
            plot_opt_prop_index = self.checkandcorrect_opt_prop_exists(plot_opt_prop_type, plot_opt_prop_name,
                                                                       createProps)
            plot_th_prop_index = self.checkandcorrect_th_prop_exists(plot_therm_prop_name, createProps)
            if plot_opt_prop_index != 999 and plot_th_prop_index != 999:
                plt_opt_prop = ptd.plots.create_AirOpticalPropertyLink(ident=plot_opt_prop_name,
                                                                              indexFctPhase=plot_opt_prop_index)
                plt_air_properties = ptd.plots.create_AirOpticalProperties(AirOpticalPropertyLink=plt_opt_prop)
            else:  #either opt_prop or th_prop does not exist
                print("ERROR opt_prop or thermal prop does not exist, please FIX or set createProps = True")
                return False

        if plt_type_num in [0,2]: #ground or ground+veg
            grd_opt_prop_index = self.checkandcorrect_opt_prop_exists(grd_opt_prop_type, grd_opt_prop_name, createProps)
            grd_th_prop_index = self.checkandcorrect_th_prop_exists(grd_therm_prop_name, createProps)
            if grd_opt_prop_index != 999 and grd_th_prop_index != 999:
                grd_opt_prop = ptd.plots.create_GroundOpticalPropertyLink(type_=grd_optprop_type_num,
                                                                          ident=grd_opt_prop_name,
                                                                          indexFctPhase=grd_opt_prop_index)
                grd_therm_prop = ptd.plots.create_GroundThermalPropertyLink(idTemperature=grd_therm_prop_name,
                                                                            indexTemperature=grd_th_prop_index)
            else: # either opt_prop or th prop does not exist
                print("ERROR opt_prop or thermal prop does not exist, please FIX or set createProps = True")
                return False

        try:
            Plot = ptd.plots.create_Plot(type_=plt_type_num, form = plt_form_num,
                                  PlotVegetationProperties= plt_vegetation_properties, PlotAirProperties=plt_air_properties,
                                  PlotWaterProperties=plt_water_proerties,
                                  GroundOpticalPropertyLink=grd_opt_prop, GroundThermalPropertyLink=grd_therm_prop)

            self.xsdobjs_dict["plots"].Plots.add_Plot(Plot)
        except ValueError:
            print("ERROR: create or add Plot failed")
            return False

        return True

    def add_sp_bands_uf(self, spbands_list):
        """
        add spectral bands, manages phase and coeff_diff modules interactions
        no check of sp_bands unicity is made (as in DART interface)
        :param spbands_list: list of spectral bands, each band containes [0]:mean_lambda and [1]: fwhm for lambda
        """
        #phase module modification

        self.add_sp_bands(spbands_list)
        # for sp_band in spbands_list:
        #     sp_int_props = ptd.phase.create_SpectralIntervalsProperties(meanLambda=sp_band[0], deltaLambda=sp_band[1])
        #     self.xsdobjs_dict["phase"].Phase.DartInputParameters.SpectralIntervals.add_SpectralIntervalsProperties(sp_int_props)
        #     sp_irr_value = ptd.phase.create_SpectralIrradianceValue()
        #     self.xsdobjs_dict["phase"].Phase.DartInputParameters.nodeIlluminationMode.SpectralIrradiance.add_SpectralIrradianceValue(sp_irr_value)

        #coeff module modification
        lambertian_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti
        hapke_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.HapkeSpecularMultiFunctions.HapkeSpecularMulti
        rpv_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.RPVMultiFunctions.RPVMulti
        veg_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti
        fluid_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.AirMultiFunctions.AirFunction

        #for i in range(len(spbands_list)):

        if len(lambertian_opt_props_list) > 0:
            self.add_lamb_multiplicative_factors_for_lut()
        if len(hapke_opt_props_list) > 0:
            self.add_hapke_multiplicative_factors_for_lut()
        if len(rpv_opt_props_list) > 0:
            self.add_rpv_multiplicative_factors_for_lut()
        if len(veg_opt_props_list) > 0:
            self.add_veg_multiplicative_factors_for_lut()
        if len(fluid_props_list) > 0: # complicated case, several air properties allowed
            self.add_air_multiplicative_factors_for_lut()


    #ToDo
    #refreshObjFromTables(auto=True) : aimed to be launched automatically after each Table Modification, or manually
    #def add_multiplots()
    #add_sequence()
    #add_optprop()
