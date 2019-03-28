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

    def __repr__(self):
        if self.simu.method == 'LIDAR':
            return ''

        description = '\n'.join(
            ['sun viewing angles (Azimuth, Zenith) : {}'.format(self.position)])

        return description

    @property
    def position(self):
        # TODO: Only works for viewing angles
        if hasattr(self.simu.core.directions.Directions, 'SunViewingAngles'):
            return [self.simu.core.directions.Directions.SunViewingAngles.sunViewingAzimuthAngle,
                    self.simu.core.directions.Directions.SunViewingAngles.sunViewingZenithAngle]

    @position.setter
    def position(self, source_pos_az_zenith):
        self.simu.core.directions.Directions.SunViewingAngles.sunViewingAzimuthAngle = source_pos_az_zenith[0]
        self.simu.core.directions.Directions.SunViewingAngles.sunViewingZenithAngle = source_pos_az_zenith[1]

