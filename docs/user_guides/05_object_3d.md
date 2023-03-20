# Object 3D

This notebook aims at showing the ways of including objects into the mockup.

```python
# imports necessary for the notebook
from path import Path
import matplotlib.pyplot as plt
import pytools4dart as ptd
```

Through a simple example, it presents the way to manage 3D objects as well as a few considéreations about DART functionning with objects.

## Construction of object file

First thing first, at the construction of an .obj file, one has to know that DART considers the object to be in a X forward, Y up system. In other words, the
vertex coordintaes must be written in the following order inside the .obj file:

```
v y z x
```

The code below creates an obj file with a rectangle of
coordinates in meters $x_{min}=2$, $y_{min}=1$, $x_{max}=5.5$, $y_{max}=4$ at $z=3$.

```python
obj_str = '''
v 4.0 3.0 2.0
v 4.0 3.0 5.5
v 1.0 3.0 5.5
v 1.0 3.0 2.0
f 2 1 4
f 3 2 4
'''

obj_file = Path('data').abspath()/'rectangle.obj'
with open(obj_file, mode='w') as f:
    f.write(obj_str)
```

## Simple simulation

The following code produces a simple RGB simulation with that rectangle 3 m over the
ground.

```python
simu = ptd.simulation('object_3d', empty=True)

simu.scene.size = [10, 10]
simu.scene.cell = [.1, .1]

# RGB bands
for wvl in [0.485, 0.555, 0.655]:
    simu.add.band(wvl=wvl, bw=0.07)

# ground optical properties
op_ground = {
    'type':'Lambertian',
    'ident':'ground',
    'databaseName':'Lambertian_mineral.db',
    'ModelName':'clay_brown'}
    #  'ModelName':'reflect_equal_1_trans_equal_1_1'}
    

simu.add.optical_property(**op_ground)
simu.scene.ground.OpticalPropertyLink.ident='ground'

# target properties
op_vegetation = {'type':'Lambertian',
              'ident': 'target',
              'databaseName':'Lambertian_vegetation.db',
              'ModelName':'grass_rye'}

op = simu.add.optical_property(**op_vegetation)

# object
obj3D = simu.add.object_3d(obj_file, xpos=0, ypos=0, zpos=0) # give position in scene
obj3D.objectDEMMode = 2 # ignore ground for vertical anchor
obj3D.ObjectOpticalProperties.OpticalPropertyLink.ident = 'target' # set optical property

# write and run simulation, and make the composite image
simu.write(overwrite=True)
simu.run.full()

# show image
rgbDpath = simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')
imageFpath = rgbDpath.glob('ima01*.png')[0]
image = plt.imread(imageFpath)
plt.imshow(image)
plt.show()
```

### objectDEMMode

Setting object option `objectDEMMode=2` tells DART to 'Ignore DEM' for the vertical position of this object. 

By default, the options is `objectDEMMode=0` corresponding to 'Put on DEM', that is setting objects $z_{min}$ to $z_{ground}$.
In our case, as the ground is flat, it would cover the object, thus the image would show only the ground reflectance.

```python
simu = ptd.simulation('object_3d')
simu.name = 'object_3d_on_DEM'
obj3D.objectDEMMode = 0 # shifts obj such that minimum Z corresponds to ground altitude, "covering" the flat obj here.
simu.write(overwrite=True)
simu.run.full()
rgbDpath = simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')

imageFpath = rgbDpath.glob('ima01*.png')[0]
image = plt.imread(imageFpath)
plt.imshow(image)
plt.show()

```

### Normal orientation

