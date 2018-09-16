#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 13:28:15 2018

@author: Dav Ebengo, Florian de Boissieu
"""

# File.vox is text file containing detail on voxelized scene

# 1. Extract comment of file.vox to vox.hdr

# Set work directory

import pandas as pd


# path="/media/DATA/DATA/SIMULATION_P1_P9/MaquettesALS_INRAP1P9_2016"
# os.chdir(path)

# Load comment line and write into new voxel.hdr file

class voxel(object):
    """
    description
    """

    def __init__(self):
        self.inputfile = ""
        self.header = []
        self.data = []

    @classmethod
    def from_vox(cls, filename):
        newVoxel = cls()
        newVoxel.inputfile = filename
        newVoxel.read_vox_header()
        newVoxel.read_vox_data()
        return (newVoxel)

    def read_vox_header(self, skiprows=1):
        """
        read header of .vox file from AMAPVox.
        :param skiprows:
        :return:
        """
        tmp=[]
        tmp2=[]
        with open(self.inputfile, "r") as file:
            i=0
            for line in file:
                i += 1
                if i > skiprows:
                    if line.startswith("#"):
                        tmp.append(line[:].strip())
                    else:
                        break

        for headerline in tmp:
            tmp2.extend(headerline.split("#")[1:])

        header = dict(map(lambda s: map(lambda s: s.strip(), s.split(':')), tmp2))

        for col in header.keys():
            if(col in ["max_corner", "min_corner", "split", "res"]):
                header[col] = map(float, header[col].split(" "))

        self.header = header

    def read_vox_data(self, skiprows=1):
        """

        :param skiprows:
        :return:
        """

        data = pd.read_csv(self.inputfile, sep=" ", comment="#", skiprows=skiprows)
        self.data = data

