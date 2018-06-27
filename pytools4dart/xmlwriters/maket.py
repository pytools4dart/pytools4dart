# !/usr/bin/env python2
#  -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 14:15:03 2018

@author: mtd

Objects and functions necessary to write the maket xml file.
It is important to note the resulting xml file is written over a single line.

"""
try:
    import xml.etree.cElementTree as etree
    print ("imported cetree")
except ImportError:
    print ("oups!, importing pytetree")
    import xml.etree.ElementTree as etree


def write_maket(simutype, changetracker, outpath):
    """write coeff_diff xml fil

    proceed in the following manner :
        -instantiate appropriate dartdir object
        -set default nodes
        -mutate depending on changetracker
        -output file to xml

    """
    phase = DartMaketXML(changetracker)

    phase.basenodes()

    phase.specnodes()
    #  phase.adoptchanges()

    phase.writexml(outpath+"maket.xml")
    return


class DartMaketXML(object):
    """object for the editing and exporting to xml of maket related parameters

    After instantiation, a default tree of nodes is created.
    Changes based on the passed "changetracker" variable have then
    to take place in order to upgrade the tree.
    All the tag names of tree nodes are supposed to be IDENTICAL to the ones
    produces by DART. The variable names are sometimes shortened.

    """

    def __init__(self, changetracker):
        mak_atr = {'dartZone': '0', 'exactlyPeriodicScene': '1'}
        self.root = etree.Element("Maket", mak_atr)
        self.tree = etree.ElementTree(self.root)
        self.changes = changetracker
        return

    def adoptchanges(changetracker, self):
        """method to update xml tree based on user-defined parameters

        here goes the magic where we change some nodes based on parameters
        it would maybe be something like this :
           - for some values, just append them somewhere
           - for the others, find them in the tree and modify them (tricky bit)

        Complete path to node to be modified will have to be explicitly written
        in this way : './Phase/DartInputParameters/SpectralDomainTir'
        for the query to work.

        """

        if "maket" in changetracker[0]:
            self.changes = changetracker[1]["atmosphere"]
            for node in self.changes:
                print "Modifying : ", node
                self.root.find(node)

            return
        else:
            return

    def basenodes(self):
        """creates all nodes and properties common to default simulations

        ComputedTransferFunctions : write transferFunctions would be the place
        where the saving of the computed atmosphere is done.
        """

        # base nodes

        latlon_atr = {'latitude': '0.0',
                      'altitude': '0.0',
                      'longitude': '0.0'}

        etree.SubElement(self.root, 'LatLon', latlon_atr)
        # parent nodes
        scene = etree.SubElement(self.root, 'Scene')
        soil = etree.SubElement(self.root, 'Soil')

        # scene branch
        celldim_atr = {'x': '1',
                       'z': '1'}
        scenedim_atr = {'y': '40.00',
                        'x': '40.00'}
        etree.SubElement(scene, 'CellDimensions', celldim_atr)
        etree.SubElement(scene, 'SceneDimensions', scenedim_atr)

        # soil branch
        optprop_atr = {'indexFctPhase': '0',
                       'ident': 'Lambertian_Phase_Function_1',
                       'type': '0'}
        thermal_atr = {'idTemperature': 'ThermalFunction290_310',
                       'indexTemperature': '0'}
        etree.SubElement(soil, 'OpticalPropertyLink', optprop_atr)
        etree.SubElement(soil, 'ThermalPropertyLink', thermal_atr)
        etree.SubElement(soil, 'Topography', {'presenceOfTopography': '0'})
        etree.SubElement(soil, 'DEM_properties', {'createTopography': '0'})
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
outpath = "/media/mtd/stock/boulot_sur_dart/temp/"

write_maket("flux", [], outpath)
