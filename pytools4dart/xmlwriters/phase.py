#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 14:15:03 2018

@author: mtd

Objects and functions necessary to write the phase xml file.
It is important to note the resulting xml file is written over a single line.

"""
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree


def write_phase(changetracker):
    """write phase xml fil

    proceed in the following manner :
        -check simutype
        -instantiate appropriate dartphase object
        -set default nodes
        -mutate depending on changetracker
        -output file to xml

    """
    simutype = changetracker[3]
    if simutype == "lidar":
        phase = LidarPhaseXML(changetracker)
    elif simutype == "flux":
        phase = FluxPhaseXML(changetracker)
    else:
        print "what the ?"
    phase.basenodes()

    phase.specnodes()
    phase.adoptchanges(changetracker)

    outpath = changetracker[2]
    phase.writexml(outpath+"phase.xml")
    return


class DartPhaseXML(object):
    """object for the editing and exporting to xml of phase related parameters

    It should not be used as such, but rather through its subclasses
    (flux and lidar).
    After instantiation, a default tree of nodes is created.
    Changes based on the passed "changetracker" variable have then
    to take place in order to upgrade the tree.
    All the tag names of tree nodes are supposed to be IDENTICAL to the ones
    produces by DART. The variable names are sometimes shortened.

    """

    def __init__(self, changetracker):
        self.root = etree.Element("Phase")
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

        if "phase" in changetracker[0]:
            self.changes = changetracker[1]["phase"]
            for node in self.changes:
                print "Modifying : ", node
                self.root.find(node)

            return
        else:
            return

    def basenodes(self):
        """creates all nodes and properties common to default simulations

        """

        expmode_dflt = {'isInterceptedPowerPerDirectionForSpecularCheck': '0',
                        'subFaceBarycenterEnabled': '1',
                        'lightPropagationThreshold': '1E-7',
                        'nbRandomPointsPerInteceptionAtmosphere': '1',
                        'accelerationEngine': '0',
                        'nbSubSubcenterTurbidEmission': '40',
                        'distanceBetweenIlluminationSubCenters': '0.1',
                        'nbThreads': '4',
                        'illuminationRepartitionMode': '2',
                        'useExternalScripts': '0',
                        'nbTrianglesWithinVoxelAcceleration': '10',
                        'thermalEmissionSurfaceSubdivision': '0.01',
                        'nbSubcenterVolume': '2',
                        'albedoThreshold': '1E-7',
                        'extrapolationMethod': '0',
                        'sparseVoxelAcceleration': '1',
                        'expertMode': '0',
                        'maxNbSceneCrossing': '1000',
                        'subFaceBarycenterSubdivision': '1',
                        'surfaceBarycenterEnabled': '1'}

        maketmodule_attrib = {'MNEProducts': '0',
                              'coverRateProducts': '0',
                              'objectGeneration': '0',
                              'areaMaketProducts': '0',
                              'laiProducts': '0'}

        # base nodes
        # # simple
        etree.SubElement(self.root, "AtmosphereRadiativeTransfer",
                         {"TOAtoBOA": "0"})
        # # parentnodes
        etree.SubElement(self.root, "ExpertModeZone", expmode_dflt)

        dartinputparameters = etree.SubElement(self.root,
                                               "DartInputParameters")
        dartproduct = etree.SubElement(self.root, "DartProduct")

        # # # dartInputParameters branch
        specprops_attrib = {'bandNumber': '0', 'meanLambda': '0.56',
                            'spectralDartMode': '0', 'deltaLambda': '0.02'}

        specintervals = etree.SubElement(dartinputparameters,
                                         "SpectralIntervals")
        etree.SubElement(specintervals, "SpectralIntervalProperties",
                         specprops_attrib)

        # # dartproduct branch
        etree.SubElement(dartproduct, "maketModuleProducts",
                         maketmodule_attrib)

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


class LidarPhaseXML(DartPhaseXML):
    """subclass of DartPhaseXML to manage lidar specific structure


    """
    def __init__(self, changetracker):
        DartPhaseXML.__init__(self, changetracker)
        self.root.set("calculatorMethod", "2")
        return

    def specnodes(self):
        """create default lidar nodes


        """

        # set dictionnaries of attributes for lidar and childres nodes
        li_attrib = {'simulateImage': '0', 'simulateSolarNoise': '0'}

        pulsedur_atr = {'pulse_energy': '1', 'gaussian_pulse_cut': '3'}
        ligeom_atr = {'lsMode': '0', 'fp_fovDef': '0',
                      'sensorArea': '0.1', 'ifSetZeroDist': '0',
                      'display': '1', 'beam_width': '0.0'}
        liilluintens_atr = {'isImportedPulse': '0',
                            'gaussian_sigma_illu': '0.368',
                            'minNoPhotonPerSubCenter': '5',
                            'numberofPhotons': '100000',
                            'shortAxisSubdivitionIllum': '100'}
        liacqui_atr = {'maximumScatteringOrder': '10',
                       'LIDAR_filter': '0',
                       'calculatorMaximumRAM': '1000',
                       'DART_simulation_identical': '0',
                       'freq_recepteur_signal_LIDAR': '1'}

        # create lidar and children nodes with set attributes
        lidar = etree.Element("Lidar", li_attrib)

        pulseduration = etree.SubElement(lidar, "PulseDuration", pulsedur_atr)
        lidargeo = etree.SubElement(lidar, "LidarGeometry", ligeom_atr)
        etree.SubElement(lidar, "LidarIlluminationIntensity", liilluintens_atr)
        etree.SubElement(lidar, "LidarAcquisitionParameters", liacqui_atr)

        # set attributes and create node for pulseDuration
        sigma_atr = {'relative_power_of_pulse': '0.5',
                     'half_pulse_duration': '2'}
        etree.SubElement(pulseduration, "SigmaDefinition", sigma_atr)

        # set attributes and create children nodes for lidarGeometry
        stwave_atr = {'photon_min_LIDAR': '50', 'photon_max_LIDAR': '50'}
        sensorangles_atr = {'sensorTheta': '30', 'sensorPhi': '45'}
        centeronground_atr = {'decalageLidar_x': '20', 'decalageLidar_y': '20'}
        footprintfovrad_atr = {'rayonLidar_reception': '15',
                               'rayonLidar_emission': '12'}
        als_atr = {'sensorHeight': '10'}

        etree.SubElement(lidargeo, "StWaveHeightRange", stwave_atr)
        etree.SubElement(lidargeo, "SensorAngles", sensorangles_atr)
        etree.SubElement(lidargeo, "CenterOnGround", centeronground_atr)
        etree.SubElement(lidargeo, "FootPrintAndFOVRadiuses",
                         footprintfovrad_atr)
        etree.SubElement(lidargeo, "ALS", als_atr)

        # append whole branch to default existing node
        self.root.find("./DartInputParameters").append(lidar)

        # set attributes and create nodes for dartModuleProducts
        Dmoduleprods_atr = {'lidarProducts': '1',
                            'radiativeBudgetProducts': '0',
                            'lidarImageProducts': '0',
                            'polarizationProducts': '0',
                            'order1Products': '1',
                            'temperaturePerTrianglePerCell': '0',
                            'allIterationsProducts': '0',
                            'brfProducts': '0'}

        liprods_atr = {'convolvedWaveform': '1',
                       'photonInformations': '0',
                       'lidarImagePanelInformation': '0',
                       'groundSensorImage': '0'}

        dartmoduleproducts = etree.Element("dartModuleProducts",
                                           Dmoduleprods_atr)
        etree.SubElement(dartmoduleproducts,
                         "lidarProductsProperties", liprods_atr)
        self.root.find("./DartProduct").append(dartmoduleproducts)

        return


class FluxPhaseXML(DartPhaseXML):
    """
    """
    def __init__(self, changetracker):
        DartPhaseXML.__init__(self, changetracker)
        self.root.set("calculatorMethod", "0")

        return

    def specnodes(self):
        """Create default fluxnodes.

        """
        etree.SubElement(self.root, "SensorImageSimulation",
                         {'importMultipleSensors': '0'})

        # Adding nodes under DartInputParameters
        dartinparams = self.root.find("./DartInputParameters")

        # direct nodes dartinput from dart input parameters
        imagesideillu_attrib = {'disableSolarIllumination': '0',
                                'sideIlluminationEnabled': '0',
                                'disableThermalEmission': '0'}
        nodeillu_attrib = {'illuminationMode': '0', 'irradianceMode': '0'}
        nodeflux_attrib = {'numberOfIteration': '5',
                           'gaussSiedelAcceleratingTechnique': '0'}
        # simple nodes
        etree.SubElement(dartinparams, "nodefluxtracking", nodeflux_attrib)
        etree.SubElement(dartinparams, "ImageSideIllumination",
                         imagesideillu_attrib)
        # branches
        spectraldomain = etree.Element("SpectralDomainTir",
                                       {"temperatureMode": "0"})
        nodeillumode = etree.Element("nodeIlluminationMode", nodeillu_attrib)

        # spectral domain branch
        skyl_attrib = {'distanceBetweenIlluminationSubCenters': '0.1',
                       'histogramThreshold': '5.0',
                       'SKYLForTemperatureAssignation': '0.0'}

        etree.SubElement(spectraldomain, "skylTemperature", skyl_attrib)

        # nodeIllumination branch
        # # irrandiancedatabase sub-branch
        irraddatanode_atr = {'irradianceTable': 'TOASolar_THKUR',
                             'irradianceColumn': 'irradiance',
                             'weightAtmosphereParameters': '1',
                             'databaseName': 'Solar_constant.db',
                             'weightReflectanceParameters': '1'}
        irraddatanode = etree.SubElement(nodeillumode,
                                         "irradianceDatabaseNode",
                                         irraddatanode_atr)

        weightingparam_atr = {'sceneAverageTemperatureForPonderation': '300'}
        etree.SubElement(irraddatanode, "WeightingParameters",
                         weightingparam_atr)

        # # spectralirradiance subbranch
        spectralirrad = etree.SubElement(nodeillumode, "SpectralIrradiance")
        commonparams_attrib = {'irraDef': '0', 'commonIrradianceCheckBox': '1',
                               'commonSkylCheckBox': '1'}
        spectralirrad_attrib = {'bandNumber': '0', 'irradiance': '0',
                                'Skyl': '0'}
        etree.SubElement(spectralirrad, "CommonParameters",
                         commonparams_attrib)
        etree.SubElement(spectralirrad, "SpectralIrrandianceValue",
                         spectralirrad_attrib)

        # Adding nodes under DartProduct
        dartprod = self.root.find("./DartProduct")

        dartmoduleprod_attrib = {'lidarProducts': '0',
                                 'radiativeBudgetProducts': '0',
                                 'lidarImageProducts': '0',
                                 'polarizationProducts': '0',
                                 'order1Products': '0',
                                 'temperaturePerTrianglePerCell': '0',
                                 'allIterationsProducts': '0',
                                 'brfProducts': '1'}
        dartmodprod = etree.SubElement(dartprod, "dartModuleProducts",
                                       dartmoduleprod_attrib)

        brfprod_attrib = {'maximalThetaImages': '25.0', 'projection': '0',
                          'sensorOversampling': '1', 'nb_scene': '1',
                          'image': '1', 'extrapolation': '1',
                          'sensorPlaneprojection': '1',
                          'centralizedBrfProduct': '1',
                          'luminanceProducts': '0',
                          'transmittanceImages': '0', 'brfProduct': '1',
                          'horizontalOversampling': '1'}
        brfprod = etree.SubElement(dartmodprod, "BrfProductsProperties",
                                   brfprod_attrib)

        emzetalement = etree.SubElement(brfprod, "ExpertModeZone_Etalement",
                                        {"etalement": "2"})
        etree.SubElement(emzetalement, "ExpertModeZone_Projection",
                         {'keepNonProjectedImage': '0'})
        etree.SubElement(emzetalement, "ExpertModeZone_PerTypeProduct",
                         {"generatePerTypeProduct": '0'})

        return


# to be expanded.....
# ZONE DE TESTS
"""outpath = "/media/mtd/stock/boulot_sur_dart/temp/"

write_phase("flux", [], outpath)"""
