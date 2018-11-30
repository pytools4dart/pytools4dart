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
This module contains the class "Scene".
"""

import pandas as pd

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
        print("ToBe Done: update des objets à partir des tables")

    def update_dims(self):
        self.update_scene_dims()
        self.update_cell_dims()

    def update_scene_dims(self):
        self.scene_dimensions = [self.simu.core.xsdobjs["maket"].Maket.Scene.SceneDimensions.x,
                                 self.simu.core.xsdobjs["maket"].Maket.Scene.SceneDimensions.y]

    def update_cell_dims(self):
        self.cell_dimensions = [self.simu.core.xsdobjs["maket"].Maket.Scene.CellDimensions.x,
                                self.simu.core.xsdobjs["maket"].Maket.Scene.CellDimensions.z]

    def update_properties_dict(self):
        """
        updates self.properties_dict variable
        """
        self.properties = self.extract_properties_dict()

    def set_scene_dims(self, scene_dims):
        x = scene_dims[0]
        y = scene_dims[1]

        self.simu.core.xsdobjs["maket"].Maket.Scene.SceneDimensions.x = x
        self.simu.core.xsdobjs["maket"].Maket.Scene.SceneDimensions.y = y

        self.update_scene_dims()


    def set_cell_dims(self, cell_dims):
        x = cell_dims[0]
        z = cell_dims[1]

        self.simu.core.xsdobjs["maket"].Maket.Scene.CellDimensions.x = x
        self.simu.core.xsdobjs["maket"].Maket.Scene.CellDimensions.z = z

        self.update_cell_dims()


