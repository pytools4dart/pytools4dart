# 1.1.4

## Fix

- stack_bands in hstools: bands were not sorted correctly,
giving randomly ordered spectra

# 1.1.3

## Fix

- new parameter from DART 1142: Center3D in object_3d geometry
- method sequence.get_db_path
- method sequence.get_sequence_df for string parameters

# 1.1.2

## Fix

- python 2/3 related:
    - open Tree_file in UTF-8
    - to_string methods of core nodes
- requirements for pip install
- headless server DART computing

- method objreader.get_dims
- method sequence.get_db_path

## Change

- update guides

# 1.1.1

## Fix
- python 2 and 3 compatibility
- windows compatibility


## Add
- documentation website
- configuration tests
- continuous integration


# 1.0

## Bug fix
- objects group numbering fixed java HashMap as in DART (makes package jnius necessary until DART change).

## Change
- change DART DAO .obj reader for C++ [tinyobj](https://gitlab.irstea.fr/florian.deboissieu/tinyobj.git),
reads .obj x10 faster. Compatibility maintained without it.

## Add
- 2D rotation and translation of voxel grid


  