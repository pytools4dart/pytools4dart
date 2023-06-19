# Optical Properties
This notebook shows examples on the management of optical properties

## Top and bottom vegetation properties

DART gives the possibility to define a
vegetation optical property with different properties for top and bottom of a
face. However, at the moment only one property database and model name can be
defined with add.optical_property. A way to overcome this issue is to create a
single optical property and define the different properties afterwards with the
core object created.

```python
import pytools4dart as ptd
simu = ptd.simulation(empty=True)
op = simu.add.optical_property(type='Vegetation', ident='leaf',
                               hasDifferentModelForBottom=1)

op.UnderstoryMultiTopModel.ModelName = 'maple_top' # top face
op.UnderstoryMultiBottomModel.ModelName = 'maple_top_bf' # bottom face
## set databaseName if not in the default database
# op.UnderstoryMultiTopModel.databaseName 
# op.UnderstoryMultiBottomModel.databaseName

print(op.to_string())
```

## Prospect

Prospect module is used to generate a spectral signature based on
physcho-chemichal properties like the concentrations of Chlorophylle (Cab),
Carotenoids (Car), ...
This module can be called for Lambertian and Vegetation
optical properties. The code below shows an example. If the database name does
not exist it will be created.

_Notes: Before DART v1264, properties generated with Prospect/Fluspect included in DART were stored in
the specified database (in directory DART/user_data/database) with a unique ModelName defined by an hash code 
of the Prospect/Fluspect input properties. 
Since DART v1264 generated optical properties are not stored anymore in order to accelerate processing, 
thus args "databaseName" and "ModelName" are not used anymore by DART in those cases._

```python
import pytools4dart as ptd
simu = ptd.simulation('op', empty=True)
for wvl in [0.485, 0.555, 0.655]:
    simu.add.band(wvl=wvl, bw=0.07)
op = simu.add.optical_property(type = 'Vegetation',
                               ident='turbid_leaf',
                               # databaseName='ProspectVegetation.db', # uncomment for DART < v1264
                               prospect={'CBrown': 0, 'Cab': 30, 'Car': 5,
                                         'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                                         'anthocyanin': 0})

op = simu.add.optical_property(type = 'Lambertian',
                               ident='grass',
                               # databaseName='ProspectLambertian.db', # uncomment for DART < v1264
                               prospect={'CBrown': 0, 'Cab': 50, 'Car': 20,
                                         'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                                         'anthocyanin': 0})

simu.scene.ground.OpticalPropertyLink.ident='grass'

simu.add.plot(type='Vegetation',op_ident='turbid_leaf')
simu.write(overwrite=True)
simu.run.full()

simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')
```

### Prospect database

The generation of Prospect/Fluspect optical properties through DART phase module
may suffer computation time issues for the generation of numerous Prospect properties:
   - ~100ms to 1s/prospect property depending on DART version,
   - computation time increases exponentially with the number of properties (not anymore the case with DART v1264 update, see notes above)

To overcome this problem, the database can be pre-computed with function [`pytools4dart.dbtools.prospect_db`)(https://pytools4dart.gitlab.io/pytools4dart/reference/pytools4dart/tools/dbtools/#prospect_db).
It reduces the generation of prospect properties and its storage in an optical properties database to ~10ms/property.

Here is an example for the generation of the database for 
1000 prospect properties (~10s computation time):
```python
import pandas as pd
import numpy as np
import pytools4dart as ptd
import time
tic = time.time()
size = 1000
prospect_properties = pd.DataFrame({'N': np.random.uniform(1,3,size),
                                    'Cab': np.random.uniform(0,30,size),
                                    'Car': np.random.uniform(0,5,size)})
db_file = ptd.getdartenv()['DART_LOCAL'] / 'database' / 'prospect_example.db')
prospect_properties = ptd.dbtools.prospect_db(db_file, **prospect_properties)
toc = time.time()
print(toc - tic)
```
It returns a DataFrame with the additional columns useful to add properties to the simulation,
such as `model` (the model name) or `prospect_file` (prospect coefficient file).

If the database already exists, it appends the new properties, otherwise the database is created.
See the function documentation for more details.

### Numerous optical properties

For large numbers of optical properties (>100), the addition with `add.optical_property` 
can take time as it will generate the default nodes and attribute values for each property.
The addition of one property takes around 40ms.

There are two ways to make it faster:
- make sure the multiplicative factors are off: `useMultiplicativeFactorForLUT=0`,
- use the first optical property as a template, it will divide the processing time by 5 to 10
i.e. copy with list comprehension, fill it with the specific values,
and paste the list into the simulation.

The downside of this method is that it bypasses checks on the unicity of `ident`
among optical properties until the simulation is written.
 
Here is an example to add 1000 optical properties previously generated with `prospect_db`:
```python
prospect_properties['ident']= ['prospect_{}'.format(i) for i in range(size)] 
prospect_properties['database'] = 'prospect_example.db'

op = simu.add.optical_property(type = 'Vegetation',
                               ident='temp_op',
                               databaseName='prospect_example.db')

print(op.to_string())

# function to copy, fill and paste properties into simulation
def add_prospect_properties(op0, df):
    # Copy reference optical property.
    oplist = [op0.copy() for i in range(len(df))]
    
    # Fill it with specific prospect properties.
    # To make it even faster, use the full path 
    # to each attributes instead of set_nodes.
    # Use op.findpaths to find them.
    for row in df.itertuples():
        op = oplist[row.Index]
        op.ident = row.ident
        op.set_nodes(ModelName = row.model)
    
    # Replace list into the parent node.
    op0.parent.UnderstoryMulti = oplist

add_prospect_properties(op, prospect_properties)
```
