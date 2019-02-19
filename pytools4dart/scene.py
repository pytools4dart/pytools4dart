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
import os
from pytools4dart.tools.constants import *
from pytools4dart.core_ui.utils import get_nodes, findall


class Scene(object):
    def __init__(self, simu):

        self.simu = simu

        self._size = self.simu.core.maket.Maket.Scene.SceneDimensions

        self._cell = self.simu.core.maket.Maket.Scene.CellDimensions

        self._properties = Properties_(self.simu)

        self.plot_file = Plot_file(self.simu)

        self.tree_file = Tree_file(self.simu)

    def __repr__(self):

        description = '\n'.join(
            ['scene size : {}'.format(self.size),
             'cell size : {}'.format(self.cell),
             'ground:',
             '\tOptical property: {}'.format(self.ground.OpticalPropertyLink.ident),
             '\tThermal property: {}'.format(self.ground.ThermalPropertyLink.idTemperature),
             'number of plots : {}'.format(self.plots.shape[0]),
             'plot file:',
             '\tpath: {}'.format(self.plot_file.filepath),
             '\tnumber of plots: {}'.format(self.plot_file.shape[0]),
             'number of object 3D : {}'.format(self.object3D.shape[0]),
             'number of tree species : {}'.format(self.tree_species.shape[0]),
             'tree file:',
             '\tpath: {}'.format(self.simu.core.get_tree_file()),
             '\tnumber of trees: {}'.format(self.tree_file.shape[0]),
             'number of optical properties : {}'.format(self.properties.optical.shape[0]),
             'number of thermal properties : {}'.format(self.properties.thermal.shape[0])])

        return description

    @property
    def size(self):
        return [self._size.x, self._size.y]

    @size.setter
    def size(self, size):
        self._size.x = size[0]
        self._size.y = size[1]

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
    def tree_species(self):
        return self.simu.core.get_tree_species()

    @property
    def properties(self):
        return self._properties

    # @property
    # def plot_file(self):
    #     return self.simu.core.get_plot_file()


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


