# -*- coding: utf-8 -*-

import pytools4dart as pt4d
import numpy as np
pt4d.configure('/home/claudia/DART/DART_5-7-1_v1061')

simu = pt4d.simulation(name='use_case_1')

simu.addband([0.400, 0.01])

dic = {'CBrown': 0.0, 'Cab': range(0,110,10), 'Car': 10,
           'Cm': 0.01, 'Cw': 0.01, 'N': 2, 'anthocyanin': 1}

simu.addprospectsequence(dic, 'proprieteoptpros', name='prospect_sequence')
simu.add_singleplot(opt='proprieteoptpros')

simu.addsequence({'wvl':np.linspace(.4,1.4,11)})

simu.write_xmls()
simu.run.sequence('prospect_sequence')


