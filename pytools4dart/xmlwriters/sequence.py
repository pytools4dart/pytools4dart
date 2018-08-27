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

Objects and functions necessary to write the sequence xml file.
It is important to note the resulting xml file is written over a single line.
NB : The DartFile node (root node) differs from the one from all the other xml.

TODO : add a loop for sequence name in order to produce all relevant file.
(but first think if it is really useful...)
"""
import os

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree


def write_sequence(changetracker):
    """write coeff_diff xml fil

    proceed in the following manner :
        -instantiate appropriate dartdir object
        -set default nodes
        -mutate depending on changetracker
        -output file to xml

    """
    if "sequence" in changetracker[0]:
        seqname = changetracker[1]['sequencename']
        # seqname = 'sequence'
        seq = DartSequenceXML(changetracker, seqname)
        seq.addsequences()
        seq.basenodes()
        pathsimu = changetracker[2]
        outpath = os.path.dirname(os.path.dirname(pathsimu))
        print outpath
        seq.writexml(os.path.join(outpath,seqname) + ".xml")
        print (os.path.join(outpath,seqname) + ".xml")
        return
    else:
        return


class DartSequenceXML(object):
    """object for the editing and exporting to xml sequence parameters

    After instantiation, a default tree of nodes is created.
    Changes based on the passed "changetracker" variable have then
    to take place in order to upgrade the tree.
    All the tag names of tree nodes are supposed to be IDENTICAL to the ones
    produces by DART. The variable names are shortened.

    """

    def __init__(self, changetracker, seqname):
        """
        the name of the sequence goes here!

        The group name may or may not correspond to the sequence name
        TODO : cleaning up!
        """
        self.seqname = seqname
        TRUC = 1
        if TRUC== 'centralwvl':
            truename = ('Phase.DartInputParameters.SpectralIntervals.'
                        'SpectralIntervalsProperties.meanLambda')
            TRUC = truename

        dir_atr = {'sequenceName': 'sequence;;' + seqname}
        self.root = etree.Element("DartSequencerDescriptor", dir_atr)
        self.tree = etree.ElementTree(self.root)
        etree.SubElement(self.root, 'DartSequencerDescriptorEntries')
        self.sequences = changetracker[1]['sequence']
        self.changes = changetracker[1]
        return

    def basenodes(self):
        """ here go the general parameters for a sequence.

        Determines which outputs are generated and deleted during the sequence
        run.
        """

        # base nodes
        pref_atr = {'atmosphereMaketLaunched':  "true",
                    'dartLaunched':  "true",
                    'deleteAll':  "false",
                    'deleteAtmosphere':  "true",
                    'deleteAtmosphereMaket':  "true",
                    'deleteDartLut':  "true",
                    'deleteDartSequenceur':  "true",
                    'deleteDartTxt':  "true",
                    'deleteDirection':  "false",
                    'deleteInputs':  "false",
                    'deleteLibPhase':  "true",
                    'deleteMaket':  "true",
                    'deleteMaketTreeResults':  "true",
                    'deleteTreePosition':  "true",
                    'deleteTriangles':  "true",
                    'demGeneratorLaunched':  "true",
                    'directionLaunched':  "true",
                    'displayEnabled':  "true",
                    'genMode':  "XML",
                    'hapkeLaunched':  "true",
                    'individualDisplayEnabled':  "false",
                    'maketLaunched':  "true",
                    'numberParallelThreads':  "4",
                    'phaseLaunched':  "true",
                    'prospectLaunched':  "false",
                    'triangleFileProcessorLaunched':  "true",
                    'useBroadBand':  "true",
                    'useSceneSpectra':  "true",
                    'vegetationLaunched':  "true",
                    'zippedResults':  "false"}

        lutpref_atr = {'addedDirection': "false",
                       'atmosToa': "true",
                       'atmosToaOrdre': "false",
                       'coupl': "false",
                       'fluorescence': "false",
                       'generateLUT': "true",
                       'iterx': "true",
                       'luminance': "true",
                       'maketCoverage': "false",
                       'ordre': "false",
                       'otherIter': "false",
                       'phiMax': "",
                       'phiMin': "",
                       'productsPerType': "false",
                       'reflectance': "true",
                       'sensor': "true",
                       'storeIndirect': "false",
                       'thetaMax': "",
                       'thetaMin': "",
                       'toa': "true"}


        etree.SubElement(self.root, 'DartSequencerPreferences', pref_atr)
        etree.SubElement(self.root, 'DartLutPreferences', lutpref_atr)

        # DartSequenceDescriptorGroup branch
        return

    def addsequences(self):
        """

        the sequence options are organised in this way :
            changetracker[1]['sequence'] is a list


        Complete path to node to be modified will have to be explicitly written
        in this way : './Phase/DartInputParameters/SpectralDomainTir'
        for the query to work.

        example of args :
        args  = "base value; step size; number of steps"
        <DartSequencerDescriptorGroup groupName="group1">

            <DartSequencerDescriptorEntry args="400;50;3"
                propertyName="Phase.DartInputParameters.SpectralIntervals.
                        SpectralIntervalsProperties.meanLambda" type="linear"/>

            <DartSequencerDescriptorEntry args="10;5;3"
                propertyName="Phase.DartInputParameters.SpectralIntervals.
                    SpectralIntervalsProperties.deltaLambda" type="linear"/>

        <DartSequencerDescriptorGroup groupName="group2">
            <DartSequencerDescriptorEntry args="0;60;2"
                propertyName="Directions.SunViewingAngles.dayOfTheYear"
                type="linear"/>

        WARNING : Sequence increments together parameters in the same group,
        and combines those in different groups:
            the above parameters give the following values for :
                SpectralIntervals ; deltaLambda ; dayOfTheYear
                400;10;0
                400;10;60
                450;15;0
                450;15;60
                500;20;0
                500;20;60

        TODO : should not be working....to check in depth
        """

        for groupname in self.sequences:
            print "Adding:", groupname, "to sequence"

            if groupname.startswith('prosequence'):
                entries = self.root.find('./DartSequencerDescriptorEntries')
                grp = etree.SubElement(entries,
                                       'DartSequencerDescriptorGroup',
                                       {'groupName': groupname})
                for param, values in self.sequences[groupname].iteritems():
                        seqarg = {'propertyName': param,
                                  'args': str(values[0])
                                  + ';' + str(values[1])
                                  + ';' + str(values[2]),
                                  'type': 'linear'}
                        etree.SubElement(grp, 'DartSequencerDescriptorEntry',
                                         seqarg)
            else:
                entries = self.root.find('./DartSequencerDescriptorEntries')
                grp = etree.SubElement(entries,
                                       'DartSequencerDescriptorGroup',
                                       {'groupName': groupname})

                for param, values in self.sequences[groupname].iteritems():
                    """ TODO : Temporary fix to replace with hdr to dict"""
                    if param == 'wvl':
                        param = ("Phase.DartInputParameters.SpectralIntervals."
                                 "SpectralIntervalsProperties.meanLambda")
                    seqarg = {'propertyName': param,
                              'args': str(values[0])
                              + ';' + str(values[1])
                              + ';' + str(values[2]),
                              'type': 'linear'}
                    etree.SubElement(grp, 'DartSequencerDescriptorEntry',
                                     seqarg)
        return

    def writexml(self, outpath):
        """ Writes the built tree to the specified path

        Also includes the version and build of DART as the root element.
        This part could(should?) be modified.
        The version number here differs from the one on all other xml files.
        """
        root = etree.Element('DartFile', {'version': '1.0'})
        root.append(self.root)
        tree = etree.ElementTree(root)
        tree.write(outpath, encoding="UTF-8", xml_declaration=True)
        return


# to be expanded.....
# # # # # # # # # # # # # # # # # # # # # # # # # # # # ZONE DE TESTS
"""outpath = "/media/mtd/stock/boulot_sur_dart/temp/"

write_directions([], outpath)
"""
