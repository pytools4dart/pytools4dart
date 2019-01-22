# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <florian.deboissiu@irstea.fr>
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
This module contains the class "Scene".
"""

import pandas as pd
import warnings
import pytools4dart as ptd
from pytools4dart.helpers import constants
from pytools4dart.add import Poly_corners, Polygone_plot_vol_info

class Scene(object):
    def __init__(self, simu):
        self.simu = simu
        self.properties = {}
        self.plots = pd.DataFrame()
        self.trees = pd.DataFrame()
        self.obj3d = pd.DataFrame()
        self.update_dims()
        # self.scene_dimensions = [self.simu.core.xsdobjs["maket"].Maket.Scene.SceneDimensions.x, self.simu.core.xsdobjs["maket"].Maket.Scene.SceneDimensions.y]
        # self.cell_dimensions = [self.simu.core.xsdobjs["maket"].Maket.Scene.CellDimensions.x, self.simu.core.xsdobjs["maket"].Maket.Scene.CellDimensions.z]

    def update_xsdobjs(self):
        self.update_plots_op_index() # update properties indexes
        self.update_plots_tp_index()
        self.update_plots_obj()
        self.update_properties_obj()
        #self.update_trees() this summary table is not yet available
        #self.update_obj3d  this summary table is not yet available

    def update_plots_op_index(self):
        """
        updates scene.plots GRD_OPT_NUMB and PLT_OPT_NUMB columns with optical properties indexes

        """
        # PLT_TYPE = pd.DataFrame([[0, 'Ground'],
        #                                [1, 'Vegetation'],
        #                                [2, 'Vegetation+Ground'],
        #                                [3, 'Fluid'],
        #                                [4, 'Water']], columns=['type_int', 'type_str'])
        properties = self.simu.scene.properties["optical"]
        op_duplicates = properties.duplicated('ident')
        if any(op_duplicates):
            properties = properties.copy()[~op_duplicates]
            warnings.warn('Optical properties contains "ident" duplicates.')

        plots = self.simu.scene.plots
        ground = plots.PLT_TYPE.cat.codes.isin([0,2])
        turbid = plots.PLT_TYPE.cat.codes.isin([1,2,3,4])

        if any(ground):
            index = pd.merge(plots[ground], properties,
                     left_on=['GRD_OPT_TYPE', 'GRD_OPT_NAME'],
                     right_on=['type', 'ident'], how='left')['index']
            if (any(index.isna())):  # signal optical properties not found
                warnings.warn('Optical properties "ident" not found: {}'.format(
                    ', '.join(plots[ground].PLT_OPT_NAME[index.isna()].unique())))
            plots.loc[ground, 'GRD_OPT_NUMB'] = index

        if any(turbid):
            index=pd.merge(
                plots[turbid],
                properties, # [properties.type.isin(['Vegetation', 'Fluid', 'Water'])]
                     left_on=['PLT_OPT_NAME'],
                     right_on=['ident'], how='left')['index']
            if(any(index.isna())): # signal optical properties not found
                warnings.warn('Optical properties "ident" not found: {}'.format(
                    ', '.join(plots[turbid].PLT_OPT_NAME[index.isna()].unique())))
            plots.loc[turbid, 'PLT_OPT_NUMB'] = index


    def update_plots_tp_index(self):
        """
        updates scene.plots GRD_THERM_NUMB and PLT_THERM_NUMB columns with temperature properties indexes

        """
        # PLT_TYPE = pd.DataFrame([[0, 'Ground'],
        #                                [1, 'Vegetation'],
        #                                [2, 'Vegetation+Ground'],
        #                                [3, 'Fluid'],
        #                                [4, 'Water']], columns=['type_int', 'type_str'])
        properties = self.simu.scene.properties["thermal"]
        tp_duplicates = properties.duplicated('idTemperature')
        if any(tp_duplicates):
            properties = properties.copy()[~tp_duplicates]
            warnings.warn('Thermal properties contains "idTemperature" duplicates.')

        plots = self.simu.scene.plots
        ground = plots.PLT_TYPE.cat.codes.isin([0, 2])
        turbid = plots.PLT_TYPE.cat.codes.isin([1, 2, 3, 4])
        # plots.PLT_TYPE = PLT_TYPE_table
        # cross PLT_TYPE=1 GROUND
        if any(ground):
            index = pd.merge(plots[ground], properties,
                     left_on=['GRD_OPT_TYPE', 'GRD_THERM_NAME'],
                     right_on=['idTemperature'], how='left')['index']
            if (any(index.isna())):  # signal thermal properties not found
                warnings.warn('Thermal properties "idTemperature" not found: {}'.format(
                    ', '.join(plots[ground].PLT_THERM_NAME[index.isna()].unique())))
            plots.loc[ground, 'GRD_THERM_NUMB'] = index


        if any(turbid):
            index = pd.merge(
                plots[turbid],
                properties,  # [properties.type.isin(['Vegetation', 'Fluid', 'Water'])]
                left_on=['PLT_THERM_NAME'],
                right_on=['idTemperature'], how='left')['index']
            if (any(index.isna())):  # signal thermal properties not found
                warnings.warn('Thermal properties "idTemperature" not found: {}'.format(
                    ', '.join(plots[turbid].PLT_THERM_NAME[index.isna()].unique())))
            plots.loc[turbid, 'PLT_THERM_NUMB'] = index


    def update_plots_obj(self):
        """
        populates core plots according to scene.plots dataframe contents
        """
        # plots_table_header = ['PLT_NUMBER', 'PLOT_SOURCE', 'PLT_TYPE', 'PT_1_X', 'PT_1_Y', 'PT_2_X', 'PT_2_Y', 'PT_3_X',
        #                       'PT_3_Y',
        #                       'PT_4_X',
        #                       'PT_4_Y',
        #                       'GRD_OPT_TYPE', 'GRD_OPT_NUMB', 'GRD_OPT_NAME', 'GRD_THERM_NUMB', 'GRD_THERM_NAME',
        #                       'PLT_OPT_NUMB', 'PLT_OPT_NAME', 'PLT_THERM_NUMB', 'PLT_THERM_NAME',
        #                       'PLT_BTM_HEI', 'PLT_HEI_MEA', 'PLT_STD_DEV', 'VEG_DENSITY_DEF', 'VEG_LAI', 'VEG_UL']

        plots_header = constants.plots_table_header
        for plot in self.plots.itertuples():
            polygon_corners = Poly_corners(x1 = plot.PT_1_X, y1 = plot.PT_1_Y, x2 = plot.PT_2_X, y2 = plot.PT_2_Y,
                                           x3 = plot.PT_3_X, y3 = plot.PT_3_Y, x4 = plot.PT_4_X, y4 = plot.PT_4_Y)
            vol_info = Polygone_plot_vol_info(poly_corners=polygon_corners, btm_hei= plot.PLT_BTM_HEI , hei_mea=plot.PLT_HEI_MEA, std_dev=plot.PLT_STD_DEV)
            self.simu.add.plot(plot_type = plot.PLT_TYPE, volume_info=vol_info, plot_opt_prop_name = plot.PLT_OPT_NAME, plot_therm_prop_name=plot.PLT_THERM_NAME,
                               grd_opt_prop_type = plot.GRD_OPT_TYPE, grd_opt_prop_name = plot.GRD_OPT_NAME, grd_therm_prop_name = plot.GRD_THERM_NAME,
                               createProps=True)

    def update_properties_obj(self):
        """
        populates core optical/thermal properties according to scene.properties dataframe (new) contents
        """
        th_props_df = self.properties["thermal_props"]
        opt_props_dict = self.properties["opt_props"]

        for (i, th_prop) in th_props_df.iterrows():
            index = self.simu.get_thermal_prop_index(th_prop["prop_name"])
            if index == None: # if thermal property does not exists, add
                self.simu.add.thermal_property(idTemperature = th_prop["prop_name"])
            else: # if thermal property exists but invalid index
                if index != th_prop["prop_index"]:
                    print("WARNING: invalid prop_index, to be corrected ")
                    th_props_df.at[i, "prop_index"] = index

        for opt_prop_type, opt_props_df in opt_props_dict.iteritems():
            for (i, opt_prop) in opt_props_df.iterrows():
                index = self.simu.get_opt_prop_index(opt_prop_type,opt_prop["prop_name"])
                if index == None:  # if optical property does not exists, add
                    self.simu.add.optical_property(opt_prop_type, ident=opt_prop["prop_name"])
                else:
                    if index != opt_prop["prop_index"]:
                        print("WARNING: invalid prop_index, to be corrected ")
                        opt_props_df.at[i,"prop_index"] = index

    def update_dims(self):
        self.update_scene_size()
        self.update_cell_size()

    def update_scene_size(self):
        self.scene_dimensions = [self.simu.core.xsdobjs["maket"].Maket.Scene.SceneDimensions.x,
                                 self.simu.core.xsdobjs["maket"].Maket.Scene.SceneDimensions.y]

    def update_cell_size(self):
        self.cell_dimensions = [self.simu.core.xsdobjs["maket"].Maket.Scene.CellDimensions.x,
                                self.simu.core.xsdobjs["maket"].Maket.Scene.CellDimensions.z]

    def update_properties_dict(self):
        """
        updates self.properties_dict variable
        """
        self.properties = self.simu.core.extract_properties_dict()

    def set_scene_size(self, scene_size):
        x = scene_size[0]
        y = scene_size[1]

        self.simu.core.xsdobjs["maket"].Maket.Scene.SceneDimensions.x = x
        self.simu.core.xsdobjs["maket"].Maket.Scene.SceneDimensions.y = y

        self.update_scene_size()


    def set_cell_size(self, cell_size):
        x = cell_size[0]
        z = cell_size[1]

        self.simu.core.xsdobjs["maket"].Maket.Scene.CellDimensions.x = x
        self.simu.core.xsdobjs["maket"].Maket.Scene.CellDimensions.z = z

        self.update_cell_size()

    def add_plot_in_DF(self):
        """
        TODo : add a row in plots DF, independently from core plots
        :return:
        """
        self.simu.update.lock_tabs = True

    def add_property_in_DF(self):
        """
        TODo : add a row in plots DF, independently from core plots
        :return:
        """
        self.simu.update.lock_tabs = True


