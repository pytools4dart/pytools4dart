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
from voxreader import voxel
from hdrtodict import hdrtodict


class simulation(object):
    """Simulation object allowing for storing and editing of all the parameters


    """

    def __init__(self, outpath):
        """initialisation

        self.plots is supposed to be a pandaDataFrame that can be modified by
        the user.
        TODO : WARNING : For now, 'flux' ( changetracker[3]) is hardcoded in
        the simulation object. It will have to be flexible depending on input.

        optprops is a dictionnary containing two lists :
            for each type : 'lambertian' or 'vegetation'
            -ident: string for name
            -database: string-path to database
            -modelname: name of opt in database
            if lambertian :
                -specular : 0 or 1, 1 if UseSpecular
            if vegetation :
                -lad : leaf angle distribution :
                    - 0: Uniform
                    - 1: Spherical
                    - 3: Planophil
        """
        # Variables to be used in subsequent methods
        self.PLOTCOLNAMES = ['corners', 'baseheight', 'density', 'optprop']
        self.BANDSCOLNAMES = ['bandnames', 'centralwvl', 'fwhm']

        self.changetracker = [[], {}, outpath, "flux"]
        self.plotsnumber = 0
        defaultlamb = ['Lambertian_Phase_Function_1',
                       'Lambertian_vegetation.db',
                       'reflect_equal_1_trans_equal_0_0',
                       '0']

        self.optprops = {'lambertians': [defaultlamb],
                         'vegetations': []}
        self.nbands = 0
        self.bands = pd.DataFrame(columns=self.BANDSCOLNAMES)
        self.plots = pd.DataFrame(columns=self.PLOTCOLNAMES)
        self.scene = [10, 10]
        self.cell = [1, 1]
        self.nspecies = 0
        self.trees = 0
        print ('New Simulation initiated')
        print('--------------\n')

    def __repr__(self):
        return "pytools4dart simulation object"

    def __str__(self):
        # TODO : Description
        return "pytools4dart simulation object"

    def _registerchange(self, param):
        """updates changetracker 0 and creates dictionnaries on the fly
        """
        if param not in self.changetracker[0]:
            self.changetracker[0].append(param)
            self.changetracker[1][param] = {}
        return

    def addband(self, invar, nmtomicron=True):
        """add spectral band to simulation sensor

        Possibility to add a band either from a HDR file, txt file, list
        or dictionnary: central band, width
        if txt data separate by spaces.
        bandnumer(optional) wavelengthcenter wavelengthwidth
        hdrnm is used to convert nm to µm when reading from header.
        TODO : check if .txt info works.

        Parameters
        ----------
        invar: list or str
            invar can be either the path to a hdr, a txt file, or a
            list containing :
                -BandName (optionnal)
                -central wavelength(in µm)
                -fwhm (in µm)
        """
        self._registerchange('phase')
        try:
            os.path.isfile(invar)
            if invar.endswith('.hdr'):
                print 'reading header'
                hdr = hdrtodict(invar)
                data = zip(hdr['band names'], hdr['wavelength'], hdr['fwhm'])
                data = pd.DataFrame(data)
                data.columns = self.BANDSCOLNAMES
                if nmtomicron:
                    data['centralwvl'] = data['centralwvl'].apply(pd.to_numeric)
                    data['fwhm'] = data['fwhm'].apply(pd.to_numeric)
                    data.loc[:, 'centralwvl'] *= 0.001
                    data.loc[:, 'fwhm'] *= 0.001

                self.bands = self.bands.append(data, ignore_index=True)
                print ("header successfully read.")
                print ("{} bands added".format(len(hdr['fwhm'])))
                print('--------------\n')

            else:
                try:
                    # Try to read bands from txt
                    print 'reading text'
                    with open(invar) as f:
                        line = f.readline()
                        band = line.split()

                    if len(band) == 2:
                        data = pd.read_csv(invar, sep=" ", header=None)
                        data.columns = ["centralwvl", "fwhm"]
                        # in order to add band numbers
                        lencol = len(data["fwhm"])
                        data['bandnumber'] = range(0, lencol)
                        self.bands = self.bands.append(data, ignore_index=True)

                    elif len(band) == 3:
                        data = pd.read_csv(invar, sep=" ", header=None)
                        data.columns = self.BANDCOLNAMES
                        self.bands = self.bands.append(data, ignore_index=True)
                except TypeError:
                    print " Trouble reading txt file"
        except TypeError:
            try:
                # Try to read band from a list
                addband = pd.Series(invar)
                if len(addband) == 2:
                    addband.name = self.nbands+1
                    addband.index = self.BANDSCOLNAMES[1:]
                    self.bands = self.bands.append(addband,
                                                   ignore_index=True)
                    self.nbands += 1

                elif len(addband) == 3:
                    addband.name = addband[0]
                    addband.index = self.BANDSCOLNAMES
                    self.bands = self.bands.append(addband, ignore_index=True)
                    self.nbands += 1

                else:
                    return
            except TypeError:
                print "Big Problem"
                return

    def addopt(self, optprop):
        """adds and optical property to the simulation

        TODO : think about : do we want optprops as an object?
        simplified management of all variables...
        Vegetation.db is Dart default.
        TODO : Managing Thermal properties?

        Parameters
        ----------
        optprop : list
            optprop is supposed to be structured this way :
                -type : 'lambertian' or 'vegetation'
                -ident: string for name
                -database: string-path to database
                -modelname: name of opt in database
                if lambertian :
                    -specular : 0 or 1, 1 if UseSpecular
                if vegetation :
                    -lad : leaf angle distribution :
                        - 0: Uniform
                        - 1: Spherical
                        - 3: Planophil

        """
        if optprop[0] == 'lambertian':
            self.optprops['lambertians'].append(optprop[1:])
        elif optprop[0] == 'vegetation':
            self.optprops['vegetations'].append(optprop[1:])
        else:
            print 'Non recognized optical property type. Returning'
            return

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

        if not ident:
            ident = self.plotsnumber
        if not corners:
            corners = ((self.scene[0],  self.scene[1]),
                       (self.scene[0],  0),
                       (0,              0),
                       (0,              self.scene[1]))

        data = [corners, baseheight, density, opt]
        miniframe = pd.DataFrame([data], columns=self.PLOTCOLNAMES)
        self.plots = self.plots.append(miniframe, ignore_index=True)
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
            return
        self._registerchange('plots')

        for param, args in parargs.iteritems():
            print 'key =', param
            print 'values =', args
            if group not in self.changetracker[1]['sequence']:
                self.changetracker[1]['sequence'][group] = {}

            self.changetracker[1]['sequence'][group][param] = args
        self.changetracker[1]['sequencename'] = name
        return

    def addtrees(self, path):
        """Add trees.txt file to the simulation

        TODO : The biggest problem is the simultaneous management of the
        trees.txt and of Dart's trees.xml.
        Here, trees are defined as lines in a panda dataframe. rows will have
        to be split into trees xml writer AND trees.txt

        The XML OPT PROP goes with a "FctPhaseIndex".
        TODO : Empy leaf cells/ leaves+ holes management!
                        -- > 'distribution' parameter
        Big question : from what will a tree be created?
        tree must contain :
            -specie ID
            -C_TYPE (type of crown geometry)
                -0 = ellipsoid, 1=ellipsoid composed, 2=cone,
                 3=trapezoid, 5=cone composed
            -X
            -Y
            -Height below crown
            -Heiht within crown
            -diameter below crown
            -Trunk Rotation
            -Trunk nutation rotation

        Parameters
        ----------
        path : string
            Path to the trees.txt file to be read into simulation
        """

        if self.nspecies == 0:
            print "Warning : No tree specie has been defined."
            print "The trees you will add have no optical link."

        if self.trees == 0:
            self.trees = pd.read_csv(path, comment='*', sep='\t')
        else:
            print "appending trees to the existing trees dataframe : "
            newtrees = pd.read_csv(path, comment='*', sep='\t')
            self.trees.append(newtrees, ignore_index=True)

            # columns
