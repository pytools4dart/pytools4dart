# -*- coding: utf-8 -*-

import pytools4dart as ptd
import os.path
from os.path import join as pjoin
ptd.configure('/home/claudia/DART/DART_5-7-1_v1061')

def run_use_case_3(testSimuName, run_required = False):
    simu = ptd.simulation(name = testSimuName)
    cd =  os.getcwd()
    ptdroot_dir = cd.split("pytools4dartMTD")[0]
    vox = ptd.voxreader.voxel().from_vox(pjoin(ptdroot_dir, "pytools4dartMTD/data/forest.vox"))

    vox.data = vox.data[(vox.data.i < 20) & (vox.data.j < 20)]
    simu.set_scene_size([20, 20])
    simu.add_plots_from_vox(vox, densitydef='ul', optprop=None)
    simu.plots['optprop'] = 'proprieteoptpros'
    simu.add_bands({'wvl': [0.485, 0.555, 0.655], 'fwhm': 0.07})

    # simu.add_sequence({'wvl':[.4,.1,10]}, group='wavelength', name='prospect_sequence')

    dic = {'CBrown': 0.0, 'Cab': [20, 30], 'Car': 10,
           'Cm': 0.01, 'Cw': 0.01, 'N': 2, 'anthocyanin': 1}
    simu.add_prospect_sequence(dic, 'proprieteoptpros', name='prospect_sequence')
    simu.write_xmls()

    simu.run.direction()
    simu.run.phase()
    simu.run.maket()

    if run_required:
        #simu.run.full()
        simu.run.dart()
        simu.stack_bands()
        simu.run.sequence('prospect_sequence')
        simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')

if __name__ == '__main__':
    run_use_case_3("use_case_3", run_required = True)