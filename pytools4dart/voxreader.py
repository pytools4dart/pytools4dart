#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 12 13:28:15 2018

@author: Dav Ebengo, Florian de Boissieu
"""

# File.vox is text file containing detail on voxelized scene

# 1. Extract comment of file.vox to vox.hdr

# Set work directory

import os
import csv
import pandas as pd
import pprint
import re
import numpy as np
import geopandas as gpd
from shapely.geometry import box

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

    def intersect(self, shapefile):
        crowns = gpd.read_file(shapefile)
        intersectList=[]
        for i in range(int(self.header["split"][0])):
            for j in range(int(self.header["split"][1])):
                cell = box(i * self.header["res"][0] + self.header["min_corner"][0],
                           j * self.header["res"][0] + self.header["min_corner"][1],
                           (i + 1) * self.header["res"][0] + self.header["min_corner"][0],
                           (j + 1) * self.header["res"][0] + self.header["min_corner"][1])
                try:
                    areas = map(lambda r: r.intersection(cell).area, crowns['geometry'])
                except:
                    print "Area not computable for i=%d, j=%d" % (i,j)
                    for p in range(len(crowns['geometry'])):
                        try:
                            crowns['geometry'][p].intersection(cell).area
                        except:
                            print "Polygon involved : %d" % p
                    areas=0


                area = np.max(areas)
                if area > 0:
                    ID = np.argmax(areas)
                    intersectList.append((i, j, ID, area))
                else:
                    ID= np.nan
                    intersectList.append((i, j, ID, area))

        intersectDF = pd.merge(pd.DataFrame(intersectList, columns=('i', 'j', 'ID', 'intersected_area')),
                       crowns, left_on="ID", right_index=True, how='left').drop("geometry", axis=1)
        self.data=pd.merge(self.data, intersectDF, on=("i", "j"))
