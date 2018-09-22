import pandas as pd
from os.path import join as pjoin
import pytools4dart as ptd


simu = ptd.simulation('use_case_2')

# Define bands
simu.add_bands({'wvl':[0.485, 0.555, 0.655], 'fwhm':0.07})

# define scene
simu.set_scene_size([40, 40])


# define optical properties for trunk
op_trunk = {
    'type':'lambertian',
    'op_name':'trunk',
    'db_name':'Lambertian_vegetation.db',
    'op_name_in_db':'bark_deciduous',
    'specular':0}

simu.add_optical_property(op_trunk)

# define optical properties for turbid vegetation
propect_prop = {'CBrown': 0, 'Cab': 30, 'Car': 5,
                'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                'anthocyanin': 0}

op_name ='leaf'
op_vegetation = {'type':'vegetation',
              'op_name': op_name,
              'db_name':'prospect.db',
              'op_name_in_db':'',
              'lad': 1,
              'prospect':propect_prop}

simu.add_optical_property(op_vegetation)

# load inventory
db_dir = pjoin(ptd.settings.getdartdir(),'database')
inventory_file = pjoin(db_dir,'trees.txt')
inventory = pd.read_csv(inventory_file, comment='*', sep='\t')

print(inventory)

# trees to scene
simu.add_trees(inventory)

# define species
simu.add_tree_species(species_id = 0, lai=-1, holes=0,
                   trunkopt='trunk',
                   trunktherm='ThermalFunction290_310',
                   vegopt='leaf',
                   vegtherm='ThermalFunction290_310')

simu.add_tree_species(species_id = 1, lai=-0.5, holes=0,
                   trunkopt='trunk',
                   trunktherm='ThermalFunction290_310',
                   vegopt='leaf',
                   vegtherm='ThermalFunction290_310')



# add sequence of chlorophyll
Cab=range(0,30,10)
simu.add_prospect_sequence({'Cab': Cab},
                           op_name='leaf',
                           name='prospect_sequence')
# show simulation
print(simu)

# write simulation
simu.write(overwrite=True)

# run sequence
simu.run.sequence('prospect_sequence')

# produce RGB of each element of prospect case
for i in range(len(Cab)):
    ptd.run.colorCompositeBands(pjoin('use_case_2', 'sequence', 'prospect_sequence_'+str(i)),2, 1, 0, 'X', 'rgb')





