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
    """Simulation object allowing for storing and editing of all the parameters



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
        This optical property if initialized by default in
        coeff_diff.addvegetation()
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

    def addsequence(self, parargs, group='default', name='sequence'):
        """add a sequence xml file with given parameters

        parargs must be a dictionnary structured in this way :
            parargs = { 'parameter1' : basevalue, stepvalue, numberofsteps}
        """
        try:
            parargs.keys()
        except TypeError:
            print 'sequence input must be a dictionnary = {parameters:args}'

        if 'sequence' not in self.changetracker[0]:
            self.changetracker[0].append('sequence')
            self.changetracker[1]['sequence'] = {}

        for param, args in parargs.iteritems():
            print 'key=', param
            print 'values=', args
            if group not in self.changetracker[1]['sequence']:
                self.changetracker[1]['sequence'][group] = {}

            self.changetracker[1]['sequence'][group][param] = args
        self.changetracker[1]['sequencename'] = name
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
