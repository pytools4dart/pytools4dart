# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
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
This module contains the class "Core".
"""

import os, glob, re
import lxml.etree as etree
import pandas as pd
from os.path import join as pjoin
import re
import warnings



import pytools4dart as ptd

from pytools4dart.tools.constants import *
from pytools4dart.core_ui.utils import get_labels, get_nodes, findall

# from pytools4dart.core_ui.plots import createDartFile
# from pytools4dart.core_ui.phase import createDartFile
# from pytools4dart.core_ui.atmosphere import createDartFile
# from pytools4dart.core_ui.coeff_diff import createDartFile
# from pytools4dart.core_ui.directions import createDartFile
# from pytools4dart.core_ui.object_3d import createDartFile
# from pytools4dart.core_ui.maket import createDartFile
# from pytools4dart.core_ui.inversion import createDartFile
# from pytools4dart.core_ui.LUT import createDartFile
# from pytools4dart.core_ui.lut import createDartFile
# from pytools4dart.core_ui.trees import createDartFile
# from pytools4dart.core_ui.triangleFile import createDartFile
# from pytools4dart.core_ui.water import createDartFile
# from pytools4dart.core_ui.urban import createDartFile

class Core(object):
    """
    Dart core object.
    """
    def __init__(self, simu, method = 0, empty = False):
        self.simu = simu

        if simu.name is not None and not empty and os.path.isdir(self.simu.getsimupath()):
            self.load()
        else:
            modules = self.get_modules_names()#["plots", "phase", "atmosphere", "coeff_diff", "directions", "object_3d","maket","inversion","trees","water","urban"]
            for module in modules:
                setattr(self, module, eval('ptd.core_ui.{}.createDartFile()'.format(module)))

            self.phase.Phase.calculatorMethod = method
            if empty:
                # self.coeff_diff.Coeff_diff.LambertianMultiFunctions.LambertianMulti = []
                self.phase.Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties = []
                if method !=2:
                    self.phase.Phase.DartInputParameters.nodeIlluminationMode.SpectralIrradiance.SpectralIrradianceValue = []

        #if the simulation exists, populate xsd_core with simulation XML files contents

    def findall(self, pat, case=False, regex=True, column='dartnode'):
        dartnodes = get_labels(pat, case, regex, column)['dartnode']
        l = []
        for dn in dartnodes:
            cn = eval('self.'+dn.split('.')[0].lower())
            l.extend(get_nodes(cn, dn))
        return l

    def get_modules_names(self):
        """
        Provide file names (without xml extension) contained in the directory whose path is given in parameter
        :param dir_path: directory paty
        :return: list of file names
        """
        templatesDpath = pjoin(ptd.__path__[0], "templates")
        templates = glob.glob(pjoin(templatesDpath, "*.xml"))
        modules = [os.path.splitext(os.path.basename(f))[0] for f in templates]
        modules = [m for m in modules if m is not 'sequence']
        return modules

    def load(self):
        """
        Load DART XML input files into core
        """
        modules = self.get_modules_names()
        for module in modules:
            filepath = pjoin(self.simu.getinputsimupath(), module+'.xml')
            setattr(self, module, eval('ptd.{}.parse("{}",silence=True)'.format(module, filepath)))

    def get_corners_from_rectangle(self, center_x, center_y, side_x, side_y):
        x1, y1 = center_x - side_x / 2.0, center_y - side_y / 2.0
        x2, y2 = center_x + side_x / 2.0, center_y - side_y / 2.0
        x3, y3 = center_x + side_x / 2.0, center_y + side_y / 2.0
        x4, y4 = center_x - side_x / 2.0, center_y + side_y / 2.0
        return x1, y1, x2, y2, x3, y3, x4, y4

    def get_plots_df(self):
        """
        extract a DataFrame containing Plots information, directly from plots_obj (self.xdsobjs_dict["plots"])
        for each plot, the fields defined in DART plots.txt file header are provided
        Additional column named "plot_source" indicates if the plot comes from XSD object or from plots.txt-like file
        :return: DataFrame containing Plot fields
        """

        #extract XSDs objs plots:
        rows = []

        plots_list = self.plots.Plots.Plot
        for i, plot in enumerate(plots_list):
            source = plot
            # plt_opt_name = findall(plot, 'Vegetation.*ident$')
            # plt_opt_numb = findall(plot, '.*indexFctPhase$')[0]
            # plt_therm_name = findall(plot, '.*idTemperature$')[0]
            # plt_therm_num = findall(plot, '\.\w+\.\w+.*indexTemperature$')[0]
            # grd_therm_name = findall(plot, '.*indexTemperature$')[0]
            plt_btm_hei, plt_hei_mea, plt_std_dev = None, None, None
            veg_density_def, veg_lai, veg_ul = None, None, None
            wat_height = wat_depth = wat_extinct = None
            plt_opt_number, plt_opt_name, plt_therm_number, plt_therm_name = None, None, None, None

            grd_opt_type, grd_opt_number, grd_opt_name, grd_therm_number, grd_therm_name = None, None, None, None, None

            plt_type = plot.type_

            if plot.form == plot_form_inv_dict["polygon"]:
                points_list = plot.Polygon2D.Point2D
                x1, y1 = points_list[0].x, points_list[0].y
                x2, y2 = points_list[1].x, points_list[1].y
                x3, y3 = points_list[2].x, points_list[2].y
                x4, y4 = points_list[3].x, points_list[3].y
            elif plot.form == plot_form_inv_dict["rectangle"]:
                center_x = plot.Rectangle2D.centreX
                center_y = plot.Rectangle2D.centreY
                side_x, side_y = plot.Rectangle2D.coteX, plot.Rectangle2D.coteY
                intrinsicRotation = plot.Rectangle2D.intrinsicRotation #not used for the moment
                x1, y1, x2, y2, x3, y3, x4, y4 = self.get_corners_from_rectangle(center_x, center_y, side_x, side_y)
            else:
                raise Exception("plot.form value {} not valid".format(plot.form))

            if plt_type in [1,2,3,4]:
                opt_prop_node_name = None
                th_prop_node_name = None
                geom_node_name = None

                if plt_type in [1,2]: # vegetation or vegetation+ground
                    opt_prop_node_name = "PlotVegetationProperties.VegetationOpticalPropertyLink"
                    th_prop_node_name = "PlotVegetationProperties.GroundThermalPropertyLink"
                    geom_node_name = "PlotVegetationProperties.VegetationGeometry"
                    if plot.PlotVegetationProperties.LAIVegetation is None:
                        veg_density_def = 1
                        veg_ul = plot.PlotVegetationProperties.UFVegetation.UF
                    else:
                        veg_density_def = 0
                        veg_lai = plot.PlotVegetationProperties.LAIVegetation.LAI
                    plt_btm_hei, plt_hei_mea, plt_std_dev = eval('plot.{}.baseheight'.format(geom_node_name)), \
                                                            eval('plot.{}.height'.format(geom_node_name)), \
                                                            eval('plot.{}.stDev'.format(geom_node_name))
                elif plt_type == 3:
                    opt_prop_node_name = "PlotAirProperties.AirOpticalProperties[0].AirOpticalPropertyLink"
                    th_prop_node_name = "PlotAirProperties.GroundThermalPropertyLink"
                    geom_node_name = "PlotAirProperties.AirGeometry"
                    plt_btm_hei, plt_hei_mea, plt_std_dev = eval('plot.{}.baseheight'.format(geom_node_name)), \
                                                            eval('plot.{}.height'.format(geom_node_name)), \
                                                            eval('plot.{}.stDev'.format(geom_node_name))
                elif plt_type == 4:
                    opt_prop_node_name = "PlotWaterProperties.WaterOpticalProperties[0].AirOpticalPropertyLink"
                    th_prop_node_name = "PlotWaterProperties.GroundThermalPropertyLink"
                    wat_height = findall(plot, 'waterHeight$')[0]
                    wat_depth = findall(plot, 'waterDepth$')[0]
                    plt_std_dev = findall(plot, 'stDev$')[0]
                    wat_extinct = findall(plot, 'extinctionCoefficient$')[0]
                    # raise Exception('Water plots summary not ready')

                plt_opt_number = eval('plot.{}.indexFctPhase'.format(opt_prop_node_name))
                plt_opt_name = eval('plot.{}.ident'.format(opt_prop_node_name))
                plt_therm_number = eval('plot.{}.indexTemperature'.format(th_prop_node_name))
                plt_therm_name = eval('plot.{}.idTemperature'.format(th_prop_node_name))



            if plt_type in [0, 2]:  # ground or vegetation+ground
                grd_opt_type = plot.GroundOpticalPropertyLink.type_
                grd_opt_number = plot.GroundOpticalPropertyLink.indexFctPhase
                grd_opt_name = plot.GroundOpticalPropertyLink.ident
                grd_therm_number = plot.GroundThermalPropertyLink.indexTemperature
                grd_therm_name = plot.GroundThermalPropertyLink.idTemperature

            row_to_add = [plt_type, x1, y1, x2, y2, x3, y3, x4, y4,
                          grd_opt_type, grd_opt_number, grd_opt_name, grd_therm_number, grd_therm_name,
                          plt_opt_number, plt_opt_name, plt_therm_number, plt_therm_name,
                          plt_btm_hei, plt_hei_mea, plt_std_dev, veg_density_def, veg_lai, veg_ul,
                          wat_depth, wat_height, wat_extinct, source]

            rows.append(row_to_add)


        # PLOTS_COLUMNS = ['PLT_NUMBER', 'PLOT_SOURCE', 'PLT_TYPE', 'PT_1_X', 'PT_1_Y', 'PT_2_X', 'PT_2_Y', 'PT_3_X', 'PT_3_Y',
        #                       'PT_4_X',
        #                       'PT_4_Y',
        #                       'GRD_OPT_TYPE', 'GRD_OPT_NUMB', 'GRD_OPT_NAME', 'GRD_THERM_NUMB', 'GRD_THERM_NAME',
        #                       'PLT_OPT_NUMB', 'PLT_OPT_NAME', 'PLT_THERM_NUMB', 'PLT_THERM_NAME',
        #                       'PLT_BTM_HEI', 'PLT_HEI_MEA', 'PLT_STD_DEV', 'VEG_DENSITY_DEF', 'VEG_LAI', 'VEG_UL', 'WAT_HEIGHT', 'WAT_DEPTH']

        plots_df = pd.DataFrame(rows, columns=PLOTS_COLUMNS+['SOURCE'])
        plots_df.PLT_TYPE = plots_df.PLT_TYPE.astype('category').cat.set_categories(PLOT_TYPES.type_int.values).cat.rename_categories(PLOT_TYPES.type_str.values)

        if self.plots.Plots.addExtraPlotsTextFile:
            filepath = self.plots.Plots.ExtraPlotsTextFileDefinition.extraPlotsFileName
            plotstxt_df = pd.read_csv(filepath, sep='\t', comment='*')
            plotstxt_df['SOURCE'] = filepath
            plots_df = pd.concat([plots_df,plotstxt_df], ignore_index = True, sort=False)

        return plots_df

    def get_object_3d_df(self):
        corenodes = get_nodes(self.simu.core.object_3d, 'object_3d.ObjectList.Object')
        source = []
        name = []
        size = []
        position = []
        groups = []
        ident = []
        for obj in corenodes:
            source.append(obj)
            g = obj.GeometricProperties
            name.append(obj.name)
            dim = g.Dimension3D
            size.append([dim.xdim, dim.ydim, dim.zdim])
            p = g.PositionProperties
            position.append([p.xpos, p.ypos, p.zpos])
            g_nodes = get_nodes(obj, 'Groups.Group')
            groups.append(len(g_nodes))
            # id = get_nodes(obj, 'ObjectOpticalProperties.OpticalPropertyLink.ident')
            # if len(id)>0:
            #     ident.append(id[0])
            # else:
            #     ident.append(None)

        df = pd.DataFrame(dict(name = name, position = position, size = size, groups = groups, source = source))
        return df

    def get_tree_species(self):
        """
        Get a DataFrame of the tree species
        Returns
        -------
            DataFrame
        """
        Trees = self.simu.core.trees.Trees
        tname = 'Trees_{}'.format(Trees.sceneModelCharacteristic)
        if Trees.sceneModelCharacteristic == 1:
            sname = 'Specie'
        else:
            sname = 'Specie_{}'.format(Trees.sceneModelCharacteristic)
        species = findall(Trees, '\.'+sname+'$')

        lai, source = [], []
        trunk_op_ident, trunk_op_type, trunk_tp_ident = [], [], []
        veg_op_ident, veg_tp_ident = [], []

        for s in species:
            lai.append(s.lai)
            veg_op_ident.append(s.CrownLevel[0].VegetationProperty.VegetationOpticalPropertyLink.ident)
            veg_tp_ident.append(s.CrownLevel[0].VegetationProperty.ThermalPropertyLink.idTemperature)
            trunk_op_type.append(s.OpticalPropertyLink.type_)
            trunk_op_ident.append(s.OpticalPropertyLink.ident)
            trunk_tp_ident.append(s.ThermalPropertyLink.idTemperature)
            source.append(s)

        columns = ['LAI', 'VEG_OPT_NAME', 'VEG_THERM_NAME',
                   'TRUNK_OPT_TYPE', 'TRUNK_OPT_NAME', 'TRUNK_THERM_NAME', 'SOURCE']

        df = pd.DataFrame(dict(lai=lai, veg_op_ident=veg_op_ident, veg_tp_ident=veg_tp_ident,
                               trunk_op_type=trunk_op_type, trunk_op_ident=trunk_op_ident,
                               trunk_tp_ident=trunk_tp_ident, source=source))
        return df

    def get_trees(self):
        Trees = self.simu.core.trees.Trees
        file = findall(Trees, '\.sceneParametersFileName$')
        if len(file) == 0:
            return
        file = file[0]
        possible_paths = [
            file,
            pjoin(self.simu.getsimupath, file),
            pjoin(ptd.getdartdir(), 'user_data', 'database', file),
            pjoin(ptd.getdartdir(), 'database', file)]
        filepath = next((p for p in possible_paths if os.path.isfile), None)
        if filepath is None:
            return

        return pd.read_csv(filepath, sep='\t', comment='*')

    def get_bands_df(self):
        """
        Extract a DataFrame of bands with wavelength,  pairs corresponding to spectral bands contained in Phase XSD Object
        :return: DataFrame contaning a list of [wvl,dl] pairs
        """

        bands = self.phase.Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties
        rows_to_add = [[b.meanLambda, b.deltaLambda, b] for b in bands]

        return pd.DataFrame(rows_to_add, columns = ['wavelength', 'bandwidth', 'source'])

    def get_virtual_directions(self):
        virtualDirs = []
        dirsList = self.directions.Directions.AddedDirections
        for dir in dirsList:
            virtualDirs.append([dir.ZenithAzimuth.directionAzimuthalAngle,
                                dir.ZenithAzimuth.directionZenithalAngle,
                                dir])
        df = pd.DataFrame(virtualDirs, columns = ['azimuth', 'zenith', 'source'])
        return virtualDirs

    def get_sensors(self):
        SensorImageSimulation = self.phase.Phase.SensorImageSimulation
        sensors = []
        for s in SensorImageSimulation.children:
            sensors.extend(get_nodes(SensorImageSimulation, s))

        s_type = [re.sub('create_', '', s.__class__.__name__) for s in sensors]
        df = pd.DataFrame(dict(type=s_type, source=sensors))[['type', 'source']]
        return df

    def get_thermal_props(self):
        """
        Provides a DataFrame containing thermal properties names and indexes of thermal properties in coeff_diff module
        th_props.id: location of thermal property in the thermal properties list
        :return: DataFrame containing thermal properties names and indexes
        """
        thermal_props_dict = {"prop_index": [], "prop_name": []}
        thermal_props_list = self.coeff_diff.Coeff_diff.Temperatures.ThermalFunction
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
        # TODO: remove
        listnodes_paths = []
        opt_props = {}
        opt_props_DF_cols =  ["prop_index", "prop_name"]

        if len(self.coeff_diff.Coeff_diff.UnderstoryMultiFunctions.UnderstoryMulti) > 0:
            listnodes_paths.append(["vegetation","UnderstoryMultiFunctions.UnderstoryMulti"])
        else:
            opt_props["vegetation"] = pd.DataFrame(columns = opt_props_DF_cols)

        if len(self.coeff_diff.Coeff_diff.LambertianMultiFunctions.LambertianMulti) > 0:
            listnodes_paths.append(["lambertian","LambertianMultiFunctions.LambertianMulti"])
        else:
            opt_props["lambertian"] = pd.DataFrame(columns = opt_props_DF_cols)

        if len(self.coeff_diff.Coeff_diff.HapkeSpecularMultiFunctions.HapkeSpecularMulti) > 0:
            listnodes_paths.append(["hapke","HapkeSpecularMultiFunctions.HapkeSpecularMulti"])
        else:
            opt_props["hapke"] = pd.DataFrame(columns=opt_props_DF_cols)

        if len(self.coeff_diff.Coeff_diff.RPVMultiFunctions.RPVMulti) > 0:
            listnodes_paths.append(["rpv","RPVMultiFunctions.RPVMulti"])
        else:
            opt_props["rpv"] = pd.DataFrame(columns=opt_props_DF_cols)

        if len(self.coeff_diff.Coeff_diff.AirMultiFunctions.AirFunction) > 0:
            listnodes_paths.append(["fluid","AirMultiFunctions.AirFunction"])
        else:
            opt_props["fluid"] = pd.DataFrame(columns=opt_props_DF_cols)

        for listnode_path in listnodes_paths:
            props_list = eval('self.coeff_diff.Coeff_diff.{}'.format(listnode_path[1]))
            prop_index_list = []
            prop_name_list = []
            for i, prop in enumerate(props_list):
                prop_index_list.append(i)
                prop_name_list.append(prop.ident)
            opt_props[listnode_path[0]] = pd.DataFrame({"prop_index" : prop_index_list, "prop_name" : prop_name_list})

        return opt_props

    def get_optical_properties(self):
        """
        Get optical properties from coeff_diff
        Returns
        -------
            pandas DataFrame with ident, index and type

        """
        # PB with Understory top/bottom?
        dartnodes = ptd.core_ui.utils.get_labels('Coeff_diff\.\w+\.\w+\.ident$')['dartnode']

        source = []
        prop_type = []
        prop_index = []
        prop_ident = []
        prop_db = []
        prop_name = []
        for dn in dartnodes:
            # dn = dartnodes.iloc[0]
            head, function, multi, _=dn.split('.')
            # ptype = re.sub('Multi', '', multi)
            # OpticalPropertyLink type names are different from Coeff_diff type names, e.g. Vegetation <-> Understory
            ptype = ptd.core_ui.utils.get_labels('^'+'.'.join([head, function])+'$')['label'].iloc[0]
            if function in self.coeff_diff.Coeff_diff.children:
                prop_list = eval('self.coeff_diff.Coeff_diff.{function}.{multi}'.format(function=function, multi=multi))
                for i, prop in enumerate(prop_list):
                    source.append(prop)
                    prop_type.append(ptype)
                    prop_index.append(i)
                    prop_ident.append(prop.ident)

                    # databaseName
                    pat = 'Coeff_diff\.{function}\.{multi}\.*\w*\.databaseName'.format(function=function, multi=multi)
                    subdns = get_labels(pat)['dartnode']
                    multidn = 'Coeff_diff.{function}.{multi}.'.format(function=function, multi=multi)
                    subdns = [re.sub( multidn, '', s) for s in subdns]
                    subcn = []
                    for sdn in subdns:
                        subcn.extend(get_nodes(prop, sdn))
                    if len(subcn) == 1:
                        prop_db.append(subcn[0])
                    elif len(subcn) > 1:
                        prop_db.append('multiple')
                    else:
                        prop_db.append(None)

                    # ModelName
                    pat = 'Coeff_diff\.{function}\.{multi}\.*\w*\.ModelName'.format(function=function, multi=multi)
                    subdns = get_labels(pat)['dartnode']
                    multidn = 'Coeff_diff.{function}.{multi}.'.format(function=function, multi=multi)
                    subdns = [re.sub(multidn, '', s) for s in subdns]
                    subcn = []
                    for sdn in subdns:
                        subcn.extend(get_nodes(prop, sdn))
                    if len(subcn) == 1:
                        prop_name.append(subcn[0])
                    elif len(subcn) > 1:
                        prop_name.append('multiple')
                    else:
                        prop_name.append(None)


        opt_props = pd.DataFrame(dict(type = prop_type, index = prop_index, ident = prop_ident,
                                      databaseName = prop_db, ModelName = prop_name, source = source))
        return opt_props

    def get_thermal_properties(self):
        """
        Provides a DataFrame containing thermal properties names and indexes of thermal properties in coeff_diff module
        th_props.id: location of thermal property in the thermal properties list
        :return: DataFrame containing thermal properties names and indexes
        """
        index, idTemperature, meanT, deltaT, source = [], [], [], [], []
        thermal_props_list = self.coeff_diff.Coeff_diff.Temperatures.ThermalFunction
        for i,th_prop in enumerate(thermal_props_list):
            index.append(i)
            idTemperature.append(th_prop.idTemperature)
            meanT.append(th_prop.meanT)
            deltaT.append(th_prop.deltaT)
            source.append(th_prop)

        return pd.DataFrame(dict(index = index, idTemperature = idTemperature, meanT = meanT,
                                 deltaT = deltaT, source = source))

    def get_optical_property_links(self):
        dartnodes = ptd.core_ui.utils.get_labels('\.*OpticalPropertyLink$')['dartnode']
        dartobject = pd.DataFrame({'corenode': [getattr(self, dartnode.split('.')[0].lower()) for dartnode in dartnodes],
                                   'dartnode': dartnodes})

        # l=[get_nodes(row.corenode, row.dartnode)for row in dartobject.itertuples()]
        optical_property_links = []
        for row in dartobject.itertuples():
            n = ptd.core_ui.utils.get_nodes(row.corenode, row.dartnode)
            optical_property_links.extend(n)
        l = []
        for opl in optical_property_links:
            if 'type_' in opl.attrib:
                opl_type = OPL_TYPES[OPL_TYPES.type_int == opl.type_].type_str.iloc[0]
            else:  # Vegetation
                opl_type = re.sub('OpticalPropertyLink', '',
                                  re.sub('create_', '', opl.__class__.__name__))

            l.append({'ident': opl.ident, 'type': opl_type,
                      'optical_property_link': opl})  # 'tindex':opl.indexFctPhase,

        # Vegetation

        return pd.DataFrame(l)

    def get_thermal_property_links(self):
        dartnodes = ptd.core_ui.utils.get_labels('\.*ThermalPropertyLink$')['dartnode']
        dartobject = pd.DataFrame(
            {'corenode': [getattr(self, dartnode.split('.')[0].lower()) for dartnode in dartnodes],
             'dartnode': dartnodes})

        # l=[get_nodes(row.corenode, row.dartnode)for row in dartobject.itertuples()]
        thermal_property_links = []
        for row in dartobject.itertuples():
            n = ptd.core_ui.utils.get_nodes(row.corenode, row.dartnode)
            thermal_property_links.extend(n)
        l = []
        for tpl in thermal_property_links:
            l.append(
                {'idTemperature': tpl.idTemperature,
                 'thermal_property_link': tpl})  # 'tindex':opl.indexFctPhase,

        return  pd.DataFrame(l)

        # if isinstance(n, list):
        #     l.extend(n)
        # else:
        #     l.append(n)
        # l = [ptd.core.get_nodes(self.xsdnodes[])for dartnode in dartnodes]

    def get_op_index(self, ident):
        """
        Get Optical Properties indexes from identification names
        Parameters
        ----------
        ident: str or list of str
            identification names, e.g. 'Lambertian_Phase_Function_1'.
        Returns
        -------
            pandas Series

        """
        # convert string to list
        if isinstance(ident, str):
            ident = [ident]

        ident_df = pd.DataFrame(dict(ident=ident))
        op = self.get_optical_properties()
        indexes = pd.merge(ident_df, op[['ident', 'index']], on='ident', how='left')
        return indexes['index']

    def get_tp_index(self, ident):
        """
        Get Thermal Properties indexes from identification names
        Parameters
        ----------
        ident: str or list of str
            identification names, e.g. 'ThermalFunction290_310'.
        Returns
        -------
            pandas Series
        """
        # convert string to list
        if isinstance(ident, str):
            ident = [ident]

        ident_df = pd.DataFrame(dict(idTemperature=ident))
        tp = self.get_thermal_properties()
        indexes = pd.merge(ident_df, tp[['idTemperature', 'index']], on='idTemperature', how='left')
        return indexes['index']

    #################
    #    UPDATES    #
    #################

    def update(self):
        self.update_opl()
        self.update_tpl()
        self.update_mf()
        self.update_bn()

    def update_opl(self):
        table_op = self.get_optical_properties()
        table_opl = self.get_optical_property_links()
        xtable_opl = pd.merge(table_opl, table_op, on=['ident', 'type'], how='left')

        wrong_opl = []
        for row in xtable_opl.itertuples():
            if pd.isna(row.index):
                wrong_opl.append(row.Index)
            else:
                row.optical_property_link.indexFctPhase = row.index
        if len(wrong_opl):
            warnings.warn("Optical Properties not found in 'coeff_diff': {}".format(', '.join(xtable_opl.ident[wrong_opl])))
            return table_opl.loc[wrong_opl]

    def update_tpl(self):
        table_tp = self.get_thermal_properties()
        table_tpl = self.get_thermal_property_links()
        xtable_tpl = pd.merge(table_tpl, table_tp, on=['idTemperature'], how='left')

        wrong_tpl = []
        for row in xtable_tpl.itertuples():
            if pd.isna(row.index):
                wrong_tpl.append(row.Index)
            else:
                row.thermal_property_link.indexTemperature = row.index
        if len(wrong_tpl):
            warnings.warn('Thermal Properties not found in "coeff_diff".')
            return (table_tpl.loc[wrong_tpl])

    def update_mf(self):
        """
        Update the number multiplicative factors for each optical property in coeff_diff module
        is equal to the number of spectral bands in phase module

        if spectral band multiplicative factors are missing in coeff_diff module,
        default multiplicative factors are introduced for each missing spectral band

        :return: True if the number of spectral bands in phase XSD module is equal to the number of spectral bandds in each optical property given in coeff_diff XSD module
                      (including if this has been corrected)
                 False otherwise
        """

        phase_spbands_nb = len(self.simu.core.phase.Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties)

        dartnodes = get_labels('Coeff_diff.*\.useSameFactorForAllBands$')['dartnode']
        for dartnode in dartnodes:
            dn = '.'.join(dartnode.split('.')[:-1]) # parent dart node
            cns = get_nodes(self.simu.core.coeff_diff, dn) # parent core node
            for cn in cns:
                multi = [c for c in cn.children if c.endswith('MultiplicativeFactorForLUT')][0]
                if cn.useSameFactorForAllBands == 1 or \
                        eval('len(cn.{multi})')!=phase_spbands_nb:
                    multiargs={}
                    for a in cn.attrib:
                        if a.endswith('Factor'):
                            multiargs[a]=eval('cn.' + a)
                    # multiargs = {a:eval('cn.'+a) for a in cn.attrib if a.endswith('Factor')}
                    new = eval('ptd.core_ui.coeff_diff.create_{multi}(**multiargs)'.format(multi=multi))
                    for i in range(phase_spbands_nb-1):
                        eval('cn.add_{multi}(new.copy())'.format(multi=multi))
                else:
                    # multiargs = {}
                    # for a in cn.attrib:
                    #     if a.endswith('Factor'):
                    #         multiargs[a]=eval('cn.' + a)
                    # # multiargs = {a: eval('cn.' + a) for a in cn.attrib if a.endswith('Factor')}
                    # new = eval('ptd.core_ui.coeff_diff.create_{multi}(**multiargs)'.format(multi=multi))
                    eval('cn.set_{multi}([])'.format(multi=multi))

    def update_bn(self):
        """
        Update band number of SpectralIntervalsProperties and SpectralIrradianceValue in the order they are found, starting from 0.
        Removes SpectralIrradianceValue that have band number higher than SpectralIntervalsProperties
        """
        DartInputParameters = self.phase.Phase.DartInputParameters
        bands = DartInputParameters.SpectralIntervals.SpectralIntervalsProperties
        bandNumbers = [b.bandNumber for b in bands]
        band_df  = pd.DataFrame(dict(band=bands, bandNumber=bandNumbers))

        irradiances = DartInputParameters.nodeIlluminationMode.SpectralIrradiance.SpectralIrradianceValue
        ir_bandNumbers = [ir.bandNumber for ir in irradiances]
        ir_df  = pd.DataFrame(dict(irradiance=irradiances, bandNumber=ir_bandNumbers))

        # sort values
        band_df = band_df.sort_values(by='bandNumber').reset_index()
        ir_df = ir_df.sort_values(by='bandNumber').reset_index()

        # renumber both
        band_df.bandNumber = band_df.index
        ir_df.bandNumber=ir_df.index

        # remove wrongly numbered irradiances
        bi_df = pd.merge(band_df, ir_df, how='left', on='bandNumber')

        # affect bandNumber and create inexistant irradiances
        for row in bi_df.itertuples():
            if pd.isna(row.irradiance):
                row.irradiance = ptd.phase.create_SpectralIrradianceValue()
            row.irradiance.bandNumber = row.bandNumber
            row.band.bandNumber = row.bandNumber

        DartInputParameters.SpectralIntervals.SpectralIntervalsProperties = list(band_df.band)
        DartInputParameters.nodeIlluminationMode.SpectralIrradiance.SpectralIrradianceValue = list(ir_df.irradiance)

    def update_ir(self):
        """
        Remove supplementary spectral irradiance and SKYL
        """

    def update_properties_dict(self):
        """
        updates self.properties_dict variable
        """
        # TODO: remove
        self.simu.scene.properties = self.extract_properties_dict()

    def extract_properties_dict(self):
        # TODO: remove
        return {"opt_props": self.get_opt_props(), "thermal_props": self.get_thermal_props(),
                "optical": self.get_optical_properties(), "thermal": self.get_thermal_properties()}

    def update_simu(self):
        """
        updates simulation user friendly interface: scene and sensor
        Returns
        -------

        """
        # TODO: remove
        # self.simu.scene.properties = self.extract_properties_dict()  # dictionnary containing "opt_props" and "thermal_props" DataFrames
        # self.simu.scene.plots = self.get_plots_df()  # DataFrame containing Plots fields according to DART Plot.txt header*
        #self.simu.scene.trees = ToDo
        #self.simu.scene.obj3d = ToDo
        self.simu.bands = self.get_bands_df()  # DataFrame containing a list of [wvl, dl] couples

