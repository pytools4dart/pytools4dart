# -*- coding: utf-8 -*-

import pytools4dart as ptd

def run_use_case_0(testSimuName, run_required = False):
    # create an empty simulation
    simu = ptd.simulation(name=testSimuName)

    # define scene size
    scene_dims = [40, 40]
    simu.set_scene_size(scene_dims)

    # add spectral bands, e.g. 0.485, 0.555, 0.655 nm
    # with 0.07 full width at half maximum
    simu.add_bands({'wvl': [0.485, 0.555, 0.655], 'fwhm': 0.07})

    # define vegetation optical properties (VOP): here using the default veg opt property suggested by DART interface
    opt_prop_name = 'Turbid_Leaf_Deciduous_Phase_Function'
    veg_opt_prop = ['vegetation', opt_prop_name, 'Vegetation.db',
                    'leaf_deciduous', 1]
    simu.add_optical_property(veg_opt_prop)

    # add a turbid plot with associated VOP
    simu.add_single_plot(op_name=opt_prop_name)

    # run simulation
    simu.write_xmls()
    simu.run.direction()
    simu.run.phase()
    simu.run.maket()
    if run_required:
        simu.run.dart()
        simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')

if __name__ == '__main__':
    run_use_case_0("use_case_0", run_required = False)