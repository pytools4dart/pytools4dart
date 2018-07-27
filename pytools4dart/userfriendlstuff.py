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

This modules contains all the user-friendly functions that interact with a
simulation object.
"""
import simulation

def simulationfromfile():
    """
    reads full set of parameters from a file and feeds its info to a simulation object
    """
    pof =simulation.simulation()
    return pof

def easysim():
    """
    basic simulation with few parameters
    """
    return

def hardersim():
    """
    a bit more complexity
    """
    return

def simtrees(outpath, header = None, trees = None):
    """Creates a simulation based on a set of files

    Takes information from a header for measured wvls,
    from a trees.txt for trees.
    A default optical property is specified for trees species.
    TODO : Refine optical property adding (interactive)
    """
    pof = simulation.simulation(outpath)

    optpropveg = ['vegetation', 'proprieteopt2',
                  '/media/mtd/stock/DART/database/Vegetation.db',
                  'ash_top', '0']
    pof.addopt(optpropveg)
    if header:
        pof.addband(header)
    if trees:
        pof.addtrees(trees)
        pof.trees['SPECIES_ID'] = 0
        pof.addtreespecie()

    return
