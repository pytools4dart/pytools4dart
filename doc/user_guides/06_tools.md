# tools
This notebook present the main functions for database management into this
package



## dbtools

Submodule `dbtools` is a toolbox of functions to manage and explore DART databases. 
At the moment there is only a small number of functions:

- **`import2db`** : add optical properties to database, **limited to Lambertian database** at the moment.
- **`get_models`** : list the models available in a DART database. 

The following example, a database named 'test.db' is created, it is filled with a spectrum named 'test spectrum'
and the model list is then extracted from the same database.

```python
from pytools4dart.tools import dbtools
import os
dbFpath = os.path.abspath('./test.db')
wavelength = [1, 2, 3]
reflectance = [.1, .2, .3]
direct_transmittance = [0, 0, 0]
diffuse_transmittance = [.9, .8, .7]
name = 'test spectrum'
dbtools.import2db(dbFpath, name=name, wavelength=wavelength, reflectance=reflectance,
          direct_transmittance=direct_transmittance, 
          diffuse_transmittance=diffuse_transmittance,
                  comments = ["# Date: 2019",
                              "# Species: test"])

dbtools.get_models(dbFpath)
```

## hstools

This module is dedicated to hyperspectral data management. It includes the following functionalities:
- read ENVI .hdr file and get band list
- 

## voxreader

This module is a reader for AMAPVox files. The class has the following capacities:
- **read AMAVox .vox file**, gives an object with attributes `header`, `data` and georeferenced `grid`.
- **intersect voxel grid with a shapefile**, e.g. to affect voxels optical properties.
- **convert to DART plots DataFrame** to be added to a DART simulation as a plots file.


```