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
from shapely.geometry import box, Polygon


class voxel(object):
    """

    description du voxel et intersection avec la couronne correspondante

    """

    def __init__(self):
        self.inputfile = ""
        self.header = []
        self.data = []
        self.grid = []

    @classmethod

    def from_vox(cls, filename):   # informations contenues dans la classe voxel (header et data)
        newVoxel = cls()
        newVoxel.inputfile = filename
        newVoxel.read_vox_header() # description de la scène voxelisées
        newVoxel.read_vox_data()  # description de chaque voxel
        newVoxel.create_grid()
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

    def create_grid(self):
        """
         Creates a geopandas dataframe with one grid cell in each row.
        """
        polygons = []
        for i in range(int(self.header["split"][0])):         # ici chaque voxel est transformée en grille (coordonnées réelles de la scène
            for j in range(int(self.header["split"][1])):
                polygons.append(box(i * self.header["res"][0] + self.header["min_corner"][0],  # les corners et la résolution (res) dans self.header
                           j * self.header["res"][0] + self.header["min_corner"][1],
                           (i + 1) * self.header["res"][0] + self.header["min_corner"][0],
                           (j + 1) * self.header["res"][0] + self.header["min_corner"][1]))
        self.grid = gpd.GeoDataFrame({'geometry':polygons})
        
        
    def intersect(self, shapefile, inplace=False):
        """
        Intersection of voxel grid with shapefile.
        :param shapefile: path to a shapefile
        :param inplace: if True adds interecting ID and attributes to data otherwise returns dataframe.
        :return: see inplace.
        """
        polygons = gpd.read_file(shapefile) # lecture du shapefile à partir de geopandas
        grid_spatial_index = self.grid.sindex
        rows = self.header["split"][0]
        intersectList=[]
        for polygon in polygons.itertuples():
            # Select cells matching with polygon
            possible_matches_index = list(grid_spatial_index.intersection(polygon.geometry.bounds))
            possible_matches = self.grid.iloc[possible_matches_index]
            precise_matches = possible_matches[possible_matches.intersects(polygon.geometry)]
            areas = map(lambda r: r.intersection(polygon.geometry).area, precise_matches['geometry'])
        
            if len(areas)>0:
                icell = precise_matches.index
                irow = map(lambda x: x % rows, icell)
                icol = map(lambda x: int(x/rows), icell)
                intersectList.append(
                        pd.DataFrame({'cell': icell, 'j':irow, 
                                      'i':icol, 'ID': polygon.Index, 'intersected_area':areas}))
        intersection=pd.concat(intersectList, axis=0)
        
        # keep polygon with max area
        intersect_max=intersection.sort_values('intersected_area', ascending=False).drop_duplicates(['cell'])
        intersectDF = pd.merge(intersect_max,
                       polygons, left_on="ID", right_index=True, how='left').drop("geometry", axis=1)
        if inplace:
            self.data=pd.merge(self.data, intersectDF, on=("i", "j"))
        else:
            return(pd.merge(self.data, intersectDF, on=("i", "j")))

    ### fastest solution goes with direct string
    def to_plot_xml(self, filename, default_LOPname="leaf_deciduous", verbose=True):
        """
        write voxel object to DART file. The column named 'LOPname'is used to set optical properties.
        :param filename: output xml file
        :param default_LOPname: default Optical Property Name to be set if no 'LOPname' column or LOPname value is NaN.
        """
        
        header = """<?xml version="1.0" encoding="utf-8"?>
<DartFile build="v1008" version="5.7.0">
    <Plots addExtraPlotsTextFile="0" isVegetation="0">
        <ImportationFichierRaster/>"""
        plot_node_template = """
        <Plot form="0" hidden="0" isDisplayed="1" repeatOnBorder="1" type="1">
            <Polygon2D>
                <Point2D x="{0}" y="{1}"/>
                <Point2D x="{2}" y="{3}"/>
                <Point2D x="{4}" y="{5}"/>
                <Point2D x="{6}" y="{7}"/>
            </Polygon2D>
            <PlotVegetationProperties densityDefinition="0" trianglePlotRepresentation="0" verticalFillMode="0">
                <VegetationGeometry baseheight="{8}" height="{9}" stDev="0"/>
                <LAIVegetation LAI="{10}"/>
                <VegetationOpticalPropertyLink ident="{11}" indexFctPhase="0"/>
                <GroundThermalPropertyLink idTemperature="ThermalFunction290_310" indexTemperature="0"/>
            </PlotVegetationProperties>
        </Plot>"""
        
        tail = """
    </Plots>
</DartFile>"""
        
        data = self.data.copy()
        if "LOPname" not in self.data.columns:
            data["LOPname"]=default_LOPname
        if data.LOPname.isna().any():  # voxels dont on dispose pas de propriétés optiques
            data.loc[pd.isna(self.data["LOPname"]), "LOPname"] = default_LOPname
        
        
        res = self.header["res"][0]

        plotlist=[]
        for row in data.itertuples(): # intégrer tous les voxels dans le fichier plot.xml

            i= row.i  # x du voxel
            j= row.j  # y du voxel
            k= row.k  # z du voxel
            LAI = -row.PadBVTotal # LAI du voxel (PadBTotal en negatif)
        
             # limite de chaque voxel
            corners = [i * res, j * res,
                       (i + 1) * res, j * res,
                       (i + 1) * res, (j + 1) * res,
                       i * res, (j + 1) * res]
            
            height = res
            baseheight = k * res # hauteur du voxel
            optPropName = row.LOPname
            # print("%d %d %d %f %s" % (i, j, k, LAI, optPropName))
        
            plotlist.append(plot_node_template.format(corners[0], corners[1],
                                                      corners[2], corners[3],
                                                      corners[4], corners[5],
                                                      corners[6], corners[7],
                                                      baseheight, height,
                                                      LAI, optPropName))

        open(filename, 'wb').write(header + ''.join(plotlist) + tail)
        if verbose:
            print("Plots saved in:\n\t%s" % filename)

        


# 5 sec. on 500k plot list
# <?xml version="1.0" encoding="utf-8"?>

