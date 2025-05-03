# pyvicar
Python shell for in-house Vicar3D Immersed Boundary Method CFD Solver. 
It enables seamless connections between numpy dataset and input/output files, 
programmable batch generation and postprocessing,
and provides tools to generate grids and surface mesh.


## Requirement
- numpy (dataset data structure)
- numpy-stl (reading .stl geometries)
- pandas (reading output tables)
- pyvista (mesh visualization and postprocessing)
- mpi4py (parallel postprocessing)

## Examples

### Input

#### Config

Configuration is set in the style of:
<pre>
from pyvicar.case.version import Case

c = Case('casepath')

c.input.parallel.npx = 4
c.input.parallel.npy = 4
c.input.bc.x1.bcx1 = 'dirichlet'
c.input.bc.x1.ux1 = 1.0

c.write()
</pre>

#### Grid

To setup nonuniform grid:
<pre>
from pyvicar.case.version import Case
from pyvicar.grid import Segment

middle = Segment.uniform_dx(start=1, end=2, dx=0.01)
left = Segment.grow_toward_left(rterminal=middle, lend=0, growthrate=1.05)
right = Segment.grow_toward_right(lterminal=middle, rend=3, growthrate=1.05)
xaxis = left + middle + right

c = Case('casepath')

c.xgrid.enable()
c.xgrid.nodes = xaxis

c.write()
</pre>

#### Geometry

To import an .stl 3D surface:
<pre>
from pyvicar.case.version import Case
from pyvicar.geometry import TriSurface

# startIdx = 1 by default, same as input file
surf = TriSurface.from_stl('geometry.stl', startIdx=1)
# TriSurface.from_xyz_conn is also provided for raw data

c = Case('casepath')

c.unstrucSurface.enable()
c.unstrucSurface.surfaces.resetnew(1)
# this index starts at 1 by default (can be set), same as input file
unstruc1 = c.unstrucSurface.surfaces[1]
unstruc1.nPoint = surface.xyz.shape[0]
unstruc1.nElem = surface.conn.shape[0]
unstruc1.xyz = surface.xyz
unstruc1.conn = surface.conn

c.write()
</pre>

or create an extruded surface based on 2D curve:
<pre>
from pyvicar.case.version import Case
from pyvicar.geometry import Spanned2DCurve

x = np.arange(0, 1.1, 0.1)
y = np.arange(0, 1.1, 0.1)
points = np.concatenate((x[:,np.newaxis], y[:,np.newaxis]), axis=1)

# Spanned2DCurve inherits TriSurface with more properties like nz
surf = Spanned2DCurve.from_2d_xy(points, nz=3, dz=0.1, startIdx=1)

...
</pre>


### Output

#### Drag Lift Forces
<pre>
import matplotlib.pyplot as plt
from pyvicar.case.version import Case

c = Case('casepath')

c.read()

# if no output is available
if not c.draglift:
    return

# .ravel() is used because the underlying dataset is a n*1 2d array
time = c.draglift[1].time.ravel()
cyp = np.zeros_like(c.draglift[1].cyp.ravel())
# compute the sum of the lift on all bodies
for body in c.draglift:
    cyp += body.cyp.ravel()

plt.plot(time, cyp, label="sum", color="k", linewidth=2)
plt.legend()
plt.show()
</pre>
