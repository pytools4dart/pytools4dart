# -*- coding: utf-8 -*-

import pytools4dart as ptd
simu = ptd.simulation(name='use_case_3')

vox = ptd.voxreader.voxel().from_vox("../../data/forest.vox")

vox.data = vox.data[(vox.data.i < 20) & (vox.data.j < 20)]
simu.set_scene_size([20, 20])
simu.add_plots_from_vox(vox, densitydef='ul', op_name=None)
simu.plots['op_name'] = 'op_prospect'
simu.add_bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})


#### Define optical properties
propect_prop = {'CBrown': 0, 'Cab': 30, 'Car': 10,
                'Cm': 0.01, 'Cw': 0.012, 'N': 1.8,
                'anthocyanin': 0}

op_vegetation = {'type':'vegetation',
              'op_name':'op_prospect',
              'db_name':'prospect.db',
              'op_name_in_db':'',
              'lad': 1,
              'prospect':propect_prop}

simu.add_optical_property(op_vegetation)

# simu.add_sequence({'wvl':[.4,.1,10]}, group='wavelength', name='prospect_sequence')

simu.add_prospect_sequence({'Cab': range(0,30,10)},
                           op_name='op_prospect',
                           name='prospect_sequence')
simu.write_xmls()
simu.run.full()

# stack bands
simu.stack_bands()
simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')

# run sequence
simu.run.sequence('prospect_sequence')


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