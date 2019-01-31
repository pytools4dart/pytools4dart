import pandas as pd
from os.path import join as pjoin
import pytools4dart as ptd


simu = ptd.simulation()
simu.name = 'use_case_2'

# empty the simulation
simu.core.xsdobjs['coeff_diff'].Coeff_diff.LambertianMultiFunctions.LambertianMulti=[]
simu.core.xsdobjs['phase'].Phase.DartInputParameters.SpectralIntervals.SpectralIntervalsProperties=[]
simu.core.xsdobjs['phase'].Phase.DartInputParameters.nodeIlluminationMode.SpectralIrradiance.SpectralIrradianceValue=[]

simu.scene.ground.OpticalPropertyLink.ident='ground'

# Define bands
for wvl in [0.485, 0.555, 0.655]:
    simu.add.band(wvl=wvl, bw=0.07)

# define scene
simu.scene.size = [40, 40]

##################################
# Optical and thermal properties #
##################################
# Optical and thermal properties are found in databases, e.g. 'Lambertian_vegetation.db'
# The list of available models in database can be list with `dbtools` module:
# ptd.helpers.dbtools.get_models('Lambertian_mineral.db')


# define optical property for ground
op_ground = {
    'type':'Lambertian',
    'ident':'ground',
    'databaseName':'Lambertian_mineral.db',
    'ModelName':'clay_brown'}

simu.add.optical_property(**op_ground)

# define optical properties for trunk
op_trunk = {
    'type':'Lambertian',
    'ident':'trunk',
    'databaseName':'Lambertian_vegetation.db',
    'ModelName':'bark_deciduous'}

simu.add.optical_property(**op_trunk)

# define optical properties for turbid vegetation
propect_prop = {'CBrown': 0, 'Cab': 30, 'Car': 5,
                'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                'anthocyanin': 0}

op_name ='leaf'
op_vegetation = {'type':'Vegetation',
              'ident': op_name,
              'databaseName':'prospect.db',
              'ModelName':'',
              'lad': 1,
              'prospect':propect_prop}

op = simu.add.optical_property(**op_vegetation)

simu.core.update()

# load inventory
db_dir = pjoin(ptd.settings.getdartdir(),'database')
inventory_file = pjoin(db_dir,'trees.txt')
inventory = pd.read_csv(inventory_file, comment='*', sep='\t')

print(inventory)

# species_id=0
simu.add.tree_species(lai=-1,
                   trunk_op_ident='trunk',
                   trunk_tp_ident='ThermalFunction290_310',
                   veg_op_ident='leaf',
                   veg_tp_ident='ThermalFunction290_310')
# species_id=1
simu.add.tree_species(lai=-0.5,
                   trunk_op_ident='trunk',
                   trunk_tp_ident='ThermalFunction290_310',
                   veg_op_ident='leaf',
                   veg_tp_ident='ThermalFunction290_310')


# trees to scene
simu.add.trees(inventory, overwrite=True, mkdir=True)

# # define species
# simu.add_tree_species(lai=-1, holes=0,
#                    trunkopt='trunk',
#                    trunktherm='ThermalFunction290_310',
#                    vegopt='leaf',
#                    vegtherm='ThermalFunction290_310')
#
# simu.add_tree_species(lai=-0.5, holes=0,
#                    trunkopt='trunk',
#                    trunktherm='ThermalFunction290_310',
#                    vegopt='leaf',
#                    vegtherm='ThermalFunction290_310')



# add sequence of chlorophyll
Cab = range(0,30,10)
sequence = simu.add.sequence()
sequence.name='prospect_sequence'
sequence.add_item(group='prospect', key='Cab', values=Cab, corenode=op)

# show simulation
print(simu)

# write simulation and sequence
simu.write(overwrite=True)

# run sequence
simu.run.sequence('prospect_sequence')

# produce RGB of each element of prospect case
for i in range(len(Cab)):
    ptd.run.colorCompositeBands(pjoin('use_case_2', 'sequence', 'prospect_sequence_'+str(i)),2, 1, 0, 'X', 'rgb')