class Plot_file(object):
    # This class was supposed to stand for plot file management
    # However it raises lots of question on how to do it
    # In the following what has been thought until now, with D as data, F as filepath
    # At initialization:
    #     - D is None and F is None:
    #         get F from core (absolute path)
    #         load D from F
    #     - D is None and F is not None
    #         set F to core
    #         load D from F
    #     - D is not None and F is None
    #         set F as default
    #         set F to core
    #     - D is not None and F is not None
    #         set F to core
    #
    # After initialization, when change:
    #     - F:nothing happens
    #     - core F: nothing happens
    #     - D: nothing happens
    #     - F content: nothing happens
    #
    # At simu write:
    #     - if D is None, nothing is done
    #     - if F is None, F is set to default
    #     ....
    # Thus this option was left away for the moment
    def __init__(self, simu, data = None, filepath = None):
        self.simu = simu
        self._data = data

        if filepath is not None:
            self.filepath = filepath # set absolute path if not None by the way
            if data is None:
                self.load()
        else:
            if data is not None: # set default name
                self.filepath = os.path.join(simu.getinputsimupath(), 'plots.txt')
            else:
                self.filepath = self.filepath
                self.load()

        # self._filepath
        # self.exists = False



        # # check si filepath exist et si oui normalise
        # if self.filepath != get_input_file_path(self.filepath):
        #     self.filepath = get_input_file_path(self.filepath)
        #
        # if self.data is None:
        #     self.load()
    @property
    def shape(self):
        if self.data is None:
            return (0, 0)
        else:
            return self.data.shape

    def load(self):
        self.filepath = self.filepath
        if self.filepath is not None and os.path.isfile(self.filepath):
            self.data = pd.read_csv(self.filepath, sep='\t', comment='*')
            self.update_names()

    def update_names(self, verbose=True):
        df = self.data

        index_columns = ['PLT_OPT_NUMB', 'PLT_THERM_NUMB', 'GRD_OPT_NUMB', 'GRD_THERM_NUMB']
        if verbose and any([c in df.columns for c in index_columns]):
            print('Updating plot file properties name...')

        if 'PLT_OPT_NUMB' in df.columns:
            PLT_OPT_TYPE = pd.merge(df[['PLT_TYPE']], PLOT_TYPES, left_on= 'PLT_TYPE', right_on='type_int', how='left')['op_type']
            df['PLT_OPT_NAME'] = self.simu.core.get_op_ident(df.PLT_OPT_NUMB, PLT_OPT_TYPE)
        if 'PLT_THERM_NUMB' in df.columns:
            df['PLT_THERM_NAME'] = self.simu.core.get_tp_ident(df.PLT_THERM_NUMB)
        if 'GRD_OPT_NUMB' in df.columns:
            GRD_OPT_TYPE = pd.merge(df[['GRD_OPT_TYPE']], OPL_TYPES, left_on='GRD_OPT_TYPE', right_on='type_int', how='left')['type_str']
            df['GRD_OPT_NAME'] = self.simu.core.get_op_ident(df.GRD_OPT_NUMB, GRD_OPT_TYPE)
        if 'GRD_THERM_NUMB' in df.columns:
            df['GRD_THERM_NAME'] = self.simu.core.get_tp_ident(df.GRD_THERM_NAME)

    def update_indexes(self, verbose=True):
        df = self.data

        name_columns = ['PLT_OPT_NAME', 'PLT_THERM_NAME', 'GRD_OPT_NAME', 'GRD_THERM_NAME']
        if verbose and any([c in df.columns for c in name_columns]):
            print('Updating plot file properties index...')

        if 'PLT_OPT_NAME' in df.columns:
            df['PLT_OPT_NUMB'] = self.simu.core.get_op_index(df.PLT_OPT_NAME)
        if 'PLT_THERM_NAME' in df.columns:
            df['PLT_THERM_NUMB'] = self.simu.core.get_tp_index(df.PLT_THERM_NAME)
        if 'GRD_OPT_NAME' in df.columns:
            df['GRD_OPT_NUMB'] = self.simu.core.get_op_index(df.GRD_OPT_NAME)
        if 'GRD_THERM_NAME' in df.columns:
            df['GRD_THERM_NUMB'] = self.simu.core.get_tp_index(df.GRD_THERM_NAME)

    @property
    def in_memory(self):
        return self._data is not None

    @property
    def filepath(self):
        return self.simu.core.get_plot_file()

    @filepath.setter
    def filepath(self, value):
        if value is not None:
            self.simu.core.plots.Plots.addExtraPlotsTextFile = 1
            self.simu.core.plots.Plots.ExtraPlotsTextFileDefinition.extraPlotsFileName = self.simu.get_input_file_path(value)

    @property
    def data(self):
        if not self.in_memory and self.filepath is not None and os.path.isfile(self.filepath):
            # check if exists
            self.load()

        return self._data

    @data.setter
    def data(self, value):

        if value is None:
            self._data = None
            return

        self._data = self.check_columns(value)
        self.update_indexes()

    def check_columns(self, value):
        mandatory_columns = ['PT_1_X', 'PT_1_Y', 'PT_2_X', 'PT_2_Y', 'PT_3_X', 'PT_3_Y', 'PT_4_X', 'PT_4_Y']
        if not all([c in value.columns for c in mandatory_columns]):
            raise Exception("Mandatory colmuns 'PT_1_X', 'PT_1_Y', 'PT_2_X', 'PT_2_Y', 'PT_3_X', 'PT_3_Y', "
                            "'PT_4_X', 'PT_4_Y' not found.")

        # subset expected columns
        expected_columns = PLOTS_COLUMNS + ['GRD_OPT_NAME', 'GRD_THERM_NAME', 'PLT_OPT_NAME', 'PLT_THERM_NAME']
        return value[[c for c in value.columns if c in expected_columns]]

    def append(self, value):
        if value is None:
            return

        self.data = pd.concat([self.data, self.check_columns(value)],
                              ignore_index=True, sort=False)

    def write(self, filepath = None, overwrite=False, verbose=True):
        """
        Writes dataframe to text file
        Parameters
        ----------
        filepath: str
            if None self.filepath is taken.
        overwrite: bool
            if True and file exists, it is overwritten

        Returns
        -------

        """
        if self._data is None: # does not load it if not already done.
            return
        else:
            self.update_indexes(verbose=verbose)

        if filepath is None:
            filepath = self.filepath

        # create directory if not found
        if not os.path.isdir(os.path.dirname(filepath)):
            raise Exception("Directory not found: '{}'. ")

        if os.path.isfile(filepath) and not overwrite:
            raise Exception('File already exist. Set overwrite to overpass.')

        with open(filepath, mode='w') as f:
            f.write(PLOTS_HEADER)

        self.data.to_csv(filepath, sep='\t', index=False, mode='a', header=True)
        if verbose:
            print("\nPlots written in '{}'".format(filepath))

