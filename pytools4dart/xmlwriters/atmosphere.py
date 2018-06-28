# !/usr/bin/env python2
#  -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 14:15:03 2018

@author: mtd

Objects and functions necessary to write the atmosphere xml file.
It is important to note the resulting xml file is written over a single line.

"""
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree


def write_atmosphere(changetracker):
    """write coeff_diff xml fil

    proceed in the following manner :
        -instantiate appropriate dartcoeff object
        -set default nodes
        -mutate depending on changetracker
        -output file to xml

    """
    atmo = DartAtmosphereXML(changetracker)
    atmo.basenodes()
    atmo.adoptchanges()

    outpath = changetracker[2]
    atmo.writexml(outpath+"atmosphere.xml")
    return


class DartAtmosphereXML(object):
    """object for the editing and exporting to xml of atmosphere related parameters

    After instantiation, a default tree of nodes is created.
    Changes based on the passed "changetracker" variable have then
    to take place in order to upgrade the tree.
    All the tag names of tree nodes are supposed to be IDENTICAL to the ones
    produces by DART. The variable names are sometimes shortened.

    """

    def __init__(self, changetracker):
        self.root = etree.Element(
                "Atmosphere",
                {'isRadiativeTransfertInBottomAtmosphereDefined': '0'}
                )
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

        if "atmosphere" in changetracker[0]:
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
        isatm = etree.SubElement(self.root, 'IsAtmosphere',
                                 {'typeOfAtmosphere': '1'})
        # simple
        atmopt_atr = {
                'hgParametersModelName': 'RURALV23',
                'gasGroup': '1',
                'co2MixRate': '365.0',
                'correctionBandModel': '1',
                'temperatureModelName': 'USSTD76',
                'scaleOtherGases': '0',
                'gasCumulativeModelName': 'USSTD76',
                'redefTemperature': '0',
                'gasModelName': 'USSTD76',
                'aerosolsModelName': 'USSTD76_RURALV23',
                'aerosolCumulativeModelName': 'RURALV23',
                'aerosolOptDepthFactor': '1',
                'databaseName': 'dart_atmosphere.db',
                'precipitableWaterAmountCkeckbox': '0',
                'ignoreGasForExtrapolation': '0'}
        etree.SubElement(isatm, 'AtmosphericOpticalPropertyModel', atmopt_atr)
        # parent nodes
        atmgeom_atr = {'minimumNumberOfDivisions': '4',
                       'discretisationAtmos': '1', 'heightOfSensor': '3000'}
        atmgeom = etree.SubElement(isatm, 'AtmosphereGeometry', atmgeom_atr)

        atmiter = etree.SubElement(isatm, 'AtmosphereIterations')

        # atmiter branch
        atmprod_atr = {'atmosphereRadiance_BOA_avantCouplage': '0',
                       'atmosphereRadiance_BOA_apresCouplage': '0',
                       'ordreUnAtmos': '0', 'atmosphereBRF_TOA': '0'}
        etree.SubElement(atmiter, 'AtmosphereProducts', atmprod_atr)

        etree.SubElement(atmiter, 'AtmosphereComponents',
                         {'upwardingFluxes': '0', 'downwardingFluxes': '0'})
        etree.SubElement(atmiter, 'AtmosphereExpertModeZone',
                         {'seuilFTAtmos': '0.0001',
                          'seuilEclairementAtmos': '0.00001',
                          'extrapol_atmos': '1'})
        # # transfer functions branch
        transfunc = etree.SubElement(atmiter, 'AtmosphereTransfertFunctions',
                                     {'inputOutputTransfertFunctions': '0'})
        etree.SubElement(transfunc, 'ComputedTransferFunctions',
                         {'writeTransferFunctions': '0'})

        # atmgeom branch
        etree.SubElement(atmgeom, 'discretisationAtmosAuto',
                         {'epsilon_atmos': '0.003', 'xAI': '400.0',
                          'gamma_atmos': '0.95', 'yAI': '400.0'})

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

write_atmosphere([], outpath)"""
