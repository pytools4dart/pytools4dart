# !/usr/bin/env python2
#  -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 14:15:03 2018

@author: mtd

Objects and functions necessary to write the plots xml file.
It is important to note the resulting xml file is written over a single line.
"""
try:
    import xml.etree.cElementTree as etree
    print ("imported cetree")
except ImportError:
    print ("oups!, importing pytetree")
    import xml.etree.ElementTree as etree

from voxReader import voxel


def write_plots(changetracker, outpath, vox=None):
    """write phase xml file

    proceed in the following manner:
        -instantiate  dartplots object
        -set default nodes
        -add more nodes depending on changetracker/vox
        -output file to xml

    Will tend to be modified for adding support of different ways to add nodes
    (i.e. panda dataframes).

    """
    plots = DartPlotsXML(changetracker)
    print "Initialized"
    plots.basenodes()
    print "basenoded"
    plots.plotsfromvox(vox)
    print "added voxels!!!"
    #  phase.adoptchanges()

    plots.writexml(outpath+"test_plots.xml")
    print " written"
    return


class DartPlotsXML(object):
    """object for the editing and exporting to xml of phase related parameters

    After instantiation, a default tree of nodes is created.
    Changes based on the passed "changetracker" variable have then to
    take place in order to upgrade the tree.
    All the tag names of tree nodes are supposed to be IDENTICAL to the ones
    produces by DART. The variable names are sometimes shortened.

    """
    PLOT_DEFAULT_ATR = {"form": "0", "hidden": "0", "isDisplayed": "1",
                        "repeatedOnBorder": "1", "type": "1"}

    def __init__(self, changetracker):
        self.root = etree.Element("Plots", {'addExtraPlotsTextFile': '0',
                                  'isVegetation': '0'})
        self.tree = etree.ElementTree(self.root)
        self.changes = changetracker
        return

    def basenodes(self):
        """creates all nodes and properties common to default simulations

        """

        # base nodes
        # # simple
        etree.SubElement(self.root, "ImportationFichierRaster")
        return

    def addplot(self, corners, baseheight, density, optprop):
        """Adds a plot based on a few basic parameters

        This method could evolve to receive a variable number of parameters.
        For now it is used mainly as the way to integrate voxels from a .vox
        file. Parameters are cast to strings in order to ensure compatibility
        with Element Tree.
        """
        # appends new plot to plots
        plot = etree.SubElement(self.root, "Plot", self.PLOT_DEFAULT_ATR)

        # Polygon 2D Branch
        polygon_plot1 = etree.SubElement(plot, "Polygon2D", {"mode": "0"})

        # # with its four defining points
        etree.SubElement(polygon_plot1, "Point2D",
                         {"x": str(corners[0][0]), "y": str((corners[0][1]))})
        etree.SubElement(polygon_plot1, "Point2D",
                         {"x": str(corners[1][0]), "y": str((corners[1][1]))})
        etree.SubElement(polygon_plot1, "Point2D",
                         {"x": str((corners[2][0])), "y": str(corners[2][1])})
        etree.SubElement(polygon_plot1, "Point2D",
                         {"x": str(corners[3][0]), "y": str(corners[3][1])})

        # plot vegetation properties branch
        vegprops_atr = {"densityDefinition": "0",
                        "trianglePlotRepresentation": "0",
                        "verticalFillMode": "0"}
        vegprops = etree.SubElement(plot, "PlotVegetationProperties",
                                    vegprops_atr)

        veggeom = {"baseheight": (baseheight), "height": "1.0",
                   "stDev": "0"}
        # here optical property passed as argument to method
        vegoptlink = {"ident": optprop, "indexFctPhase": "0"}
        grdthermalprop = {"idTemperature": "ThermalFunction290_310",
                          "indexTemperature": "0"}

        # here density parameter added in LAI
        etree.SubElement(vegprops, "VegetationGeometry", veggeom)
        etree.SubElement(vegprops, "LAIVegetation", {"LAI": density})
        etree.SubElement(vegprops, "VegetationOpticalPropertyLink", vegoptlink)
        etree.SubElement(vegprops, "GroundThermalPropertyLink", grdthermalprop)
        return

    def plotsfromvox(self, path):
        """Adds Plots based on AMAP vox file.

        Based on code from Claudia, Florian and Dav.
        Needs "voxreader". Most complicated function being: intersect,
        that is needed in Dav's project to get the optical properties of the
        voxels depending on another file.
        """

        vox = voxel.from_vox(path)

        res = vox.header["res"][0]
        i = 0
        for index, row in vox.data.iterrows():
            i += 1
            i = row.i  # voxel x
            j = row.j  # voxel y
            k = row.k  # voxel z
            optPropName = "test_" + str(i)
            LAI = str(row.PadBVTotal)  # voxel LAI(PadBTotal en negatif)

            corners = (((i * res), (j * res)),
                       ((i + 1 * res), (j * res)),
                       (((i + 1) * res), ((j + 1) * res)),
                       ((i * res), ((j + 1) * res)))

            height = res
            baseheight = str(k * height)  # voxel height

            self.addplot(corners, baseheight, LAI, optPropName)
        return

    def adoptchanges(self, changetracker):
        """method to update xml tree based on user-defined parameters

        here goes the magic where we change some nodes based on parameters
        it would maybe be something like this:
           - for some values, just append them somewhere
           - for the others, find them in the tree and modify them (tricky bit)

        Complete path to node to be modified will have to be explicitly written
        in this way: './Phase/DartInputParameters/SpectralDomainTir'
        for the query to work.
        """

        if "phase" in changetracker[0]:
            self.changes = changetracker[1]["phase"]
            for node in self.changes:
                print "Modifying: ", node
                self.root.find(node)

            return
        else:
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
        tree.write(outpath)
        return


# to be expanded.....
# # # # # # # # # # # # # # # # # # # # # # # # # # # # ZONE DE TESTS
"""
import time
start = time.time()
print("very very short - 10 voxels")

outpath = "/media/mtd/stock/boulot_sur_dart/temp/"
vox = "/home/mtd/Desktop/testplots/Extended_modR_fus3_veryveryshort.vox"
write_plots([], outpath, vox)
end = time.time()
print(end - start)
print("")
print("")
"""
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
