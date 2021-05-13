# tools
This notebook present the main functions for database management into this
package

## dbtools

Submodule [`dbtools`](https://pytools4dart.gitlab.io/pytools4dart/reference/pytools4dart/tools/dbtools/)
is a toolbox of functions to manage and explore DART databases. 

Here are the main functions:

- **`import2db`** : add optical properties to database, **limited to Lambertian database** at the moment.
- **`get_models`** : list the models available in a DART database.
- **`optical_properties_db`**: create or append DART optical properties database, especially adapted to large database (10x faster than in DART).
- **`prospect_db`**: create or append an optical properties database with prospect, 
especially adapted to large database (100x faster than in DART). 
For examples, see https://pytools4dart.gitlab.io/pytools4dart/docs/user_guides/03_optical_properties/#prospect-database.

The following example creates a database named 'test.db', it is filled with a spectrum named 'test spectrum'
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

Submodule [`hstools`](https://pytools4dart.gitlab.io/pytools4dart/reference/pytools4dart/tools/hstools)
is dedicated to hyperspectral data management. It includes the following functionalities:

- read ENVI .hdr file and get band list
- stack dart bands
- rotate raster to standard GIS orientation
- get wavelength and FWHM values from hdr
- normalize data to min-max range

Check https://pytools4dart.gitlab.io/pytools4dart/reference/pytools4dart/tools/hstools for details.

## OBJtools

Submodule [`OBJtools`](https://pytools4dart.gitlab.io/pytools4dart/reference/pytools4dart/tools/OBJtools) has a few
functions to manage obj files:
- `objreader`: a class to read an obj file and get its extent, names of groups, ...
- `dtm2obj`: convert a raster file to an obj file
- `ply2obj`: convert a ply file to an obj file

## voxreader

Submodule [`voxreader`](https://pytools4dart.gitlab.io/pytools4dart/reference/pytools4dart/tools/voxreader) 
helps to manage voxelised plant area density (PAD) data and prepare them to define numerous turbid plots in a DART simulation.

The class has the following capacities:
- **read AMAPVox .vox file**, gives an object with attributes `header`, `data` and georeferenced `grid`.
Column 'PadBVTotal' of AMAPVox file is renamed 'pad' for ease of use.
- **create from data**, with i,j,k voxel indexes and corresponding Plant Area Density. 
- **apply affine 2D transformation to grid**, typically to rotate and translate voxel space. 
- **intersect voxel grid with a polygons or a raster**, e.g. to affect voxels optical properties.
- **export to DART plots DataFrame** to be added to a DART simulation as a plots file.

Here is an example of code (see use cases 3, 5 and 6 for other examples):
 - read an AMAPVox file,
 - plot the grid, 
 - apply xy affine transformation
 - define crowns and use them to define the voxels optical properties
 - convert to a plot DataFrame to be added to a simulation.
 
```python
import pytools4dart as ptd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, box

# read the voxelisation file
vox = ptd.voxreader.voxel().from_vox("data/forest.vox")
print(vox.header)
print(vox.data)

# plot grid
vox.grid.plot(color='w', edgecolor='k')

# center grid and rotate of 45 deg.
vox.affine_transform((1, 0, 0, 1, -20, -30))
rot = np.sin(np.pi/4)
vox.affine_transform((rot, rot, -rot, rot, 0, 0))
ax = vox.grid.plot(color='w', edgecolor='k')

# define crowns
# polygons = [box(-5, -5, 0, 0), box(+5, +5, 0, 0)]
polygons = [Point(-4,-4).buffer(3), box(+5, +5, 0, 0)]
op = ['veg1', 'veg2']
crowns = gpd.GeoDataFrame({'PLT_OPT_NAME':op, 'geometry': polygons})
crowns.plot(color='red', ax=ax)

# intersect with polygons
vox.intersect(crowns, inplace=True)
# set default value of PLT_OPT_NAME
vox.data.PLT_OPT_NAME.loc[pd.isna(vox.data.PLT_OPT_NAME)]="default"
# check unique values of PLT_OPT_NAME
vox.data.PLT_OPT_NAME.unique()

# plot the intersected area values
gidata = vox.grid.merge(vox.data.loc[vox.data.k==10], on = ['i', 'j'], how='left')
ax = gidata.plot(column='intersected_area', edgecolor='k',cmap='Reds')

# Export to DART plot dataframe
vox.to_plots(keep_columns='PLT_OPT_NAME').iloc[range(5)]
```
