# pyvicar
Python shell for in-house Vicar3D Immersed Boundary Method CFD Solver. 
It enables seamless connections between numpy dataset and input/output files, 
programmable batch generation and postprocessing,
and provides tools to generate grids and surface mesh.


## Dependencies
- python>=3.8,<3.13
- numpy (dataset data structure)
- scipy (postprocessing tools)
- numpy-stl (reading .stl geometries)
- trimesh (operating triangular meshes)
- pandas (reading output tables)
- h5py (storing database, can be auto handled by conda)
- matplotlib (visualize dataset)
- mpi4py (parallel postprocessing)
- ffmpeg (convert frames to video files, can be auto handled by conda)
- ffmpeg-python (python controller of above)

## Install
Before installing pyvicar, 
make sure the following dependencies are handled well

### mpi, mpi4py

If using existing MPI library, 
make sure the mpi4py wrapper links against it correctly:
<pre>
which mpicc
pip install --no-binary mpi4py --no-cache-dir --force-reinstall mpi4py
python -c "from mpi4py import MPI; print(MPI.Get_library_version())"
</pre>

For a full new MPI environment handled by conda, simply:
<pre>
conda install -c conda-forge mpi4py
</pre>
and conda will auto install an MPI impl.
But ViCar3D relies on intel toolchain so typically 
one will need to pip build and link to intel MPI.

### ffmpeg, ffmpeg-python

Use conda to install ffmpeg backend and python wrapper together:
<pre>
conda install -c conda-forge ffmpeg-python
</pre>

### vtk, pyvista

VTK can use X server, off-screen CPU, or off-screen GPU,
but pip does not provide full pre-builts on these backends,
so recommend using conda directly.
Typically one need to install osmesa build on cluster 
otherwise it will be stuck in endless wait for an X server.
When postprocessing is taking too much time while 
still generating nothing, it might be in a deadlock 
waiting for the response from an X server that does not even exists. 
egl is not tested and x/osmesa based on cpu are the stable recommended approach. 
<pre>
conda install -c conda-forge vtk           # normal with x server
conda install -c conda-forge vtk=*=osmesa* # headless cpu
conda install -c conda-forge vtk=*=egl*    # headless gpu

python -c "import vtk; rw = vtk.vtkRenderWindow(); print(rw.GetClassName())"
</pre>
Especially on cluster or X display server is not available, 
make sure this shows an OS (Off Screen) type.

Then, pyvista is available on conda-forge 
so it can be installed in either way.
<pre>
conda install -c conda-forge pyvista # conda forge
pip install pyvista                  # pip install
</pre>
or it will be pip installed automatically 
when directly calling pip install pyvicar

### pyvicar
<pre>
git clone https://github.com/XianlinSheng/pyvicar.git
cd pyvicar
git checkout v1.0.0 # or other release tag
pip install .
</pre>
pip can install the rest automatically.
If one want to keep consistency with conda:
<pre>
conda install -c conda-forge    \
    numpy scipy numpy-stl       \
    trimesh pandas h5py matplotlib
</pre>



## Examples

Foundamentally, configuration is set in the style of:
<pre>
from pyvicar.case import Case

c = Case('case_folder_path')

c.input.parallel.npx = 4
c.input.parallel.npy = 4

c.input.domain.xout = 10
c.input.domain.yout = 5
c.input.domain.zout = 5

c.input.domain.nx = 129
c.input.domain.ny = 65
c.input.domain.nz = 65

c.input.bc.x1.bcx1 = 'dirichlet'
c.input.bc.x1.ux1 = 1.0

c.write()
</pre>
Default values will apply if not specified,
check the generated files to see the defaults.

To setup custom grid:
<pre>
from pyvicar.case import Case
from pyvicar.grid import Segment

middle = Segment.uniform_dx(start=1, end=2, dx=0.01)
left = Segment.grow_toward_left(rterminal=middle, lend=0, growthrate=1.05)
right = Segment.grow_toward_right(lterminal=middle, rend=3, growthrate=1.05)
xaxis = left + middle + right

c = Case('case_folder_path')

c.xgrid.enable()
c.xgrid.nodes = xaxis

c.write()
</pre>

These basic operations are equivalent of setting input files but programmable.
When starting to set multiple bodies, cases, and optimize grid refinements and generations,
these might seem too low-level, so in fact pyvicar already wraps up 
some frequently-used operations into tool functions
and can accomplish a human-level command by one function call.

For example, the following short script 
can setup a flow past sphere at given resolution
in 10 lines of code, with a sphere mesh being made, 
a suitable and locally refined grid being generated,
multiple coupled body element and placement entries being handled,
several lines of BC type and values being compressed,
and physical parameters being transformed.
<pre>
from pyvicar.case import Case

d = 1
U = 1
re = 200
dx = d / 20

c = Case('case_folder_path')
gm = c.create_grid(l0=d, dx=dx)
body, surf = c.append_sphere(d / 2, dx, gm.center)
c.set_inlet("x1", [U, 0, 0])
c.set_re(re, U=U, L=d)

c.write()
</pre>

ViCar3D has multiple versions for different or special uses,
and pyvicar provides the ability to use them in the same API
for common jobs.
Even for unique features it will still keep a 
consistent style of using and help query.
A standard ViCar3D distribution contains a 
bin/ for executables, and a lib/ for internal dependencies 
and pyvicar_addons support.
In the above few examples we were using the minimal common
built-in config formats and entry options, 
and to work on a specific distribution,
simply change how to import the Case class:
<pre>
import pyvicar

Case = pyvicar.import_case("your/path/to/distribution")

d = 1
U = 1
re = 200
dx = d / 20

c = Case('case_folder_path')
gm = c.create_grid(l0=d, dx=dx)
body, surf = c.append_sphere(d / 2, dx, gm.center)
c.set_inlet("x1", [U, 0, 0])
c.set_re(re, U=U, L=d)

c.write()
</pre>
The distribution path is the root folder that sees root/bin, root/lib.
Sanity and version check will be done during importing,
and it will throw exceptions if the installation
is not complete, the support is corrupted, 
or the support relies on features too old or too new in this pyvicar framework.
Different distributions may vary in the available options 
of the entries, may provide additional models or features, 
and tool functions too.

Further examples are located in the examples folder 
covering how to generate 2D/3D bodies, make common postprocessings, 
and to manage a complete project with multiple simulations 
and batched postprocessings.
These examples shown in this pyvicar main framework are considered
common jobs and are supported in all distributions.
Examples of unique features will be bundled with the 
pyvicar_addons in a specific ViCar3D version.

