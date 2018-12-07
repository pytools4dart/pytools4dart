# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
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
This module contains the class "Checker".
"""

import pandas as pd

from pytools4dart.helpers.constants import *

class Checker(object):

    def __init__(self, simu):
        self.simu = simu

    def module_dependencies(self):
        """
        Cross check XSD module dependencies:

        * check optical properties names associated to scene objects (plots, soil, object3D, trees(To be done)) exist in optical/thermal properties lists (coeff_diff.xml file)
        * check if the number of spectral intervals associated to each optical property in coeff_diff
         is equal to the number of spectral bands in phase.xml file

        if optical/thermal property associated to scene object is missing in the optical/thermal property list, a warning is printed, asking the user to fix this inconsistency.

        if spectral band multiplicative factors are missing in coeff_diff.xml file with respect to the number of spectral bands in phase.xml file,
        additional default multiplicative factors are introduced

        :return:    True if every checks are satisfied (even if additional multiplicative factor have been created),
                    False if one or several checks are not satisfied
        """
        print ("checking module dependencies")
        check1 = self.simu.add.check_and_correct_sp_bands()
        check2 = self.properties_indexes()
        if (check1 and check2):
            print("Module Dependencies OK")
        else:
            print("ERROR: There are Module Dependencies ISSUES")
        return (check1 and check2)

    def is_tree_txt_file_considered(self):
        return self.simu.core.xsdobjs["trees"].Trees.Trees_1 != None


    def properties_indexes(self, createProps = False):
        """
        Cross check properties of every mockup element (plots, scene, object3d, trees) with properties DataFrames.
        Att: In the case of plots.txt et trees.txt, we can only check if the given property index does exist
        :return:
        """
        self.simu.core.update()
        check_plots = self.plots_props()
        check_scene = self.scene_props()
        check_object3d = self.object_3d_props()
        if self.is_tree_txt_file_considered():# if additional tree.txt like file is considered
            check_trees_txt_props = self.trees_txt_props()
        else:
            check_trees_txt_props = True  # has no impact on return value

        return check_plots and check_scene and check_object3d and check_trees_txt_props


    def plots_props(self):
        """
        Check plots optical/thermal properties consistency
        If property does not exist, an Error message is printed, asking the user to fix
        If property does exist but indexes correspondance is not ensured, this is corrected and a warning message is printed
        :return: True if check is ok or if just indexes inconsistency is corrected, False in any other case.
        """
        check_plots_opt_props = self.plots_opt_props()
        check_plots_thermal_props = self.plots_thermal_props()

        if self.simu.is_plots_txt_file_considered(): # if additional plots.txt like file is considered
            check_plots_txt_props = self.plots_txt_props()
        else:
            check_plots_txt_props = True # has no impact on return value

        return check_plots_opt_props and check_plots_thermal_props and check_plots_txt_props

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
        plots_full_table = self.simu.scene.plots

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
        plots_full_table = self.simu.scene.plots

        plots_by_plot_type = {}  # dictionnary of full plot data frames splitted according to opt_prop_type (vegetation, turbid, lamb, hapke, rpv)
        plots_by_plot_type["veg_vegplusground_fluid"] = plots_full_table[
            plots_full_table['PLT_TYPE'].isin([1, 2, 3])]  # plot type = vegetation or vegetation+ground or fluid
        plots_by_plot_type["ground"] =  plots_full_table[plots_full_table['PLT_TYPE'].isin([0,2])]

        return plots_by_plot_type

    def plots_opt_props(self):
        check = True
        opt_props = self.simu.scene.properties["opt_props"]
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
                        print("%s property %s does not exist, please FIX" % (opt_prop_type,missing_prop))
                else: #opt_prop_type in ["lambertian","hapke","rpv"]
                    missing_props = plots[~(plots['GRD_OPT_NAME'].isin(cross_props["prop_name"]))]['GRD_OPT_NAME']
                    for missing_prop in missing_props:
                        print("%s property %s does not exist, please FIX" % (opt_prop_type,missing_prop))

            else: # if plots/ground properties DO exist in properties list, check if indexes match
                if opt_prop_type in ["vegetation","fluid"]:
                    eq_serie = cross_props["prop_index"].eq(cross_props["PLT_OPT_NUMB"])
                    if len(eq_serie[eq_serie == False]):
                        print("ERROR: indexes inconsistency, proceed to correction ")# TO Be TESTED!!
                        for i, eq_value in enumerate(eq_serie):
                            if eq_value == False:
                                plot_number = cross_props["PLT_NUMB"]
                                prop_index = cross_props[i]["prop_index"]
                                self.simu.scene.plots.iloc[plot_number]["PLT_OPT_NUMB"] = prop_index
                                plot = self.simu.core.xsdobjs["plots"].Plots.Plot[plot_number]
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
                                self.simu.scene.plots.iloc[plot_number]["GRD_OPT_NUMB"] = prop_index  # correct index in Plots DataFrame
                                #correct index in PlotsObject:
                                plot = self.simu.core.xsdobjs["plots"].Plots.Plot[plot_number]
                                plot.GroundOpticalPropertyLink.indexFctPhase = prop_index
        return check

    def plots_thermal_props(self):

        check = True

        thermal_props = self.simu.scene.properties["thermal_props"]
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
                        print("%s property %s does not exist, please FIX" % (plot_type, missing_prop))
                else:  # plot_type == "ground"
                    missing_props = plots[~(plots['GRD_THERM_NAME'].isin(cross_props["prop_name"]))]['GRD_THERM_NAME']
                    for missing_prop in missing_props:
                        print("%s property %s does not exist, please FIX" % (plot_type, missing_prop))
            else:  # if plots/ground properties do exist in properties list, check if indexes match
                if plot_type == "veg_vegplusground_fluid":
                    eq_serie = cross_props["prop_index"].eq(cross_props["PLT_THERM_NUMB"])
                    if len(eq_serie[eq_serie == False]):
                        print("ERROR: indexes inconsistency, proceed to correction ") # TO Be TESTED!!
                        for i, eq_value in enumerate(eq_serie):
                            if eq_value == False:
                                plot_number = cross_props["PLT_NUMB"]
                                prop_index = cross_props[i]["prop_index"]
                                self.simu.scene.plots.iloc[plot_number]["PLT_THERM_NUMB"] = prop_index
                                plot = self.simu.core.xsdobjs["plots"].Plots.Plot[plot_number]
                                plot.PlotVegetationProperties.GroundThermalPropertyLink.indexTemperature = prop_index
                else:  # plot_type == "ground"
                    eq_serie = cross_props["prop_index"].eq(cross_props["GRD_THERM_NUMB"])
                    if len(eq_serie[eq_serie == False]):
                        print("ERROR: indexes inconsistency, proceed to correction ")  # TO Be TESTED!!
                        for i, eq_value in enumerate(eq_serie):
                            if eq_value == False:
                                plot_number = cross_props["PLT_NUMB"]
                                prop_index = cross_props[i]["prop_index"]
                                self.simu.scene.plots.iloc[plot_number]["GRD_THERM_NUMB"] = prop_index
                                plot = self.simu.core.xsdobjs["plots"].Plots.Plot[plot_number]
                                plot.GroundThermalPropertyLink.indexTemperature = prop_index
        return check

    def scene_props(self):
        """
        check if optical property associated to soil exist in optical properties list
        :return:True if associated properties are found in properties lists, False if not
        """
        check = True
        #opt_prop
        opt_prop = self.simu.core.xsdobjs["maket"].Maket.Soil.OpticalPropertyLink
        opt_prop_name = opt_prop.ident
        opt_prop_type = grd_opt_prop_types_dict[opt_prop.type_]
        #index_opt_prop = self.checkandcorrect_opt_prop_exists(opt_prop_type,opt_prop_name,createProps)
        index_opt_prop = self.simu.get_opt_prop_index(opt_prop_type,opt_prop_name)

        th_prop = self.simu.core.xsdobjs["maket"].Maket.Soil.ThermalPropertyLink
        th_prop_name = th_prop.idTemperature
        #index_th_prop = self.checkandcorrect_th_prop_exists(th_prop_name, createProps)
        index_th_prop = self.simu.get_thermal_prop_index(th_prop_name)

        if index_opt_prop == None or index_th_prop == None:
                print("ERROR: opt_prop %s or th_prop %s does not exist, please fix" % (opt_prop_name,th_prop_name))
                return False
        else:
            if opt_prop.indexFctPhase != index_opt_prop:
                print("warning:  opt_prop %s index inconsistency, correcting index" % opt_prop_name)
                opt_prop.indexFctPhase = index_opt_prop
            if th_prop.indexTemperature != index_th_prop:
                print("warning:  th_prop %s index inconsistency, correcting index" % th_prop_name)
                th_prop.indexTemperature = index_th_prop

        return check

    def object_3d_props(self):
        """
        check if optical/thermal properties associated to all 3d objects groups exist in optical properties list
        if any optical/thermal proprerty does not exist, an Error message is displayed
        :return: True if every property associated to 3D ojects exist in properties lists
        """
        check = True

        obj3dList = self.simu.core.xsdobjs["object_3d"].object_3d.ObjectList.Object
        for obj3d in obj3dList:
            if obj3d.hasGroups == 1: # are there groups?
                groups = obj3d.Groups.Group
                for group in groups:
                    opt_prop = group.GroupOpticalProperties.OpticalPropertyLink
                    opt_prop_type = opt_prop.type_
                    opt_prop_name = opt_prop.ident
                    index_opt_prop = self.simu.get_opt_prop_index(grd_opt_prop_types_dict[opt_prop_type], opt_prop_name)

                    th_prop = group.GroupOpticalProperties.ThermalPropertyLink
                    th_prop_name = th_prop.idTemperature
                    index_th_prop = self.simu.get_thermal_prop_index(th_prop_name)

                    back_opt_prop = group.GroupOpticalProperties.BackFaceOpticalProperty.OpticalPropertyLink
                    back_opt_prop_type = back_opt_prop.type_
                    back_opt_prop_name = back_opt_prop.ident
                    index_back_opt_prop = self.simu.get_opt_prop_index(grd_opt_prop_types_dict[back_opt_prop_type], back_opt_prop_name)


                    back_th_prop = group.GroupOpticalProperties.BackFaceThermalProperty.ThermalPropertyLink
                    back_th_prop_name = back_th_prop.idTemperature
                    index_back_th_prop = self.simu.get_thermal_prop_index(back_th_prop_name)

                    if index_opt_prop == None or index_th_prop == None or index_back_opt_prop == None or index_back_th_prop == None:
                            print("ERROR: opt_prop %s or th_prop %s does not exist, please FIX" % (opt_prop_name,th_prop_name))
                            return False
                    else:
                        if opt_prop.indexFctPhase != index_opt_prop:
                            print("warning:  opt_prop %s index inconsistency, correcting index" % opt_prop_name)
                            opt_prop.indexFctPhase = index_opt_prop
                        if th_prop.indexTemperature != index_th_prop:
                            print("warning:  th_prop %s index inconsistency, correcting index" % th_prop_name)
                            th_prop.indexTemperature = index_th_prop
                        if back_opt_prop.indexFctPhase != index_back_opt_prop:
                            print("warning:  opt_prop %s index inconsistency, correcting index" % back_opt_prop_name)
                            opt_prop.indexFctPhase = index_back_opt_prop
                        if back_th_prop.indexTemperature != index_back_th_prop:
                            print("warning:  th_prop %s index inconsistency, correcting index" % back_th_prop_name)
                            th_prop.indexTemperature = index_back_th_prop
            else: # object without groups
                opt_prop = obj3d.ObjectOpticalProperties.OpticalPropertyLink
                opt_prop_type = opt_prop.type_
                opt_prop_name = opt_prop.ident
                index_opt_prop = self.simu.get_opt_prop_index(grd_opt_prop_types_dict[opt_prop_type], opt_prop_name)

                th_prop = obj3d.ObjectOpticalProperties.ThermalPropertyLink
                th_prop_name = th_prop.idTemperature
                index_th_prop = self.simu.get_thermal_prop_index(th_prop_name)

                if index_opt_prop == None or index_th_prop == None:
                    print("ERROR: opt_prop %s or th_prop %s does not exist, please FIX" % (opt_prop_name, th_prop_name))
                    return False
                else:
                    if opt_prop.indexFctPhase != index_opt_prop:
                        print("warning:  opt_prop %s index inconsistency, correcting index" % opt_prop_name)
                        opt_prop.indexFctPhase = index_opt_prop
                    if th_prop.indexTemperature != index_th_prop:
                        print("warning:  th_prop %s index inconsistency, correcting index" % th_prop_name)
                        th_prop.indexTemperature = index_th_prop
        return check

    def trees_txt_props(self):
        """
        check if 1/species ID given in trees.txt file exist
        and 2/ if opt/thermal properties associated to each specie do exist
        :return: True if every thing is ok, False if not
        """
        #self.update_properties_dict()
        veg_opt_props = self.simu.scene.properties["opt_props"]
        check = True

        file_path = self.simu.core.xsdobjs["trees"].Trees.Trees_1.sceneParametersFileName

        trees_df = self.simu.read_dart_txt_file_with_header(file_path, "\t")

        species_ids = trees_df['SPECIES_ID'].drop_duplicates()

        species_list = self.simu.core.xsdobjs["trees"].Trees.Trees_1.Specie

        for specie_id in species_ids:
            if int(specie_id) > len(species_list) - 1:
                print("Warning: specie_id %d does not exist in species list, please FIX" % int(specie_id))# launch warning, but allow simulation to go on, as in DART

        for i, specie in enumerate(species_list):
            trunk_opt_prop_link = specie.OpticalPropertyLink
            trunk_th_prop_link = specie.ThermalPropertyLink

            trunk_opt_idx = self.simu.get_opt_prop_index(grd_opt_prop_types_dict[trunk_opt_prop_link.type_] ,trunk_opt_prop_link.ident)
            trunk_th_idx = self.simu.get_thermal_prop_index(trunk_th_prop_link.idTemperature)

            if trunk_opt_idx == None:
                print("trunk_opt_prop %s for specie %d do not exist, please FIX" % (trunk_opt_prop_link.ident, i) )
                check = False

            if trunk_th_idx == None:
                print("trunk_th_prop %s for specie %d do not exist, please FIX" % (trunk_th_prop_link.idTemperature, i) )
                check = False

            crown_props_list = specie.CrownLevel
            for j, crown_prop in enumerate(crown_props_list):
                print("checking specie nb %d, crown level nb %d" % (i,j))
                crown_opt_prop_link = crown_prop.OpticalPropertyLink
                crown_th_prop_link = crown_prop.ThermalPropertyLink
                crown_veg_prop_link = crown_prop.VegetationProperty.VegetationOpticalPropertyLink
                crown_veg_th_link = crown_prop.VegetationProperty.ThermalPropertyLink
                crown_opt_idx = self.simu.get_opt_prop_index(grd_opt_prop_types_dict[crown_opt_prop_link.type_] ,crown_opt_prop_link.ident)
                crown_th_idx = self.simu.get_thermal_prop_index(crown_th_prop_link.idTemperature)
                crown_veg_opt_idx = self.simu.get_opt_prop_index("vegetation" ,crown_veg_prop_link.ident)
                crown_veg_th_idx = self.simu.get_thermal_prop_index(crown_veg_th_link.idTemperature)

                if crown_opt_idx == None:
                    print("crown_opt_prop %s for specie %d do not exist, please FIX" % (crown_opt_prop_link.ident, i) )
                    check = False

                if crown_th_idx == None:
                    print("crown_th_prop %s for specie %d do not exist, please FIX" % (crown_th_prop_link.idTemperature, i) )
                    check = False

                if crown_veg_opt_idx == None:
                    print("crown_veg_opt %s for specie %d do not exist, please FIX" % (crown_veg_prop_link.ident, i) )
                    check = False

                if crown_veg_th_idx == None:
                    print("crown_veg_th %s for specie %d do not exist, please FIX" % (crown_veg_th_link.idTemperature,i) )
                    check = False
        return check

    def plots_txt_props(self):
        """
        check if optical/thermal properties indexes given in plots.txt exist in properties lists
        WARNING: this method must not be called if self.xsd_core["plots"].Plots.addExtraPlotsTextFile != 1:
        :return:
        """
        self.simu.core.update_properties_dict()
        opt_props = self.simu.scene.properties["opt_props"]
        th_props = self.simu.scene.properties["thermal_props"]
        check = True

        file_path = self.simu.core.xsdobjs["plots"].Plots.ExtraPlotsTextFileDefinition.extraPlotsFileName

        plots_df = self.simu.read_dart_txt_file_with_header(file_path, " ")

        #GRD_OPT_TYPE GRD_OPT_NUMB GRD_THERM_NUMB PLT_OPT_NUMB PLT_THERM_NUMB
        if 'GRD_OPT_TYPE' in plots_df.keys() and 'GRD_OPT_NUMB' in plots_df.keys():
            grd_opt_props = plots_df[['GRD_OPT_TYPE','GRD_OPT_NUMB']].drop_duplicates()
            for i, grd_opt_prop in grd_opt_props.iterrows():
                opt_prop_type = grd_opt_prop_types_dict[int(grd_opt_prop['GRD_OPT_TYPE'])]
                opt_prop_index = int(grd_opt_prop['GRD_OPT_NUMB'])
                if len(opt_props[opt_prop_type]) < opt_prop_index + 1:
                    print(
                                "ERROR in %s file column GRD_OPT_NUMB: optical property index %d do not exist in properties list, please FIX" % (
                        file_path, opt_prop_index))
                    check = False

        if 'GRD_THERM_NUMB' in plots_df.keys():
            grd_therm_numbs = plots_df['GRD_THERM_NUMB'].drop_duplicates()
            for grd_therm_num in grd_therm_numbs:
                th_prop_index = int(grd_therm_num)
                if len(th_props) < th_prop_index + 1:
                    print(
                                "ERROR in %s file column GRD_THERM_NUMB: thermal property index %d do not exist in properties list, please FIX" % (
                        file_path, th_prop_index))
                    check = False

        if 'PLT_OPT_NUMB' in plots_df.keys():
            plt_opt_numbs = plots_df['PLT_OPT_NUMB'].drop_duplicates()
            for plt_opt_num in plt_opt_numbs:
                opt_prop_type = "vegetation"
                opt_prop_index = int(plt_opt_num)
                if len(opt_props[opt_prop_type]) < opt_prop_index + 1:
                    print(
                                "ERROR in %s file column PLT_OPT_NUMB: optical property index %d do not exist in properties list, please FIX" % (
                        file_path, opt_prop_index))
                    check = False

        if 'PLT_THERM_NUMB' in plots_df.keys():
            plt_therm_numbs = plots_df['PLT_THERM_NUMB'].drop_duplicates()
            for plt_therm_num in plt_therm_numbs:
                th_prop_index = int(plt_therm_num)
                if len(th_props) < th_prop_index + 1:
                    print(
                                "ERROR in %s file column PLT_THERM_NUMB: thermal property index %d do not exist in properties list, please FIX" % (
                        file_path, th_prop_index))
                    check = False

        return check


