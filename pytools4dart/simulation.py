#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
===============================================================================
# PROGRAMMERS:
#
# Eric Chraibi <eric.chraibi@irstea.fr>, Florian de Boissieu <florian.deboissieu@irstea.fr>
# https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
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
from os.path import join as pjoin
import pandas as pd
import subprocess
import pprint
import numpy as np
# local imports
import xmlwriters as dxml
from helpers.voxreader import voxel
from helpers.hstools import read_ENVI_hdr, get_hdr_bands, get_bands_files, get_wavelengths, stack_dart_bands
from settings import getsimupath, get_simu_input_path, get_simu_output_path
import pytools4dart.run as run

# from helpers.foldermngt import checksettings


class simulation(object):
    """Simulation object corresponding to a DART simulation.
    It allows for storing and editing parameters, and running simulation
    """

    def __init__(self, name = None):
        """
        Initialisation
        Parameters
        ----------
        name: str
            Name of the simulation

        TODO : WARNING : For now, 'flux' ( changetracker[3]) is hardcoded in
        the simulation object. It will have to be flexible depending on input.
        Temperatures not managed.

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

        self.name = name

        # Variables to be used in subsequent methods
        self.PLOTCOLNAMES = ['x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 'y4',
                             'zmin', 'dz', 'density',
                             'densitydef', 'optprop']
        self.BANDSCOLNAMES = ['wvl', 'fwhm']

        self.changetracker = [[], {}, "flux"]

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

        self.prosparams = ['CBrown', 'Cab', 'Car', 'Cm',
                           'Cw', 'N', 'anthocyanin']
        self.prossequence = 0

        self.run = run.runners(self)

        print ('New Simulation initiated')
        print('--------------\n')

    def __repr__(self):
        return "pytools4dart simulation object"

    def __str__(self):
        # TODO : Description
        return "pytools4dart simulation object"

    def _registerchange(self, param):
        """update changetracker 0 and creates dictionnaries on the fly
        Parameters
        ----------
        param: list
            Parameters to be added or updated

        Returns
        -------
            None
        """
        if param not in self.changetracker[0]:
            self.changetracker[0].append(param)
            self.changetracker[1][param] = {}
        return


    def add_bands(self, x, verbose=False):
        """add spectral band to simulation sensor

        Possibility to add a band either from a HDR file, txt file, list
        or dictionnary: central band, width
        if txt data separate by spaces.
        bandnumer(optional) wavelengthcenter wavelengthwidth
        hdrnm is used to convert nm to µm when reading from header.
        TODO : check if .txt info works. Split into 3 smaller helper functions

        Parameters
        ----------
        x: DataFrame, dict or str
            - if DataFrame it is expected to have columns 'wvl' and 'fwhm'
            - if dict it is expected to have elements: 'wvl' and 'fwhm'
            - if str it should be the path to an ENVI hdr
            or a csv file with 2 columns
        """
        if isinstance(x, pd.DataFrame):
            # check columns:
            if not set(self.BANDSCOLNAMES).issubset(x.columns):
                print("'wvl' or 'fwhm' is missing.")
            self.bands = self.bands.append(x.loc[:, self.BANDSCOLNAMES], ignore_index=True)
            self._registerchange('phase')

        elif isinstance(x, dict):
            self.add_bands(pd.DataFrame(columns=x.keys()).\
                         append(x, ignore_index=True), verbose)
        elif isinstance(x, basestring):
            if not os.path.isfile(x):
                print 'File not found: '+x
                return
            if x.endswith('.hdr'):
                hdr = read_ENVI_hdr(x)
                data = get_hdr_bands(hdr).rename({'wavelength':'wvl'})
                self.add_bands(data)
                if verbose:
                    print ("header successfully read.")
                    print ("{} bands added".format(len(hdr['fwhm'])))
                    print('--------------\n')

            else:
                try:
                    # Try to read bands from txt
                    print 'reading text'
                    with open(x) as f:
                        line = f.readline()
                        band = line.split()

                    if len(band) == 2:
                        data = pd.read_csv(x, sep=" ", header=None)
                        data.columns = ['wvl', 'fwhm']
                        # in order to add band numbers
                        lencol = len(data['fwhm'])
                        data['bandnumber'] = range(0, lencol)
                        self.bands = self.bands.append(data, ignore_index=True)

                    elif len(band) == 3:
                        data = pd.read_csv(x, sep=" ", header=None)
                        data.columns = self.BANDCOLNAMES
                        self.bands = self.bands.append(data, ignore_index=True)
                except TypeError:
                    print " Trouble reading txt file"

        else:
            print('x type not supported')

    def addopt(self, optprop):
        """adds and optical property to the simulation

        TODO : think about : do we want optprops as an object?
        TODO : Managing Thermal properties?
        TODO : Add Error catching!

        Parameters
        ----------
        optprop : list
            with the following ordered elements:
                    - type : 'lambertian' or 'vegetation'
                    - ident: string for name
                    - database: string-path to database
                    - modelname: name of opt in database

                if lambertian :
                    - specular : 0 or 1, 1 if UseSpecular
                if vegetation :
                    - lad : leaf angle distribution :
                        - 0: Uniform
                        - 1: Spherical
                        - 3: Planophil

            default lambertian in DART is:
            ['lambertian', 'Lambertian_Phase_Function_1', 'Lambertian_vegetation.db',
            'reflect_equal_1_trans_equal_0_0', 0]

            default vegetation in DART is:
            ['vegetation', 'Turbid_Leaf_Deciduous_Phase_Function', 'Vegetation.db',
            'leaf_deciuous', 1]

        """
        self._registerchange('coeff_diff')
        if optprop[0] == 'lambertian':
            if optprop[1] in self.optprops['lambertians']:
                print 'Please chose a new name for the new optical property'
                print 'Returning'
            else:
                self.optprops['lambertians'].append(optprop[1:])
                self.setindexprops()
        elif optprop[0] == 'vegetation':
            if optprop[1] in self.optprops['vegetations']:
                print 'Please chose a new name for the new optical property'
                print 'Returning'
            else:
                self.optprops['vegetations'].append(optprop[1:])
                self.setindexprops()
        else:
            print 'Non recognized optical property type. Returning'
            return

        return

    def addsequence(self, parargs, group='default', name='sequencepytdart',
                    verbose=False, variationmode='linear'):
        """add a sequence xml file with given parameters

        Parameters
        ---------
        parargs : dic
            must be a dictionnary structured in this way :
            parargs = { 'parameter1' : basevalue, stepvalue, numberofsteps}
        group : str, optional
            string assigning a name to the group of the sequence. This allows
            for the combination of variation of parameters in a single sequence
        name : str, optional
            name of the sequence (given to the xml file).
        TODO : For now only LINEAR, should be possible to change to enumerate
        """
        try:
            parargs.keys()
        except AttributeError:
            print 'sequence input must be a dictionnary = {parameters:args}'
            return
        self._registerchange('sequence')

        for param, args in parargs.iteritems():
            if verbose:
                print 'key =', param
                print 'values =', args
            if group not in self.changetracker[1]['sequence']:
                self.changetracker[1]['sequence'][group] = {}

            self.changetracker[1]['sequence'][group][param] = args

        try:
            self.changetracker[1]['sequencename']
        except KeyError:
            self.changetracker[1]['sequencename'] = name
        else:
            print 'The xml sequence file was already named {}' \
                .format(self.changetracker[1]['sequencename'])
            return
        return

    def addprospectsequence(self, dic, optident, group=None,
                            name='prospect_sequence', lad=1):
        """adds a sequence of prospect generated optical properties

        Parameters
        ---------
        dic : dict
            must be a dictionary containing the prospect parameters
            and the assigned value. For now only one parameter can vary.
        optident : str
            name of the prospect optical property. For now created independently
            via addopt()

        TODO : Absolutey NOT Optimized nor clean!
        """
        # Here go the conditions for prospect, probably to write in another
        # function
        self._registerchange('prospect')
        self._registerchange('sequence')

        # definition of the 'blank' prospect optical property
        prosoptveg = ['vegetation', optident, 'prospect', 'blank', lad]
        self.addopt(prosoptveg)

        self.setindexprops()
        try:
            index = self.indexopts['vegetations'][optident]
        except KeyError:
            print 'Undefined optical Property!'
            print 'Please define first a blank prospect optical property.'
            print 'Returning.\n'
            return
        else:
            baseprospectstring = ('Coeff_diff.UnderstoryMultiFunctions.'
                                  'UnderstoryMulti[{}].'
                                  'ProspectExternalModule.'
                                  'ProspectExternParameters.')
            baseprospectstring = baseprospectstring.replace('{}', str(index))

            if not group:
                group = 'prosequence{}'.format(self.prossequence)
            elif not group.startswith('prosequence'):
                group = 'prosequence'+group
            maxlen = 0
            prosdic = {}
            for params in dic.iteritems():
                if params[0] not in self.prosparams:
                    raise ValueError('please enter one of the following'
                                     'values :{}'.format(self.prosparams))

                prosdic[baseprospectstring+params[0]] = params[1]
                # records max lengths of parameter to duplicate single values.
                if isinstance(params[1], list) and len(params[1]) > maxlen:
                    maxlen = len(params[1])
            # TODO : better type checking : in order to go from single element
            # to maxlen length list of identical values
            for key, value in prosdic.iteritems():
                if not isinstance(value, list):
                    prosdic[key] = [value] * maxlen
                elif len(value) != maxlen:
                    print "Error in Prospect parameter"
                    return

            self.addsequence(prosdic, group=group,
                             name=name, variationmode='enumerate')
            self.prossequence += 1
        return

    def add_singleplot(self, corners=None, baseheight=1, density=1,
                      opt="custom", ident=None, height=1, densitydef='ul'):
        """adds a plot to the scene with certain parameters

        For now, if no corners are specified, a default plot is created
        covering the whole scene). If no optical property is specified, a
        "custom" one is assigned:  vegetation - leaf deciduous.
        This optical property if initialized by default in
        coeff_diff.addvegetation()

        Parameters
        ----------
            corners : list, optional
                list of 4 lists, each containing the x and y of a corner
            baseheight: int, optional
                base height of the plot
            density : int, optional
                density of the plot
            opt : str, optional
                ident of the optical property assigned to the plot. Does not
                have to be created at the assignation time.
            ident: str, optional
                ident of the plot. Unused for now.
            densitydef: str, optional
                 defines the interpretation of the density value :
                     ul = m²/ m³
                     lai = m²/m²
        TODO : think about simpler corner definition
        TODO : add modifiable height
        """
        self._registerchange('plots')

        if not ident:
            ident = self.plotsnumber
        if not corners:
            corners = [[self.scene[0],  self.scene[1]],
                       [self.scene[0],  0],
                       [0,              0],
                       [0,              self.scene[1]]]
        data = np.array(corners).flatten().tolist()+[baseheight, height, density, densitydef, opt]
        miniframe = pd.DataFrame([data], columns=self.PLOTCOLNAMES)
        self.plots = self.plots.append(miniframe, ignore_index=True)
        self.plotsnumber += 1
        return

    def add_multiplots(self, data, colnames={'x1':'x1', 'y1':'y1', 'x2':'x2', 'y2':'y2',
                                            'x3':'x3', 'y3':'y3', 'x4':'x4', 'y4':'y4',
                                            'baseheight':'baseheight', 'height':'height',
                                            'density':'density', 'densitydef':'densitydef',
                                            'optprop':'optprop'}):
        """
        Appends a dataframe to plots based on a dictionnary

        Parameters
        ----------
        data : DataFrame
            Plots properties.
        colnames : dict
            Column names corresponding to PLOTSCOLNAMES.
        """

        """Appends a dataframe to plots based on a dictionnary

        dic = {Olndame:Newname, .....}
        new names in self.PLOTSCOLNAMES
        TODO : Error catching and protection of self.plots in case of
        modifications

        """
        self._registerchange('plots')
        data.rename(columns=dic, inplace=True)
        plots = self.plots.append(data, ignore_index=True)
        self.plots = plots

        print ("Dataframe successfully appended to plots")

        return

    def add_plots_from_vox(self, vox, densitydef='ul', optprop=None):
        """Add Plots based on AMAPVox file.

        Parameters
        ---------
            path: str
                path to the AMAPVox file
            densitydef: str
                'lai' or 'ul'
        """
        self._registerchange('plots')
        self.changetracker[1]['plots']['voxels'] = True

        voxlist = []
        res = vox.header["res"][0]

        # itertuples is 10x faster than apply (already faster than iterrows)
        # operation was tested
        # remove Ul=0 value, as it means empty voxel
        for row in vox.data[vox.data.PadBVTotal!=0].itertuples():
            i = row.i  # voxel x
            j = row.j  # voxel y
            k = row.k  # voxel z
            density = row.PadBVTotal  # voxel density

            corners = [i * res, j * res,
                       (i + 1) * res, j * res,
                       (i + 1) * res, (j + 1) * res,
                       i * res, (j + 1) * res]

            height = res
            baseheight = k * height  # voxel height

            voxlist.append(corners+[baseheight, res, density,
                            densitydef, optprop])

        data = pd.DataFrame(voxlist, columns=self.PLOTCOLNAMES)

        self.plots = self.plots.append(data, ignore_index=True)
        print ("Plots added from .vox file.")
        print ("Optical properties have to be added in the column 'optprop'\n")
        return


    def addtrees(self, data):
        """Add trees.txt file to the simulation


        The XML OPT PROP goes with a "FctPhaseIndex".
        TODO : other than 'exact location + exact parameters'
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
        data : pandas DataFrame
            see Notes for details on mandatory and optional columns.

        Notes
        -----
        `data` should have the following columns:
         SPECIES_ID, POS_X  POS_Y  T_HEI_BELOW  T_HEI_WITHIN  T_DIA_BELOW  C_TYPE  C_HEI  C_GEO_1  C_GEO_2

        """

        if self.nspecies == 0:
            print "Warning : No tree specie has been defined."
            print "The trees you will add have no optical link."

        if self.trees == 0:
            self.trees = data
        else:
            print "appending trees to the existing trees dataframe : "
            self.trees.append(data, ignore_index=True)

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

    def addtreespecies(self, species_id, lai=4.0, holes=0,
                      trunkopt='Lambertian_Phase_Function_1',
                      trunktherm='ThermalFunction290_310',
                      vegopt='custom',
                      vegtherm='ThermalFunction290_310'):
        """adds a tree specie to the simulation

        Parameters
        ----------
        idspecie : int
        netrees : int, optional
        properties of a specie :
            - number of trees
            - LAI > 0 or Ul <0
            - hole simulation
            - trunk opt prop
            - trunk therm prop
            - veg opt prop
            - veg therm prop
        TODO : Error catching when only trees or species are defined!
        """
        # specie = {'id': self.nspecies, 'ntrees': ntrees, 'lai': lai,
        #        'crowns': [[holes, trunkopt, trunktherm, vegopt, vegtherm]]}

        ntrees=0

        cols = ['species_id', 'ntrees', 'lai', 'holes',
                'trunkopt', 'trunktherm', 'vegopt', 'vegtherm']
        if self.nspecies == 0:
            self.species = pd.DataFrame(columns=cols)

        if species_id in self.species.species_id.values:
                print "Warning: you overwrote tree species: "+str(species_id)
                self.species = self.species[self.species.species_id != species_id]

        species_props = [species_id, ntrees, lai, holes,
                         trunkopt, trunktherm, vegopt, vegtherm]
        species = pd.DataFrame(data=[species_props], columns=cols)
        self.species = self.species.append(species, ignore_index=True)
        self.nspecies += 1
        self._registerchange('trees')
        print ("A tree specie has been added. Make sure the specified optical "
               "properties match those defined in self.optsprops\n")
        print ("Warning : Treespecies' ids must be consecutive, "
               "begining with 0 in order to effectively match those define in "
               "trees.txt.\n")

        print('--------------\n')

        return

    def setindexprops(self):
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

    def properties(self):
        """List general properties of the simulation

        TODO : Find a nice way to print the panda dataframe, and all variables
        add all relevant informations. And more or less verbose modes.
        (And maybe a txt output)
        """
        print "Simulation properties"
        print '__________________________________\n'
        self.listmodifications()
        print '\nscene dimensions : {}\n'.format(self.scene)
        print 'cell dimensions : {}\n'.format(self.cell)
        print 'table of  plots\n{} \n'.format(self.plots)
        print 'defined optical properties: \n'
        pprint.pprint(self.optprops)
        print '\nmeasured wavelengths :\n'
        print self.bands
        print '__________________________________\n'
        return

    def setoptplots(self, opt, mode=None):
        """sets the optical property of the plots

        Parameters
        ----------
        opt: str
            Name of optical property

        TODO : modify and add options : superior plots...
        For now sets ALL plots to the same 'opt' optical property
        Specific assignment can be done in self.plots['optprop'] directly.
        """
        if not self.plots:
            print "There are no plots in this simulation"
            return
        else:
            self.plots['optprop'] = opt
        return

    def set_scene_size(self, scene):
        """set scene size

        Parameters:
        ----------
        scene: list
            [x,y] size of scene
        TODO: error catching
        """
        self._registerchange('maket')
        self.scene = scene
        print 'Scene length set to:', scene[0]
        print 'Scene width set to:', scene[1]
        self.changetracker[1]['maket']['scene'] = self.scene
        return

    def set_cell_size(self, cell):
        """set cell size

        Parameters
        ----------
            cell: list
                [x,y] size of cell
        TODO : maybe a bit more verbose?
        """
        self._registerchange('maket')
        self.cell = cell
        return

    def listmodifications(self):
        """returns record of changed xml files relative to default simulation

        TODO : stuff to make all that look nicer.
        """
        print 'Impacted xml files:'
        print self.changetracker[0]

        return

    def pickfile(self, path):
        """Select an existing .xml dart file to use instead of generating one

        Parameters
        ----------
            path: str
                Complete path to an xml file to be copied to the new simulation
                in place of a pyt4dart generated file.

        Notes
        -----
            File copy is made after simulation updates and will overwrite any
            previous change. Use carefully as it can lead to erroneous simulation,
            example changing the order of optical properties in coeff_diff.xml
        """
        dartfile = os.path.splitext(os.path.basename(path))
        self.changetracker[1]['pickfile'][dartfile] = path
        return

    def getsfileparams(self, path):
        """gets the parameters of an existing xml file

        TODO: Lot of work. But important : read xmlfiles into python simulation
        """
        return

    def stack_bands(self, zenith=0, azimuth=0, dartdir=None):
        """Stack bands into an ENVI .bil file

        Parameters
        ----------
        zenith: float
            Zenith viewing angle
        azimuth: float
            Azimuth viewing angle
        dartdir: str
            see getdartdir.

        Returns
        -------
            str: output file path
        """

        simu_input_dir = get_simu_input_path(self.name, dartdir)
        simu_output_dir = get_simu_output_path(self.name, dartdir)

        bands = get_bands_files(simu_output_dir, band_sub_dir=pjoin('BRF', 'ITERX', 'IMAGES_DART'))

        band_files=bands.path[(bands.zenith==0) & (bands.azimuth==0)]

        wvl = get_wavelengths(simu_input_dir)

        outputfile = pjoin(simu_output_dir, os.path.basename(band_files.iloc[0]).replace('.mpr','.bil'))

        stack_dart_bands(band_files, outputfile, wavelengths=wvl.wavelength.values, fwhm=wvl.fwhm.values, verbose=True)

        return outputfile

    def write_xmls(self, simu_name=None, dartdir=None):
        """Writes the xml files with all defined input parameters

        Parameters
        ----------
        simu_name: str
            Simulation name. If None, self.name is taken.
        dartdir: str
            If None, default dartdir is taken. See getdartdir

        Returns
        -------
            str: simulation path


        WARNING : For now this function is the only proper way to write
        the DART xmls.
        """
        # self.checksimu()

        if not simu_name:
            simu_name = self.name

        if not simu_name:
            raise ValueError('Simulation name not defined.')

        simupath = getsimupath(simu_name, dartdir)

        if not os.path.isdir(simupath):
            os.mkdir(simupath)

        simuinputpath = get_simu_input_path(simu_name, dartdir)

        if not os.path.isdir(simuinputpath):
            os.mkdir(simuinputpath)

        print 'Writing XML files'
        self.bands.index += 1
        """
        WARNING : important to write coeff diff before indexing opt props :
            coeff diff needs all optprops info, whereas the other writers
            only need ident + index.
        WARNING : here the structure for changetracker[1]['trees'] is defined.
        TODO : Better Check and Error catch for trees.(and in general)
        And general simplification.
        """
        # Setting changetracker
        self.setindexprops()
        self.changetracker[1]['coeff_diff'] = self.optprops

        if 'phase' in self.changetracker[0]:
            self.changetracker[1]['phase']['bands'] = self.bands

        dxml.write_coeff_diff(self.changetracker, self.name, dartdir)

        self.changetracker[1]['indexopts'] = self.indexopts
        self.changetracker[1]['plots'] = self.plots
        # Effectively write xmls
        dxml.write_atmosphere(self.changetracker, self.name, dartdir)
        dxml.write_directions(self.changetracker, self.name, dartdir)
        dxml.write_inversion(self.changetracker, self.name, dartdir)
        dxml.write_maket(self.changetracker, self.name, dartdir)
        dxml.write_object_3d(self.changetracker, self.name, dartdir)
        dxml.write_phase(self.changetracker, self.name, dartdir)
        dxml.write_plots(self.changetracker, self.name, dartdir)
        dxml.write_sequence(self.changetracker, self.name, dartdir)

        # Special stuff for trees : writing trees.txt and pass the path
        # But bad condition...for now
        if self.nspecies > 0:
            self.changetracker[1]['trees'] = self.trees
            self.changetracker[1]['treespecies'] = self.species
        dxml.write_trees(self.changetracker, self.name, dartdir)

        dxml.write_urban(self.changetracker, self.name, dartdir)
        dxml.write_water(self.changetracker, self.name, dartdir)
        print "pyt4dart XML files written to {}".format(simuinputpath)

        self.writepickedfiles()
        return simupath

    def writepickedfiles(self):
        """Effectively writes selected files to be copied into simulation
        """
        try:
            for name in self.changetracker[1]['pickfile']:
                dxml.copyxml(name, self.changetracker)
                print '{} overwritten with {}'.format(
                        name, self.changetracker[1]['pickfile'][name])
        except KeyError:
            return
        return

    def write_sequence(self, sequence_path = None, dartdir = None):
        """Only writes the ongoing sequence xml.
        """
        if not sequence_path:
            sequence_path
        dxml.write_sequence(self.changetracker, self.name, dartdir)
        return

    def getsimupath(self, dartdir=None):
        """

        Parameters
        ----------
        dartdir

        Returns
        -------
            str: Simulation full path

        """
        return getsimupath(self.name, dartdir)

    def get_sequence_db_path(self, sequence_name, dartdir=None):
        """
        Path of sequence database
        Parameters
        ----------
        sequence_name
        dartdir

        Returns
        -------
            str: Path of sequence database

        """

        return pjoin(getsimupath(self.name, dartdir), self.name+'_'+sequence_name+'.db')

# ##################################test zone
if __name__ == '__main__':
    import time

    start = time.time()
    # Case Study 1 ################
    PathDART            = '/media/mtd/stock/DART_5-7-1_v1061/'
    SimulationName      = 'testprosequence10'
    SequenceName        = 'prospect_sequence.xml'

    pof = simulation(PathDART+'user_data/simulations/'+SimulationName+'/')
    pof.addsingleplot(opt='proprieteoptpros')
    proplot = ['vegetation','proprieteoptplot','Vegetation.db',
                  'needle_spruce_stressed', '0']
    # prosoptveg = ['vegetation', 'proprieteoptpros', 'prospect', 'blank', 0]
    pof.addopt(proplot)
    pof.add_bands([0.400, 0.01])
#    pof.add_bands([0.450, 0.01])
#    pof.add_bands([0.500, 0.01])

#
#    pof.add_bands([0.450, 0.01])
#    pof.add_bands([0.500, 0.01])
#    pof.add_bands([0.550, 0.01])
#    pof.add_bands([0.600, 0.01])
#    pof.add_bands([0.650, 0.01])
#    pof.add_bands([0.700, 0.01])
#    pof.add_bands([0.750, 0.01])
#    pof.add_bands([0.800, 0.01])
    # pof.addopt(prosoptveg)
    dic = {'CBrown': [0.8, 0.2, 0.0], 'Cab': [5, 27, 71.5], 'Car': 10,
           'Cm': 0.01, 'Cw': 0.01, 'N': 2, 'anthocyanin': 1}

    pof.addprospectsequence(dic, 'proprieteoptpros', name='prospect_sequence')
    pof.addsequence({'wvl':[0.400,0.050,8]},
                    group = 'wvl', name = 'prospect_sequence')
    corner = [[1, 1],
              [1, 2],
              [2, 2],
              [2, 1]]
    pof.addsingleplot(corners=corner,opt='proprieteoptpros' )
    # pof.addsequence({'wvl':[400,20,8]})

    pof.write_xmls()

    # define path for tools
    PathTOOLS = PathDART + 'tools/linux/'
    # define name for script to be run
    namescript = 'dart-sequence.sh'

    # define option
    OptionStart = '-start'
    CmdJoin = PathTOOLS + namescript + ' ' + SimulationName+'/'+SequenceName \
     + ' ' + OptionStart
    subprocess.Popen(['/bin/bash', '-c', CmdJoin],
                     stdout=subprocess.PIPE).wait()

    ###################################
    # case study 2
    # Trees simulated with prospect, over a plot of dry grass
    # S2 bands
    """
    PathDART            = '/media/mtd/stock/DART_5-7-1_v1061/'
    SimulationName      = 'testrees2'
    SequenceName        = 'testrees.xml'

    pof = simulation(PathDART+'user_data/simulations/'+SimulationName+'/')
    pof.set_scene_size([40, 40])
    pof.addtreespecie(1)
    pof.addtreespecie(1, vegopt = 'proprieteopt2',
                      trunkopt = 'Lambertian_Phase_Function_1')
    pof.addtreespecie(0, vegopt = 'proprieteplot',
                      trunkopt = 'Lambertian_Phase_Function_1')
    pof.add_bands("/media/mtd/stock/boulot_sur_dart/temp/hdr/crop2.hdr")
    optprop = ['lambertian', 'proprieteopt', 'Lambertian_vegetation.db',
               'lichen', '0']
    pof.addopt(optprop)
    corners = [[1, 1],
               [1, 5],
               [5, 7],
               [7, 1],
               ]
    # pof.addsingleplot(corners = corners, opt = 'proprieteplot')
    optpropplot = ['vegetation', 'proprieteplot',
                  'Vegetation.db',
                  'grass_dry', '0']
    pof.addopt(optpropplot)
    optpropveg = ['vegetation', 'proprieteopt2',
                  'Vegetation.db',
                  'ash_top', '0']
    pof.addopt(optpropveg)
    path = '/media/mtd/stock/boulot_sur_dart/temp/model_trees.txt'
    pof.addtrees(path)
    pof.trees['SPECIES_ID'] = 2
    pof.addtreespecie(2, vegopt = 'prosopt')
    dic = {'CBrown': 0.0, 'Cab': [7, 20.5, 40.3, 82.5], 'Car': 10,
           'Cm': 0.01, 'Cw': 0.01, 'N': 2, 'anthocyanin': 1}
    pof.addprospectsequence(dic, 'prosopt')
    pof.write_xmls()

    # define path for tools
    PathTOOLS = PathDART + 'tools/linux/'
    # define name for script to be run
    namescript = 'dart-sequence.sh'

    # define option
    OptionStart = '-start'
    CmdJoin = PathTOOLS + namescript + ' ' + SimulationName+'/'+SequenceName \
    + ' ' + OptionStart
    subprocess.Popen(['/bin/bash', '-c', CmdJoin],
                     stdout=subprocess.PIPE).wait()

    """
    # #####################################
    # case study 3

    # # #####################################
    """
    pof = simulation('/media/mtd/stock/boulot_sur_dart/temp/test_debug')
    optpropveg = ['vegetation', 'proprieteopt',
                  '/media/mtd/stock/DART/database/Vegetation.db',
                  'leaf_deciduous', '0']
    pof.addopt(optpropveg)
    print pof.changetracker[0]
    optpropveg = ['vegetation', 'proprieteopt2',
                  '/media/mtd/stock/DART/database/Vegetation.db',
                  'elm_top', '0']
    pof.addopt(optpropveg)
    print pof.changetracker[0]

    pof.addsingleplot(opt='proprieteopt', densitydef='UL')
    print pof.changetracker[0]

    pof.addsequence({'wvl': (0.400, 0.50, 10)})
    print pof.changetracker[0]

    #pof.add_bands([])

    pof.write_xmls()

    """
    """
    pof.set_scene_size([5, 5])
    corners = [[3,  4],
               [3,  0],
               [0,  0],
               [0,  4]]
    pof.addsingleplot(corners=corners, opt='proprieteopt2')

    dic = {'CBrown': [3, 4, 5], 'Cab': 5, 'Car': 1,
           'Cm': 1, 'Cw': 4, 'N': 2, 'anthocyanin': 1}
    # dummy optprop
    pof.addsingleplot(corners=corners, opt='proprieteopt2', densitydef='UL')

    optpropveg = ['vegetation', 'proprieteopt2',
                  '/media/mtd/stock/DART/database/Vegetation.db',
                  'ash_top', '0']
    pof.addopt(optpropveg)
    optpropveg = ['vegetation', 'proprieteopt2',
              '/media/mtd/stock/DART/database/Vegetation.db',
              'beech_middle', '0']
    pof.addopt(optpropveg)
    optpropveg = ['vegetation', 'proprieteopt2',
                  '/media/mtd/stock/DART/database/Vegetation.db',
                  'beech_bottom', '0']
    pof.addopt(optpropveg)
    optpropveg = ['vegetation', 'proprieteopt2',
                  '/media/mtd/stock/DART/database/Vegetation.db',
                  'beech_top', '0']
    pof.addopt(optpropveg)

    pof.addsequence({'wvl': (400,50,3)})
    # pof.addprospectsequence(dic, 'proprieteoptpros')
    # dxml.write_coeff_diff(pof.changetracker)
    pof.write_xmls()
    """
    """
    """
    # prosoptveg = ['vegetation', 'proprieteoptpros', 'prospect', 'blank', 0]
    # pof.addopt(prosoptveg)
    """
    """
    """
    pof = simulation('/media/mtd/stock/boulot_sur_dart/temp/'
                     'essai_sequence/input/')


    corners = [[3,  4],
               [3,  0],
               [0,  0],
               [0,  4]]
    pof.addsingleplot(corners=corners, opt='proprieteopt2', densitydef='UL')
    pof.set_scene_size([5, 5])
    optpropveg = ['vegetation', 'proprieteopt2',
                  '/media/mtd/stock/DART/database/Vegetation.db',
                  'ash_top', '0']
    pof.addopt(optpropveg)
    dic = {'CBrown':[3,4,5], 'Cab': 5, 'Car':1,
           'Cm':1, 'Cw':4, 'N':2, 'anthocyanin':1}
    prosoptveg = ['vegetation','proprieteoptpros', 'prospect', 'blank',0]
    pof.addopt(prosoptveg)
    pof.addprospectsequence(dic, 'proprieteoptpros')
    pof.write_sequence()
    """
    """
    # progress bar
    import time
import sys

toolbar_width = 40

# setup toolbar
sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

for i in xrange(toolbar_width):
    time.sleep(0.1) # do real work here
    # update the bar
    sys.stdout.write("-")
    sys.stdout.flush()

sys.stdout.write("\n")
    """
    """
    corners = ((3,  4),
               (3,  0),
               (0,  0),
               (0,  4))
    pof.addsingleplot(corners=corners, opt='proprieteopt2')
    pof.addsingleplot(corners=corners, opt='proprieteopt3')
    pof.addsingleplot(corners=corners, opt='proprieteopt1')

    #   pof.add_bands([1, 2, 3])
    #   pof.add_bands([2, 2, 3])
    pof.add_bands([12, 2, 3])
    pof.add_bands("/media/mtd/stock/boulot_sur_dart/temp/hdr/crop2.hdr")
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

    end = time.time()
    print(end - start)
    """
    end = time.time()
    print end - start