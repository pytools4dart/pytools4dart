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
This module contains some useful constants.
"""

spbands_fields = ['wvl', 'fwhm']

grd_opt_prop_types_dict = {0: "lambertian", 2: "hapke", 4: "rpv"}
grd_opt_prop_types_inv_dict = {"lambertian": 0, "hapke": 2, "rpv": 4}
plot_types_dict = {0: "ground", 1: "vegetation", 2: "veg_ground", 3: "fluid"}
plot_types_inv_dict = {"ground": 0, "vegetation": 1, "veg_ground": 2, "fluid": 3}
plot_form_dict = {0: "polygon", 1: "rectangle"}
plot_form_inv_dict = {"polygon": 0, "rectangle": 1}