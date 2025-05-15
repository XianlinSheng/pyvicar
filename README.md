# pyvicar
Python shell for in-house Vicar3D Immersed Boundary Method CFD Solver. 
It enables seamless connections between numpy dataset and input/output files, 
programmable batch generation and postprocessing,
and provides tools to generate grids and surface mesh.


## Requirement
- numpy (dataset data structure)
- numpy-stl (reading .stl geometries)
- pandas (reading output tables)
- matplotlib (visualize dataset)
- mpi4py (parallel postprocessing)
- ffmpeg-python (convert frames to video files)
- pyvista (mesh visualization and postprocessing) Important:
*on an off-screen server, 
a specific osmesa build of vtk needs to be installed before pyvista*:
<pre>
conda install -c conda-forge vtk=*=osmesa*
conda install -c conda-forge pyvista # or pip install pyvista
</pre>
conda forge might not have the newest python build for pyvista, 
but pip install will work too.


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

#### Animations
<pre>
import pyvista as pv
from itertools import product
import pyvicar.tools.mpi as mpi
from pyvicar.case.version import Case


# sync mode (default): all processors working on same case
mpi.set_sync()


cases = ["case1", "..."]
for case in cases:
    c = Case(case)

    c.read()
    c.post.enable()
    c.post.animations.enable()
    c.post.animations.del_animations()
    anivel = c.post.animations.add_new("vel")
    anivel.frames.enable()

    for vtk in c.dump.vtk.mpi_dispatch():
        mesh = vtk.to_pyvista()
        # here starts pyvista

        plotter = pv.Plotter(off_screen=True)
        # contour scalar bar
        scalar_bar_args = {
            "title_font_size": 40,
            "label_font_size": 36,
            "position_x": 0.9,      # horizontal position (0 to 1)
            "position_y": 0.05,     # vertical position (0 to 1)
            "width": 0.05,
            "height": 0.3,
            "vertical": True,       # or False for horizontal bar
            "color": "white",
        }
        plotter.add_mesh(
            clipped_slice,
            scalars="VEL",
            cmap="coolwarm",
            clim=[0, 1.2],
            scalar_bar_args=scalar_bar_args,
        )

        plotter.view_xy()           # Set view to XY plane
        plotter.set_background("white")
        plotter.camera.parallel_projection = True
        plotter.camera.zoom(2.2)

        # save to a frame png
        anivel.frames.from_pyvista(
            vtk.seriesi, plotter, window_size=[3840, 2160]
        )


# async mode: processors are irrelavant to each other
# this is necessary if running mpi async
mpi.set_async()


anis = ["vel", "..."]
span = list(product(cases, anis))       # cartesian product (flatten nested loops)
for case, aniname in mpi.dispatch(span):
    c = Case(case)

    c.read()
    # convert frames to videos
    c.post.animations[aniname].frames.to_video(quiet=True)

</pre>
where MPI is used to postprocess in parallel. 
The script with MPI is fully compatible with pure serial one:
<pre>
python post_with_mpi.py
</pre>
is equivalent to a serial code. To run in parallel, use:
<pre>
mpirun -np x python post_with_mpi.py
</pre>

Two parallel modes are shown in the example: sync and async.

Sync mode is used when all processors work on the same directory (case), 
so they need to be synchronized to update any changes in the folder 
and the tree structure of Case.
All processors are aligned: 

- upon mpi.set_sync() ends (initial alignment)
- upon mpi.set_async() starts (final alignment)
- right after folder / file changes (all necessary middle keypoints)

The keypoints during the process are handled internally, 
and at the beginning there is an implicitly set_sync(),
so one may ignore setting modes when all processors are always modifying same cases.
For example, in the same case, use multiple processors to generate frames in parallel.

However, when trying to modify different cases, Case needs to know that it does not need to 
wait for others when it is modifying something, so explicit set_async() is mandatory
before starting an async block.


