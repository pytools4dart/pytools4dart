#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 14:15:03 2018

@author: mtd

This module contains the class "simulation".
This class allows for the storing of all of data relevant to the simulation.
It can be either created by one of the functions of the UFPD
(UserFriendlyPytoolsforDart),
or interactively in code lines.

The purpose of this module is not to produce the Dart xml input files.
It acts as a buffer between the "raw" parameter related information, and the
xml editing functions.
"""
import xmlwriters as dxml
from voxReader import voxel
import pandas as pd


class simulation(object):
    """Simulation object allowing for storing and editing of all the parameters



    """

    def __init__(self, outpath):
        """initialisation

        self.plots is supposed to be a pandaDataFrame that can be modified by
        the user.

        """
        self.changetracker = [[], {}, outpath, "flux"]
        self.plotsnumber = 0
        self.optsprops = {'prop1': 'Lambertian_Phase_Function_1',
                          'prop2': 'custom'}
        self.plots = None
        self.scene = [10, 10]

    def _registerchange(self, param):
        if param not in self.changetracker[0]:
            self.changetracker[0].append(param)
            self.changetracker[1][param] = {}
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

    def plotsfromvox(self, path):
        """Adds Plots based on AMAP vox file.

        Based on code from Claudia, Florian and Dav.
        Needs "voxreader". Most complicated function being: intersect,
        that is needed in Dav's project to get the optical properties of the
        voxels depending on another file.
        For now redundant : panda from panda..
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

            corners = (((i * res), (j * res)),
                       ((i + 1 * res), (j * res)),
                       (((i + 1) * res), ((j + 1) * res)),
                       ((i * res), ((j + 1) * res)))

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

        TODO
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


# ##################################zone de tests
if __name__ == '__main__':
    pof = simulation('/media/mtd/stock/boulot_sur_dart/temp/'
                     'essai_sequence/input')
    pof.addplot()
    pof.addsequence({'hello': (1, 2, 3)})
    pof.write_xmls()
