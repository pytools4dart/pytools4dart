#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 14:15:03 2018

@author: mtd

This module contains the class "simulation".
This class allows for the storing of all of data relevant to the simulation.
It can be either created by one of the functions of the UFPD (UserFriendlyPytoolsforDart),
or interactively in code lines.

The purpose of this module is not to produce the Dart xml input files.
It acts as a buffer between the "raw" parameter related information, and the 
xml editing functions.
"""

class simulation(object):
    """Simulation object allowing for the storing and editing of all the parameters
    
    
    
    """
    
    
    def __init__(self):
        """initialisation
        
        """
        self.changetracker=[]
        
    def addparameterX(param,self):
        """interactively add a parameter
        
        """
        self.param=param
        return
    
    def listmodifications():
        """returns record of modifications to simulation
        
        """
        return
    
    def launch(self):
        """launch the simulation with set parameters
        
        """
    
        return
###################################zone de tests
