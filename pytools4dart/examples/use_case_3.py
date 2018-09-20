# -*- coding: utf-8 -*-

import pytools4dart as ptd
simu = ptd.simulation(name='use_case_3')

vox = ptd.voxreader.voxel().from_vox("../../data/forest.vox")

vox.data = vox.data[(vox.data.i < 20) & (vox.data.j < 20)]
simu.set_scene_size([20, 20])
simu.add_plots_from_vox(vox, densitydef='ul', optprop=None)
simu.plots['optprop'] = 'proprieteoptpros'
simu.add_bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})

# simu.add_sequence({'wvl':[.4,.1,10]}, group='wavelength', name='prospect_sequence')

dic = {'CBrown': 0.0, 'Cab': [20, 30], 'Car': 10,
           'Cm': 0.01, 'Cw': 0.01, 'N': 2, 'anthocyanin': 1}
simu.add_prospect_sequence(dic, 'proprieteoptpros', name='prospect_sequence')
simu.write_xmls()
simu.run.full()

simu.stack_bands()
simu.run.sequence('prospect_sequence')

simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')

# def f2(a=None, b=None, c=None):
#     print([a,b,c])
# import pandas as pd
# data=pd.DataFrame([[[0,1], 1, 2]]*10, columns={'a', 'b', 'c'})
#
# def f1(data):
#
#     for row in data.itertuples():
#         print(row.__dict__.keys())
#
#
#
# import xml.etree.cElementTree as etree
# import os
# plotsxml = etree.parse(os.path.expanduser("~/IRSTEA/Software/DART_5-7-1_v1061/user_data/simulations/simulationTest/input/plots.xml"))
# root = plotsxml.getroot()
#
# root =etree.Element("Plots", {'addExtraPlotsTextFile': '0',
#                                             'isVegetation': '0'})
# etree.SubElement(self.root, "ImportationFichierRaster")
#
# tree = etree.ElementTree(root)
# etree.tostring(root)
# plots = root.find('Plots')
# plots.set('addExtraPlotsTextFile','1')
# etree.SubElement(plots, 'ExtraPlotsTextFileDefinition', {'extraPlotsFileName':'plots.txt'})
#
# print(etree.tostring(root))