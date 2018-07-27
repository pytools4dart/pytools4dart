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

Objects and functions necessary to write the maket xml file.
It is important to note the resulting xml file is written over a single line.
TODO : easier maket possibilities
"""
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree
from shutil import copyfile


def write_maket(changetracker):
    """write coeff_diff xml fil

    proceed in the following manner :
        -instantiate appropriate dartdir object
        -set default nodes
        -mutate depending on changetracker
        -output file to xml
    TODO : Function to be put in common between all wmlwriters?
    """
    outpath = changetracker[2]

    if 'usefile' in changetracker[1]:
        if 'maket' in changetracker['usefile']:
            copyfile(changetracker['usefile']['maket'], outpath)

    else:
        maket = DartMaketXML(changetracker)
        maket.basenodes()
        maket.adoptchanges(changetracker)

        maket.writexml(outpath+"maket.xml")
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
        self.changes = changetracker['maket']

        if 'scene' in self.changes:
            self.scene = self.changes['scene']
        else:
            self.scene = [10, 10]
        return

    def adoptchanges(self, changetracker):
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
            # possibly stuff to do here, but not sure
            return
        return

    def basenodes(self):
        """creates all nodes and properties common to default simulations

        ComputedTransferFunctions : write transferFunctions would be the place
        where the saving of the computed atmosphere is done.
        """

        xscene = self.scene[0]
        yscene = self.scene[1]
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
        scenedim_atr = {'y': str(yscene),
                        'x': str(xscene)}
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
if __name__ == '__main__':
    """outpath = "/media/mtd/stock/boulot_sur_dart/temp/"

    write_maket("flux", [], outpath)"""
