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

class Scene(object):
    def __init__(self, simu):

        self.simu = simu

        self._size = self.simu.core.maket.Maket.Scene.SceneDimensions

        self._cell = self.simu.core.maket.Maket.Scene.CellDimensions

        self._properties = Properties_(self.simu)

    def __repr__(self):

        description = '\n'.join(
            ['scene size : {}'.format(self.size),
             'cell size : {}'.format(self.cell),
             'ground:',
             '\tOptical property: {}'.format(self.ground.OpticalPropertyLink.ident),
             '\tThermal property: {}'.format(self.ground.ThermalPropertyLink.idTemperature),
             'number of plots : {}'.format(self.plots.shape[0]),
             'plot file: {}'.format(self.plot_file),
             'number of object 3D : {}'.format(self.object3D.shape[0]),
             'number of tree species : {}'.format(self.tree_species.shape[0]),
             'tree file: {}'.format(self.simu.core.get_tree_file()),
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
    def trees(self):
        return self.simu.core.get_trees()

    @property
    def tree_species(self):
        return self.simu.core.get_tree_species()

    @property
    def properties(self):
        return self._properties

    @property
    def plot_file(self):
        return self.simu.core.get_plot_file()


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

