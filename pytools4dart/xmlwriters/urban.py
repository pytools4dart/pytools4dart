# !/usr/bin/env python2
#  -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 14:15:03 2018

@author: mtd

Objects and functions necessary to write the urban xml file.
It is important to note the resulting xml file is written over a single line.

"""
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree


def write_urban(changetracker):
    """write urban xml fil

    proceed in the following manner :
        -instantiate appropriate dartdir object
        -set default nodes
        -mutate depending on changetracker
        -output file to xml

    """
    urban = DartUrbanXML(changetracker)

    urban.basenodes()

    urban.adoptchanges()

    outpath = changetracker[2]
    urban.writexml(outpath+"urban.xml")
    return


class DartUrbanXML(object):
    """object for the editing and exporting to xml of atmosphere related parameters

    After instantiation, a default tree of nodes is created.
    Changes based on the passed "changetracker" variable have then
    to take place in order to upgrade the tree.
    All the tag names of tree nodes are supposed to be IDENTICAL to the ones
    produces by DART. The variable names are sometimes shortened.

    """

    def __init__(self, changetracker):

        self.root = etree.Element("Urban", {})
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

        if "urban" in changetracker[0]:
            self.changes = changetracker[1]["urban"]
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

        etree.SubElement(self.root, 'Buildings', {})
        etree.SubElement(self.root, 'Roads', {})
        etree.SubElement(self.root, 'SmallWalls', {})

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

write_directions([], outpath)
"""
