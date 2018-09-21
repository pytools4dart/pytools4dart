import pandas as pd
import numpy as np
import pytools4dart as ptd
from os.path import join as pjoin

db_dir = pjoin(ptd.settings.getdartdir(),'database')
inventory_file = pjoin(db_dir,'trees.txt')

inventory = pd.read_csv(inventory_file, comment='*', sep='\t')

simu = ptd.simulation('use_case_2')

simu.set_scene_size([40, 40])

print(inventory)

simu.add_bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})
simu.add_trees(inventory)
simu.add_tree_species(species_id = 0, lai=-0.25, holes=0,
                   trunkopt='trunk',
                   trunktherm='ThermalFunction290_310',
                   vegopt='leafs',
                   vegtherm='ThermalFunction290_310')

simu.add_tree_species(species_id = 1, lai=-0.1, holes=0,
                   trunkopt='trunk',
                   trunktherm='ThermalFunction290_310',
                   vegopt='leafs',
                   vegtherm='ThermalFunction290_310')

# simu.add_optical_property(['lambertian', 'ground', 'Lambertian_mineral.db',
#              'clay_brown', 0])

simu.add_optical_property(['lambertian', 'trunk', 'Lambertian_vegetation.db',
             'bark_deciduous', 0])

# simu.add_optical_property(['vegetation', 'leafs', 'Vegetation.db',
#              'leaf_deciduous', 1])
Cab = range(0,40,10)
dic = {'CBrown': 0.0, 'Cab': Cab, 'Car': 10,
           'Cm': 0.01, 'Cw': 0.012, 'N': 1.8, 'anthocyanin': 0}

simu.add_prospect_sequence(dic, 'leafs', name='prospect_sequence')

print(simu)


simu.write_xmls()
simu.run.full()

simu.run.sequence('prospect_sequence')

# produce RGB of each element of prospect case
for i in range(len(Cab)):
    ptd.run.colorCompositeBands(pjoin('use_case_2', 'sequence', 'prospect_sequence_'+str(i)),2, 1, 0, 'X', 'rgb')





