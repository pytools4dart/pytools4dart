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
This module contains the class "Acquisition".
"""

#class Sensor(): ToDo

import pytools4dart as ptd


class Acquisition(object):

    def __init__(self, simu):
        self.simu = simu
        self.sensors = []
        self.bands = self.simu.core.extract_sp_bands_table()
        self.virtualDirections = self.get_virtual_directions()

    def update_virtualDirections(self):
        self.virtualDirections = self.get_virtual_directions()

    def get_virtual_directions(self):
        virtualDirs = []
        dirsList = self.simu.core.xsdobjs["directions"].Directions.AddedDirections
        for dir in dirsList:
            virtualDirs.append([dir.ZenithAzimuth.directionAzimuthalAngle, dir.ZenithAzimuth.directionZenithalAngle])
        return virtualDirs

    def add_virtual_direction (self, dirAzimuthZenith):
        dir = ptd.directions.create_AddedDirections(ZenithAzimuth = ptd.directions.create_ZenithAzimuth(directionAzimuthalAngle= dirAzimuthZenith[0], directionZenithalAngle=dirAzimuthZenith[1]))
        self.simu.core.xsdobjs["directions"].Directions.add_AddedDirections(dir)
        self.update_virtualDirections()

    def update_xsdobjs(self):
        print("ToBe Done: update des objets à partir des tables")
        #update bands

    def add_spband_in_DF(self):
        """
        TODo : add a spectral band in bands DF, independently from core spectral intervals
        :return:
        """
        self.simu.update.lock_tabs = True
