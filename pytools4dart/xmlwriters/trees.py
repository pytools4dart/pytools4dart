# !/usr/bin/env python2
#  -*- coding: utf-8 -*-
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

Objects and functions necessary to write the trees xml file.
It is important to note the resulting xml file is written over a single line.

"""
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree


def write_trees(changetracker):
    """write coeff_diff xml fil

    proceed in the following manner :
        -instantiate appropriate dartdir object
        -set default nodes
        -mutate depending on changetracker
        -output file to xml

    """
    trees = DartTreesXML(changetracker)

    trees.basenodes()

    trees.adoptchanges(changetracker)

    outpath = changetracker[2]
    trees.writexml(outpath+"trees.xml")
    return


class DartTreesXML(object):
    """object for the exporting to xml of atmosphere related parameters

    After instantiation, a default tree of nodes is created.
    Changes based on the passed "changetracker" variable have then
    to take place in order to upgrade the tree.
    All the tag names of tree nodes are supposed to be IDENTICAL to the ones
    produces by DART. The variable names are sometimes shortened.

    Particularity of trees : the "base xml tree" is almost empty.

    """

    def __init__(self, changetracker):
        self.changes = changetracker
        self.root = None
        return

    def adoptchanges(self):
        """method to update xml tree based on user-defined parameters

        here goes the magic where we change some nodes based on parameters
        it would maybe be something like this :
           - for some values, just append them somewhere
           - for the others, find them in the tree and modify them (tricky bit)

        Complete path to node to be modified will have to be explicitly written
        in this way : './Phase/DartInputParameters/SpectralDomainTir'
        for the query to work.

        """

        if "trees" in self.changes[0]:
            self.changes = self.changes[1]["trees"]
            if 1 in self.changes['mode']:

                self.treeone(self.changes[1])
            if 2 in self.changes['mode']:
                print "doing even more!"
            return
        else:
            return

    def basenodes(self):
        """
        """
        return

    def treeone(self, pathtree, ntrees, lai, optprop, indexoptprop):
        """creates all nodes and properties common to default simulations

        ComputedTransferFunctions : write transferFunctions would be the place
        where the saving of the computed atmosphere is done.
        """
        trees_atr = {'sceneModelCharacteristic': '1', 'isTrees': '1'}
        self.root = etree.Element('Trees', trees_atr)
        etree.SubElement(self.root, 'TreeGeneralOptions',
                         {'triangleTreeRepresentation': '0'})

        treeone_atr = {'laiZone': '0',
                       'sceneParametersFileName': pathtree}
        subroot = etree.SubElement(self.root, "Trees_1", treeone_atr)
        specie_atr = {'numberOfTreesInWholeScene': str(ntrees),
                      'branchesAndTwigsSimulation': '0', 'lai': str(lai)}
        specie = etree.SubElement(subroot, 'Specie', specie_atr)

        trunkopt = None
        # specie branch
        opt_atr = {'indexFctPhase': '0', 'ident': trunkopt, 'type': '0'}
        therm_atr = {'idTemperature': 'ThermalFunction290_310',
                     'indexTemperature': '0'}
        # TODO : Here are properties that could be changed
        crown_atr = {'verticalWeightForUf': '1.00', 'distribution': '0',
                     'relativeHeightVsCrownHeight': '1.00',
                     'laiConservation': '1',
                     'relativeTrunkDiameterWithinCrown': '0.50'}

        etree.SubElement(specie, 'OpticalPropertyLink', opt_atr)
        etree.SubElement(specie, 'ThermalPropertyLink', therm_atr)
        crown = etree.SubElement(specie, 'CrownLevel', crown_atr)

        # Crown sub branch
        cropt_atr = {'indexFctPhase': '0',
                     'ident': 'Lambertian_Phase_Function_1', 'type': '0'}
        crotherm_atr = {'idTemperature': 'ThermalFunction290_310',
                        'indexTemperature': '0'}
        etree.SubElement(crown, 'OpticalPropertyLink', cropt_atr)
        etree.SubElement(crown, 'ThermalPropertyLink', crotherm_atr)

        veg = etree.SubElement(crown, 'VegetationProperty')

        # Vegetation Sub Sub branch
        # TODO : check how indectFctPhase works!!
        vegopt_atr = {'indexFctPhase': indexoptprop,
                      'ident': optprop}
        vegtherm_atr = {'idTemperature': 'ThermalFunction290_310',
                        'indexTemperature': '0'}
        etree.SubElement(veg, 'VegetationOpticalPropertyLink', vegopt_atr)
        etree.SubElement(veg, 'ThermalPropertyLink', vegtherm_atr)

        # base nodes
        # etree.SubElement(self.root, 'SunViewingAngles', sunangles_atr)

        return

    def writexml(self, outpath):
        """ Writes the built tree to the specified path

        Also includes the version and build of DART as the root element.
        This part could(should?) be modified.
        """
        root = etree.Element('DartFile',
                             {'version': '5.7.0', 'build': 'v1033'})
        if self.root is not None:
            root.append(self.root)
        tree = etree.ElementTree(root)
        tree.write(outpath, encoding="UTF-8", xml_declaration=True)
        return


# to be expanded.....
# # # # # # # # # # # # # # # # # # # # # # # # # # # # ZONE DE TESTS
if __name__ == '__main__':

    outpath = "/media/mtd/stock/boulot_sur_dart/temp/"

    write_trees([], outpath)
