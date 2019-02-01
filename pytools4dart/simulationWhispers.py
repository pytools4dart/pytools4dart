# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Eric Chraibi <eric.chraibi@irstea.fr>, Florian de Boissieu <fdeboiss@gmail.com>
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
import shutil
import warnings

# local imports
import xmlwriters as dxml
from tools.voxreader import voxel
from tools.hstools import read_ENVI_hdr, get_hdr_bands, get_bands_files, get_wavelengths, stack_dart_bands
from settings import getsimupath, get_simu_input_path, get_simu_output_path
import pytools4dart.run as run
import tools.dbtools as dbtools

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
        """
        # TODO : WARNING : For now, 'flux' ( changetracker[3]) is hardcoded in

        self.changetracker = [[], {}, "flux"]

        self.name = name # name of the simulation
        self.scene = [10, 10] # scene size in meters
        self.cell = [1, 1] # cell size in meters


        # Variables to be used in subsequent methods
        self.BANDSCOLNAMES = ['wvl', 'fwhm']

        self.optprops = {'lambertians': [],
                         'vegetations': []}

        self.add_optical_property({'type': 'lambertian',
                               'op_name': 'Lambertian_Phase_Function_1',
                               'db_name': 'Lambertian_vegetation.db',
                               'op_name_in_db': 'reflect_equal_1_trans_equal_0_0',
                               'specular': 0})

        self.nbands = 0
        self.bands = pd.DataFrame(columns=self.BANDSCOLNAMES)

        # Plots variables
        self.PLOTCOLNAMES = ['x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 'y4',
                             'zmin', 'dz', 'density',
                             'densitydef', 'op_name']
        self.plots = pd.DataFrame(columns=self.PLOTCOLNAMES) # plots description

        self.nspecies = 0
        self.trees = 0

        self.prosparams = ['CBrown', 'Cab', 'Car', 'Cm',
                           'Cw', 'N', 'anthocyanin']
        self.prossequence = 0

        self.run = run.runners(self)

        print ('New Simulation initiated')
        print('--------------\n')

    def __repr__(self):
        description ='\n'.join(
            ["\nSimulation '{}'".format(self.name),
             '__________________________________\n',
             'scene size : {}'.format(self.scene),
             'cell size : {}'.format(self.cell),
             'number of plots : {}'.format(len(self.plots)),
             'number of optical properties : {}'.format(len(self.optprops)),
             'number of bands : {}'.format(len(self.bands)),
             '__________________________________\n'])

        return description

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
        """add spectral band to simulated sensor

        Add a band either from DataFrame, dictionary, HDR file or txt file.
        Values are considered in µm.

        Parameters
        ----------
        x: DataFrame, dict or str
            - if DataFrame it is expected to have columns 'wvl' and 'fwhm'
            - if dict it is expected to have elements: 'wvl' and 'fwhm'
            - if str it should be the path to an ENVI hdr
            or a csv file with 2 columns

        """
        # TODO : check if .txt info works. Split into 3 smaller helper functions

        if isinstance(x, pd.DataFrame):
            # check columns:
            if not set(self.BANDSCOLNAMES).issubset(x.columns):
                print("'wvl' or 'fwhm' is missing.")
            self.bands = self.bands.append(x.loc[:, self.BANDSCOLNAMES], ignore_index=True)
            self._registerchange('phase')

        elif isinstance(x, dict):
            try:
                df=pd.DataFrame(x)
            except TypeError:
                try: # case of scalars
                    df=pd.DataFrame(x, index=[0])
                except TypeError:
                    raise ValueError('Could not transform to DataFrame.')
            self.add_bands(df, verbose)

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

    def add_optical_property(self, optprop,verbose=False):
        """adds and optical property to the simulation

        Parameters
        ----------
        optprop : dict
            with the following elements:
                    - type : 'lambertian' or 'vegetation'
                    - op_name: string for name
                    - db_name: string to database
                    - op_name_in_db: name of opt in database

                if lambertian :
                    - specular : 0 or 1, 1 if UseSpecular
                if vegetation :
                    - lad : leaf angle distribution :
                        - 0: Uniform
                        - 1: Spherical
                        - 3: Planophil

            prospect properties can be added with key 'prospect'.
            It must be a dictionary with elements


        Examples
        --------
        .. code-block:: python

            import pytools4dart as ptd
            simu=ptd.simulation('lambertian')

            simu.add_optical_property({
                'type':'lambertian',
                'op_name':'Lambertian_Phase_Function_1',
                'db_name':'Lambertian_vegetation.db',
                'op_name_in_db':'reflect_equal_1_trans_equal_0_0',
                'specular': 0})

            simu.add_optical_property({
                'type':'vegetation',
                'op_name':'Turbid_Leaf_Deciduous_Phase_Function',
                'db_name':'Vegetation.db',
                'op_name_in_db':'leaf_deciduous',
                'lad': 1})

            simu.add_optical_property({
                'type':'vegetation',
                'op_name':'op_prospect',
                'db_name':'prospect.db',
                'op_name_in_db':'',
                'lad': 1,
                'prospect':{'CBrown': '0.0', 'Cab': '30', 'Car': '12',
                           'Cm': '0.01', 'Cw': '0.012', 'N': '1.8',
                           'anthocyanin': '0'}})


        """
        # TODO : think about : do we want optprops as an object?
        # TODO : Managing Thermal properties?
        # TODO : Add Error catching!

        #check if requested model and db exist, although it could be created a posteriori with prospect
        try:
            dbmodels_names = dbtools.get_models(optprop['db_name'])['name'].values.tolist()
            optprop_name_in_db = optprop['op_name_in_db']
            if not (optprop_name_in_db in dbmodels_names):
                warnings.warn("model '{0}' not found in {1}".format(optprop['op_name_in_db'],
                                                                    optprop['db_name']))
        except Exception as e:
            warnings.warn(str(e))



        self._registerchange('coeff_diff')
        if optprop['type'] == 'lambertian':
            if optprop['op_name'] in self.optprops['lambertians']:
                raise ValueError('Optical property name already used: ' + optprop['op_name'])
            else:
                self.optprops['lambertians'].append({k:v for k,v in optprop.iteritems() if k != 'type'})
                self._set_index_props()
        elif optprop['type'] == 'vegetation':
            if optprop['op_name'] in self.optprops['vegetations']:
                raise ValueError('Optical property name already used: ' + optprop['op_name'])
            else:
                self.optprops['vegetations'].append({k:v for k,v in optprop.iteritems() if k != 'type'})
                self._set_index_props()
        else:
            print 'Non recognized optical property type. Returning'
            return

        if verbose:
            print('Optical property added.')

        return

    def add_sequence(self, param, group='group1', name='sequence',
                    verbose=False):
        """add a sequence xml file with given parameters

        Parameters
        ---------
        param : dict
            must be a dictionary structured in this way :
            parargs = { 'parameter1' : [value_0, value_1, ...]}
        group : str, optional
            string assigning a name to the group of the sequence. This allows
            for the combination of variation of parameters in a single sequence
        name : str, optional
            name of the sequence (given to the xml file).

        Notes
        -----
        parameters can be found as 'dartnode' in:
        ```
        import pytools4dart as ptd
        ptd.core_ui.utils.get_labels()
        ```

        As parameters are not very user-friendly, some parameters have acronym:
            wvl: central wavelength

        Example
        -------
        .. code-block:: python

            import pytools4dart as ptd
            simu = ptd.simulation('CHL')
            simu.add_band({'wvl':0.4, 'fwhm':0.07})
            simu.add_sequence(id=0, {'wvl':[0.4, 0.5, 0.6]},
                group='wavelength', name='chl_sequence')

        """
        if not isinstance(param, dict):
            raise ValueError('argument must be a dictionary = {parameters:args}')

        self._registerchange('sequence')

        for k, v in param.iteritems():
            if verbose:
                print 'key =', k
                print 'values =', v
            if group not in self.changetracker[1]['sequence']:
                self.changetracker[1]['sequence'][group] = {}
            else:
                # check length
                group_len =[len(gv) for gv in self.changetracker[1]['sequence'][group]][0]
                if len(v) != group_len:
                    raise ValueError('Members of group {} must be of length {}'.format(group, group_len))


            self.changetracker[1]['sequence'][group][k] = v

        try:
            self.changetracker[1]['sequencename']
        except KeyError:
            self.changetracker[1]['sequencename'] = name
        else:
            print 'The xml sequence file was already named {}' \
                .format(self.changetracker[1]['sequencename'])
            return
        return

    def add_prospect_sequence(self, param, op_name, group='group1',
                            name='prospect_sequence'):
        """adds a sequence of prospect generated optical properties

        Parameters
        ---------
        param : dict
            must be a dictionary containing the prospect parameters
            and the assigned value. For now only one parameter can vary.
        op_name : str
            name of the prospect optical property. For now created independently
            via add_optical_property()

        """
        # TODO : Absolutey NOT Optimized nor clean!

        # Here go the conditions for prospect, probably to write in another
        # function
        self._registerchange('prospect')
        self._registerchange('sequence')

        # definition of the 'blank' prospect optical property
        # prosoptveg = ['vegetation', op_name, 'prospect', 'blank', lad]
        # self.add_optical_property(prosoptveg)

        self._set_index_props()
        try:
            index = self.indexopts['vegetations'][op_name]
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
            for params in param.iteritems():
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

            self.add_sequence(prosdic, group=group,
                             name=name)
            self.prossequence += 1
        return

    def add_single_plot(self, corners=None, baseheight=1, density=1,
                      op_name="custom", height=1, densitydef='ul'):
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
            op_name : str, optional
                name of the optical property assigned to the plot. This optical property must exist
                in the opt properties list before running dart modules,
                even if it is not mandatory it to be created before the assignation time.
            densitydef: str, optional
                 defines the interpretation of the density value :
                     ul = m²/ m³
                     lai = m²/m²
        """
        # TODO : think about simpler corner definition
        # TODO : add modifiable height

        self._registerchange('plots')

        if not corners:
            corners = [[self.scene[0],  self.scene[1]],
                       [self.scene[0],  0],
                       [0,              0],
                       [0,              self.scene[1]]]
        data = np.array(corners).flatten().tolist()+[baseheight, height, density, densitydef, op_name]
        miniframe = pd.DataFrame([data], columns=self.PLOTCOLNAMES)
        self.plots = self.plots.append(miniframe, ignore_index=True)

        return

    def add_plots(self, data, colnames={'x1':'x1', 'y1':'y1', 'x2':'x2', 'y2':'y2',
                                            'x3':'x3', 'y3':'y3', 'x4':'x4', 'y4':'y4',
                                            'baseheight':'baseheight', 'height':'height',
                                            'density':'density', 'densitydef':'densitydef',
                                            'op_name':'op_name'}):
        """
        Appends a dataframe to plots based on a dictionary

        Parameters
        ----------
        data : DataFrame
            Plots properties.
        colnames : dict
            Column names corresponding to the standard names (see self.COLNAMES)
        """

        """Appends a dataframe to plots based on a dictionary

        dic = {Olndame:Newname, .....}
        new names in self.PLOTSCOLNAMES
        TODO : Error catching and protection of self.plots in case of
        modifications

        """
        self._registerchange('plots')
        data.rename(columns=colnames, inplace=True)
        plots = self.plots.append(data, ignore_index=True)
        self.plots = plots

        print ("Dataframe successfully appended to plots")

        return

    def add_plots_from_vox(self, vox, densitydef='ul', op_name=None, verbose=False):
        """Add plots based on AMAPVox file.

        Parameters
        ---------
            vox: object of class voxel
                lidar voxelized data, see pytools4dart.tools.voxreader
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
                            densitydef, op_name])

        data = pd.DataFrame(voxlist, columns=self.PLOTCOLNAMES)

        self.plots = self.plots.append(data, ignore_index=True)
        if verbose:
            print ("{} plots added with first optical property.".format(len(data)))

        return


    def add_trees(self, data):
        """Add tree data to the simulation


        data must contain :
            -specie ID
            -C_TYPE (type of crown geometry)
                -0 = ellipsoid, 1=ellipsoid composed, 2=cone,
                 3=trapezoid, 5=cone composed
            -X
            -Y
            -Height below crown
            -Height within crown
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
        # TODO : other than 'exact location + exact parameters'
        # TODO : Empy leaf cells/ leaves+ holes management!
        #                 -- > 'distribution' parameter

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

    def add_tree_species(self, species_id, lai=4.0, holes=0,
                      trunkopt='Lambertian_Phase_Function_1',
                      trunktherm='ThermalFunction290_310',
                      vegopt='',
                      vegtherm='ThermalFunction290_310'):
        """

        Parameters
        ----------
        species_id: int
            Numerical identifier of species.
        lai: float
            considered as leaf area index (LAI) if lai > 0
            leaf area density (Ul) if lai <0
        holes: float
            propertion of holes in crown
        trunkopt: str
            optical property name for trunk
        trunktherm: str
            thermal property name for trunk
        vegopt: str
            optical property name for turbid crown
        vegtherm: str
            thermal property name for turbid crown

        Returns
        -------

        """
        # TODO : Error catching when only trees or species are defined!
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

    def _set_index_props(self):
        """Creates the index for optical properties

        This function is necessary in order to have easy tracking of
        optical properties indices "IndexFctPhase" which is referenced a lot
        in Dart XMLs.
        """
        # TODO : Index Thermal properties!

        index = 0
        self.index_lamb = {}
        for lamb in self.optprops['lambertians']:
            self.index_lamb[lamb['op_name']] = index
            index += 1
        index = 0
        self.index_veg = {}
        for veg in self.optprops['vegetations']:
            self.index_veg[veg['op_name']] = index
            index += 1
        self.indexopts = {'lambertians': self.index_lamb,
                          'vegetations': self.index_veg}

        return

    def set_scene_size(self, scene_dims):
        """set scene size

        Parameters:
        ----------
        scene: 2D vector
            [x,y] size of scene
        """
        # TODO: error catching

        self._registerchange('maket')
        self.scene = scene_dims
        print 'Scene length set to:', scene_dims[0]
        print 'Scene width set to:', scene_dims[1]
        self.changetracker[1]['maket']['scene'] = self.scene
        return

    def set_cell_size(self, cell):
        """set cell size

        Parameters
        ----------
            cell: list
                [x,y] size of cell
        """
        # TODO : maybe a bit more verbose?

        self._registerchange('maket')
        self.cell = cell
        return

    def listmodifications(self):
        """returns record of changed xml files relative to default simulation
        """
        # TODO : stuff to make all that look nicer.

        return '\n'.join(['Impacted xml files:',
                  str(self.changetracker[0])])

    def pickfile(self, path):
        """Select an existing dart xml file to use instead of generating one

        Parameters
        ----------
            path: str
                Complete path to an xml file to be copied to the new simulation
                in place of a pyt4dart generated file.

        Notes
        -----
            File copy is made after simulation updates and will overwrite any
            previous change.

            Dart has some dependencies between input xml files,
            e.g. between number of bands (defined in phase.xml)
            and optical properties factors (defined in coeff_diff.xml).
            Therefore, it should be used very carefully as it can lead to erroneous simulation.
        """
        dartfile = os.path.splitext(os.path.basename(path))
        self.changetracker[1]['pickfile'][dartfile] = path
        return

    def stack_bands(self, zenith=0, azimuth=0):
        """Stack bands into an ENVI .bil file

        Parameters
        ----------
        zenith: float
            Zenith viewing angle
        azimuth: float
            Azimuth viewing angle

        Returns
        -------
            str: output file path
        """

        simu_input_dir = get_simu_input_path(self.name)
        simu_output_dir = get_simu_output_path(self.name)

        bands = get_bands_files(simu_output_dir, band_sub_dir=pjoin('BRF', 'ITERX', 'IMAGES_DART'))

        band_files=bands.path[(bands.zenith==0) & (bands.azimuth==0)]

        wvl = get_wavelengths(simu_input_dir)

        outputfile = pjoin(simu_output_dir, os.path.basename(band_files.iloc[0]).replace('.mpr','.bil'))

        stack_dart_bands(band_files, outputfile, wavelengths=wvl.wavelength.values, fwhm=wvl.fwhm.values, verbose=True)

        return outputfile

    def write(self, simu_name=None, overwrite=False):
        """Writes the xml files with all defined input parameters

        Parameters
        ----------
        simu_name: str
            Simulation name. If None, self.name is taken.

        Returns
        -------
            str: simulation path
        """
        # self.checksimu()

        if not simu_name:
            simu_name = self.name

        if not simu_name:
            raise ValueError('Simulation name not defined.')

        simupath = getsimupath(simu_name)

        if os.path.isdir(simupath):
            if overwrite:
                shutil.rmtree(simupath)
            else:
                raise ValueError('Simulation directory already exists:\n{}'.format(simupath)+
                             '\n\nChange name or set overwrite argument.')

        os.mkdir(simupath)

        simuinputpath = get_simu_input_path(simu_name)

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
        self._set_index_props()
        self.changetracker[1]['coeff_diff'] = self.optprops

        if 'phase' in self.changetracker[0]:
            self.changetracker[1]['phase']['bands'] = self.bands

        dxml.write_coeff_diff(self.changetracker, self.name)

        self.changetracker[1]['indexopts'] = self.indexopts
        self.changetracker[1]['plots'] = self.plots
        # Effectively write xmls
        dxml.write_atmosphere(self.changetracker, self.name)
        dxml.write_directions(self.changetracker, self.name)
        dxml.write_inversion(self.changetracker, self.name)
        dxml.write_maket(self.changetracker, self.name)
        dxml.write_object_3d(self.changetracker, self.name)
        dxml.write_phase(self.changetracker, self.name)
        dxml.write_plots(self.changetracker, self.name)
        dxml.write_sequence(self.changetracker, self.name)

        # Special stuff for trees : writing trees.txt and pass the path
        # But bad condition...for now
        if self.nspecies > 0:
            self.changetracker[1]['trees'] = self.trees
            self.changetracker[1]['treespecies'] = self.species
        dxml.write_trees(self.changetracker, self.name)

        dxml.write_urban(self.changetracker, self.name)
        dxml.write_water(self.changetracker, self.name)
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

    def write_sequence(self, sequence_path = None):
        """Only writes the ongoing sequence xml.
        """
        if not sequence_path:
            sequence_path
        dxml.write_sequence(self.changetracker, self.name)
        return

    def getsimupath(self):
        """
        Get simulation directory path

        Returns
        -------
            str: Simulation full path

        """
        return getsimupath(self.name)



    def get_sequence_db_path(self, sequence_name):
        """
        Path of sequence database
        Parameters
        ----------
        sequence_name

        Returns
        -------
            str: Path of sequence database

        """

        return pjoin(getsimupath(self.name), self.name+'_'+sequence_name+'.db')

