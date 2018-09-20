# !/usr/bin/env python2
#  -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Eric Chraibi <eric.chraibi@irstea.fr>, Florian de Boissieu <florian.deboissieu@irstea.fr>
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
Objects and functions necessary to write the inversion xml file.
It is important to note the resulting xml file is written over a single line.
"""
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree
from dartxml import DartXml


def write_inversion(changetracker, simu_name):
    """write inversion xml file

    proceed in the following manner :
        -instantiate appropriate dartdir object
        -set default nodes
        -mutate depending on changetracker
        -output file to xml

    """
    inversion = DartInversionXML(changetracker)

    inversion.basenodes()

    inversion.adoptchanges(changetracker)

    inversion.writexml(simu_name, 'inversion.xml')
    return


class DartInversionXML(DartXml):
    """object for the editing and exporting to xml of atmosphere related parameters

    After instantiation, a default tree of nodes is created.
    Changes based on the passed "changetracker" variable have then
    to take place in order to upgrade the tree.
    All the tag names of tree nodes are supposed to be IDENTICAL to the ones
    produces by DART. The variable names are sometimes shortened.

    """

    def __init__(self, changetracker):
        dir_atr = {'runInversion': '0'}
        self.root = etree.Element("DartInversion", dir_atr)
        self.tree = etree.ElementTree(self.root)
        self.changes = changetracker
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

        if "inversion" in changetracker[0]:
            self.changes = changetracker[1]["inversion"]
            for node in self.changes:
                print "Modifying : ", node
                self.root.find(node)

            return
        else:
            return

    def basenodes(self):
        """creates all nodes and properties common to default simulations
        """
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


# to be expanded.....
# # # # # # # # # # # # # # # # # # # # # # # # # # # # ZONE DE TESTS
"""outpath = "/media/mtd/stock/boulot_sur_dart/temp/"

write_directions([], outpath)
"""
