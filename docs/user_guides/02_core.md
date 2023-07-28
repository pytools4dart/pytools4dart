# Core
This notebooks describes the structure and methods of core.

## Core content

The core contains all the input xml files of DART, loaded into python objects.
It contains the following modules:

- atmosphere, 
- coeff_diff, 
- directions, 
- inversion, 
- maket,
- object_3d, 
- phase, 
- plots, 
- trees, 
- urban, 
- water,
- and sequence if one was added. 

The list of these modules is available through `core.children`:

```python
import pytools4dart as ptd
simu = ptd.simulation()
simu.core.children
```

Each module of core is a tree of objects corresponding to DART xml configuration file.

### Find a parameter

All the module parameters can be listed with:

```python
ptd.utils.get_labels()
```

The label column is what can be found in the GUI, the dartnode column is the corresponding node path in the simulation core. For a specific simulation, only a subset of these parameters is used. As an example, for a passive remote sensing simulation only the parameters specific to this mode will be available.

The full parameter table is extracted from DART files, thus it will depend on the DART version. All the available nodes and attributes for the last DART version are also available in [DART parameters](../DART_parameters.md).


For a specific search of a parameter encoutered in the GUI, e.g. the "Exactly periodic scene" in the editor menu "Earth Scene", a pattern can be used to filter the search results:
```python
ptd.utils.get_labels("Exactly periodic scene", column="label")
```

### Explore simulation parameters

In order to explore the content of the core modules of a simulation, each core node has the methods:
  
  - `to_string()`: convert the structure to an xml string
  - `path()`: get the absolute path of the node within the module
  - `subpaths()`: list of all subnode paths
  - `findpaths()`: list of the subnode paths corresponding to a regular expression.
  - `set_nodes()`: set a value to a subnode.


Other useful functions for core exploration are in `pytools4dart.core_ui.utils`:
  
  - `ptd.utils.get_nodes()`: get the subnodes corresponding to a subpath.
  - `ptd.utils.findall()`: get all the subnodes values and paths corresonding to a regular expression.
  - `ptd.diff()`: print the difference between two simulations or two core nodes or subnodes, for a whole simulation comparison see [simulation user guide](./01_simulation.md)

```python
import pytools4dart as ptd
from pytools4dart.core_ui.utils import get_nodes, findall, set_nodes

print(simu.core.coeff_diff.to_string())    

# list all subpaths
simu.core.coeff_diff.subpaths()

# find paths ending with '.ident'
simu.core.coeff_diff.findpaths('\.ident$')

# change ident of the default lambertian property 
print(simu.scene.properties.optical)
simu.core.coeff_diff.set_nodes(ident='leaf', ModelName='leaf_deciduous', databaseName='Lambertian_vegetation.db')
print(simu.scene.properties.optical)

# create a vegetation property
op = simu.add.optical_property(type='Vegetation', ident='turbid_leaf', ModelName='leaf_deciduous', databaseName='Lambertian_vegetation.db')
print(simu.core.coeff_diff.to_string())

# convert to double face
op.set_nodes(hasDifferentModelForBottom=1)
print(simu.core.coeff_diff.to_string())

# assign 'maple_top' to topface and 'maple_top_bf' for bottomface
op.set_nodes(ModelName=['maple_top', 'maple_top_bf'])
findall(simu.core.coeff_diff.Coeff_diff, 'ModelName$', path=True)

# get the values of nodes ending with LambertianMulti.ident
get_nodes(simu.core.coeff_diff.Coeff_diff.LambertianMultiFunctions, 'LambertianMulti.ident')

# convert to simple face
set_nodes(op, hasDifferentModelForBottom=0)
# Warning, changing to simple face will change the model
# to default turbid Vegetation model: leaf_deciduous
findall(simu.core.coeff_diff.Coeff_diff, 'ModelName$', path=True)

# find all nodes ending with [0]."something".ModelName
findall(simu.core.coeff_diff.Coeff_diff, '\[0\]\..+ModelName$', path=True, use_labels=False)


# difference between simu and simuTest
simuTest = ptd.simulation('simulationTest')
ptd.diff(simu.core, simuTest.core)
```

Core also contains several getters and updaters. Getters allow to extract
summaries, e.g. the optical properties table. The updaters are used to update
cross-module fields, such as the match between optical properties (in
coeff_diff) and optical property links (in plots, object_3d, trees, etc.).

```python
print(simu.core.get_optical_properties())
```

## Modules


Within core modules, each node has three essential attributes:
  
  - children: names of the children, i.e. subnodes.
  - attrib: names of the attributes, i.e. parameters.
  - parent: address of the parent object in the structure

```python
simu.core.phase.Phase.children
simu.core.phase.Phase.attrib
simu.core.phase.Phase.parent
```

The children and attributes are class properties. When attributes are changed,
the structure is automatically updated, setting parameters to default values,
just like in DART GUI.

```python
simu.core.phase.Phase.calculatorMethod = 0 # Flux Tracking
print(simu.core.phase.to_string())
simu.core.phase.Phase.calculatorMethod = 2 # LIDAR
print(simu.core.phase.to_string())
```

Subnodes expecting a list have other specific methods:

 - add,
 - insert,
 - replace.

```python
plot = ptd.plots.create_Plot()
simu.core.plots.Plots.add_Plot(plot)
```

The classes of each core module are available at the package root under the
module name, e.g. `ptd.plots`.

The classes are named with the pattern `create_{node_name}`,
e.g. `ptd.create_LambertianMultiFunctions()`
to create a default node `LambertianMultiFunctions`. 

Each class has documentation similar to the one given in DART GUI.

