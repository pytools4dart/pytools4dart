#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 14:15:03 2018

@author: mtd

Objects and functions necessary to write the phase xml file. 

"""
try:
    import xml.etree.cElementTree as etree
    print ("imported cetree")
except ImportError:
    print ("oups!, importing pytetree")
    import xml.etree.ElementTree as etree


def write_phase(simutype,changetracker,outpath):
    """write phase xml fil
    
    proceed in the following manner : 
        -checks and gets relevant variables in Simu
        -passes them down to node objects
        -constructs all nodes
        -write xml
        
    """
    if simutype=="lidar":
        phase = lidarPhasexml(changetracker)
    elif simutype=="flux":
        phase = fluxPhasexml(changetracker)
    else :
        print "what the ?"
    phase.basenodes()
    phase.adoptchanges()
    tree=etree.ElementTree(phase.root)
    tree.write(outpath+"phase.xml")
    return


class dartphasexml(object):
    """object for the editing and expoting to xml of phase related parameters
    
    """
    
    def __init__(self):
        self.root=etree.Element("Phase")
        self.tree=etree.ElementTree(self.root)
        return   
    def adoptchanges(changetracker,self):
        if "phase" in changetracker[0]:
            self.changes= changetracker[1]["phase"]
            """
            here goes the magic where we change some nodes with some parameters!
            it would maybe be something like this :
               - for some values, just append them somewhere
               - for the others, find them in the tree and modify them (tricky bit)
            """
            
            return
        else:
            return
        
    
    def basenodes(self):
        """creates all nodes and properties common to default simulations
        
        """
        
        
        expertmode_default={'isInterceptedPowerPerDirectionForSpecularCheck': '0',
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
        
        specprops_attrib={'bandNumber': '0','meanLambda': '0.56',
                      'spectralDartMode': '0','deltaLambda': '0.02'}
    
        maketmodule_attrib={'MNEProducts': '0',
                             'coverRateProducts': '0',
                             'objectGeneration': '0',
                             'areaMaketProducts': '0',
                             'laiProducts': '0'}
        
        
        #base nodes
        ##simple
        etree.SubElement(self.root,"ExpertModeZone",attrib=expertmode_default)        
        etree.SubElement(self.root,"AtmosphereRadiativeTransfer",attrib={"TOAtoBOA":"0"})
        ##parentnodes
        dartinputparameters=etree.SubElement(self.root,"DartinputParameters")        
        dartproduct=etree.SubElement(self.root,"DartProduct")
        
        ###dartInputParameters branch
        etree.SubElement(dartinputparameters,"SpectralIntervalProperties",
                                 attrib={"atmosphereApparentTemperature": "260.0"})        
        spectralintervals=etree.SubElement(dartinputparameters,"SpectralIntervals")
        etree.SubElement(spectralintervals,"SpectralIntervalProperties",attrib=specprops_attrib)
        
        ##dartproduct branch
        etree.SubElement(dartproduct,attrib=maketmodule_attrib)

            
        return
               
    


class lidarPhasexml(dartphasexml):
    """
    """
    def __init__(self):
        dartphasexml.__init__(self)
        self.root.set("calculatorMethod","2")
        return
    
    def lidarnodes(self):
        """create default lidar nodes
        
        
        """
        
        #set dictionnaries of attributes for lidar and childres nodes        
        lidar_attrib={'simulateImage': '0', 'simulateSolarNoise': '0'}
        
        pulseduration_attrib={'pulse_energy': '1', 'gaussian_pulse_cut': '3'}
        lidargeometry_attrib={'lsMode': '0', 'fp_fovDef': '0',
                              'sensorArea': '0.1', 'ifSetZeroDist': '0',
                              'display': '1', 'beam_width': '0.0'}
        lidarilluintens_attrib={'isImportedPulse': '0',
                                'gaussian_sigma_illu': '0.368',
                                'minNoPhotonPerSubCenter': '5',
                                'numberofPhotons': '100000',
                                'shortAxisSubdivitionIllum': '100'}        
        lidaracquisition_attrib={'maximumScatteringOrder': '10',
                                 'LIDAR_filter': '0',
                                 'calculatorMaximumRAM': '1000',
                                 'DART_simulation_identical': '0',
                                 'freq_recepteur_signal_LIDAR': '1'}        
        
        #create lidar and children nodes with set attributes
        lidar=etree.Element("Lidar", attrib=lidar_attrib)
        
        pulseduration=etree.SubElement(lidar,"PulseDuration", attrib=pulseduration_attrib)
        lidargeo=etree.SubElement(lidar,"LidarGeometry", attrib= lidargeometry_attrib)
        etree.SubElement(lidar,"LidarIlluminationIntensity", attrib=lidarilluintens_attrib)
        etree.SubElement(lidar,"LidarAcquisitionParameters", attrib=lidaracquisition_attrib)
        
        #set attributes and create node for pulseDuration
        sigma_attrib={'relative_power_of_pulse': '0.5',
                      'half_pulse_duration': '2'}
        etree.SubElement(pulseduration,"SigmaDefinition",attrib=sigma_attrib)
        
        
        #set attributes and create children nodes for lidarGeometry
        stwave_attrib={'photon_min_LIDAR': '50', 'photon_max_LIDAR': '50'}
        sensorangles_attrib={'sensorTheta': '30', 'sensorPhi': '45'}
        centeronground_attrib={'decalageLidar_x': '20', 'decalageLidar_y': '20'}
        footprintfovrad_attrib={'rayonLidar_reception': '15', 'rayonLidar_emission': '12'}
        als_attrib={'sensorHeight': '10'}
         
        etree.SubElement(lidargeo,"StWaveHeightRange",attrib=stwave_attrib)
        etree.SubElement(lidargeo,"SensorAngles", attrib=sensorangles_attrib)
        etree.SubElement(lidargeo,"CenterOnGround", attrib=centeronground_attrib)
        etree.SubElement(lidargeo,"FootPrintAndFOVRadiuses",footprintfovrad_attrib)
        etree.SubElement(lidargeo,"ALS",als_attrib)


        #append whole branch to default existing node         
        self.root.find("./DartInputParameters").append(lidar)
        
        #set attributes and create node for pulseDuration
        DmoduleProducts_attrib={'lidarProducts': '1',
                                   'radiativeBudgetProducts': '0',
                                   'lidarImageProducts': '0',
                                   'polarizationProducts': '0',
                                   'order1Products': '1',
                                   'temperaturePerTrianglePerCell': '0',
                                   'allIterationsProducts': '0',
                                   'brfProducts': '0'}
        
        lidarproductsprops_attrib={'convolvedWaveform': '1',
                                    'photonInformations': '0',
                                    'lidarImagePanelInformation': '0',
                                    'groundSensorImage': '0'}
        
        dartmoduleproducts=etree.Element("dartModuleProducts",attrib=DmoduleProducts_attrib)
        etree.SubElement(dartmoduleproducts,"lidarProductsProperties",attrib=lidarproductsprops_attrib)
        self.root.find("./DartProduct").append(dartmoduleproducts)
        
        return

class fluxPhasexml(dartphasexml):
    """
    """
    def __init__(self):
        dartphasexml.__init__(self)
        self.root.set("calculatorMethod","0")
        
        return
    def fluxnodes(self):
        
        dartinparams=self.root.find("./DartInputparameters")
        
        #direct nodes dartinput from dart input parameters        
        imagesideillu_attrib={'disableSolarIllumination': '0',
                              'sideIlluminationEnabled': '0',
                              'disableThermalEmission': '0'}
        nodeillu_attrib={'illuminationMode': '0', 'irradianceMode': '0'}
        nodeflux_attrib={'numberOfIteration': '5',
                         'gaussSiedelAcceleratingTechnique': '0'}
        #simple nodes
        etree.SubElement(dartinparams,"nodefluxtracking", nodeflux_attrib)
        etree.SubElement(dartinparams,"ImageSideIllumination",imagesideillu_attrib)
        #branches
        spectraldomain=etree.Element("SpectralDomainTir",attrib={"temperatureMode":"0"})
        nodeillumode=etree.Element("nodeIlluminationMode",attrib=nodeillu_attrib)
       
        #spectral domain branch
        skyl_attrib={'distanceBetweenIlluminationSubCenters': '0.1',
                     'histogramThreshold': '5.0',
                     'SKYLForTemperatureAssignation': '0.0'}
        
        etree.SubElement(spectraldomain,"skylTemperature",attrib=skyl_attrib)
        
        #nodeIllumination branch  
        ##irrandiancedatabase sub-branch
        irraddatanode_attrib={'irradianceTable': 'TOASolar_THKUR',
                              'irradianceColumn': 'irradiance',
                              'weightAtmosphereParameters': '1',
                              'databaseName': 'Solar_constant.db',
                              'weightReflectanceParameters': '1'}
        irraddatanode=etree.SubElement(nodeillumode,"irradianceDatabaseNode",
                                       attrib=irraddatanode_attrib)
        
        weightingparam_attrib={'sceneAverageTemperatureForPonderation': '300'}
        etree.SubElement(irraddatanode,"WeightingParameters",weightingparam_attrib)
        
        ##spectralirradiance subbranch
        spectralirrad=etree.SubElement(nodeillumode,"SpectralIrradiance")
        commonparams_attrib={'irraDef': '0', 'commonIrradianceCheckBox': '1',
                             'commonSkylCheckBox': '1'}
        spectralirrad_attrib={'bandNumber': '0', 'irradiance': '0',
                              'Skyl': '0'}
        etree.SubElement(spectralirrad,"CommonParameters",attrib=commonparams_attrib)
        etree.SubElement(spectralirrad,"SpectralIrrandianceValue",
                         attrib=spectralirrad_attrib)

        return
        
def write_directions():
    """
    """
    return
def write_coeff_diff():
    """
    """
    return



class opticalproperty(object):
    """
    object that helps getting user defined parameter in DART-xml file.
    """
    def __init__(self):
        return
    
#to be expended.....