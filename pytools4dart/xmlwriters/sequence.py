# !/usr/bin/env python2
#  -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 14:15:03 2018

@author: mtd

Objects and functions necessary to write the sequence xml file.
It is important to note the resulting xml file is written over a single line.
NB : The DartFile node (root node) differs from the one from all the other xml.

"""
try:
    import xml.etree.cElementTree as etree
    print ("imported cetree")
except ImportError:
    print ("oups!, importing pytetree")
    import xml.etree.ElementTree as etree


def write_sequence(simutype, changetracker, outpath, seqname):
    """write coeff_diff xml fil

    proceed in the following manner :
        -instantiate appropriate dartdir object
        -set default nodes
        -mutate depending on changetracker
        -output file to xml

    """
    phase = DartSequenceXML(changetracker)

    phase.basenodes()

    phase.specnodes()
    #  phase.adoptchanges()

    phase.writexml(outpath + seqname + ".xml")
    return


class DartSequenceXML(object):
    """object for the editing and exporting to xml of atmosphere related parameters

    After instantiation, a default tree of nodes is created.
    Changes based on the passed "changetracker" variable have then
    to take place in order to upgrade the tree.
    All the tag names of tree nodes are supposed to be IDENTICAL to the ones
    produces by DART. The variable names are sometimes shortened

    """

    def __init__(self, changetracker):
        """
        the name of the sequence goes here!

        The group name may or may not correspond to the sequence name
        """
        seqname = changetracker[100000]
        dir_atr = {'sequenceName': 'sequence;;' + seqname}
        self.root = etree.Element("DartSequencerDescriptor", dir_atr)
        self.tree = etree.ElementTree(self.root)
        self.changes = changetracker
        return


    def basenodes(self):
        """creates all nodes and properties common to default simulations

        ComputedTransferFunctions : write transferFunctions would be the place
        where the saving of the computed atmosphere is done.
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

        # DartSequenceDescriptorGroup branch
        return

    def addsequence(changetracker, self):
        """method to update xml tree based on user-defined parameters

        here goes the magic where we change some nodes based on parameters
        it would maybe be something like this :
           - for some values, just append them somewhere
           - for the others, find them in the tree and modify them (tricky bit)

        Complete path to node to be modified will have to be explicitly written
        in this way : './Phase/DartInputParameters/SpectralDomainTir'
        for the query to work.

        """

        if "atmosphere" in changetracker[0]:
            self.changes = changetracker[1]["sequence"]
            for props in self.changes:

                print "Adding : ", props[0]
                groupname = props[0]
                entries = self.root.find('./DartSequencerDescriptorEntries')
                grp = etree.SubElement(entries,
                                       'DartSequencerDescriptorGroup',
                                       {'groupName': groupname})

                seqarg = {'propertyName': 'Phase.DartInputParameters.'      \
                          'SpectralIntervals.SpectralIntervalsProperties.'  \
                          'meanLambda',
                          'args': '400;50;3',
                          'type': 'linear'}
                seqarg = props[1]
                etree.SubElement(grp, 'DartSequencerDescriptorEntry', seqarg)
            return
        else:
            return

    def writexml(self, outpath):
        """ Writes the built tree to the specified path

        Also includes the version and build of DART as the root element.
        This part could(should?) be modified.
        The version number here differs from the one on all other xml files.
        """
        root = etree.Element('DartFile',
                             {'version': '1.0'})
        root.append(self.root)
        tree = etree.ElementTree(root)
        tree.write(outpath, encoding="UTF-8", xml_declaration=True)
        return


# to be expanded.....
# # # # # # # # # # # # # # # # # # # # # # # # # # # # ZONE DE TESTS
outpath = "/media/mtd/stock/boulot_sur_dart/temp/"

write_directions("flux", [], outpath)
