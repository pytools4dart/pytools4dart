#  -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Eric Chraibi <eric.chraibi@irstea.fr>, Florian de Boissieu <florian.deboissieu@irstea.fr>
# https://gitlab.irstea.fr/florian.deboissieu/pytools4dart
#
#
# This file is part of the pytools4dart package.
#
# pytools4dart is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
#
# ===============================================================================
"""
Objects and functions necessary to write the plots xml file.
It is important to note the resulting xml file is written over a single line.
"""
try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree
from dartxml import DartXml

from pytools4dart.settings import getsimupath, getdartdir
from os.path import join as pjoin
import pandas as pd
import numpy as np


def write_plots(changetracker, simu_name):
    """write phase xml file

    proceed in the following manner:
        -instantiate  dartplots object
        -set default nodes
        -add more nodes depending on changetracker/vox
        -output file to xml

    Will tend to be modified for adding support of different ways to add nodes
    (i.e. panda dataframes).

    """
    plots = DartPlotsXML(changetracker, simu_name)
    plots.basenodes()
    plots.adoptchanges()

    plots.writexml(simu_name, 'plots.xml')
    return


class DartPlotsXML(DartXml):
    """object for the editing and exporting to xml of phase related parameters

    After instantiation, a default tree of nodes is created.
    Changes based on the passed "changetracker" variable have then to
    take place in order to upgrade the tree.
    All the tag names of tree nodes are supposed to be IDENTICAL to the ones
    produces by DART. The variable names are sometimes shortened.

    TODO : In order to properly link a plot to an optical property, both the
    ident and an index number have to be passed.

    """
    PLOT_DEFAULT_ATR = {"form": "0", "hidden": "0", "isDisplayed": "1",
                        "repeatedOnBorder": "1", "type": "1"}

    def __init__(self, changetracker, simu_name):
        """

        Here is initialized the index for the optical properties.
        The dictionary referencing allows for easier calling inside the
        'add plot' method.
        """

        if not simu_name:
            raise ValueError("Simulation name is 'None'.")
        self.changes = changetracker
        self.simu_name = simu_name
        self.dartdir = getdartdir()
        self.root = None
        self.plotsfile = pjoin(getsimupath(self.simu_name, self.dartdir), '_'.join([self.simu_name, 'plots.txt']))

        # self.basenodes()

        # self.tree = etree.ElementTree(self.root)


    def basenodes(self):
        """creates all nodes and properties common to default simulations

        """

        # base nodes
        # # simple
        self.root = etree.Element("Plots", {'addExtraPlotsTextFile': '0',
                                            'isVegetation': '0'})
        etree.SubElement(self.root, "ImportationFichierRaster")

    def adoptchanges(self):

        if 'plots' in self.changes[0]:
            self.root.set('addExtraPlotsTextFile', '1')
            etree.SubElement(self.root, 'ExtraPlotsTextFileDefinition', {'extraPlotsFileName': self.plotsfile})

            self.write_plots_txt()


            # self.indexopts = changetracker[1]['indexopts']
            # self.changes = changetracker[1]['plots']
            """
            try:
                self.opts = changetracker[1]['coeff_diff']
                index = 0
                self.index_lamb = {}
                for lamb in self.opts['lambertians']:
                    self.index_lamb[lamb[0]] = index
                    index += 1
                index = 0
                self.index_veg = {}
                for veg in self.opts['vegetations']:
                    self.index_veg[veg[0]] = index
                    index += 1
            except KeyError:
            """
            # print "Adding plot(s) to simulation."
            # return
        # else:
        #     # print "No plot in simulation."
        # return

    # def adoptchanges(self):
    #     """method to update xml tree based on user-defined parameters
    #
    #     here goes the magic where we change some nodes based on parameters
    #     it would maybe be something like this:
    #        - for some values, just append them somewhere
    #        - for the others, find them in the tree and modify them (tricky bit)
    #
    #     Complete path to node to be modified will have to be explicitly written
    #     in this way: './Phase/DartInputParameters/SpectralDomainTir'
    #     for the query to work.
    #
    #     Work In Progress : Relies on changetracker architecture
    #     for now : architecture relies on dictionnaries containing dictionnaries
    #     plot is a dictionary, containing certain keywords.
    #     Those dictionnaries are initialized in the addplot method of simulation
    #
    #
    #     """
    #     if self.changes is not None:
    #         self.plotsfrompanda(self.changes)
    #     return
    #

    def write_plots_txt(self):
        indexopt = self.changes[1]['indexopts']
        plotsdf = self.changes[1]['plots']

        # convert
        simu_plots_coords = ['x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 'y4', 'zmin', 'dz']
        dart_plots_coords = 'PT_1_X PT_1_Y PT_2_X PT_2_Y PT_3_X PT_3_Y PT_4_X PT_4_Y PLT_BTM_HEI PLT_HEI_MEA'.split()
        simu2dart_plots_coords = {simu_plots_coords[i]: dart_plots_coords[i] for i in range(len(simu_plots_coords))}

        outdf = plotsdf[simu_plots_coords].rename(index=str, columns=simu2dart_plots_coords)
        outdf['PLT_OPT_NUMB'] = [indexopt['vegetations'][i] for i in plotsdf.op_name.tolist()]
        outdf['PLT_TYPE']=1
        outdf['VEG_DENSITY_DEF'] = plotsdf.densitydef.apply(lambda x: 0 if x.lower()=='LAI' else 1).values

        if all(outdf.VEG_DENSITY_DEF):
            outdf['VEG_UL'] = plotsdf.density.values
        else:
            outdf['VEG_LAI'] = plotsdf.density.values

        outdf.to_csv(self.plotsfile, header=True, index=False, sep=' ')



    # def plotsfrompanda(self, data, columns={
    #     'corners':'corners', 'baseheight':'baseheight', 'height':'height',
    #     'density':'density', 'optprop':'optprop', 'densitydef':'densitydef'}):
    #     """adds plots in elementree from a pandaDataFrame
    #
    #     TODO: feed whole row directly to addplot without sloppy referencing?
    #     """
    #     for index, row in data.itertuples():
    #         corners = row.corners
    #         baseheight = row.baseheight
    #         height = row.height
    #         density = row.density
    #         optprop = row.optprop
    #         densitydef = row.densitydef
    #         self.addplot(*row)
    #     return
    #
    # def addplot(self, corners, baseheight, height, density, optprop, densitydef):
    #     """Adds a plot based on a few basic parameters
    #
    #     This method could evolve to receive a variable number of parameters.
    #     For now it is used mainly as the way to integrate voxels from a .vox
    #     file. Parameters are cast to strings in order to ensure compatibility
    #     with Element Tree.
    #     """
    #     if densitydef == 'lai' or 'LAI':
    #         densdef = '0'
    #     if densitydef == 'ul' or 'UL':
    #         densdef = '1'
    #     # appends new plot to plots
    #     plot = etree.SubElement(self.root, "Plot", self.PLOT_DEFAULT_ATR)
    #
    #     # Polygon 2D Branch
    #     polygon_plot1 = etree.SubElement(plot, "Polygon2D", {"mode": "0"})
    #
    #     # # with its four defining points
    #     etree.SubElement(polygon_plot1, "Point2D",
    #                      {"x": str(corners[0][0]), "y": str((corners[0][1]))})
    #     etree.SubElement(polygon_plot1, "Point2D",
    #                      {"x": str(corners[1][0]), "y": str((corners[1][1]))})
    #     etree.SubElement(polygon_plot1, "Point2D",
    #                      {"x": str((corners[2][0])), "y": str(corners[2][1])})
    #     etree.SubElement(polygon_plot1, "Point2D",
    #                      {"x": str(corners[3][0]), "y": str(corners[3][1])})
    #
    #     # plot vegetation properties branch
    #     vegprops_atr = {"densityDefinition": densdef,
    #                     "trianglePlotRepresentation": "0",
    #                     "verticalFillMode": "0"}
    #     vegprops = etree.SubElement(plot, "PlotVegetationProperties",
    #                                 vegprops_atr)
    #
    #     veggeom = {"baseheight": (str(baseheight)), "height": str(height),
    #                "stDev": "0.0"}
    #     # here optical property passed as argument to method
    #     # TODO : better way of referencing indices....!!!
    #
    #     if optprop in self.indexopts['lambertians']:
    #         indexphase = self.indexopts['lambertians'][optprop]
    #     elif optprop in self.indexopts['vegetations']:
    #         indexphase = self.indexopts['vegetations'][optprop]
    #     else:
    #         print "Unrecognized optical property for plot"
    #         return
    #
    #     vegoptlink = {"ident": str(optprop), "indexFctPhase": str(indexphase)}
    #     grdthermalprop = {"idTemperature": "ThermalFunction290_310",
    #                       "indexTemperature": "0"}
    #
    #     etree.SubElement(vegprops, "VegetationGeometry", veggeom)
    #     etree.SubElement(vegprops, "VegetationOpticalPropertyLink", vegoptlink)
    #     etree.SubElement(vegprops, "GroundThermalPropertyLink", grdthermalprop)
    #
    #     # here density parameter added in LAI or ul
    #     if densitydef in ('lai', 'LAI'):
    #         etree.SubElement(vegprops, "LAIVegetation", {"LAI": str(density)})
    #     elif densitydef in ('ul', 'UL'):
    #         etree.SubElement(vegprops, "UFVegetation", {"UF": str(density)})
    #     else:
    #         # TODO : put a warning when not recognised
    #         print "Not recognised density definition : {}".format(densitydef)
    #         etree.SubElement(vegprops, "UFVegetation", {"UF": str(density)})
    #     return
    #
    #


    # def writexml(self, outpath):
    #     """ Writes the built tree to the specified path
    #
    #     Also includes the version and build of DART as the root element.
    #     This part could(should?) be modified.
    #     """
    #     root = etree.Element('DartFile',
    #                          {'version': '5.7.1', 'build': 'v1061'})
    #     root.append(self.root)
    #     tree = etree.ElementTree(root)
    #     tree.write(outpath, encoding="UTF-8", xml_declaration=True)
    #
    #     return
    #

# to be expanded.....
# # # # # # # # # # # # # # # # # # # # # # # # # # # # ZONE DE TESTS
# THOSE TESTS ARE BROKEN. I4M SERIOUS.
# In order for them to work need of rewriting the arguments with
# "changetracker" syntax.
# import time
# start = time.time()
# print("very very short - 10 voxels")
#
# outpath = "/media/mtd/stock/boulot_sur_dart/temp/"
# vox = "/home/mtd/Desktop/testplots/Extended_modR_fus3_veryveryshort.vox"
# write_plots([], outpath, vox)
# end = time.time()
# print(end - start)
# print("")
# print("")

# start = time.time()
# print("very short - 1000 voxels")
#
# outpath="/media/mtd/stock/boulot_sur_dart/temp/"
# vox = "/home/mtd/Desktop/testplots/Extended_modR_fus3_veryshort.vox"
# write_plots([],outpath,vox)
# end = time.time()
# print(end - start)
# print("")
# print("")

#
# start = time.time()
# print("just short: 8000 voxels")
#
# outpath="/media/mtd/stock/boulot_sur_dart/temp/"
# vox = "/home/mtd/Desktop/testplots/Extended_modR_fus3_short.vox"
# write_plots([],outpath,vox)
# end = time.time()
# print(end - start)
# print("")
# print("")
#
#
# print("just short: 50 000 voxels")
# start = time.time()
# outpath="/media/mtd/stock/boulot_sur_dart/temp/"
# vox = "/home/mtd/Desktop/testplots/Extended_modR_fus3_shorishisky.vox"
# write_plots([],outpath,vox)
# end = time.time()
# print(end - start)
# print("")
# print("")
# start = time.time()
# print("shorish: 100 000 voxels")
#
# outpath="/media/mtd/stock/boulot_sur_dart/temp/"
# vox = "/home/mtd/Desktop/testplots/Extended_modR_fus3_shorish.vox"
# write_plots([],outpath,vox)
# end = time.time()
# print(end - start)
# print("")
# print("")
#
#
# start = time.time()
# print("medium: 200 000 voxels")
#
# outpath="/media/mtd/stock/boulot_sur_dart/temp/"
# vox = "/home/mtd/Desktop/testplots/Extended_modR_fus3_medium.vox"
# write_plots([],outpath,vox)
# end = time.time()
# print(end - start)
# print("")
# print("")
#
#
# start = time.time()
# print("longer: 500 000 voxels")
#
# outpath="/media/mtd/stock/boulot_sur_dart/temp/"
# vox = "/home/mtd/Desktop/testplots/Extended_modR_fus3_longer.vox"
# write_plots([],outpath,vox)
# end = time.time()
# print(end - start)
# print("")
# print("")
#
# start = time.time()
# print("long: 1 033 000 voxels")
#
# outpath="/media/mtd/stock/boulot_sur_dart/temp/"
# vox = "/home/mtd/Desktop/testplots/Extended_modR_fus3_afraiditslong.vox"
# write_plots([],outpath,vox)
# end = time.time()
# print(end - start)

# import platform
#
# print "Machine: ", platform.machine()
# print "Platform: ", platform.platform()
# print "processor", platform.processor()

# very short: 8 000
# short: 20 000
# shorish: 100 000
#  medium: 208 000
#  longer: 505 000 lignes


"""
very short - 1000 voxels
Initialized
basenoded
added voxels!!!
 written
0.207509994507
start = time.time()
print("longer: 500 000 voxels")

outpath="/media/mtd/stock/boulot_sur_dart/temp/"
vox = "/home/mtd/Desktop/testplots/Extended_modR_fus3_longer.vox"
write_plots([],outpath,vox)
end = time.time()
print(end - start)
print("")
print("")

just short: 8000 voxels
Initialized
basenoded
added voxels!!!
 written
1.1093981266


just short: 50 000 voxels
Initialized
basenoded
added voxels!!!
 written
6.50199604034


shorish: 100 000 voxels
Initialized
basenoded
/media/mtd/stock/boulot_sur_dart/pytools4DARTmtd/pytools4dartMTD/pytools4dart
/writedartxml/plots.py:35: DtypeWarning: Columns (9) have mixed types.
Specify dtype option on import or set low_memory=False.
  plots.plotsfromvox(vox)
added voxels!!!
 written
15.6107609272


medium: 200 000 voxels
Initialized
basenoded
added voxels!!!
 written
27.2974088192


longer: 500 000 voxels
Initialized
basenoded
added voxels!!!
 written
65.114274025


long: 1 033 000 voxels
Initialized
basenoded
added voxels!!!
 written
129.540043831

Machine:  x86_64
Platform:  Linux-4.13.0-45-generic-x86_64-with-debian-stretch-sid
processor x86_64
"""
