# Simulation

Simulation object is corresponding to a DART simulation parameter editor.
It allows for creating or loading a simulation, editing its parameters and running the simulation.

## Create a simulation

```python
import pytools4dart as ptd
simu = ptd.simulation('my_new_simu', empty=True)
print(simu) # display summary of simulation
``` 
Argument `empty=True` removes the default band automatically created by DART.

## Load a simulation
In order to load an existing simulation:
```python
simu_test = ptd.simulation('simulationTest')
print(simu_test) # display summary of simulation
```

If the simulation does not exist, a default simulation is created, see [details](#empty-simulation).

## Compare simulations

Compare simulations summaries:
```python
simu1 = ptd.simulation('my_new_simu1', empty=True)
simu2 = ptd.simulation('my_new_simu2')
ptd.diff(simu1, simu2)
```

Compare core nodes:
```python
ptd.diff(simu1.core, simu2.core)
ptd.diff(simu1.core.phase, simu2.core.phase)
```

## Details

### Simulation object
`simulation` object contains the following attributes:

  - core: objects representing DART XML input files (coeff_diff,
    directions, phase, ...) with a raw interface to access and change parameters.

    Each module correspond to a part of DART GUI. As in DART GUI, changes propagates
    automatically to subnodes. 
    
    All available parameters can be listed with `pytools4dart.utils.get_labels()` 
    or in the file labels/labels.tab of the directory pytools4dart of
    package. This list depends on the version of DART pyttols4dart was configured with.
    See [core user guide](./02_core.md) for more details.

  - scene: summary and fast access to the main elements of the mockup scene:
    size, resolution, properties (optical, thermal), plots, object_3d, trees.

  - sensor: summary and fast access to the main element of acquisition:
    bands, sensors, etc.

  - source: summary and fast access to the main elements of the source definition.

  - sequences: the list of sequences that have been added. 
    Each contains its own core, adders to add
    groups and items, and runners to run the sequence simulation and post-process
    the results (stack bands, make RGB composites).

  - add: list of user friendly adders to add elements to
    scene, acquisition, source and sequence.

  - run: list of available runners to:
    - run DART full, 
    - run DART step by step (direction, phase, maket, dart)
    - run sequences
    - build composite images (e.g. RGB)
    - stack raster bands into an ENVI file 
      
It also contains property attributes (read-only):
    - method : the simulation method, i.e. Flux Tracking (0), Monte Carlo (1), Lidar (2).
    - simu_dir, input_dir, output_dir: directory of simulation and input, output subdirectories
     

And the methods:    
    - summary(): a method to print summary, similarly to Scene, Sensor, Source, Sequence.
    - write(): method to write the simulation before running it
    - get_input_file_path(): to get the path of simulation input files
    
The following code shows these different elements:

```python
import pytools4dart as ptd

# Load simulation 'simulationTest'
simu = ptd.simulation('simulationTest')

# Print simulation summary
print(simu)

# Show object attributes
vars(simu)

# Show object properties, i.e. attributes with specific getter/setter
[v for v in vars(type(simu))
    if isinstance(getattr(type(simu), v), property)]

# Show object methods
[v for v in vars(type(simu))
    if callable(getattr(type(simu), v)) and
    not v.startswith('_')]

# Write the simulation
simu.write()

# Run the simulation
simu.run.full()

```

### Empty simulation

In order to run a default simulation without error, when creating a new simulation with DART GUI, it creates as default:
 - a Lambertian optical property called `Lambertian_Phase_Function_1` with model `reflect_equal_1_trans_equal_0_0`
 from database `Lambertian_vegetation.db` (located in $DART_HOME/database). It is used as the default optical property
 for the ground.
 
 - a spectral band at wavelength 560 nm with bandwidth 20 nm

Within `pytools4dart`, while a default optical property can be useful, 
e.g. not to worry about the optical property of the ground,
the default band could generate unintended processing. 

When creating the new simulation, setting argument `empty=True` removes the default band:

```python
simu = ptd.simulation('simulationTest', empty=True)
``` 

To remove default Lambertian property, one can use the following code 
after creating the simulation:

```python
simu.core.coeff_diff.set_nodes(LambertianMulti=[])
``` 
