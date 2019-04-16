---
title: Cross dependcies between core modules
Author: Florian de Boissieu
Date: 2019-01-22
---


This document aims at listing the dependencies between DART xml nodes (usually of different files) that are not ruled by the templates.

# Optical Property Links and Optical Properties
Optical Property Links (`OpticalPropertyLink` in the code) are present in all elements of the scene (Plots, Trees, object_3d, ...). 
The key to the corresponding optical property is made through the attributes `index` and `type`.
However, for ease of use in DART GUI, the user chooses through `OpticalPropertyLink.ident`. 

A different strategy is adopted in the package. `ident` is the primary key (one cannot name two properties with the same name). 
Optical Property Link are created with `index=0`, and the `index` is updated afterwards with method `update_op` or at `write`.

# Multiplicative Factors and Spectral Bands
Multiplicative factors are used to modify spectral signature in `coeff_diff` module. 
DART requires as many `MultiplicativeFactorForLUT` as the number of spectral bands defined in `phase` module,
and this whether the option `useSameFactorForAllBands` is `0` or `1`.

In the package it is made with `update_mf`.

# Band number
In DART GUI, band number is automatically updated at each band new declaration or removal.

In the package the same is done with `update_band_numbers`.

It is not done at each modification of the band list as it would slow down the addition of several thousands in hyperspectral.
However, the band numbering is automatically updated when writing the simulation.