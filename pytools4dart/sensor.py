# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <florian.deboissieu@irstea.fr>
# https://gitlab.com/pytools4dart/pytools4dart
#
# COPYRIGHT:
#
# Copyright 2018-2019 Florian de Boissieu
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
This module contains the class "Sensor".
"""


class Sensor(object):
    """
    All that concerns the sensing: sensors, bands, etc.
    """

    def __init__(self, simu):
        self.simu = simu

    def __repr__(self):
        description = '\n'.join([
            'number of bands: {}'.format(self.bands.shape[0])
        ])

        return description

    @property
    def bands(self):
        return self.simu.core.get_bands_df()

    @property
    def virtualDirections(self):
        return self.simu.core.get_virtual_directions()

    @property
    def sensors(self):
        return self.simu.core.get_sensors()
