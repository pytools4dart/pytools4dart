# !/usr/bin/env python2
#  -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 14:15:03 2018

@author: mtd

Objects and functions necessary to write the coeff_diff xml file.
It is important to note the resulting xml file is written over a single line.
TODO :
    Add a vegetation optical property
    Add optical property from db

"""
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree


def write_coeff_diff(changetracker):
    """write coeff_diff xml fil

    proceed in the following manner :
        -instantiate appropriate dartcoeff object
        -set default nodes
        -mutate depending on changetracker
        -output file to xml

    """
    coeff = DartCoefXML(changetracker)
    coeff.basenodes()
    coeff.addvegetation()
    coeff.adoptchanges(changetracker)

    outpath = changetracker[2]
    coeff.writexml(outpath+"coeff_diff.xml")
    return


class DartCoefXML(object):
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
        self.changes = changetracker
        return

    def adoptchanges(self, changetracker):
        """method to update xml tree based on user-defined parameters

        here goes the magic where we change some nodes based on parameters

        Complete path to node to be modified will have to be explicitly written
        in this way : './Phase/DartInputParameters/SpectralDomainTir'
        for the query to work.
        TODO.
        """

        if "phase" in changetracker[0]:
            self.changes = changetracker[1]["coeff_diff"]
            for node in self.changes:
                print "Modifying : ", node
                self.root.find(node)

            return
        else:
            return

    def basenodes(self):
        """creates all nodes and properties common to default simulations

        """

        # base nodes
        # # simple
        etree.SubElement(self.root, 'HapkeSpecularMultiFunctions')
        etree.SubElement(self.root, 'RPVMultiFunctions')
        etree.SubElement(self.root, 'AirMultiFunctions')

        understory_atr = {'integrationStepOnTheta': '1',
                          'integrationStepOnPhi': '10',
                          'outputLADFile': '0'}
        etree.SubElement(self.root, 'UnderstoryMultiFunctions', understory_atr)

        # parent nodes
        # # lambertian branch  : default lambertian created Dart simulations
        lambmulti_atr = {'ident': 'Lambertian_Phase_Function_1',
                         'useSpecular': '0',
                         'roStDev': '0.000',
                         'ModelName': 'reflect_equal_1_trans_equal_0_0',
                         'databaseName': 'Lambertian_vegetation.db',
                         'useMultiplicativeFactorForLUT': '1'}
        lambmultif = etree.SubElement(self.root, "LambertianMultiFunctions")
        lambmulti = etree.SubElement(lambmultif, "LambertianMulti",
                                     lambmulti_atr)
        prosp_atr = {'useProspectExternalModule': '0', 'isFluorescent': '0'}
        lambnode_atr = {'diffuseTransmittanceFactor': '1',
                        'directTransmittanceFactor': '1',
                        'useSameOpticalFactorMatrixForAllBands': '0',
                        'reflectanceFactor': '1',
                        'useSameFactorForAllBands': '1',
                        'specularIntensityFactor': '1'}

        etree.SubElement(lambmulti, 'ProspectExternalModule', prosp_atr)
        etree.SubElement(lambmulti, 'lambertianNodeMultiplicativeFactorForLUT',
                         lambnode_atr)

        # # temperatures branch
        temp = etree.SubElement(self.root, 'Temperatures')
        thermal_atr = {'meanT': '300.0',
                       'idTemperature': 'ThermalFunction290_310',
                       'deltaT': '20.0', 'singleTemperatureSurface': '1',
                       'override3DMatrix': '0', 'useOpticalFactorMatrix': '0'}
        etree.SubElement(temp, 'ThermalFunction', thermal_atr)

        return

    def addvegetation(self):
        """ Adds a vegetation Node

        This module will require some work as it probably will be our most used
        one. How to parameter Prospect? Access Database? etc...
        """
        rootveg = self.root.find("./UnderstoryMultiFunctions")
        veg_atr = {'ident': 'custom', 'dimFoliar': '0.01', 'lad': '1',
                   'useSpecular': '0', 'ModelName': 'leaf_deciduous',
                   'databaseName': 'Vegetation.db',
                   'useMultiplicativeFactorForLUT': '1',
                   'useOpticalFactorMatrix': '0'}

        veg = etree.SubElement(rootveg, 'UnderstoryMulti', veg_atr)

        clump_atr = {'omegaMax': '0.0', 'clumpinga': '0.0',
                     'clumpingb': '0.0', 'omegaMin': '1.0'}
        etree.SubElement(veg, 'DirectionalClumpingIndexProperties', clump_atr)

        prospect_atr = {'useProspectExternalModule': '0', 'isFluorescent': '0'}
        multilutnode_atr = {'useSameFactorForAllBands': '1',
                            'adaxialReflectanceFactor': '1.0',
                            'useSameOpticalFactorMatrixForAllBands': '0',
                            'abaxialReflectanceFactor': '1.0',
                            'LeafTransmittanceFactor': '1.0'}

        etree.SubElement(veg, 'ProspectExternalModule', prospect_atr)
        multilut = etree.SubElement(veg,
                                    'understoryNodeMultiplicativeFactorForLUT',
                                    multilutnode_atr)

        multilut_atr = {'useOpticalFactorMatrix': '0',
                        'adaxialReflectanceFactor': '1.0',
                        'abaxialReflectanceFactor': '1.0',
                        'LeafTransmittanceFactor': '1.0'}
        etree.SubElement(multilut, 'understoryMultiplicativeFactorForLUT',
                         multilut_atr)

        return

    def writexml(self, outpath):
        """ Writes the built tree to the specified path

        Also includes the version and build of DART as the root element.
        This part could(should?) be modified.
        """
        root = etree.Element('DartFile',
                             {'version': '5.7.0', 'build': 'v1033'})
        root.append(self.root)
        tree = etree.ElementTree(root)
        tree.write(outpath, encoding="UTF-8", xml_declaration=True)
        return


# to be expanded.....
# # # # # # # # # # # # # # # # # # # # # # # # # # # # ZONE DE TESTS
"""outpath = "/media/mtd/stock/boulot_sur_dart/temp/"

write_coeff_diff([], outpath)"""
