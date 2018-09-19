# -*- coding: utf-8 -*-

import pytools4dart as ptd
import numpy as np
from os.path import join as pjoin
import pytools4dart.settings as settings

def run_use_case_1(testSimuName, run_required = False):

    simu = ptd.simulation(name = testSimuName)

    simu.add_bands({'wvl': [0.485, 0.555, 0.655], 'fwhm': 0.07})

    dic = {'CBrown': 0.0, 'Cab': range(0, 30, 10), 'Car': 10,
           'Cm': 0.01, 'Cw': 0.01, 'N': 2, 'anthocyanin': 1}

    simu.addprospectsequence(dic, 'proprieteoptpros', name='prospect_sequence')
    simu.add_singleplot(opt='proprieteoptpros')

    simu.addsequence({'wvl': np.linspace(.4, .8, 5)})

    simu.write_xmls()
    if run_required:
        simu.run.sequence('prospect_sequence')


if __name__ == '__main__':
    run_use_case_1("use_case_1", run_required = False)