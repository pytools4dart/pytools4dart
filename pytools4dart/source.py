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
This module contains the class "Source".
"""

class Source(object):
    def __init__(self, simu):
        self.simu = simu
        self.update_source_position()

    def update_source_position(self):
        self.position = self.get_source_position()

    def get_source_position(self):
        source_pos = [ self.simu.core.directions.Directions.SunViewingAngles.sunViewingAzimuthAngle, \
                     self.simu.core.directions.Directions.SunViewingAngles.sunViewingZenithAngle ]
        return source_pos

    def set_source_position(self, source_pos_az_zenith):
        self.simu.core.directions.Directions.SunViewingAngles.sunViewingAzimuthAngle = source_pos_az_zenith[0]
        self.simu.core.directions.Directions.SunViewingAngles.sunViewingZenithAngle = source_pos_az_zenith[1]
        self.update_source_position()
