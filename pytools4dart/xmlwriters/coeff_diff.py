# !/usr/bin/env python2
#  -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Eric Chraibi <eric.chraibi@irstea.fr>, Florian de Boissieu <florian.deboissieu@irstea.fr>
# https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
#
# Copyright 2018 TETIS
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
Objects and functions necessary to write the coeff_diff xml file.
It is important to note the resulting xml file is written over a single line.
TODO :
    Add a vegetation optical property

"""
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree
from dartxml import DartXml


def write_coeff_diff(changetracker, simu_name, dartdir=None):
    """write coeff_diff xml fil

    proceed in the following manner :
        -instantiate appropriate dartcoeff object
        -set default nodes
        -mutate depending on changetracker
        -output file to xml

    """
    coeff = DartCoefXML(changetracker)
    coeff.basenodes()
    coeff.adoptchanges()

    coeff.writexml(simu_name, 'coeff_diff.xml', dartdir)
    return


class DartCoefXML(DartXml):
    """object for the editing and exporting to xml of phase related parameters

    It should not be used as such, but rather through its subclasses
    (flux and lidar).
    After instantiation, a default tree of nodes is created.
    Changes based on the passed "changetracker" variable have then
    to take place in order to upgrade the tree.
    All the tag names of tree nodes are supposed to be IDENTICAL to the ones
    produces by DART. The variable names are sometimes shortened.

    """

    def __init__(self, changetracker):
        self.root = etree.Element("Coeff_diff", {'fluorescenceFile': '0',
                                  'fluorescenceProducts': '0'})
        self.tree = etree.ElementTree(self.root)
        self.changes = changetracker[1]['coeff_diff']
        if 'phase' in changetracker[0]:
            self.nbands = changetracker[1]['phase']['bands'].shape[0]
        else:
            self.nbands = 1
        return

    def adoptchanges(self):
        """method to update xml tree based on user-defined parameters

        here goes the magic where we change some nodes based on parameters

        Complete path to node to be modified will have to be explicitly written
        in this way : './Phase/DartInputParameters/SpectralDomainTir'
        for the query to work.
        TODO : Unsure if error checking works this way....
        """
        try:
            for lamb in self.changes['lambertians']:
                self.addlamb(lamb)
        except KeyError:
            pass

        try:
            for veg in self.changes['vegetations']:
                self.addvegetation(veg)
        except KeyError:
            pass

        return

    def basenodes(self, default_lamb=False):
        """creates all nodes and properties common to default simulations

        a default lambertian optical property is created unless otherwise
        specified
        """

        # base nodes
        # # simple
        lambmultif = etree.SubElement(self.root, "LambertianMultiFunctions")

        etree.SubElement(self.root, 'HapkeSpecularMultiFunctions')
        etree.SubElement(self.root, 'RPVMultiFunctions')
        understory_atr = {'integrationStepOnTheta': '1',
                          'integrationStepOnPhi': '10',
                          'outputLADFile': '0'}
        etree.SubElement(self.root, 'UnderstoryMultiFunctions', understory_atr)

        etree.SubElement(self.root, 'AirMultiFunctions')


        # parent nodes
        # # lambertian branch  : default lambertian created in Dart simulations

        if default_lamb:
            # # # lambertian default object
            lambmulti_atr = {'ident': 'Lambertian_Phase_Function_1',
                             'useSpecular': '0',
                             'roStDev': '0.000',
                             'ModelName': 'reflect_equal_1_trans_equal_0_0',
                             'databaseName': 'Lambertian_vegetation.db',
                             'useMultiplicativeFactorForLUT': '0'}
            lambmulti = etree.SubElement(lambmultif, "LambertianMulti",
                                         lambmulti_atr)
            prosp_atr = {'useProspectExternalModule': '0',
                         'isFluorescent': '0'}
            etree.SubElement(lambmulti, 'ProspectExternalModule', prosp_atr)

        # # temperatures branch
        temp = etree.SubElement(self.root, 'Temperatures')
        thermal_atr = {'meanT': '300.0',
                       'idTemperature': 'ThermalFunction290_310',
                       'deltaT': '20.0', 'singleTemperatureSurface': '1',
                       'override3DMatrix': '0', 'useOpticalFactorMatrix': '0'}
        etree.SubElement(temp, 'ThermalFunction', thermal_atr)
        return

    def addlamb(self, optprop):
        """add a lambertian optical property
        """

        ident = optprop[0]
        database = optprop[1]
        modelname = optprop[2]
        specular = optprop[3]
        # 'reflect_equal_1_trans_equal_0_0', specular='0'
        rootlamb = self.root.find("./LambertianMultiFunctions")
        lamb_atr = {'ident': ident,
                    'useSpecular': str(specular),
                    'roStDev': '0.000',
                    'ModelName': modelname,
                    'databaseName': database,
                    'useMultiplicativeFactorForLUT': '0'}
        lambmulti = etree.SubElement(rootlamb, "LambertianMulti", lamb_atr)

        # Other parameters. Supposed to be necessary for Dart Functionning
        prosp_atr = {'useProspectExternalModule': '0',
                     'isFluorescent': '0'}
        etree.SubElement(lambmulti, 'ProspectExternalModule', prosp_atr)

        ## Only usefull when useMultiplicativeFactorForLUT can be '1'
        # lambnode_atr = {'diffuseTransmittanceFactor': '1',
        #                 'directTransmittanceFactor': '1',
        #                 'useSameOpticalFactorMatrixForAllBands': '0',
        #                 'reflectanceFactor': '1',
        #                 'useSameFactorForAllBands': '0',
        #                 'specularIntensityFactor': '1'}
        #
        # lamb_nodelut = etree.SubElement(
        #         lambmulti, 'lambertianNodeMultiplicativeFactorForLUT',
        #         lambnode_atr)
        # lamb_lutatr = {'diffuseTransmittanceFactor': '1',
        #                'specularIntensityFactor': '1',
        #                'reflectanceFactor': '1',
        #                'directTransmittanceFactor': '1',
        #                'useOpticalFactorMatrix': '0'}
        # for i in range(self.nbands):
        #     etree.SubElement(lamb_nodelut,
        #                      'lambertianMultiplicativeFactorForLUT',
        #                      lamb_lutatr)

        return

    def addvegetation(self, optprop):
        """ Adds a vegetation Node

        This module will require some work as it probably will be our most used
        one. How to parameter Prospect? Access Database? etc...
        TODO : add custom prospect optprop
        WARNING : Remember first element of optprop (lamb/veg) was sliced off.
        lad = Leaf Angle distribution
        Uniform : 0
        Spherical : 1
        Planophil : 3

        ident=None, database='Vegetation.db',
        modelname='leaf_deciduous', lad=1
        """
        if 'prospect' in optprop:
            if 'blank' in optprop:
                ident = optprop[0]
                lad = optprop[3]

                print ('blank prospect generated optical property')
                rootveg = self.root.find("./UnderstoryMultiFunctions")
                veg_atr = {'ident': ident, 'dimFoliar': '0.01',
                           'lad': str(lad),
                           'useSpecular': '0', 'ModelName': '',
                           'databaseName': 'ProspectVegetation.db',
                           'useMultiplicativeFactorForLUT': '0',
                           'useOpticalFactorMatrix': '0'}
                veg = etree.SubElement(rootveg, 'UnderstoryMulti', veg_atr)

                clump_atr = {'omegaMax': '0', 'clumpinga': '0',
                             'clumpingb': '0', 'omegaMin': '1'}
                etree.SubElement(veg, 'DirectionalClumpingIndexProperties',
                                 clump_atr)
                pros = {'isFluorescent': "0",
                        'useProspectExternalModule': '1'}
                prospect = etree.SubElement(veg, 'ProspectExternalModule',
                                            pros)
                subpros_atr = {'CBrown': '0.0', 'Cab': '30', 'Car': '10.',
                               'Cm': '0.01', 'Cw': '0.012', 'N': '1.8',
                               'anthocyanin': '0',
                               'inputProspectFile': 'Prospect_Fluspect/'
                                   'Optipar2017_ProspectD.txt'}
                etree.SubElement(prospect, 'ProspectExternParameters',
                                 subpros_atr)
            else:
                print 'Custom prospect optical property not yet implemented'
        else:

            ident = optprop[0]
            database = optprop[1]
            modelname = optprop[2]
            lad = optprop[3]

            rootveg = self.root.find("./UnderstoryMultiFunctions")
            veg_atr = {'ident': ident, 'dimFoliar': '0.01', 'lad': str(lad),
                       'useSpecular': '0', 'ModelName': modelname,
                       'databaseName': database,
                       'useMultiplicativeFactorForLUT': '0',
                       'useOpticalFactorMatrix': '0'}

            veg = etree.SubElement(rootveg, 'UnderstoryMulti', veg_atr)

            clump_atr = {'omegaMax': '0', 'clumpinga': '0',
                         'clumpingb': '0', 'omegaMin': '1'}
            etree.SubElement(veg, 'DirectionalClumpingIndexProperties',
                             clump_atr)

            prospect_atr = {'useProspectExternalModule': '0',
                            'isFluorescent': '0'}

            etree.SubElement(veg, 'ProspectExternalModule', prospect_atr)

            ## When useMultiplicativeFactorForLUT=1 will be available
            # multilutnode_atr = {'LeafTransmittanceFactor': '1',
            #                     'abaxialReflectanceFactor': '1',
            #                     'adaxialReflectanceFactor': '1',
            #                     'useSameFactorForAllBands': '1',
            #                     'useSameOpticalFactorMatrixForAllBands': '0',
            #                     }
            # mlut = etree.SubElement(veg,
            #                         'understoryNodeMultiplicativeFactorForLUT',
            #                         multilutnode_atr)
            # multilut_atr = {'useOpticalFactorMatrix': '0',
            #                 'adaxialReflectanceFactor': '1.0',
            #                 'abaxialReflectanceFactor': '1.0',
            #                 'LeafTransmittanceFactor': '1.0'}
            # for i in range(self.nbands+1):
            # etree.SubElement(mlut,
            #                 'understoryMultiplicativeFactorForLUT',
            #                 multilut_atr)
        return

    # def writexml(self, outpath):
    #     """ Writes the built tree to the specified path
    #
    #     Also includes the version and build of DART as the root element.
    #     This part could(should?) be modified.
    #     """
    #     root = etree.Element('DartFile',
    #                          {'version': '5.7.1', 'build': 'v1061'})
    #     root.append(self.root)
    #     tree = etree.ElementTree(root)
    #     tree.write(outpath, encoding="UTF-8", xml_declaration=True)
    #     return
    #

# to be expanded.....
# # # # # # # # # # # # # # # # # # # # # # # # # # # # ZONE DE TESTS
"""outpath = "/media/mtd/stock/boulot_sur_dart/temp/"

write_coeff_diff([], outpath)"""
