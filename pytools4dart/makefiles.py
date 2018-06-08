#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 14:15:03 2018

@author: mtd

set of functions to be used in order to launch a simulation : 
    -write xml files
    -feed them to DART

"""
try:
    import xml.etree.cElementTree as etree
    print ("imported cetree")
except ImportError:
    print ("oups!, importing pytetree")
    import xml.etree.ElementTree as etree


def write_XMLfiles(simulation):
    """write all xml files
    
    """
    
    write_phase()
    write_directions()
    write_coeff_diff()
    return


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


class dartPhasexml(object):
    """object for the editing and expoting to xml of phase related parameters
    
    """
    
    def __init__(self,changetracker):
        root = etree.Element("Phase")
        self.root=root
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
        art=etree.SubElement(self.root,"AtmosphereRadiativeTransfer")
        art.set("TOAtoBOA","0")
        
        
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
        
        expertmode=etree.SubElement(self.root,"ExpertModeZone")
        for key in expertmode_default.keys():
            expertmode.set(key,expertmode_default[key])
        
        dartinputparameters=etree.SubElement(self.root,"DartinputParameters")
        
        spectralintervals=etree.SubElement(dartinputparameters,"SpectralIntervals")
        
        specprops_default={'bandNumber': '0',
                           'meanLambda': '0.56',
                           'spectralDartMode': '0',
                           'deltaLambda': '0.02'}
        spectralintprops=etree.SubElement(spectralintervals,"SpectralIntervalProperties")
        for key in specprops_default.keys():
            spectralintprops.set(key,expertmode_default[key])
        
        
        temp_atmosphere=etree.SubElement(dartinputparameters,"SpectralIntervalProperties")
        temp_atmosphere.set("atmosphereApparentTemperature", "260.0")
        
        
        dartproduct=etree.SubElement(self.root,"DartProduct")
        
        maketmodule_default={'MNEProducts': '0',
                             'coverRateProducts': '0',
                             'objectGeneration': '0',
                             'areaMaketProducts': '0',
                             'laiProducts': '0'}
        maketmodule=etree.SubElement(dartproduct)
        for key in maketmodule_default:
            maketmodule.set(key,maketmodule_default[key])
            
            
        return
               
    


class lidarPhasexml(dartPhasexml):
    """
    """
    def __init__(self):
        self.root.set("calculatorMethod","2")
        return
    
    def lidarnodes(self):
        
        
        
        return

class fluxPhasexml(dartPhasexml):
    """
    """
    def __init__(self):
        self.root.set("calculatorMethod","0")
        
        return
    def fluxnodes(self):
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