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
from settings import getsimupath, get_simu_input_path, get_simu_output_path
import pytools4dart.run as run
import helpers.dbtools as dbtools

import pytools4dart as ptd

from pytools4dart.xsdschema.plots import createDartFile as PlotsRoot
from pytools4dart.xsdschema.phase import createDartFile as PhaseRoot
from pytools4dart.xsdschema.atmosphere import createDartFile as AtmosphereRoot
from pytools4dart.xsdschema.coeff_diff import createDartFile as CoeffDiffRoot
from pytools4dart.xsdschema.directions import createDartFile as DirectionsRoot
from pytools4dart.xsdschema.object_3d import createDartFile as Object3dRoot
from pytools4dart.xsdschema.maket import createDartFile as MaketRoot
from pytools4dart.xsdschema.inversion import createDartFile as InversionRoot
from pytools4dart.xsdschema.LUT import createDartFile as LUTRoot
from pytools4dart.xsdschema.lut import createDartFile as lutRoot
from pytools4dart.xsdschema.trees import createDartFile as TreesRoot
from pytools4dart.xsdschema.triangleFile import createDartFile as TriangleFileRoot
from pytools4dart.xsdschema.water import createDartFile as WaterRoot
from pytools4dart.xsdschema.urban import createDartFile as UrbanRoot

spbands_fields = ['wvl', 'fwhm']
opt_props_fields = ['type', 'op_name', 'db_name', 'op_name_in_db', 'specular']
plot_fields = ['x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 'y4',
               'zmin', 'dz', 'density',
               'densitydef', 'op_name']

