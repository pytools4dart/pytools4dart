#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
===============================================================================
# PROGRAMMERS:
#
# Eric Chraibi <eric.chraibi@irstea.fr>  -
https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
#
# Copyright 2018 Eric Chraibi
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
===============================================================================
to be called this way :
    from xmlwriters import *

"""
from atmosphere import write_atmosphere
from coeff_diff import write_coeff_diff
from directions import write_directions
from inversion import write_inversion
from maket import write_maket
from object_3d import write_object_3d
from phase import write_phase
from plots import write_plots
from sequence import write_sequence
from trees import write_trees
from urban import write_urban
from water import write_water


__all__ = ['atmosphere', 'coeff_diff', 'directions', 'inversion',
           'maket', 'object_3d', 'phase', 'plots', 'sequence', 'trees',
           'urban', 'water']
