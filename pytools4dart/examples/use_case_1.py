# -*- coding: utf-8 -*-

import pytools4dart as ptd
import numpy as np

simu = ptd.simulation(name='use_case_1')

simu.add_bands({'wvl':0.4, 'fwhm':0.07})

dic = {'CBrown': 0.0, 'Cab': range(0,30,10), 'Car': 10,
           'Cm': 0.01, 'Cw': 0.01, 'N': 2, 'anthocyanin': 1}

simu.addprospectsequence(dic, 'proprieteoptpros', name='prospect_sequence')
simu.add_singleplot(opt='proprieteoptpros')

simu.addsequence({'wvl':np.linspace(.4,.8,5)})

simu.write_xmls()
simu.run.sequence('prospect_sequence')


