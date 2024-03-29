# DART conventions

The conventions adopted in DART may be different of the usual/general standard of GIS,
specially concerning the scene orientation and the azimuth angles.
This user guide documents these specific conventions of DART that the user should bear in mind 
to parametrize correctly the simulations.

These conventions are illustrated within use_case_6.py (scene orientation) and use_case_7.py (solar azimuth angle).

## Scene orientation

The orientation standard usually used in GIS for rasters is the following:
```
o -- x+
:
y-
```
In that case a raster file read with GDAL would have the following properties:

- geotransform, i.e. the transformation to x,y coordinates from col,row index:
    
    ```python
    T = (xres, 0, xmin, 0, yres, ymax) # with yres < 0
    x = col * T[0] + T[2]
    y = row * T[4] + T[5]
    ```     
    
- array of values, with the convention that top left is row,col = 0,0:
    - index row,col = 0,0 --> pixel at xmin, ymax
    - index row,col = 1,0 --> pixel at xmin, ymax + yres
    - index row,col = 0,1 --> pixel at xmin + xres, ymax

Although GDAL allows to parametrize differently, several codes/software and help that is given on the forum admit
the above convention as the rule.  

The scene orientation in DART has the convention of image:
```
o -- y+
:
x+
```

Thus the raster images produced by a simulation are following this same convention, which has consequences on:
- geotransform, i.e. the transformation to x,y coordinates from col,row index:
    
    ```python
    T = (yres, 0, ymin, 0, xres, xmin) # with yres > 0
    x = row * T[4] + T[5]
    y = col * T[0] + T[2]
    ```    
- indexes of array:
    - index row,col = 0,0 --> pixel at xmin, ymin
    - index row,col = 1,0 --> pixel at xmin + xres, ymin
    - index row,col = 0,1 --> pixel at xmin, ymin + yres


As one can notice, there is only a 90° rotation between the two configurations, 
and an opposit ordination of y-axis.
The rotation from DART convention to GIS convention can be achieved with function `pytools4dart.hstools.rotate_raster`.
It is a 2 steps operation:
- reorder the transposition parameters: (yres, 0, ymin, 0, xres, xmin) --> (xres, 0, xmin, 0, -yres, ymax)
- transpose and flip up-down the array: `img_gis = np.flipud(im_dart.transpose())`

The rotation of the raster from DART orientation to GIS standard orientation is also the default behavior of `stack_bands`
 
See the `use_case_6.py` for an example in real.


## Azimuth angle

The standard definition of the azimuth angle, adopted in numerous fields (navigation, satellite, meteorology, ...), 
is North = 0° and increases clock-wise, i.e. East = 90°, South = 180°, West = 270°. 
Thus with the usual GIS raster standard, i.e. x as the West-East axis and y as the South-North axis:
```
       0° (y+)
       |
270° --o-- 90° (x+)
       |
      180°
```

In DART, the azimuth angle convention is:
```
      90° (y+)
       |                                            
180° --o-- 0° (x+)
       |
      270°
      
or keeping DART orientation:

      180°
       |
270° --o-- 90° (y+)
       |
       0° (x+)
```
See `use_case_7.py` for an example of the impact of solar azimuth angle on the shades.

Thus, to compute a DART azimuth angle from a standard azimuth angle and reverse, the operation is the following:
```python
az_dart = np.mod(90. - az_std, 360.)
az_std = np.mod(90. - az_dart, 360.)
``` 

## Sun location by date and scene coordinates

In DART, instead of defining the Sun angles, it is possible to have the Sun location computed giving the geographical coordinates of the scene
and the date of acquisition. However, the South is considered to be at azimuth = 0° when the scene is located in the North hemisphere,
i.e. (x+) direction in the DART angle system, and the opposit when considering 

In order to have the South correctly located, (y-) direction for scene, the azimuth of the Sun location can be shifted by -90°. See the end `use_case_7.py` for an example.

