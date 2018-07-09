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
This module contains the class "simulation".
This class allows for the storing of all of data relevant to the simulation.
It can be either created by one of the functions of the UFPD
(UserFriendlyPytoolsforDart),
or interactively in code lines.

The purpose of this module is not to produce the Dart xml input files.
It acts as a buffer between the "raw" parameter related information, and the
xml editing functions.
"""

import os
import pandas as pd
# local imports
import xmlwriters as dxml
from voxReader import voxel


class simulation(object):
    """Simulation object allowing for storing and editing of all the parameters



    """

    def __init__(self, outpath):
        """initialisation

        self.plots is supposed to be a pandaDataFrame that can be modified by
        the user.
        WARNING : For now, 'flux' ( changetracker[3]) is hardcoded in the
        simulation object. It will have to be flexible depending on input.

        """
        self.changetracker = [[], {}, outpath, "flux"]
        self.plotsnumber = 0
        self.optsprops = {'prop1': 'Lambertian_Phase_Function_1',
                          'prop2': 'custom'}
        self.nbands = 0
        self.plots = None
        self.scene = [10, 10]

    def _registerchange(self, param):
        """updates changetracker 0 and creates dictionnaries on the fly
        """
        if param not in self.changetracker[0]:
            self.changetracker[0].append(param)
            self.changetracker[1][param] = {}
        return

    def addband(self, invar):
        """add spectral band to simulation sensor

        Possibility to add a band either from a HDR file, txt file, list
        or dictionnary: central band, width
        """
        self._registerchange('phase')
        if os.path.isfile(invar):
            if invar.endswith('.hdr'):
                print 'hey'
            else:
                print 'ho'
        else:
            try:
                self.changetracker[1]['phase']
            except TypeError:
                print "Hey man, you sure your variable's correct?"
        return

    def addsingleplot(self, corners=None, baseheight=1, density=1,
                      opt="custom", ident=None):
        """adds a plot to the scene with certain parameters

        For now, if no corners are specified, a default plot is created
        covering the whole scene). If no optical property is specified, a
        "custom" one is assigned:  vegetation - leaf deciduous.
        This optical property if initialized by default in
        coeff_diff.addvegetation()
        """
        self._registerchange('plots')
        if not self.plots:
            self.plots = pd.DataFrame(columns=['corners', 'baseheight',
                                               'density', 'optprop'])

        if not ident:
            ident = self.plotsnumber
        if not corners:
            corners = ((self.scene[0],  self.scene[1]),
                       (self.scene[0],  0),
                       (0,              0),
                       (0,              self.scene[1]))

        data = [corners, baseheight, density, opt]
        cols = ['corners', 'baseheight', 'density', 'optprop']
        miniframe = pd.DataFrame(dict(zip(cols, data)))
        self.plots.append(miniframe)
        self.plotsnumber += 1
        return

    def addsequence(self, parargs, group='default', name='sequence'):
        """add a sequence xml file with given parameters

        parargs must be a dictionnary structured in this way :
            parargs = { 'parameter1' : basevalue, stepvalue, numberofsteps}
        """
        try:
            parargs.keys()
        except TypeError:
            print 'sequence input must be a dictionnary = {parameters:args}'

        self._registerchange('plots')

        for param, args in parargs.iteritems():
            print 'key=', param
            print 'values=', args
            if group not in self.changetracker[1]['sequence']:
                self.changetracker[1]['sequence'][group] = {}

            self.changetracker[1]['sequence'][group][param] = args
        self.changetracker[1]['sequencename'] = name
        return

    def setscene(self, scene):
        """change scene dimensions
        """
        self._registerchange('maket')
        self.scene = scene
        return

    def setoptplots(self, opt, mode=None):
        """sets the optical property of the plots

        TODO : modify and add options : superior plots...
        """
        if not self.plots:
            print "There are no plots in this simulation"
            return
        else:
            self.plots['optprop'] = opt
        return

    def plotsfromvox(self, path):
        """Adds Plots based on AMAP vox file.

        Based on code from Claudia, Florian and Dav.
        Needs "voxreader". Most complicated function being: intersect,
        that is needed in Dav's project to get the optical properties of the
        voxels depending on another file.
        For now redundant : panda from panda..
        TODO : simplification, for now a pd is read into another pd
        """
        self._registerchange('plots')
        self.changetracker[1]['plots']['voxels'] = True
        vox = voxel.from_vox(path)
        voxlist = []
        colnames = ['corners', 'baseheight', 'density', 'optprop']
        res = vox.header["res"][0]

        for index, row in vox.data.iterrows():
            i = row.i  # voxel x
            j = row.j  # voxel y
            k = row.k  # voxel z
            optPropName = None
            LAI = str(row.PadBVTotal)  # voxel LAI(PadBTotal en negatif)

            corners = (((i * res),          (j * res)),
                       ((i + 1 * res),      (j * res)),
                       (((i + 1) * res),    ((j + 1) * res)),
                       ((i * res),          ((j + 1) * res)))

            height = res
            baseheight = str(k * height)  # voxel height

            voxlist.append(dict(zip(colnames,
                                    [corners, baseheight, LAI, optPropName])))
            self.plotsnumber += 1

        self.plots = \
            pd.DataFrame(voxlist, columns=colnames)
        print ("Plots added from .vox file.")
        print ("Optical properties have to be added in the column 'optprop' ")
        return

    def listmodifications(self):
        """returns record of modifications to simulation

        TODO : stuff
        """
        print 'Impacted xml files:'
        print self.changetracker[0]

        return

    def write_xmls(self):
        """writes the xmls with all defined input parameters

        The functions are written so that default parameters are first written,
        then updated with the given changes contained in "changetracker".
        """
        self.changetracker['plots']['voxels'] = self.plots

        dxml.write_atmosphere(self.changetracker)
        dxml.write_coeff_diff(self.changetracker)
        dxml.write_directions(self.changetracker)
        dxml.write_inversion(self.changetracker)
        dxml.write_maket(self.changetracker)
        dxml.write_object_3d(self.changetracker)
        dxml.write_phase(self.changetracker)
        dxml.write_plots(self.changetracker)
        dxml.write_sequence(self.changetracker)
        dxml.write_trees(self.changetracker)
        dxml.write_urban(self.changetracker)
        dxml.write_water(self.changetracker)
        return

    def launch(self):
        """launch the simulation with set parameters

        """

        return

    def pickupfile(self, path):
        """uses a previously defined .xml dart file
        """
        dartfile = os.path.splitext(os.path.basename(path))
        self.changetracker[1]['usefile'][dartfile] = path
        return

    def getsfileparams(self, path):
        """gets the parameters of
        """
        return


# ##################################test zone
if __name__ == '__main__':
    pof = simulation('/media/mtd/stock/boulot_sur_dart/temp/'
                     'essai_sequence/input')
    pof.addplot()
    pof.addsequence({'hello': (1, 2, 3)})
    pof.write_xmls()
