# Simulation

Simulation object is corresponding to a DART simulation.
It allows for storing
and editing parameters, and running simulation.

It contains the following
attributes:

  - core: objects representing DART XML input files (coeff_diff,
directions, phase, ...) with a raw interface to access and change parameters.
Each module correspond to a part of DART GUI. As in DART GUI, changes propagates
automatically to subnodes. All available parameters are listed in
pytools4dart.core_ui.utils.get_labels() or in the file labels/labels.tab of the
package. See [core use guide](#core) for more details.

  - scene: summary and fast access to
the main elements of the mockup scene : size, resolution, properties (optical,
thermal), plots, object_3d, trees.

  - sensor: summary and fast access to the
main element of acquisition: bands, sensors, etc.

  - source: summary and fast
access to the main elements of the source definition.

  - sequences: the list
of sequences that have been added. Each contains its own core, and adders to add
groups and items.

  - add: list of user friendly adders to add elements to
scene, acquisition, source and sequence.

  - run: list of available runners,
full, step by step, composites, sequences.

The following code shows the elements of the content of these different elements:

```python
import pytools4dart as ptd

simu = ptd.simulation('simulationTest')

```
