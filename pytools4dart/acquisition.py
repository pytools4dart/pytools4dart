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

    @property
    def bands(self):
        return self.simu.core.get_bands_df()
    @bands.setter
    def bands(self, value):
        raise Exception('Element not settable.')

    @property
    def virtualDirections(self):
        return self.simu.core.get_virtual_directions()
    @virtualDirections.setter
    def virtualDirections(self, value):
        raise Exception('Element not settable.')


    def update_xsdobjs(self):
        print("ToBe Done: update des objets à partir des tables")
        #update bands

    def add_spband_in_DF(self):
        """
        TODo : add a spectral band in bands DF, independently from core spectral intervals
        :return:
        """
        self.simu.update.lock_tabs = True
