# coding: utf-8

########################################################################################################################
## Ce module a pour objectif de definir des fonctions qui permettent de lire le fichier .vox et .shp et de les inter- ##
## secter                                                                                                             ##
########################################################################################################################

import os
import csv
import pandas as pd
import pprint
import re
import numpy as np
import geopandas as gpd
from shapely.geometry import box


class voxel(object):
    """

    description du voxel et intersection avec la couronne correspondante

    """

    def __init__(self):
        self.inputfile = ""
        self.header = []
        self.data = []

    @classmethod

    def from_vox(cls, filename):   # informations contenues dans la classe voxel (header et data)
        newVoxel = cls()
        newVoxel.inputfile = filename
        newVoxel.read_vox_header() # description de la scène voxelisées
        newVoxel.read_vox_data()  # description de chaque voxel
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

        self.header = header  # caractéristique de la scène (corners)

    def read_vox_data(self, skiprows=1):
        """
        read data of .vox file from AMAPVox
        :param skiprows:
        :return:
        """

        data = pd.read_csv(self.inputfile, sep=" ", comment="#", skiprows=skiprows)
        self.data = data  # lecture de chaque voxel

    def intersect(self, shapefile):

        """
        intersection of voxel with crowns shapefile
        :param shapefile:
        :return:
        """
        crowns = gpd.read_file(shapefile) # lecture du shapefile à partir de geopandas
        intersectList=[]
        for i in range(int(self.header["split"][0])):         # ici chaque voxel est transformée en grille (coordonnées réelles de la scène
            for j in range(int(self.header["split"][1])):
                cell = box(i * self.header["res"][0] + self.header["min_corner"][0],  # les corners et la résolution (res) dans self.header
                           j * self.header["res"][0] + self.header["min_corner"][1],
                           (i + 1) * self.header["res"][0] + self.header["min_corner"][0],
                           (j + 1) * self.header["res"][0] + self.header["min_corner"][1])
                try:
                    areas = map(lambda r: r.intersection(cell).area, crowns['geometry'])
                except:
                    print "Area not computable for i=%d, j=%d" % (i,j)
                    for p in range(len(crowns['geometry'])):
                        try:
                            crowns['geometry'][p].intersection(cell).area  # intersection de chaque voxel avec le shp de couronnes délinéées
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


