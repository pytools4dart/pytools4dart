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
from pytools4dart.tools import constants

class Scene(object):
    def __init__(self, simu):

        self.simu = simu

        self._size = self.simu.core.maket.Maket.Scene.SceneDimensions

        self._cell = self.simu.core.maket.Maket.Scene.CellDimensions

        self._properties = Properties_(self.simu)
        # self.trees = pd.DataFrame()
        # self.obj3d = pd.DataFrame()
        # self.update_dims()
        # self.scene_dimensions = [self.simu.core.maket.Maket.Scene.SceneDimensions.x, self.simu.core.maket.Maket.Scene.SceneDimensions.y]
        # self.cell_dimensions = [self.simu.core.maket.Maket.Scene.CellDimensions.x, self.simu.core.maket.Maket.Scene.CellDimensions.z]

    def __repr__(self):

        description = '\n'.join(
            ['scene size : {}'.format(self.size),
             'cell size : {}'.format(self.cell),
             'ground:',
             '\tOptical property: {}'.format(self.ground.OpticalPropertyLink.ident),
             '\tThermal property: {}'.format(self.ground.ThermalPropertyLink.idTemperature),
             'number of plots : {}'.format(self.plots.shape[0]),
             'number of object 3D : {}'.format(self.object3D.shape[0]),
             'number of tree species : {}'.format(self.tree_species.shape[0]),
             'number of optical properties : {}'.format(self.properties.optical.shape[0]),
             'number of thermal properties : {}'.format(self.properties.thermal.shape[0])])

        return description

    @property
    def size(self):
        return [self._size.x, self._size.y]

        # return [self.simu.core.maket.Maket.Scene.SceneDimensions.x,
        #         self.simu.core.maket.Maket.Scene.SceneDimensions.y]

    @size.setter
    def size(self, size):
        self._size.x = size[0]
        self._size.y = size[1]
        # self.simu.core.maket.Maket.Scene.SceneDimensions.x = size[0]
        # self.simu.core.maket.Maket.Scene.SceneDimensions.y = size[1]

    @property
    def cell(self):
        return [self.simu.core.maket.Maket.Scene.CellDimensions.x,
                self.simu.core.maket.Maket.Scene.CellDimensions.z]

    @cell.setter
    def cell(self, size):
        self.simu.core.maket.Maket.Scene.CellDimensions.x = size[0]
        self.simu.core.maket.Maket.Scene.CellDimensions.z = size[1]

    @property
    def ground(self):
        return self.simu.core.maket.Maket.Soil

    @property
    def plots(self):
        return self.simu.core.get_plots_df()

    @property
    def object3D(self):
        return self.simu.core.get_object_3d_df()

    @property
    def trees(self):
        return self.simu.core.get_trees()

    @property
    def tree_species(self):
        return self.simu.core.get_tree_species()

    @property
    def properties(self):
        return self._properties
    # @properties.setter
    # def properties(self, value):
    #     raise Exception('Element not settable.')


    # def update_xsdobjs(self):
    #     self.update_plots_op_index() # update properties indexes
    #     self.update_plots_tp_index()
    #     self.update_plots_obj()
    #     self.update_properties_obj()
    #     #self.update_trees() this summary table is not yet available
    #     #self.update_obj3d  this summary table is not yet available



    # def update_plots_obj(self):
    #     """
    #     populates core plots according to scene.plots dataframe contents
    #     """
    #     # PLOTS_COLUMNS = ['PLT_NUMBER', 'PLOT_SOURCE', 'PLT_TYPE', 'PT_1_X', 'PT_1_Y', 'PT_2_X', 'PT_2_Y', 'PT_3_X',
    #     #                       'PT_3_Y',
    #     #                       'PT_4_X',
    #     #                       'PT_4_Y',
    #     #                       'GRD_OPT_TYPE', 'GRD_OPT_NUMB', 'GRD_OPT_NAME', 'GRD_THERM_NUMB', 'GRD_THERM_NAME',
    #     #                       'PLT_OPT_NUMB', 'PLT_OPT_NAME', 'PLT_THERM_NUMB', 'PLT_THERM_NAME',
    #     #                       'PLT_BTM_HEI', 'PLT_HEI_MEA', 'PLT_STD_DEV', 'VEG_DENSITY_DEF', 'VEG_LAI', 'VEG_UL']
    #
    #     plots_header = constants.PLOTS_COLUMNS
    #     for plot in self.plots.itertuples():
    #         polygon_corners = Poly_corners(x1 = plot.PT_1_X, y1 = plot.PT_1_Y, x2 = plot.PT_2_X, y2 = plot.PT_2_Y,
    #                                        x3 = plot.PT_3_X, y3 = plot.PT_3_Y, x4 = plot.PT_4_X, y4 = plot.PT_4_Y)
    #         vol_info = Polygone_plot_vol_info(poly_corners=polygon_corners, btm_hei= plot.PLT_BTM_HEI , hei_mea=plot.PLT_HEI_MEA, std_dev=plot.PLT_STD_DEV)
    #         self.simu.add.plot(plot_type = plot.PLT_TYPE, volume_info=vol_info, plot_opt_prop_name = plot.PLT_OPT_NAME, plot_therm_prop_name=plot.PLT_THERM_NAME,
    #                            grd_opt_prop_type = plot.GRD_OPT_TYPE, grd_opt_prop_name = plot.GRD_OPT_NAME, grd_therm_prop_name = plot.GRD_THERM_NAME,
    #                            createProps=True)
    #
    # def update_properties_obj(self):
    #     """
    #     populates core optical/thermal properties according to scene.properties dataframe (new) contents
    #     """
    #     th_props_df = self.properties["thermal_props"]
    #     opt_props_dict = self.properties["opt_props"]
    #
    #     for (i, th_prop) in th_props_df.iterrows():
    #         index = self.simu.get_thermal_prop_index(th_prop["prop_name"])
    #         if index == None: # if thermal property does not exists, add
    #             self.simu.add.thermal_property(idTemperature = th_prop["prop_name"])
    #         else: # if thermal property exists but invalid index
    #             if index != th_prop["prop_index"]:
    #                 print("WARNING: invalid prop_index, to be corrected ")
    #                 th_props_df.at[i, "prop_index"] = index
    #
    #     for opt_prop_type, opt_props_df in opt_props_dict.iteritems():
    #         for (i, opt_prop) in opt_props_df.iterrows():
    #             index = self.simu.get_opt_prop_index(opt_prop_type,opt_prop["prop_name"])
    #             if index == None:  # if optical property does not exists, add
    #                 self.simu.add.optical_property(opt_prop_type, ident=opt_prop["prop_name"])
    #             else:
    #                 if index != opt_prop["prop_index"]:
    #                     print("WARNING: invalid prop_index, to be corrected ")
    #                     opt_props_df.at[i,"prop_index"] = index
    #
    # def update_dims(self):
    #     self.update_scene_size()
    #     self.update_cell_size()
    #
    # def update_scene_size(self):
    #     self.scene_dimensions = [self.simu.core.maket.Maket.Scene.SceneDimensions.x,
    #                              self.simu.core.maket.Maket.Scene.SceneDimensions.y]
    #
    # def update_cell_size(self):
    #     self.cell_dimensions = [self.simu.core.maket.Maket.Scene.CellDimensions.x,
    #                             self.simu.core.maket.Maket.Scene.CellDimensions.z]
    #
    # def update_properties_dict(self):
    #     """
    #     updates self.properties_dict variable
    #     """
    #     self.properties = self.simu.core.extract_properties_dict()
    #
    #
    # def set_cell_size(self, cell_size):
    #     x = cell_size[0]
    #     z = cell_size[1]
    #
    #     self.simu.core.maket.Maket.Scene.CellDimensions.x = x
    #     self.simu.core.maket.Maket.Scene.CellDimensions.z = z
    #
    #     self.update_cell_size()
    #
    # def add_plot_in_DF(self):
    #     """
    #     TODo : add a row in plots DF, independently from core plots
    #     :return:
    #     """
    #     self.simu.update.lock_tabs = True
    #
    # def add_property_in_DF(self):
    #     """
    #     TODo : add a row in plots DF, independently from core plots
    #     :return:
    #     """
    #     self.simu.update.lock_tabs = True



class Properties_(object):
    def __init__(self, simu):
        self.simu = simu

    def __repr__(self):
        description = '\n'.join([
            'optical properties: {}'.format(self.optical.type.value_counts().to_dict()),
            'thermal properties: {}'.format(self.thermal.shape[0])
        ])
        return description

    @property
    def optical(self):
        return self.simu.core.get_optical_properties()

    @property
    def thermal(self):
        return self.simu.core.get_thermal_properties()

