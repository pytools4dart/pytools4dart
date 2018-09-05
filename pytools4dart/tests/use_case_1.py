import pytools4dart as pt4d
import time
import os
start = time.time()
# Case Study 1 ################
# PathDART            = '/media/claudia/Donnees/Linux/DART_5-6-7_v1000/'
# SimulationName      = 'testprosequence10'
# SequenceName        = 'prospect_sequence.xml'

simu = pt4d.simulation('test1')
simu.addsingleplot(opt='proprieteoptpros')
proplot = ['vegetation', 'proprieteoptplot', 'Vegetation.db',
           'needle_spruce_stressed', '0']
# prosoptveg = ['vegetation', 'proprieteoptpros', 'prospect', 'blank', 0]
simu.addopt(proplot)
simu.addband([0.400, 0.01])

dic = {'CBrown': [0.8, 0.2, 0.0], 'Cab': [5, 27, 71.5], 'Car': 10,
       'Cm': 0.01, 'Cw': 0.01, 'N': 2, 'anthocyanin': 1}

simu.addprospectsequence(dic, 'proprieteoptpros', name='prospect_sequence')
simu.addsequence({'wvl': [0.400, 0.050, 8]},
                group='wvl', name='prospect_sequence')
corner = [[1, 1],
          [1, 2],
          [2, 2],
          [2, 1]]
simu.addsingleplot(corners=corner, opt='proprieteoptpros')
# pof.addsequence({'wvl':[400,20,8]})

simu.write_xmls()

pt4d.run.sequence(os.path.join("test1","sequence.xml"))

