# Cross dependcies between core modules

This document aims at listing the dependencies between DART xml nodes 
(usually of different xml files) that are not ruled by the templates. 
These dependencies are handled in pakage `pytools4dart` with update methods automatically
called when writing the simulation to configuration XML files (`simulation.write()`).

_If you find any cross-dependency that is not well handled by pytools4dart, please let us know._

## Optical Property Links and Optical Properties

In DART, an optical property is identified by two attributes:
    
- `type` (Lambertian, Vegetation, etc.)
- `ident` , i.e. its name defined by user,
- `index` implicitly defined as its position in the list. 

As an example, when creating a new simulation, it creates by default a Lambertian property named 
`Lambertian_Phase_Function_1` that has the index 0 of Lambertian optical properties.
If a new Lambertian optical property was created it would have the index 1.
If a new turbid Vegetation optical property was defined it would have an index 0.

In DART GUI, when attributing an optical property to an element of the scene
(Plots, Trees, object_3d, ..., or any part of it), a drop down list appears 
to allow the user selecting the name of the wanted property. When selecting a property, 
in the background DART GUI fills a node `OpticalPropertyLink`, e.g. in file plots.xml, with its `type`, `ident` 
and corresponding `index` number.

However, when running a simulation, DART only considers its `type` and `index`.
Its `ident` is not taken into account. In consequence, if the `ident` of an 
`OpticalPropertyLink` is modified 
manually in the XML file, e.g. plots.xml, and not in the optical property file 
(coeff_diff.xml),
no error is thrown, although `ident` is not corresponding
to the right `index`.

To avoid such an issue in package `pytools4dart`, `ident` is considered as the
indexing value. Thus, `index` value is not considered during the configuration of the simulation.
The index is automatically updated at the writing of the scene element configuration files, using method
`update_opl` (for OpticalPropertyLink update) of `core` class. This behaviour implies 
a restriction when choosing the name (`ident`): it must be unique across the 
optical properties of the simulation.

## Thermal proerties

The same issue as for optical properties arrises with thermal properties and attributes `idTemperature`,
i.e. given name, and `indexTemperature`, i.e. index number, of nodes `ThermalPropertyLink`.
Thus, a behaviours similar to optical properties was adopted in `pytools4dart`
for thermal properties: method `update_tpl` updates automatically the `ThermalPropertyLink`
with the `indexTemperature` number corresponding to the `idTemperature`. The `idTemperature`
must be unique among thermal properties.

## Band number

Band number has an issue similar to optical properties.
In DART GUI, band number is automatically updated at each new declaration or removal of a band.

In `pytools4dart` the update is done with method `update_bn`.

The band number update is not done at each modification of the band list as 
it would slow down the addition of several thousands bands, e.g. in hyperspectral simualtion.
The band numbering is automatically updated when writing the simulation.

## Multiplicative Factors and Spectral Bands

Multiplicative factors are used to modify spectral signature in `coeff_diff` module. 
DART requires as many `MultiplicativeFactorForLUT` as the number of spectral bands defined in `phase` module,
whether the option `useSameFactorForAllBands` is `0` or `1`.

In `pytools4dart` it is made with method `update_mf`.