class Tree_file(object):
    # This class was supposed to stand for plot file management
    # However it raises lots of question on how to do it
    # In the following what has been thought until now, with D as data, F as filepath
    # At initialization:
    #     - D is None and F is None:
    #         get F from core (absolute path)
    #         load D from F
    #     - D is None and F is not None
    #         set F to core
    #         load D from F
    #     - D is not None and F is None
    #         set F as default
    #         set F to core
    #     - D is not None and F is not None
    #         set F to core
    #
    # After initialization, when change:
    #     - F:nothing happens
    #     - core F: should it be reloaded to D??? How can it be done???
    #     - D: write ???
    #     - F content: ???
    #
    # At simu write:
    #     - if F and core F different
    #     ....
    # Thus this option was left away for the moment
    def __init__(self, simu, data = None, filepath = None):
        self.simu = simu
        self._data = data

        if filepath is not None:
            self.filepath = filepath # set absolute path if not None by the way
            if data is None:
                self.load()
        else:
            if data is not None: # set default name
                self.filepath = os.path.join(simu.getinputsimupath(), 'trees.txt')
            else:
                self.filepath = self.filepath
                self.load()

        # self._filepath
        # self.exists = False



        # # check si filepath exist et si oui normalise
        # if self.filepath != get_input_file_path(self.filepath):
        #     self.filepath = get_input_file_path(self.filepath)
        #
        # if self.data is None:
        #     self.load()
    @property
    def shape(self):
        if self.data is None:
            return (0, 0)
        else:
            return self.data.shape

    def load(self):
        self.filepath = self.filepath
        if self.filepath is not None and os.path.isfile(self.filepath):
            self.data = pd.read_csv(self.filepath, sep='\t', comment='*')

    @property
    def in_memory(self):
        return self._data is not None

    @property
    def filepath(self):
        return self.simu.core.get_tree_file()

    @filepath.setter
    def filepath(self, value):
        if value is not None:
            Trees = self.simu.core.trees.Trees
            Trees.isTrees = 1
            _, nodepath = findall(Trees, 'sceneParametersFileName', path=True)
            if len(nodepath) != 1:
                raise Exception('Multiple Tree files found.')

            filepath = self.simu.get_input_file_path(value)
            exec (nodepath[0] + '=filepath')


    @property
    def data(self):
        if not self.in_memory and os.path.isfile(self.filepath):
            # check if exists
            self.load()

        return self._data

    @data.setter
    def data(self, value):

        if value is None:
            self._data = None
            return

        self._data = self.check_columns(value)

    def check_columns(self, value):
        mandatory_columns = ['SPECIES_ID', 'POS_X', 'POS_Y']
        if not all([c in value.columns for c in mandatory_columns]):
            raise Exception("Mandatory colmuns 'SPECIES_ID', 'POS_X', 'POS_Y' not found.")

        expected_columns = TREES_COLUMNS
        return value[[c for c in value.columns if c in expected_columns]]

    def append(self, value):
        if value is None:
            return

        self.data = pd.concat([self.data, self.check_columns(value)],
                              ignore_index=True, sort=False)

    def write(self, filepath = None, overwrite=False, verbose=True):
        """
        Writes dataframe to text file
        Parameters
        ----------
        filepath: str
            if None self.filepath is taken.
        overwrite: bool
            if True and file exists, it is overwritten

        Returns
        -------

        """
        if self._data is None: # does not load it if not already done.
            return

        if filepath is None:
            filepath = self.filepath

        # create directory if not found
        if not os.path.isdir(os.path.dirname(filepath)):
            raise Exception("Directory not found: '{}'. ")

        if os.path.isfile(filepath) and not overwrite:
            raise Exception('File already exist. Set overwrite to overpass.')

        with open(filepath, mode='w') as f:
            f.write(TREES_HEADER)

        self.data.to_csv(filepath, sep='\t', index=False, mode='a', header=True)
        if verbose:
            print("\nTrees written in '{}'".format(filepath))
