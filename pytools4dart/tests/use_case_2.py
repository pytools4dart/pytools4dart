import pandas as pd
import numpy as np
import pytools4dart as pt4d

inventory_file = '/home/boissieu/Florian/IRSTEA/Software/DART_5-7-1_v1061/database/trees.txt'
inventory = pd.read_csv(inventory_file, comment='*', sep='\t')

simu = pt4d.simulation('use_case_2')

print(inventory)
simu.addtrees(inventory)
simu.addtreespecie(idspecie = 0, lai=-0.25, holes=None,
                   trunkopt='trunk',
                   trunktherm='ThermalFunction290_310',
                   vegopt='leafs',
                   vegtherm='ThermalFunction290_310')
simu.addopt(['lambertian', 'trunk', 'Lambertian_vegetation.db',
             'bark_deciduous', 0])

dic = {'CBrown': 0.0, 'Cab': range(0,110,10), 'Car': 10,
           'Cm': 0.01, 'Cw': 0.01, 'N': 2, 'anthocyanin': 1}

simu.addprospectsequence(dic, 'leafs', name='prospect_sequence')

simu.addsequence({'wvl':np.linspace(.4,1.4,11)})
simu.write_xmls()






