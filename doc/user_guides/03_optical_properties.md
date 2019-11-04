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
optical properties. The code below shos an example. If the database name does
not exist it will be created.

```python
import pytools4dart as ptd
simu = ptd.simulation('op', empty=True)
for wvl in [0.485, 0.555, 0.655]:
    simu.add.band(wvl=wvl, bw=0.07)
op = simu.add.optical_property(type = 'Vegetation',
                               ident='turbid_leaf',
                               databaseName='ProspectVegetation.db',
                               ModelName='',
                               prospect={'CBrown': 0, 'Cab': 30, 'Car': 5,
                                         'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                                         'anthocyanin': 0})

op = simu.add.optical_property(type = 'Lambertian',
                               ident='grass',
                               databaseName='ProspectLambertian.db',
                               ModelName='',
                               prospect={'CBrown': 0, 'Cab': 50, 'Car': 20,
                                         'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                                         'anthocyanin': 0})

simu.scene.ground.OpticalPropertyLink.ident='grass'

simu.add.plot(type='Vegetation',op_ident='turbid_leaf')
simu.write(overwrite=True)
simu.run.full()

simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')


```
