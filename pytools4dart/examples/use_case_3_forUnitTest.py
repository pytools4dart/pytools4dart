# -*- coding: utf-8 -*-

import pytools4dart as pt4d
import os.path
pt4d.configure('/home/claudia/DART/DART_5-7-1_v1061')

def run_use_case_3(testSimuName, run_required = False):
    simu = pt4d.simulation(name=testSimuName)
    current_dir = os.path.dirname(os.path.realpath(__file__))
    vox = pt4d.voxreader.voxel().from_vox(os.path.join(current_dir,"../../data/forest.vox"))

    vox.data = vox.data[(vox.data.i < 20) & (vox.data.j < 20)]
    simu.set_scene_size([20, 20])
    simu.add_plots_from_vox(vox, densitydef='ul', optprop=None)
    simu.plots['optprop'] = 'proprieteoptpros'
    simu.addband([0.485, 0.07])
    simu.addband([0.555, 0.07])
    simu.addband([0.655, 0.07])

    # simu.addsequence({'wvl':[.4,.1,10]}, group='wavelength', name='prospect_sequence')

    dic = {'CBrown': 0.0, 'Cab': [20, 30], 'Car': 10,
           'Cm': 0.01, 'Cw': 0.01, 'N': 2, 'anthocyanin': 1}
    simu.addprospectsequence(dic, 'proprieteoptpros', name='prospect_sequence')
    simu.write_xmls()

    if run_required:
        simu.run.full()
        simu.stack_bands()
        simu.run.sequence('prospect_sequence')

if __name__ == '__main__':
    run_use_case_3("use_case_3", run_required = True)