This notebooks present the main functions for database management into this
package

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