class simulation(object):
    """Simulation object corresponding to a DART simulation.
    It allows for storing and editing parameters, and running simulation
    xsdobjs_dict contains objects built according to XSD modules specification, access is given through a key which matches with XSDfile name
    """
    def __init__(self, name = None):
        self.name = name
        self.xsdobjs_dict = {}
        self.xsdobjs_dict["plots"] = PlotsRoot()
        self.xsdobjs_dict["phase"] = PhaseRoot()
        self.xsdobjs_dict["atmosphere"] = AtmosphereRoot()
        self.xsdobjs_dict["coeff_diff"] = CoeffDiffRoot()
        self.xsdobjs_dict["directions"] = DirectionsRoot()
        self.xsdobjs_dict["object_3d"] = Object3dRoot()
        self.xsdobjs_dict["maket"] = MaketRoot()
        self.xsdobjs_dict["inversion"] = InversionRoot()
        self.xsdobjs_dict["trees"] = TreesRoot()
        self.xsdobjs_dict["water"] = WaterRoot()
        self.xsdobjs_dict["urban"] = UrbanRoot()
        for xsdobj in self.xsdobjs_dict.values():
            xsdobj.factory()

        # self.urban_obj = UrbanRoot()
        # self.urban_obj.factory()

        #get XMLRootNodes:
        if name != None and os.path.isdir(self.getsimupath()):
            self.read_from_xml()


        self.properties_dict = {"opt_props":self.get_opt_props(), "thermal_props": self.get_thermal_props()}

        self.runners = run.runners(self)

    def read_from_xml(self):
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

        # version précédente, avec chaque objet nommé: self.plots_obj.build(self.xml_root_nodes_dict["plots"])

        #QUESTION:  Ces fichiers qui suivent ne sont peut être pas à lire, surtout pas le fichier TriangleFile?????

        if "LUT" in self.xml_root_nodes_dict.keys():
            # self.LUT_obj = LUTRoot()
            # self.LUT_obj.factory()
            # self.LUT_obj.build(self.xml_root_nodes_dict["LUT"])
            self.xsdobjs_dict["LUT"] = LUTRoot()
            self.xsdobjs_dict["LUT"].factory()
            self.xsdobjs_dict["LUT"].build(self.xml_root_nodes_dict["LUT"])

        if "lut" in self.xml_root_nodes_dict.keys():
            # self.lut_obj = lutRoot()
            # self.lut_obj.factory()
            # self.lut_obj.build(self.xml_root_nodes_dict["lut"])
            self.xsdobjs_dict["lut"] = lutRoot()
            self.xsdobjs_dict["lut"].factory()
            self.xsdobjs_dict["lut"].build(self.xml_root_nodes_dict["lut"])

        if "triangleFile" in self.xml_root_nodes_dict.keys():
            # self.triangleFile_obj = TriangleFileRoot()
            # self.triangleFile_obj.factory()
            # self.triangleFile_obj.build(self.xml_root_nodes_dict["triangleFile"])
            self.xsdobjs_dict["triangleFile"] = TriangleFileRoot()
            self.xsdobjs_dict["triangleFile"].factory()
            self.xsdobjs_dict["triangleFile"].build(self.xml_root_nodes_dict["triangleFile"])

        self.extract_tables_from_objs()

    def extract_tables_from_objs(self):
        self.plots_full_table = self.extract_plots_full_table()
        self.spbands_table = self.extract_sp_bands_table()

    # def extract_plots_table(self):
    #     self.plots_table = pd.DataFrame(columns=plot_fields)
    #     plots_list = self.xsdobjs_dict["plots"].Plots.Plot
    #     rows_to_add = []
    #     for plot in plots_list:
    #         points_list = plot.Polygon2D.Point2D
    #         x1, y1 = points_list[0].x, points_list[0].y
    #         x2, y2 = points_list[1].x, points_list[1].y
    #         x3, y3 = points_list[2].x, points_list[2].y
    #         x4, y4 = points_list[3].x, points_list[3].y
    #
    #         zmin, dz = plot.PlotVegetationProperties.VegetationGeometry.baseheight, plot.PlotVegetationProperties.VegetationGeometry.height
    #         density_definition, density = plot.PlotVegetationProperties.densityDefinition, plot.PlotVegetationProperties.LAIVegetation.LAI
    #         opt_prop_name =  plot.PlotVegetationProperties.VegetationOpticalPropertyLink.ident
    #
    #         row_to_add = [x1, y1, x2, y2, x3, y3, x4, y4, zmin, dz, density_definition, density, opt_prop_name]
    #         rows_to_add.append(row_to_add)
    #
    #     self.plots_table = pd.DataFrame(rows_to_add, columns = plot_fields)

    def extract_sp_bands_table(self):
        self.spbands_table = pd.DataFrame(columns = spbands_fields)
        spbands_list = self.xsdobjs_dict["phase"].Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties

        rows_to_add = []
        for sp_interval in spbands_list:
            wvl, dl = sp_interval.meanLambda, sp_interval.deltaLambda
            row_to_add = [wvl, dl]
            rows_to_add.append(row_to_add)

        return pd.DataFrame(rows_to_add, columns = spbands_fields)

    # def extract_opt_props_table(self):
    #     self.optprops_table = {'lambertian': pd.DataFrame(columns=opt_props_fields),
    #                            'vegetation': pd.DataFrame(columns=opt_props_fields)}
    #     #lambertians
    #     lamb_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti
    #     rows_to_add = []
    #     for lamb_opt_prop in lamb_opt_props_list:
    #         type = "lambertian"
    #         db_name =  lamb_opt_prop.databaseName
    #         op_prop_name_in_db = lamb_opt_prop.ModelName
    #         op_prop_name = lamb_opt_prop.ident
    #         specular = lamb_opt_prop.useSpecular
    #         row_to_add = type, op_prop_name, db_name, op_prop_name_in_db, specular
    #         rows_to_add.append(row_to_add)
    #     self.optprops_table["lambertian"] = pd.DataFrame(rows_to_add, columns = opt_props_fields)
    #
    #     #vegetation
    #     vegetation_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti
    #     rows_to_add = []
    #     for veg_opt_prop in vegetation_opt_props_list:
    #         type = "vegetation"
    #         db_name = veg_opt_prop.databaseName
    #         op_prop_name_in_db = veg_opt_prop.ModelName
    #         op_prop_name = veg_opt_prop.ident
    #         specular = veg_opt_prop.useSpecular
    #         #LAD???
    #         row_to_add = type, op_prop_name, db_name, op_prop_name_in_db, specular
    #         rows_to_add.append(row_to_add)
    #     self.optprops_table["vegetation"] = pd.DataFrame(rows_to_add, columns=opt_props_fields)

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

    def writeToXMLFromObj(self, modified_simu_name = None):
        check = self.check_module_dependencies()

        if check == True: # introduce exception treatment instead
            if modified_simu_name != None:
                new_simu_path = pjoin(self.getsimupath(), "..", modified_simu_name)
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
            print("please correct dependencies issues before writing files")

    def check_properties_indexes_through_tables(self):
        """
        Att: Dans le cas des fichiers plots.txt et trees.txt, on peut juste vérifier que le numéro de proprieté (optique/thermique) existe
        :return:
        """
        self.extract_tables_from_objs()
        check_plots = self.cross_check_plots_props()
        # check_scene = self.cross_check_scene_props(self.properties_dict)
        # check_object3d = self.cross_check_object3d_props(self.properties_dict)
        # check_trees = self.cross_check_trees_props(self.properties_dict) # only if trees.txt is referenced
        return check_plots
        # return check_plots and check_scene and check_object3d and check_trees

    def get_plots_dfs_by_opt_prop_type(self):
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
        cross_plots_opt_props_dict = {} # jointure of opt_props_dict and plots/ground optical properties
        for opt_prop_type in opt_props.keys():
            if opt_prop_type in ["vegetation","fluid"]:
                cross_plots_opt_props_dict[opt_prop_type] = pd.merge(opt_props[opt_prop_type], plots_dfs_by_opt_prop_type[opt_prop_type],
                                                                     left_on = ['names'],right_on=['PLT_OPT_NAME'])
            else: #lambertian, hapke, rpv
                cross_plots_opt_props_dict[opt_prop_type] = pd.merge(opt_props[opt_prop_type], plots_dfs_by_opt_prop_type[opt_prop_type],
                                                                     left_on=['names'], right_on=['GRD_OPT_NAME'])
        for opt_prop_type in opt_props.keys():
            plots = plots_dfs_by_opt_prop_type[opt_prop_type]
            cross_props = cross_plots_opt_props_dict[opt_prop_type]
            if len(plots) > len(cross_props): # number of plots is greater than the number of retrieved optical properties (mission plot opt properties)
                check = False
                print("ERROR: missing %d %s optical properties:" % (len(plots) - len(cross_props), opt_prop_type))
                if opt_prop_type in ["vegetation","fluid"]:
                    missing_props = plots[~(plots['PLT_OPT_NAME'].isin(cross_props['names']))]['PLT_OPT_NAME']
                    for missing_prop in missing_props:
                        print("%s property %s is does not exist, please FIX" % (opt_prop_type,missing_prop))
                else: #opt_prop_type in ["lambertian","hapke","rpv"]
                    missing_props = plots[~(plots['GRD_OPT_NAME'].isin(cross_props['names']))]['GRD_OPT_NAME']
                    for missing_prop in missing_props:
                        print("%s property %s is does not exist, please FIX" % (opt_prop_type,missing_prop))
            else: # if plots/ground properties do exist in properties list, check if indexes do match
                if opt_prop_type in ["vegetation","fluid"]:
                    eq_serie = cross_props["indexes"].eq(cross_props["PLT_OPT_NUMB"])
                    if len(eq_serie[eq_serie == False]):
                        print("ERROR: indexes inconsistency, TOBE CORRECTED")
                else: # opt_prop_type in ["lambertian","hapke","rpv"]
                    eq_serie = cross_props["indexes"].eq(cross_props["GRD_OPT_NUMB"])
                    if len(eq_serie[eq_serie == False]):
                        print("ERROR: indexes inconsistency, TOBE CORRECTED")

        return check

    def check_plots_thermal_props(self):

        check = True

        thermal_props = self.properties_dict["thermal_props"]
        cross_plots_therm_props_dict = {}  # jointure of opt_props_dict and plots/ground optical properties

        plot_types = ["veg_vegplusground_fluid","ground"]
        plots_dfs_by_plot_type = self.get_plots_dfs_by_plot_type()

        cross_plots_therm_props_dict["veg_vegplusground_fluid"] = pd.merge(thermal_props, plots_dfs_by_plot_type["veg_vegplusground_fluid"],
                                                               left_on=['names'], right_on=['PLT_THERM_NAME'])
        cross_plots_therm_props_dict["ground"] = pd.merge(thermal_props,plots_dfs_by_plot_type["ground"],
                                                                           left_on=['names'],right_on=['GRD_THERM_NAME'])
        for plot_type in plot_types:
            plots = plots_dfs_by_plot_type[plot_type]
            cross_props = cross_plots_therm_props_dict[plot_type]
            if len(plots) > len(cross_props):
                check = False
                print("ERROR: missing %d %s thermal properties:" % ( len(plots) - len(cross_props), plot_type ) )
                if plot_type == "veg_vegplusground_fluid":
                    missing_props = plots[~(plots['PLT_THERM_NAME'].isin(cross_props['names']))]['PLT_THERM_NAME']
                    for missing_prop in missing_props:
                        print("%s property %s is does not exist, please FIX" % (plot_type, missing_prop))
                else:  # plot_type == "ground"
                    missing_props = plots[~(plots['GRD_THERM_NAME'].isin(cross_props['names']))]['GRD_THERM_NAME']
                    for missing_prop in missing_props:
                        print("%s property %s is does not exist, please FIX" % (plot_type, missing_prop))
            else:  # if plots/ground properties do exist in properties list, check if indexes do match
                if plot_type == "veg_vegplusground_fluid":
                    eq_serie = cross_props["indexes"].eq(cross_props["PLT_THERM_NUMB"])
                    if len(eq_serie[eq_serie == False]):
                        print("ERROR: indexes inconsistency, TOBE CORRECTED")
                else:  # plot_type == "ground"
                    eq_serie = cross_props["indexes"].eq(cross_props["GRD_THERM_NUMB"])
                    if len(eq_serie[eq_serie == False]):
                        print("ERROR: indexes inconsistency, TOBE CORRECTED")

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
        # #################check optical properties
        # opt_props = self.properties_dict["opt_props"]
        # plots_dfs_by_opt_prop_type = self.get_plots_dfs_by_opt_prop_type()
        # cross_plots_opt_props_dict = {} # jointure of opt_props_dict and plots/ground optical properties
        # for opt_prop_type in opt_props.keys():
        #     if opt_prop_type in ["vegetation","fluid"]:
        #         cross_plots_opt_props_dict[opt_prop_type] = pd.merge(opt_props[opt_prop_type], plots_dfs_by_opt_prop_type[opt_prop_type],
        #                                                              left_on = ['names'],right_on=['PLT_OPT_NAME'])
        #     else: #lambertian, hapke, rpv
        #         cross_plots_opt_props_dict[opt_prop_type] = pd.merge(opt_props[opt_prop_type], plots_dfs_by_opt_prop_type[opt_prop_type],
        #                                                              left_on=['names'], right_on=['GRD_OPT_NAME'])
        # for opt_prop_type in opt_props.keys():
        #     plots = plots_dfs_by_opt_prop_type[opt_prop_type]
        #     cross_props = cross_plots_opt_props_dict[opt_prop_type]
        #     if len(plots) > len(cross_props): # number of plots is greater than the number of retrieved optical properties (mission plot opt properties)
        #         check = False
        #         print("ERROR: missing %d %s optical properties:" % (len(plots) - len(cross_props), opt_prop_type))
        #         if opt_prop_type in ["vegetation","fluid"]:
        #             missing_props = plots[~(plots['PLT_OPT_NAME'].isin(cross_props['names']))]['PLT_OPT_NAME']
        #             for missing_prop in missing_props:
        #                 print("%s property %s is does not exist, please FIX" % (opt_prop_type,missing_prop))
        #         else: #opt_prop_type in ["lambertian","hapke","rpv"]
        #             missing_props = plots[~(plots['GRD_OPT_NAME'].isin(cross_props['names']))]['GRD_OPT_NAME']
        #             for missing_prop in missing_props:
        #                 print("%s property %s is does not exist, please FIX" % (opt_prop_type,missing_prop))
        #     else: # if plots/ground properties do exist in properties list, check if indexes do match
        #         if opt_prop_type in ["vegetation","fluid"]:
        #             eq_serie = cross_props["indexes"].eq(cross_props["PLT_OPT_NUMB"])
        #             if len(eq_serie[eq_serie == False]):
        #                 print("ERROR: indexes inconsistency, TOBE CORRECTED")
        #         else: # opt_prop_type in ["lambertian","hapke","rpv"]
        #             eq_serie = cross_props["indexes"].eq(cross_props["GRD_OPT_NUMB"])
        #             if len(eq_serie[eq_serie == False]):
        #                 print("ERROR: indexes inconsistency, TOBE CORRECTED")
        #
        # #################END OF check optical properties
        # #################check thermal properties
        #
        # thermal_props = self.properties_dict["thermal_props"]
        # cross_plots_therm_props_dict = {}  # jointure of opt_props_dict and plots/ground optical properties
        #
        # plot_types = ["veg_vegplusground_fluid","ground"]
        # plots_dfs_by_plot_type = self.get_plots_dfs_by_plot_type()
        #
        # cross_plots_therm_props_dict["veg_vegplusground_fluid"] = pd.merge(thermal_props, plots_dfs_by_plot_type["veg_vegplusground_fluid"],
        #                                                        left_on=['names'], right_on=['PLT_THERM_NAME'])
        # cross_plots_therm_props_dict["ground"] = pd.merge(thermal_props,plots_dfs_by_plot_type["ground"],
        #                                                                    left_on=['names'],right_on=['GRD_THERM_NAME'])
        # for plot_type in plot_types:
        #     plots = plots_dfs_by_plot_type[plot_type]
        #     cross_props = cross_plots_therm_props_dict[plot_type]
        #     if len(plots) > len(cross_props):
        #         check = False
        #         print("ERROR: missing %d %s thermal properties:" % ( len(plots) - len(cross_props), plot_type ) )
        #         if plot_type == "veg_vegplusground_fluid":
        #             missing_props = plots[~(plots['PLT_OPT_NAME'].isin(cross_props['names']))]['PLT_OPT_NAME']
        #             for missing_prop in missing_props:
        #                 print("%s property %s is does not exist, please FIX" % (plot_type, missing_prop))
        #         else:  # plot_type == "ground"
        #             missing_props = plots[~(plots['GRD_OPT_NAME'].isin(cross_props['names']))]['GRD_OPT_NAME']
        #             for missing_prop in missing_props:
        #                 print("%s property %s is does not exist, please FIX" % (plot_type, missing_prop))
        #     else:  # if plots/ground properties do exist in properties list, check if indexes do match
        #         if plot_type == "veg_vegplusground_fluid":
        #             eq_serie = cross_props["indexes"].eq(cross_props["PLT_OPT_NUMB"])
        #             if len(eq_serie[eq_serie == False]):
        #                 print("ERROR: indexes inconsistency, TOBE CORRECTED")
        #         else:  # plot_type == "ground"
        #             eq_serie = cross_props["indexes"].eq(cross_props["GRD_OPT_NUMB"])
        #             if len(eq_serie[eq_serie == False]):
        #                 print("ERROR: indexes inconsistency, TOBE CORRECTED")

        # check plots.txt indexes

    # def cross_check_plots_props(self):
    #     """
    #     Check plots optical/thermal properties consistency
    #     If property does not exist, an Error message is printed, asking the user to fix
    #     If property does exist but indexes correspondance is not ensured, this is corrected and a warning message is printed
    #     ToDo if any plots.txt check if opt/thermal property indexes given in those files are present in properties lists, if not, just Warn the user an let her/him fix
    #     :return: True if check is ok or if just indexes inconsistency is corrected, False in any other case.
    #     """
    #     check = True
    #
    #     #check plot optical properties
    #     plots_opt_props = self.get_plots_opt_props()  # dataFrame containing opt props associated to plots
    #     plots_thermal_props = self.get_plots_thermal_props()  # dataFrame containing thermal props associated to plots
    #     opt_props = self.properties_dict["opt_props"]
    #     thermal_props = self.properties_dict["thermal_props"]
    #     cross_plots_opt_props = pd.merge(opt_props["vegetation"], plots_opt_props, on = ['opt_prop_names'])
    #     if len(cross_plots_opt_props.index) != len(plots_opt_props):
    #         missing_plots_opt_props = plots_opt_props[~(plots_opt_props['opt_prop_names'].isin(cross_plots_opt_props['opt_prop_names']))]
    #         for opt_prop_name in missing_plots_opt_props['opt_prop_names']:
    #             print("Error: optical property %s associated to plot does not exist in vegetation optical properties list. Please fix " % opt_prop_name)
    #         check = False
    #     else:
    #         #check that indexes and ids are identical, if not, correct
    #         eq_serie = cross_plots_opt_props["th_props.id"].eq(cross_plots_opt_props["plots_th_props.index"])
    #         cross_plots_opt_props["index_eq"] = cross_plots_opt_props["th_props.id"].eq(cross_plots_opt_props["plots_th_props.index"])
    #
    #         if len(eq_serie[eq_serie == False]):
    #             self.correct_plots_opt_props() # read cross_plots_opt_props[index_eq for index_eq = False] -> find correspondance, correct in Plots Object
    #         print("Warning: Plots Opt Props Indexes inconsistency has been corrected")
    #
    #     #check plot thermal properties
    #     cross_plots_th_props = pd.merge(thermal_props, plots_thermal_props, on=['th_prop_names'])
    #     if len(cross_plots_th_props.index) != len(plots_thermal_props):
    #         missing_plots_th_props = plots_thermal_props[
    #             ~(plots_thermal_props['opt_prop_names'].isin(cross_plots_th_props['opt_prop_names']))]
    #         for th_prop_name in missing_plots_th_props['opt_prop_names']:
    #                 print("Error: optical property %s associated to plot does not exist in vegetation optical properties list" % th_prop_name)
    #         check = False
    #     else:
    #         #check that indexes and ids are identical, if not, correct
    #         eq_serie = cross_plots_th_props["th_props.id"].eq(cross_plots_th_props["plots_th_props.index"])
    #         if len(eq_serie[eq_serie == False]):
    #             self.correct_plots_th_props()  # read cross_plots_thermal_props[index_eq for index_eq = False] -> find correspondance, correct in Plots Object
    #             print("Warning: Plots Thermal Props Indexes inconsistency has been corrected")
    #
    #     return check

    def get_thermal_props(self):
        """
        th_props.id: location of thermal property in the thermal properties list
        :return: DataFrame containing thermal properties names and indexes
        """
        thermal_props_dict = {"indexes": [], "names": []}
        thermal_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.Temperatures.ThermalFunction
        for i,th_prop in enumerate(thermal_props_list):
            thermal_props_dict["indexes"].append(i)
            thermal_props_dict["names"].append(th_prop.idTemperature)
        return pd.DataFrame(thermal_props_dict)

    def get_opt_props(self):
        """
        veg_props.id: location of optical property in the vegetation optical properties list
        lamb_props.id: location of optical property in the lambertian optical properties list
        hapke_props.id: location of optical property in the hapke optical properties list
        rpv_props.id: location of optical property in the rpv optical properties list
        :return: dictionnary containing, for each optical prop type, a DataFrame containing optical properties names and indexes
        """

        veg_opt_props_dict = {"indexes": [], "names": []}
        lamb_opt_props_dict = {"indexes": [], "names": []}
        hapke_opt_props_dict = {"indexes": [], "names": []}
        rpv_opt_props_dict = {"indexes": [], "names": []}
        fluid_opt_props_dict = {"indexes": [], "names": []}

        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti) > 0:
            veg_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti
            for i, veg_prop in enumerate(veg_props_list):
                veg_opt_props_dict["indexes"].append(i)
                veg_opt_props_dict["names"].append(veg_prop.ident)

        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti) > 0:
            lamb_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti
            for i,lamb_prop in enumerate(lamb_props_list):
                lamb_opt_props_dict["indexes"].append(i)
                lamb_opt_props_dict["names"].append(lamb_prop.ident)

        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.HapkeSpecularMultiFunctions.HapkeSpecularMulti) > 0:
            hapke_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.HapkeSpecularMultiFunctions.HapkeSpecularMulti
            for i, hapke_prop in enumerate(hapke_props_list):
                hapke_opt_props_dict["indexes"].append(i)
                hapke_opt_props_dict["names"].append(hapke_prop.ident)

        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.RPVMultiFunctions.RPVMulti) > 0:
            rpv_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.RPVMultiFunctions.RPVMulti
            for i, rpv_prop in enumerate(rpv_props_list):
                rpv_opt_props_dict["indexes"].append(i)
                rpv_opt_props_dict["names"].append(rpv_prop.ident)

        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.AirMultiFunctions.AirFunction) > 0:
            fluid_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.AirMultiFunctions.AirFunction
            for i, fluid_prop in enumerate(fluid_props_list):
                fluid_opt_props_dict["indexes"].append(i)
                fluid_opt_props_dict["names"].append(fluid_prop.ident)

        opt_props = {"vegetation": pd.DataFrame(veg_opt_props_dict), "lambertian" : pd.DataFrame(lamb_opt_props_dict),
                     "hapke" : pd.DataFrame(hapke_opt_props_dict), "rpv":pd.DataFrame(rpv_opt_props_dict),
                     "fluid" : pd.DataFrame(fluid_opt_props_dict)}

        return opt_props

    def extract_plots_full_table(self):
        """
        extract a DataFrame containing Plots information, directly from plots_obj (self.xdsobjs_dict["plots"])
        :return: DataFrame containing Plot fields
        """
        plots_table_header = ['PLT_TYPE', 'PT_1_X', 'PT_1_Y', 'PT_2_X', 'PT_2_Y', 'PT_3_X', 'PT_3_Y', 'PT_4_X',
                              'PT_4_Y',
                              'GRD_OPT_TYPE', 'GRD_OPT_NUMB', 'GRD_OPT_NAME', 'GRD_THERM_NUMB', 'GRD_THERM_NAME',
                              'PLT_OPT_NUMB', 'PLT_OPT_NAME', 'PLT_THERM_NUMB', 'PLT_THERM_NAME',
                              'PLT_BTM_HEI','PLT_HEI_MEA', 'PLT_STD_DEV', 'VEG_DENSITY_DEF', 'VEG_LAI', 'VEG_UL']
        plots_opt_props_dict = {}

        for field in plots_table_header:
            plots_opt_props_dict[field] = []

        rows = []

        plots_list = self.xsdobjs_dict["plots"].Plots.Plot
        for plot in plots_list:
            plt_btm_hei, plt_hei_mea, plt_std_dev = None, None, None
            vet_density_def, veg_lai, veg_ul = None, None, None

            plot_opt_number, plot_opt_name, plt_therm_number, plt_therm_name = None, None, None, None

            grd_opt_type, grd_opt_number, grd_opt_name, plt_therm_number, plt_therm_name = None, None, None, None, None

            plt_type = plot.type_

            #if plot.form = "corners": else: calculate corners
            points_list = plot.Polygon2D.Point2D
            x1, y1 = points_list[0].x, points_list[0].y
            x2, y2 = points_list[1].x, points_list[1].y
            x3, y3 = points_list[2].x, points_list[2].y
            x4, y4 = points_list[3].x, points_list[3].y


            if plt_type in [1,2]: # vegetation or vegetation+ground
                plot_opt_number = plot.PlotVegetationProperties.VegetationOpticalPropertyLink.indexFctPhase
                plot_opt_name = plot.PlotVegetationProperties.VegetationOpticalPropertyLink.ident
                plt_therm_number = plot.PlotVegetationProperties.GroundThermalPropertyLink.indexTemperature
                plt_therm_name = plot.PlotVegetationProperties.GroundThermalPropertyLink.idTemperature

                plt_btm_hei, plt_hei_mea, plt_std_dev = plot.PlotVegetationProperties.VegetationGeometry.baseheight, \
                                                        plot.PlotVegetationProperties.VegetationGeometry.height, \
                                                        plot.PlotVegetationProperties.VegetationGeometry.stDev

                veg_density_def = plot.PlotVegetationProperties.densityDefinition
                if veg_density_def == 0:
                    veg_lai = plot.PlotVegetationProperties.LAIVegetation.LAI
                if veg_density_def == 1:
                    veg_ul = plot.PlotVegetationProperties.UFVegetation.UF

            if plt_type in [0,2]:# ground or vegetation+ground
                grd_opt_type = plot.GroundOpticalPropertyLink.type_
                grd_opt_number = plot.GroundOpticalPropertyLink.indexFctPhase
                grd_opt_name = plot.GroundOpticalPropertyLink.ident
                grd_therm_number = plot.GroundThermalPropertyLink.indexTemperature
                grd_therm_name = plot.GroundThermalPropertyLink.idTemperature

            if plt_type == 3: #fluid
                plot_opt_number = plot.PlotAirProperties.AirOpticalProperties[0].AirOpticalPropertyLink.indexFctPhase
                plot_opt_name = plot.PlotAirProperties.AirOpticalProperties[0].AirOpticalPropertyLink.ident
                plt_therm_number = plot.PlotAirProperties.GroundThermalPropertyLink.indexTemperature
                plt_therm_name = plot.PlotAirProperties.GroundThermalPropertyLink.idTemperature

                plt_btm_hei, plt_hei_mea, plt_std_dev = plot.PlotAirProperties.AirGeometry.baseheight, \
                                                        plot.PlotAirProperties.AirGeometry.height, \
                                                        plot.PlotAirProperties.AirGeometry.stDev

            # plots_table_header = ['PLT_TYPE', 'PT_1_X', 'PT_1_Y', 'PT_2_X', 'PT_2_Y', 'PT_3_X', 'PT_3_Y', 'PT_4_X',
            #                       'PT_4_Y',
            #                       'GRD_OPT_TYPE', 'GRD_OPT_NUMB', 'GRD_OPT_NAME', 'GRD_THERM_NUMB', 'GRD_THERM_NAME',
            #                       'PLT_OPT_NUMB', 'PLT_OPT_NAME', 'PLT_THERM_NUMB', 'PLT_THERM_NAME',
            #                       'PLT_BTM_HEI', 'PLT_HEI_MEA', 'PLT_STD_DEV', 'VEG_DENSITY_DEF', 'VEG_LAI', 'VEG_UL']

            row_to_add = [plt_type, x1, y1, x2, y2, x3, y3, x4, y4,
                          grd_opt_type, grd_opt_number, grd_opt_name, grd_therm_number, grd_therm_name,
                          plot_opt_number, plot_opt_name, plt_therm_number, plt_therm_name,
                          plt_btm_hei, plt_hei_mea, plt_std_dev, veg_density_def, veg_lai, veg_ul]

            rows.append(row_to_add)

        return pd.DataFrame(rows, columns=plots_table_header)

    # def get_plots_opt_props(self):
    #     """
    #     plots_opt_props.index: indexFctPhase attribute of the (vegetation) optical property associated to the plot
    #     :return:
    #     """
    #     plots_opt_props_dict = {"plots_opt_props.index": [], "opt_prop_names": []}
    #     plots_list = self.xsdobjs_dict["plots"].Plots.Plot
    #     for plot in plots_list:
    #         plots_opt_props_dict["plots_opt_props.index"].append(plot.PlotVegetationProperties.VegetationOpticalPropertyLink.indexFctPhase)
    #         plots_opt_props_dict["opt_prop_names"].append(plot.PlotVegetationProperties.VegetationOpticalPropertyLink.ident)
    #     return pd.DataFrame(plots_opt_props_dict)
    #
    # def get_plots_thermal_props(self):
    #     """
    #     plots_th_props.index: indexTemperature attribute of the thermal property associated to the plot
    #     :return:
    #     """
    #     plots_th_props_dict = {"indexes": [], "names": []}
    #     plots_list = self.xsdobjs_dict["plots"].Plots.Plot
    #     for plot in plots_list:
    #         plots_th_props_dict["indexes"].append(plot.PlotVegetationProperties.GroundThermalPropertyLink.indexTemperature)
    #         plots_th_props_dict["names"].append(plot.PlotVegetationProperties.GroundThermalPropertyLink.idTemperature)
    #     return pd.DataFrame(plots_th_props_dict)


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
        check1 = self.check_sp_bands()
        check2 = self.check_properties_indexes_through_tables()
        #check2 = self.check_plots_optical_props()
        #check3 = self.check_scene_optical_props()
        #check4 = self.check_object_3d_opt_props()
        #return(check1 and check2 and check3 and check4)
        return (check1 and check2)

    def check_sp_bands(self):
        """
        check that the number of number of parameters associated to optical properties for each spectral band is different to the number of spectral bands in phase.xml file

        if spectral band multiplicative factors are missing in coeff_diff XSD module with respect to the number of spectral bands in phase XSD module,
        default multiplicative factors are introduced for each missing spectral band

        :return: True if the number of spectral bands in phase XSD module is equal to the number of spectral bandds in each optical property given in coeff_diff XSD module
                      (including if this has been corrected)
                 False otherwise
        """
        check = False
        spbands_nb_phase = len(self.xsdobjs_dict["phase"].Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties)

        #lambertian opt properties
        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti)>0:
            spbands_nb_coeff_lamb = len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti[0].
                                        lambertianNodeMultiplicativeFactorForLUT.lambertianMultiplicativeFactorForLUT)
        else:
            spbands_nb_coeff_lamb=0

        #hapke opt properties
        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.HapkeMultiFunctions.HapkeMulti)>0:
            spbands_nb_coeff_hapke = len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.HapkeMultiFunctions.HapkeMulti[0].
                                        hapkeNodeMultiplicativeFactorForLUT.hapkeMultiplicativeFactorForLUT)
        else:
            spbands_nb_coeff_hapke=0

        #rpv opt properties
        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.RPVMultiFunctions.RPVMulti)>0:
            spbands_nb_coeff_rpv = len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.RPVMultiFunctions.RPVMulti[0].
                                        RPVNodeMultiplicativeFactorForLUT.RPVMultiplicativeFactorForLUT)
        else:
            spbands_nb_coeff_rpv=0

        #fluid opt properties
        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.AirMultiFunctions.AirFunction)>0:
            spbands_nb_coeff_air = len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.AirMultiFunctions.AirFunction[0].
                                        AirFunctionNodeMultiplicativeFactorForLUT.AirFunctionMultiplicativeFactorForLUT)
        else:
            spbands_nb_coeff_air=0


        #understory opt properties
        if len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti) > 0:
            spbands_nb_coeff_veg = len(self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti[0].
                                       understoryNodeMultiplicativeFactorForLUT.understoryMultiplicativeFactorForLUT)
        else:
            spbands_nb_coeff_veg = 0

        #if needed, correct sp bands number phase and coeff_diff module inconsistency: this code should be very much compacted!!!
        if spbands_nb_phase != spbands_nb_coeff_lamb or spbands_nb_phase != spbands_nb_coeff_hapke or spbands_nb_phase != spbands_nb_coeff_rpv or spbands_nb_phase != spbands_nb_coeff_air or spbands_nb_phase != spbands_nb_coeff_veg : #we take xsdobjs_dict["phase"] as the reference
            if spbands_nb_coeff_lamb < spbands_nb_phase:
                nb_missing_spbands = spbands_nb_phase - spbands_nb_coeff_lamb
                print("warning: ")
                print("adding %d spectral bands with global multiplicative factor to each lambertian optical property" % nb_missing_spbands)
                for i in range (spbands_nb_phase - spbands_nb_coeff_lamb):
                    self.add_lamb_multiplicative_factor_for_lut()
                check = True

            if spbands_nb_coeff_hapke < spbands_nb_phase:
                nb_missing_spbands = spbands_nb_phase - spbands_nb_coeff_hapke
                print("warning: ")
                print("adding %d spectral bands with global multiplicative factor to each hapke optical property" % nb_missing_spbands)
                for i in range (spbands_nb_phase - spbands_nb_coeff_hapke):
                    self.add_hapke_multiplicative_factor_for_lut()
                check = True

            if spbands_nb_coeff_rpv < spbands_nb_phase:
                nb_missing_spbands = spbands_nb_phase - spbands_nb_coeff_rpv
                print("warning: ")
                print("adding %d spectral bands with global multiplicative factor to each rpv optical property" % nb_missing_spbands)
                for i in range (spbands_nb_phase - spbands_nb_coeff_rpv):
                    self.add_rpv_multiplicative_factor_for_lut()
                check = True

            if spbands_nb_coeff_air < spbands_nb_phase:
                nb_missing_spbands = spbands_nb_phase - spbands_nb_coeff_air
                print("warning: ")
                print("adding %d spectral bands with global multiplicative factor to each air optical property" % nb_missing_spbands)
                for i in range (spbands_nb_phase - spbands_nb_coeff_air):
                    self.add_air_multiplicative_factor_for_lut()
                check = True

            if spbands_nb_coeff_veg < spbands_nb_phase:
                nb_mission_spbands = spbands_nb_phase - spbands_nb_coeff_veg
                print("warning: ")
                print("adding %d spectral bands with global multiplicative factor to each vegetation optical properties" % nb_mission_spbands)
                for i in range (spbands_nb_phase - spbands_nb_coeff_lamb):
                    self.add_veg_multiplicative_factor_for_lut()
                check = True
        else:
            check = True
        return check

    def add_hapke_multiplicative_factor_for_lut(self):
        """
        add a multiplicatif factor for each lambertian optical property in coeff_diff module
        """
        hapke_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti
        for hapke_opt_prop in hapke_opt_props_list:
            hapke_opt_prop.hapkeNodeMultiplicativeFactorForLUT.add_hapkeMultiplicativeFactorForLUT(ptd.coeff_diff.create_hapkeMultiplicativeFactorForLUT())

    def add_rpv_multiplicative_factor_for_lut(self):
        """
        add a multiplicatif factor for each lambertian optical property in coeff_diff module
        """
        rpv_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.RPVMultiFunctions.RPVMulti
        for rpv_opt_prop in rpv_opt_props_list:
            rpv_opt_prop.RPVNodeMultiplicativeFactorForLUT.add_RPVMultiplicativeFactorForLUT(ptd.coeff_diff.create_RPVMultiplicativeFactorForLUT())

    def add_air_multiplicative_factor_for_lut(self):
        """
        add a multiplicatif factor for each lambertian optical property in coeff_diff module
        """
        air_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.AirMultiFunctions.AirFunction
        for air_opt_prop in air_opt_props_list:
            air_opt_prop.RPVNodeMultiplicativeFactorForLUT.add_AirFunctionMultiplicativeFactorForLUT(ptd.coeff_diff.create_AirFunctionMultiplicativeFactorForLUT())


    def add_lamb_multiplicative_factor_for_lut(self):
        """
        add a multiplicatif factor for each lambertian optical property in coeff_diff module
        """
        lambertian_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti
        for lamb_opt_prop in lambertian_opt_props_list:
            lamb_opt_prop.lambertianNodeMultiplicativeFactorForLUT.add_lambertianMultiplicativeFactorForLUT(ptd.coeff_diff.create_lambertianMultiplicativeFactorForLUT())

    def add_veg_multiplicative_factor_for_lut(self):
        """
        add a multiplicatif factor for each vegetation optical property in coeff_diff module
        """
        veg_opt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti
        for veg_opt_prop in veg_opt_props_list:
            veg_opt_prop.understoryNodeMultiplicativeFactorForLUT.add_understoryMultiplicativeFactorForLUT(ptd.coeff_diff.create_understoryMultiplicativeFactorForLUT())

    # def get_vegoptprop_index(self, vegoptprop_name):
    #     """
    #     search for vegetation property having ident attribute matching vegoptprop_name in coeff_diff object
    #     :param vegoptprop_name:
    #     :return: if found, index of vegetation property in the vegetation opt properties list, None if not found
    #     """
    #     index = None
    #     vegopt_props_list = self.xsdobjs_dict["coeff_diff"].Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti
    #     for i,vegopt_prop in enumerate(vegopt_props_list):
    #         if vegopt_prop.ident == vegoptprop_name:
    #             index = i
    #             return index
    #     return index
    #
    # def get_lamboptprop_index(self, lamboptprop_name):
    #     """
    #     search for lambertian property having ident attribute matching lamboptprop_name in coeff_diff object
    #     :param lamboptprop_name:
    #     :return: if found , index of lambertian property in the vegetation opt properties list, None if not found
    #     """
    #     index = None
    #     lambopt_propsList = self.xsdobjs_dict["coeff_diff"].Coeff_diff.LambertianMultiFunctions.LambertianMulti
    #     for i,lambOptProp in enumerate(lambopt_propsList):
    #         if lambOptProp.ident == lamboptprop_name:
    #             index = i
    #             return index
    #     return index


    # def check_plots_optical_props(self):
    #     """
    #     check if every optical property associated to plots exist in optical properties list (ToDo: thermal properties, ThermalPropertyLink, idTemperature, indexTemperature)
    #     :return: True if associated properties are found in properties lists, False if not
    #     """
    #     check = True
    #     plots_list = self.xsdobjs_dict["plots"].Plots.Plot
    #     for i,plot in enumerate(plots_list):
    #         prop_name = plot.PlotVegetationProperties.VegetationOpticalPropertyLink.ident
    #         print("plot %d: checking vegopt_prop %s" % (i,prop_name))
    #         index = self.get_vegoptprop_index(prop_name)
    #         if (index == None):
    #             print("warning: opt_prop %s does not exist in vegetation Optical Properties List" % prop_name)
    #             return False
    #         else:
    #             if plot.PlotVegetationProperties.VegetationOpticalPropertyLink.indexFctPhase != index:
    #                 print("warning:  opt_prop %s index inconsistency, correcting index" % prop_name)
    #                 plot.PlotVegetationProperties.VegetationOpticalPropertyLink.indexFctPhase = index
    #     return check

    def check_scene_optical_props(self):
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

    def check_object_3d_opt_props(self):
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
            new_simu_path = pjoin(self.getsimupath(), "..",modified_simu_name)
            new_inputsimu_path = pjoin(new_simu_path, "input")
            xml_file_path = pjoin(new_inputsimu_path, fname + ".xml")
        else:
            xml_file_path = pjoin(self.getinputsimupath(), fname + ".xml")
        xml_file = open(xml_file_path, "w")
        xml_file.write(xmlstr)
        xml_file.close()


###################################################
##### USER FRIENDLY FUNCTIONS ###################

    def add_sp_bands(self, spbands_list):
        for sp_band in spbands_list:
            sp_int_props = ptd.phase.create_SpectralIntervalsProperties(meanLambda=sp_band[0], deltaLambda=sp_band[1])
            self.xsdobjs_dict["phase"].Phase.DartInputParameters.SpectralIntervals.add_SpectralIntervalsProperties(sp_int_props)
            sp_irr_value = ptd.phase.create_SpectralIrradianceValue()
            self.xsdobjs_dict["phase"].Phase.DartInputParameters.nodeIlluminationMode.SpectralIrradiance.add_SpectralIrradianceValue(sp_irr_value)


    #ToDo
    #refreshObjFromTables(auto=True) : aimed to be launched automatically after each Table Modification, or manually
    #def add_bands()
    #def add_multiplots()
    #add_sequence()
    #add_optprop()
    # def writeToXML(self):
