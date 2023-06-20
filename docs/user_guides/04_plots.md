# Plots

This notebooks shows the several ways of adding plots to a simulation. Indeed,
there aer three ways of adding plots that will depend on the objective:
  - add plot one at a time: `simu.add.plot`
    - pros: easy for common options
    - cons: limited to certain parameters, not adapted for more than a thousand plots (10 s)
		
  - plots file or data.frame: `simu.add.plots`
    - pros: adapted for large number of plots, accelerates DART mockup generation (much faster than with `plots.xml`)
    - cons: limited to certain parameters, although most are available

  - raw interface: `core.plots.Plots.add_Plot`
    - pros: all parameters accessible
    - cons: not addapted for more than a thousand plots (10 s.)

__Warning:__ a plot that has a surface inferior to 10% of the simulation cell surface is ignored by DART, e.g. a plot of 0.3x0.3 = 0.09 is ignored if the cell is 1x1. The cell size in xy could be adapted to 0.5 in order to take it into account.

## User-friendly interface

The user-friendly
interface to plot is the method `simulation.add.plot`. It is the easiest way to
add a plot to a simulation. It is a shortcut to the raw interface. As such it is
restrained to a limited the number of parameters: type, geometry and
coordinates, optical and thermal properties. 

Here is an example of adding two
plots: one of leaf deciduous trees, one of grass and ground.

```python
import pytools4dart as ptd
simu = ptd.simulation('ptd/single_plot', empty=True)
simu.scene.size = [10,10]

simu.add.optical_property(type='Vegetation', ident='leaf_deciduous', 
                          ModelName = 'leaf_deciduous', databaseName = 'Lambertian_vegetation.db')

simu.add.optical_property(type='Vegetation', ident='grass', 
                          ModelName = 'grass_rye', databaseName = 'Lambertian_vegetation.db')

simu.add.optical_property(type='Lambertian', ident='ground', 
                          ModelName = 'loam_gravelly_brown', databaseName = 'Lambertian_mineral.db')

simu.add.plot(type='Vegetation', corners=[[0, 0], [10,0], [10, 10], [0, 10]],
              height = 3, baseheight=1, op_ident = 'leaf_deciduous')

simu.add.plot(type='Ground + Vegetation', corners=[[0, 0], [10,0], [10, 10], [0, 10]],
              height = 1, baseheight=0, op_ident = 'grass',
              grd_op_type = 'Lambertian', grd_op_ident = 'ground')

simu.write()

simu.run.full()

```

## Raw interface

The raw interface, `core_ui` allows the access
to any parameter. 

The list of all the available parameters can be found with:

```python
ptd.core_ui.utils.get_labels('^Plots.Plot')
```

However, not all the parameters are available at the same time. Some are
available only on the condition others have been set before. To illustrate the
purpose, lets check the structure of the plots that have been generated in
previous step:

```python
print(simu.core.plots.Plots.to_string())
```

Here both plots are defined with a vegetation Leaf Area Index (LAI) of value 1.
Lets modify the first plot defining a Leaf Area Density of value $0.3 m^2/m^3$
represented with triangles. The operation must be made in successive steps:

1. change density definition

2. define new density value

3. change leaf area density to triangle representation,
i.e. DART will generate triangles of a
certain size randomly distributed in space but respecting the UF value.

```python
plot = simu.core.plots.Plots.Plot[1]
plot.PlotVegetationProperties.densityDefinition=1
print(plot.to_string())

plot.PlotVegetationProperties.UFVegetation.UF = 0.3

plot.PlotVegetationProperties.trianglePlotRepresentation=1

simu.write()

simu.run.full()
```

## Plots file


Another possibiliy offered by DART is to use an ASCII
file containing the plots specifications in a table (see
`$DART_HOME/database/plots.txt` for an example). The main advantage is that DART
mockup is computed much faster than with the corresponding plots.xml file. A
drawback of this method is that the optical and thermal properties of a plot are
expected to be the indexes of the defined optical and thermal property (e.g.
columns `PLT_OPT_NUMB` and `PLT_THERM_NUMB` in plots.txt). Another drawback of
plots file is that their properties cannot be called in a sequence. As well,
keep in mind is that it allows a access to the main plot parameters, but the
rest is fixed with DART default values.

In python using a tabular file allows
managing the plots in a dataframe, which is much faster and easier for numerous
plots. In order to make easier the link to optical and therma properties are
made through names instead of indexes. For example, if the columns
`PLT_OPT_NAME` and `PLT_THERM_NAME` are present, they will be used to update the
corresponding `PLT_OPT_NUMB` and `PLT_THERM_NUMB` expected by DART.

```python
# Example plots.txt
plots_file = ptd.getdartdir() / 'database' / 'plots.txt'
ptd.tools.plots.read(plots_file)

```

To illustrate the use of plots file, let's add 10x10 Vegetation plots of $1m^3$
with a gradient of Chlorophyll concentration (`Cab` parameter in prospect).

```python
import pytools4dart as ptd
import pandas as pd
simu = ptd.simulation('Cab_gradient', empty=True)

# set scene size
simu.scene.size = [20, 20]

# add spectral RGB bands, e.g. B=0.485, G=0.555, R=0.655 nm
# with 0.07 full width at half maximum
for wvl in [0.485, 0.555, 0.655]:
    simu.add.band(wvl=wvl, bw=0.07)

simu.core.maket.Maket.exactlyPeriodicScene=0

PLT_TYPE = 1 # Vegetation
BORDER_REPETITION = 0
PLT_BTM_HEI = 0 # baseheight of plot (m)
PLT_HEI_MEA = 1 # plot height (m)
VEG_DENSITY_DEF = 1
VEG_UL = 1
plots = []

for i in range(10):
    for j in range(10):
        plot_number = i+10*j
        PT_1_X, PT_1_Y = i, j
        PT_2_X, PT_2_Y = i+1, j
        PT_3_X, PT_3_Y = i+1, j+1
        PT_4_X, PT_4_Y = i, j+1
        PLT_OPT_NAME = 'op_prospect_{}'.format(plot_number)
        # PLT_OPT_NAME = 'prospect_op'
        simu.add.optical_property(type='Vegetation', ident=PLT_OPT_NAME,
                                  databaseName = 'prospect_test.db', ModelName='', 
                                  prospect={'CBrown': 0, 'Cab': float(plot_number)/2, 'Car': 5,
                                            'Cm': 0.01, 'Cw': 0.01, 'N': 1.8,
                                            'anthocyanin': 0})
        
        plots.append([PLT_TYPE, BORDER_REPETITION, PT_1_X, PT_1_Y, PT_2_X, PT_2_Y, PT_3_X, PT_3_Y, PT_4_X, PT_4_Y, PLT_BTM_HEI, PLT_HEI_MEA, PLT_OPT_NAME])

plots_df = pd.DataFrame(plots, columns = ['PLT_TYPE', 'BORDER_REPETITION', 'PT_1_X', 'PT_1_Y', 'PT_2_X', 'PT_2_Y', 'PT_3_X', 'PT_3_Y', 'PT_4_X', 'PT_4_Y', 
                                          'PLT_BTM_HEI', 'PLT_HEI_MEA', 'PLT_OPT_NAME'])

simu.add.plots(plots_df)

# write simulation
simu.write(overwrite=True)
# run simulation
simu.run.full()

simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')

```