#            # cols = ['SPECIES_ID', 'C_TYPE', 'POS_X', 'POS_Y', 'T_HEI_BELOW',
#                    'T_HEI_WITHIN', 'DIA_BELOW','T_ROT_NUT',' T_ROT_PRE',
#                    'C_HEI', 'C_GEO_1', 'C_GEO_2', 'XMLtrunkoptprop',
#                    'XMLtrunkopttype',
#                    'XMLtrunkthermalprop', 'XMLvegoptprop', 'XMLvegthermprop',
#                    'XMLleafholes', ]
        self._registerchange('trees')
        print "trees added."
        print ("Species can be modified through the \"SpeciesID\" column of "
               "the dataframe : simulation.trees")
        print('--------------\n')
        return

    def addtreespecie(self, ntrees='1', lai='4.0', holes='0',
                      trunkopt='Lambertian_Phase_Function_1',
                      trunktherm='ThermalFunction290_310',
                      vegopt='custom',
                      vegtherm='ThermalFunction290_310'):
        """
        properties of a specie :
            - number of trees
            - LAI > 0 or Ul <0
            - hole simulation
            - trunk opt prop
            - trunk therm prop
            - veg opt prop
            - veg therm prop
        """
        if self.nspecies == 0:
            self.species = []

        specie = {'id': self.nspecies, 'ntrees': ntrees, 'lai': lai,
                  'crowns': [[holes, trunkopt, trunktherm, vegopt, vegtherm]]}
        self.species.append(specie)
        self.nspecies += 1
        self._registerchange('trees')
        print ("A tree specie has been added. Make sure the specified optical "
               "properties match those defined in self.optsprops\n")
        print('--------------\n')

        return

    def setscene(self, scene):
        """change scene dimensions

        """
        self._registerchange('maket')
        self.scene = scene
        return

    def setcell(self, cell):
        """change cell dimensions
        TODO : maybe a bit more verbose?
        """
        self._registerchange('maket')
        self.cell = cell
        return

    def setoptplots(self, opt, mode=None):
        """sets the optical property of the plots

        TODO : modify and add options : superior plots...
        For now sets ALL plots to the same 'opt' optical property
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
        res = vox.header["res"][0]

        for index, row in vox.data.iterrows():
            i = row.i  # voxel x
            j = row.j  # voxel y
            k = row.k  # voxel z
            optpropname = None
            LAI = str(row.PadBVTotal)  # voxel LAI(PadBTotal en negatif)

            corners = (((i * res),          (j * res)),
                       ((i + 1 * res),      (j * res)),
                       (((i + 1) * res),    ((j + 1) * res)),
                       ((i * res),          ((j + 1) * res)))

            height = res
            baseheight = str(k * height)  # voxel height

            voxlist.append(dict(zip(self.PLOTCOLNAMES,
                                    [corners, baseheight, LAI, optpropname])))
            self.plotsnumber += 1
        data = pd.DataFrame(voxlist, columns=self.PLOTCOLNAMES)
        self.plots.append(data, ignore_index=True)
        print ("Plots added from .vox file.")
        print ("Optical properties have to be added in the column 'optprop'\n")
        return

    def indexprops(self):
        """Creates the index for optical properties

        This function is necessary in order to have easy tracking of
        optical properties indices "IndexFctPhase" which is referenced a lot
        in Dart XMLs.
        TODO : Index Thermal properties!
        """
        index = 0
        self.index_lamb = {}
        for lamb in self.optprops['lambertians']:
            self.index_lamb[lamb[0]] = index
            index += 1
        index = 0
        self.index_veg = {}
        for veg in self.optprops['vegetations']:
            self.index_veg[veg[0]] = index
            index += 1
        self.indexopts = {'lambertians': self.index_lamb,
                          'vegetations': self.index_veg}

        return

    def listmodifications(self):
        """returns record of modifications to simulation

        TODO : stuff to make all that look nicer.
        """
        print 'Impacted xml files:'
        print self.changetracker[0]

        return

    def write_xmls(self):
        """writes the xmls with all defined input parameters

        The functions are written so that default parameters are first written,
        then updated with the given changes contained in "changetracker".
        WARNING : For now this function is the only proper way to write
        the DART xmls.
        """
        # self.checksimu()

        print 'Writing XML files'
        # WARNING : Terminology Problem?
        self.bands.index += 1
        """
        TODO : stuff to do here to properly write "trees.txt"
        if self.istrees:
            self.trees.to_string()

        WARNING : important to write coeff diff before indexing opt props :
            coeff diff needs all optprops info, whereas the other writers
            only need ident + index.
        WARNING : here the structure for changetracker[1]['trees'] is defined.
        TODO : Better Check and Error catch for trees.(and in general)
        """
        # Setting changetracker
        self.indexprops()
        self.changetracker[1]['coeff_diff'] = self.optprops
        dxml.write_coeff_diff(self.changetracker)

        self.changetracker[1]['indexopts'] = self.indexopts

        self.changetracker[1]['plots'] = self.plots
        self.changetracker[1]['phase']['bands'] = self.bands

        self.changetracker[1]['maket']

        # Effectively write xmls
        dxml.write_atmosphere(self.changetracker)
        dxml.write_directions(self.changetracker)
        dxml.write_inversion(self.changetracker)
        dxml.write_maket(self.changetracker)
        dxml.write_object_3d(self.changetracker)
        dxml.write_phase(self.changetracker)
        dxml.write_plots(self.changetracker)
        dxml.write_sequence(self.changetracker)
        # Special stuff for trees : writing trees.txt and pass the path
        # But bad condition...for now
        if self.nspecies > 0:
            pathtrees = self.changetracker[2]+'pytrees.txt'
            self.trees.to_csv(pathtrees, sep="\t", header=True, index=False)
            self.changetracker[1]['trees'] = pathtrees
            self.changetracker[1]['treespecies'] = self.species
            dxml.write_trees(self.changetracker)

        dxml.write_urban(self.changetracker)
        dxml.write_water(self.changetracker)
        return

    def launch(self):
        """launch the simulation with set parameters

        TODO : subprocess.popen stuff...
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
    import time
    start = time.time()
    """
    pof = simulation('/media/mtd/stock/boulot_sur_dart/temp/'
                     'essai_sequence/input/')
    corners = ((3,  4),
               (3,  0),
               (0,  0),
               (0,  4))
    pof.addsingleplot(corners=corners, opt='proprieteopt2')
    pof.addsingleplot(corners=corners, opt='proprieteopt3')
    pof.addsingleplot(corners=corners, opt='proprieteopt1')

    #   pof.addband([1, 2, 3])
    #   pof.addband([2, 2, 3])
    pof.addband([12, 2, 3])
    pof.addband("/media/mtd/stock/boulot_sur_dart/temp/hdr/crop2.hdr")
    optprop = ['lambertian', 'proprieteopt', 'Vegetation.db', 'truc', '0']
    pof.addopt(optprop)

    optpropveg = ['vegetation', 'proprieteopt2',
                  '/media/mtd/stock/DART/database/Vegetation.db',
                  'ash_top', '0']
    pof.addopt(optpropveg)

    optpropveg = ['vegetation', 'proprieteopt1',
                  '/media/mtd/stock/DART/database/Vegetation.db',
                  'elm_top', '0']
    pof.addopt(optpropveg)

    optpropveg = ['vegetation', 'proprieteopt3',
                  '/media/mtd/stock/DART/database/Vegetation.db',
                  'beech_middle', '0']

    pof.addopt(optpropveg)

    pof.listmodifications()
    #   pof.addsequence({'hello': (1, 2, 3)})
    pof.write_xmls()
    print(pof.bands)
    """
    pof = simulation('/media/mtd/stock/boulot_sur_dart/temp/'
                     'testrees/input/')
    pof.addtreespecie(vegopt = 'proprieteopt2',
                      trunkopt = 'Lambertian_Phase_Function_1')

    pof.addband("/media/mtd/stock/boulot_sur_dart/temp/hdr/crop2.hdr")
    optprop = ['lambertian', 'proprieteopt', 'Vegetation.db',
               'citrus_sinensis', '0']
    pof.addopt(optprop)

    optpropveg = ['vegetation', 'proprieteopt2',
                  '/media/mtd/stock/DART/database/Vegetation.db',
                  'ash_top', '0']
    pof.addopt(optpropveg)
    path = '/media/mtd/stock/boulot_sur_dart/temp/testrees/model_trees.txt'
    pof.addtrees(path)
    pof.addsingleplot(opt='proprieteopt2')
    pof.trees['SPECIES_ID'] = 0
    pof.write_xmls()
    end = time.time()
    print(end - start)
