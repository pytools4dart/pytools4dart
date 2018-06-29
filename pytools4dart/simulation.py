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


class simulation(object):
    """Simulation object allowing for the storing and editing of all the parameters



    """

    def __init__(self, outpath):
        """initialisation

        """
        self.changetracker = [[], {}, outpath, "flux"]
        self.plotsnumber = 0
        self.optsprops = {'prop1': 'Lambertian_Phase_Function_1'}

    def addparameterX(self, param):
        """interactively add a parameter

        """
        self.param = param
        return

    def addplot(self, corners=None, baseheight=None, density=None,
                opt="custom", ident=None):
        """adds a plot to the scene with certain parameters

        For now, if no corners are specified, a default plot is created
        covering 10 by 10 meters (perspective to change it to cover the whole
        scene). If no optical property is specified, a "custom" one is assigned
        vegetation - leaf deciduous.
        """
        if not ident:
            ident = self.plotsnumber
        if not corners:
            plottype = "default"

        if "plots" not in self.changetracker[0]:
            self.changetracker[0].append("plots")
            self.changetracker[1]['plots'] = {}

        self.changetracker[1]['plots']['plot_' + str(ident)] = {
            'plottype': plottype, 'opt': opt, 'corners': corners,
            'baseheight': baseheight, 'density': density}
        self.plotsnumber += 1

        return

    def setscene():
        return

    def listmodifications(self):
        """returns record of modifications to simulation

        """
        return

    def write_xmls(self):
        """writes the xmls with all defined input parameters

        The functions are written so that default parameters are first written,
        then updated with the given changes contained in "changetracker".
        """

        dxml.write_atmosphere(self.changetracker)
        dxml.write_coeff_diff(self.changetracker)
        dxml.write_directions(self.changetracker)
        dxml.write_inversion(self.changetracker)
        dxml.write_maket(self.changetracker)
        dxml.write_object_3d(self.changetracker)
        dxml.write_phase(self.changetracker)
        dxml.write_plots(self.changetracker)
        # dxml.write_sequence(self.changetracker)
        dxml.write_trees(self.changetracker)
        dxml.write_urban(self.changetracker)
        dxml.write_water(self.changetracker)
        return

    def launch(self):
        """launch the simulation with set parameters

        """

        return


# ##################################zone de tests
pof = simulation('/media/mtd/stock/boulot_sur_dart/temp/check/')
pof.addplot()
pof.write_xmls()
