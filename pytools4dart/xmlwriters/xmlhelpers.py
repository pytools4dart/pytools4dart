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

This module is a test zone with basic functions to visualize, write and edit
etree objects and xml files.

"""

import os
import sys
import xmlschema
from pytools4dart.settings import getdartdir, getdartversion

try:
    import xml.etree.cElementTree as etree
    print ("imported cetree")
except ImportError:
    print ("oups!, importing pytetree")
    import xml.etree.ElementTree as etree


def dartxmlroot(dartdir = None):
    if not dartdir:
        dartdir = getdartdir()

    version, _, build = getdartversion(dartdir)

    root = etree.Element('DartFile',
                     {'version': version, 'build': build})

def valxmlxsd(filename_xml, filename_xsd):
    """ validates xml based on xsd file

    works if stuff is in same order
    """
    my_schema = xmlschema.XMLSchema(filename_xsd)
    my_schema.validate(filename_xml)

    return


def validatexml(filename_xml, filename_xsd):
    """validating xml with xsd file

    credits to : https://emredjan.github.io/blog/2017/04/08/validating-xml/
    BUT DOESN'T WORK YET
    """
    from lxml import etree
    from io import StringIO

    # open and read schema file
    with open(filename_xsd, 'r') as schema_file:
        schema_to_check = schema_file.read()

    # open and read xml file
    with open(filename_xml, 'r') as xml_file:
        xml_to_check = xml_file.read()

    # changed following line from :
    # xmlschema_doc = etree.parse(StringIO(schema_to_check))
    # to :
    xmlschema_doc = etree.parse(StringIO(schema_to_check.decode('utf-8')))
#
    xmlschema = etree.XMLSchema(xmlschema_doc)
    # parse xml
    try:
        doc = etree.parse(StringIO(xml_to_check))
        print('XML well formed, syntax ok.')

    # check for file IO error
    except IOError:
        print('Invalid File')

    # check for XML syntax errors
    except etree.XMLSyntaxError as err:
        print('XML Syntax Error, see error_syntax.log')
        with open('error_syntax.log', 'w') as error_log_file:
            error_log_file.write(str(err.error_log))
        quit()

    except:
        print('Unknown error, exiting.')
        quit()
    # validate against schema
    try:
        xmlschema.assertValid(doc)
        print('XML valid, schema validation ok.')

    except etree.DocumentInvalid as err:
        print('Schema validation error, see error_schema.log')
        with open('error_schema.log', 'w') as error_log_file:
            error_log_file.write(str(err.error_log))
        quit()

    except:
        print('Unknown error, exiting.')
        quit()

    return


# prettify xml :
# https://norwied.wordpress.com/2013/08/27/307/
def indent(elem, level=0):
    """To prettify an xml tree.

    use indent(element) on the root element of the tree.
    more precisely :
    tree = indent(element)
    tree.write(path, xml-decaration = True, encoding = "utf-8", method="xml")
    """
    i = "\n" + level*"    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
    return


def get_children(node, attribute=False, length=0):
    """prints the hierarchy of an xml file with graphic indentation

    iteratively gets children of an etree node.
    """

    print "".join(("|", (length+1)*"--", ">")), node.tag
    if attribute:
        print (length+1) * "-----", node.attrib
    if len(node) > 0:
        for nephew in node:

            print "".join(("|", (length+2)*"--", ">")), nephew.tag
            if attribute:
                print (length+2)*"-----", nephew.attrib
            if len(nephew.getchildren()) > 0:
                for i in range(len(nephew)):
                    get_children(nephew[i], True, length+2)
    return


def get_all_structures(pathin, pathout=None):
    """calls get children on all xml files in a directory,
    and print results in another if wanted
    """

    if pathout:
        orig = sys.stdout
    for fichier in os.listdir(pathin):
        if fichier.endswith(".xml"):

            a = pathin+fichier

            sys.stdout = open(pathout+os.path.basename(fichier)+".txt", "w")
            tree = etree.parse(a)
            root = tree.getroot()
            print root.tag  # , root.attrib
            for child in root:
                print child.tag, child.attrib
                if len(child.getchildren()) > 0:
                    for i in range(len(child)):
                        get_children(child[i], True, 0)
            if pathout:
                sys.stdout.flush()
    if pathout:
        sys.stdout = orig
    return
if __name__ == "__main__":
    """
    pathseq = '/media/mtd/stock/DART/user_data/simulations/test/'
    pathout = '/media/mtd/stock/boulot_sur_dart/temp/compare/seq/'
    get_all_structures(pathseq+'seq/', pathout)

    """
    pathin = "/media/mtd/stock/DART_5-7-1_v1061/user_data/simulations/testprosequence/input/"
    pathessai = '/media/mtd/stock/boulot_sur_dart/temp/essai_sequence/input/'
    pathout = '/media/mtd/stock/boulot_sur_dart/temp/compare/seq/'


    get_all_structures(pathin, pathout+'dart/')
    get_all_structures(pathessai, pathout+'essai/')
    """
    # XML validation
    #inpath = '/media/mtd/stock/boulot_sur_dart/temp/essai_sequence/'
    #xsd = "/media/mtd/stock/boulot_sur_dart/XSDs/schemaXml/"
    #
    #fichier = "inputphase"
    #valxmlxsd('/media/mtd/stock/DART/user_data/simulations/empty/input/'
    #          + 'phase'+".xml", xsd+'phase'+".xsd")
    #print "ah?"
    #valxmlxsd(inpath+fichier+".xml", xsd+'phase'+".xsd")
    #"""

    # Get structure of a single xml file
    """
    pathin = "/media/mtd/stock/DART/user_data/simulations/essai_sequence/input/"
    pathessai = '/media/mtd/stock/boulot_sur_dart/temp/essai_sequence/input/'
    otherpath = "/media/mtd/stock/boulot_sur_dart/temp/"
    # pathout="/media/mtd/stock/boulot_sur_dart/temp/empty_strucs(djasimulee)/"
    fichier = "coeff_diff.xml"
    a = pathin+fichier
    tree = etree.parse(a)
    root = tree.getroot()

    get_children(root, True)
    """
    """
    # print 'And now, for something completely different'


    # get structures of xml files in a folder, and prints them to file if needed
    # pathin="/media/mtd/stock/DART/user_data/simulations/sequence_wvl/"seq_bdwvlwidth.xml
    # pathout="/media/mtd/stock/boulot_sur_dart/temp/"
    # get_all_structures(pathin)

    """
    """
    #https://stackoverflow.com/questions/3605680/creating-a-simple-xml-file-using-python

    import xml.etree.cElementTree as ET

    root = ET.Element("root")
    doc = ET.SubElement(root, "doc")

    ET.SubElement(doc, "field1", name="blah").text = "some value1"
    ET.SubElement(doc, "field2", name="asdfasd").text = "some vlaue2"

    tree = ET.ElementTree(root)
    tree.write("filename.xml")

    output :
    <root>
     <doc>
         <field1 name="blah">some value1</field1>
         <field2 name="asdfasd">some vlaue2</field2>
     </doc>

    </root>
    """

    #
    # class idee(object):
    #    def __init__(self):
    #        self.time=0
    #        self.root=etree.Element("Base")
    #        self.tree=etree.ElementTree(self.root)
    #        expertmode=0
    #    def think(self):
    #        print "hum"
    #        return
    #    def doctrine(self):
    #        expertmode=etree.SubElement(self.root,"ExpertModeZone")
    #        return
    # class emotion(idee):
    #    def __init__(self):
    #        idee.__init__(self)
    #        return
    #    def essai(self):
    #        return
    #
    # pheno=emotion()
    # pheno.doctrine()
