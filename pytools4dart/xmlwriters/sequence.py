# !/usr/bin/env python2
#  -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 14:15:03 2018

@author: mtd

Objects and functions necessary to write the sequence xml file.
It is important to note the resulting xml file is written over a single line.
NB : The DartFile node (root node) differs from the one from all the other xml.

TODO : add a loop for sequence name in order to produce all relevant file.
(but first think if it is really useful...)
"""
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
        seq = DartSequenceXML(changetracker[1]['sequence'], seqname)
        seq.basenodes()
        seq.addsequence()
        outpath = changetracker[2]
        seq.writexml(outpath + seqname + ".xml")
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
        """
        self.seqname = seqname
        dir_atr = {'sequenceName': 'sequence;;' + seqname}
        self.root = etree.Element("DartSequencerDescriptor", dir_atr)
        self.tree = etree.ElementTree(self.root)
        self.changes = changetracker
        return

    def basenodes(self):
        """ here go the general parameters for a sequence.

        Determines which outputs are generated and deleted during the sequence
        run.
        """

        # base nodes
        pref_atr = {'triangleFileProcessorLaunched': 'true',
                    'deleteMaket': 'false',
                    'directionLaunched': 'true',
                    'deleteDartSequenceur': 'false',
                    'deleteLibPhase': 'false',
                    'maketLaunched': 'true',
                    'atmosphereMaketLaunched': 'true',
                    'dartLaunched': 'true',
                    'deleteDartTxt': 'false',
                    'individualDisplayEnabled': 'false',
                    'deleteTriangles': 'false',
                    'phaseLaunched': 'true',
                    'zippedResults': 'false',
                    'deleteInputs': 'false',
                    'genMode': 'XML',
                    'deleteTreePosition': 'false',
                    'deleteDirection': 'false',
                    'hapkeLaunched': 'true',
                    'useBroadBand': 'true',
                    'numberParallelThreads': '4',
                    'prospectLaunched': 'false',
                    'vegetationLaunched': 'true',
                    'deleteAtmosphere': 'false',
                    'displayEnabled': 'true',
                    'deleteAtmosphereMaket': 'false',
                    'demGeneratorLaunched': 'true',
                    'deleteDartLut': 'false',
                    'useSceneSpectra': 'true',
                    'deleteAll': 'false',
                    'deleteMaketTreeResults': 'false'}

        lutpref_atr = {'luminance': 'true',         'phiMin': '',
                       'addedDirection': 'false',   'coupl': 'true',
                       'fluorescence': 'true',      'productsPerType': 'false',
                       'phiMax': '',                'storeIndirect': 'false',
                       'ordre': 'true',             'atmosToa': 'true',
                       'thetaMax': '',              'reflectance': 'true',
                       'atmosToaOrdre': 'true',     'iterx': 'true',
                       'otherIter': 'true',         'generateLUT': 'true',
                       'sensor': 'true',            'toa': 'true',
                       'thetaMin': '',              'maketCoverage': 'false'}

        etree.SubElement(self.root, 'DartSequencerPreferences', pref_atr)
        etree.SubElement(self.root, 'DartLutPreferences', lutpref_atr)
        etree.SubElement(self.root, 'DartSequencerDescriptorEntries')

        # DartSequenceDescriptorGroup branch
        return

    def addsequence(self):
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

        """

        for groupname in self.changes:
            print "Adding:", groupname, "to sequence"
            entries = self.root.find('./DartSequencerDescriptorEntries')
            grp = etree.SubElement(entries,
                                   'DartSequencerDescriptorGroup',
                                   {'groupName': groupname})

            for param, values in self.changes[groupname].iteritems():
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