Another issue that may occure is the wrong orientation of the face normals. 
DART considers the face normal vector to define which is the "front face" (same direction as the face normal) and which is the back face (opposit direction to the face normal).
The face normal is defined by the order of the faces vertices using the [right hand rule](https://en.wikipedia.org/wiki/Right-hand_rule#/media/File:Right-hand_grip_rule.svg).

When the normal are wrongly defined, the corresponding triangle may not appear, i.e. absorbing all light.
To illustrate this issue, the following code flips up-side down one of the triangles changing `f 2 1
4` to `f 4 1 2`. The same simulation as [the first one](#simple-simulation) is then run.

```python
# show the top view of the shape 
plt.clf()
plt.scatter([2,5.5,5.5,2],[4,4,1,1])
for i, [x, y] in enumerate(zip([2,5.5,5.5,2],[4,4,1,1])): 
    plt.text(x+.1,y,str((i+1)))
plt.show()

obj_str = '''
v 4.0 3.0 2.0
v 4.0 3.0 5.5
v 1.0 3.0 5.5
v 1.0 3.0 2.0
f 4 1 2
f 3 2 4
'''

obj_file = Path('data').abspath()/'rectangle_wrong.obj'
with open(obj_file, mode='w') as f:
    f.write(obj_str)

simu = ptd.simulation('object_3d')
simu.name = 'object_3d_wrong_orientation' # new simulation based on previous
obj3D = simu.scene.object3D.source[0]
obj3D.file_src = obj_file
simu.write(overwrite=True)
simu.run.full()
rgbDpath = simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')

imageFpath = rgbDpath.glob('ima01*.png')[0]
image = plt.imread(imageFpath)
plt.clf()
plt.imshow(image)
plt.show()
```

One way to avoid this problem, without having to check that all the triangles are facing correctly the light source, 
is to consider the triangles are double face giving the same optical properties to
both sides. However, keep in mind that this will allow reflections on the back face...

```python
obj3D.ObjectOpticalProperties.doubleFace=1
obj3D.ObjectOpticalProperties.BackFaceOpticalProperty.OpticalPropertyLink.ident = 'target'

simu.write(overwrite=True)
simu.run.full()
rgbDpath = simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')

imageFpath = rgbDpath.glob('ima01*.png')[0]
image = plt.imread(imageFpath)
plt.clf()
plt.imshow(image)
plt.show()
```

## Object with group

Objects can contain groups. In that case, optical and thermal properties can be set at the scale of the object (option `sameOPObject=1`), 
or at the scale of the of the group (option `sameOPObject=0`).

In the same manner as for optical properties and bands, it is the group number that is meaningful for DART in the attribution of the properties.
However, unlike for properties or bands, it is not the position in the group list that tells the group number, but the group name inside the file.
As such, if a group is given the wrong group number (e.g. changed manually), the properties would be wrongly attributed to another group. 

```python
simu = ptd.simulation('object_3d')
simu.name = 'ptd_Cherry_Tree' # new simulation based on previous
# remove previous object
obj3D = simu.core.object_3d.object_3d.ObjectList.Object = []
# add a tree object with 2 groups
obj_file = ptd.getdartdir()/'database'/'3D_Objects'/'Tree'/'Accurate_Trees'/'Cherry_tree'/'Merisier_Adulte.obj'
obj3D = simu.add.object_3d(obj_file, xpos=5, ypos=5, xscale=2, yscale=2, zscale=2)

for g in obj3D.Groups.Group:
    print('{} : {}'.format(g.num, g.name))

# add optical properties
simu.add.optical_property(ident='wood', ModelName='fraxinus_excelsior_stem',
                          databaseName='Lambertian_vegetation.db')
simu.add.optical_property(ident='leaf', ModelName='fraxinus_excelsior_leaf',
                          databaseName='Lambertian_vegetation.db')

obj3D.Groups.Group[0].set_nodes(ident='leaf')
obj3D.Groups.Group[1].set_nodes(ident='wood')

simu.write(overwrite=True)
simu.run.full()
rgbDpath = simu.run.colorCompositeBands(red=2, green=1, blue=0, iteration='X', outdir='rgb')

imageFpath = rgbDpath.glob('ima01*.png')[0]
image = plt.imread(imageFpath)
plt.clf()
plt.imshow(image)
plt.show()
```
