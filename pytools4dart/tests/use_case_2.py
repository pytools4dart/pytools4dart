import pandas as pd
import numpy as np
import pytools4dart as pt4d

inventory_file = '/home/boissieu/Florian/IRSTEA/Software/DART_5-7-1_v1061/database/trees.txt'
inventory = pd.read_csv(inventory_file, comment='*', sep='\t')

simu = pt4d.simulation('use_case_2')
simu.set_scene_size([40, 40])

print(inventory)

for wvl in np.linspace(0.4, 1.4, 11):
    simu.addband([wvl, 0.01])

simu.addtrees(inventory)
simu.addtreespecies(species_id = 0, lai=-0.25, holes=0,
                   trunkopt='trunk',
                   trunktherm='ThermalFunction290_310',
                   vegopt='leafs',
                   vegtherm='ThermalFunction290_310')
simu.addtreespecies(species_id = 1, lai=-0.1, holes=0,
                   trunkopt='trunk',
                   trunktherm='ThermalFunction290_310',
                   vegopt='leafs',
                   vegtherm='ThermalFunction290_310')

# simu.addopt(['lambertian', 'ground', 'Lambertian_mineral.db',
#              'clay_brown', 0])

simu.addopt(['lambertian', 'trunk', 'Lambertian_vegetation.db',
             'bark_deciduous', 0])

# simu.addopt(['vegetation', 'leafs', 'Vegetation.db',
#              'leaf_deciduous', 1])

dic = {'CBrown': 0.0, 'Cab': range(0,110,10), 'Car': 10,
           'Cm': 0.01, 'Cw': 0.012, 'N': 1.8, 'anthocyanin': 0}

simu.addprospectsequence(dic, 'leafs', name='prospect_sequence')

simu.write_xmls()
simu.run.sequence('prospect_sequence')






