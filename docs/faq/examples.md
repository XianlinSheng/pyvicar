# Examples FAQ


## How do I find the best example to start with?

Examples are grouped in [examples](#examples/) folder. 
If focusing on generating a single case, you should focus on `01_geometry` and `02_motion`. 
If no motion is involved, use `01_geometry` and choose an example given the
dimensionality (2/3D), geometry topology (solid/membrane), and how the data is provided (preset/data). 
`trisurf` is to use data prepared in python script and assemble into a supported structure.
See [What is a 2D case?](#what-is-a-2d-case), 
[What are the geometry topologies?](#what-are-the-geometry-topologies), 
[What geometry presets are available?](#what-geometry-presets-are-available), 
[What are the data structures of geometries?](#what-are-the-data-structures-of-geometries).  
If motion is present, use `02_motion` as the starting point. 
These examples also cover 2/3D and solid/membrane, but only use preset geometries.
If the geometry is described by data, 
fetch the geometry creation block in a suitable `01_geometry` example 
and replace the one in `02_motion` as part of your later modifications.
See [How is a geometry created in different ways?](#how-is-the-geometry-created-in-different-ways),
[Why do I start with motion and substitute geometry but not reversed?]
(#why-do-i-start-with-motion-and-substitute-geometry-but-not-reversed)
If doing postprocessing on a single case, use `03_postprocess` and choose the needed job.
If multiple dump jobs are needed, 
prefer `07_compact_post` rather than combining single jobs one by one.
See [What is dump post?](#what-is-dump-post), [What is compact post?](#what-is-compact-post).
If working on a project, use `04_project` and find a suitable study style.
Typically a flow past sphere would suffice and further modifications can refer to single-case senario.
See [What is a project and study?](#what-is-a-project-and-study).


## What do I typically do after adapting an example?

Once you have chosen an example, first get familiar with it and try to run it if possible.
This gives you a clean start without coming back and worrying about environment later.
See [How to run an example?](#how-to-run-an-example),
[What is the typical layout of an example script?](#what-is-the-typical-layout-of-an-example-script).
Then, modify the blocks accordingly that need specified settings.
The layouts in `01_geometry` and `02_motion` are almost the same, 
so you can also grab the needed block from another example file.
Typically combining blocks in these example files would solve your questions about how to set,
but the exact data to set may come from other sources or computations.
If you want to use a third party python package,
prefer the existing ones listed in `pyproject.toml` dependencies.
If it is not explicitly required to remove a certain block,
you should keep the content in the example because they can be essential basics,
without which the settings might be incomplete,
or they are likely needed in the future so it is pointless to remove it.
See [settings](#docs/faq/settings.md) and [functions](#docs/faq/functions.md) sections 
for details on their roles and behaviors.


## What is a 2D case?

ViCar3D architecture is coded in 3D but can solve 2D problems 
by making z direction containing only 2 cells, 
but note that 2D is still different from simply choosing a special number of cells in z. 
In pyvicar, you can forget about the tricky requirements in ViCar3D and provide only the 2D geometries, 
where a solid is a closed curve in 2D coordinate list, and a membrane is an open one. 
There will be a dim2=True option in grid model and dz argument to append a geometry. 
See the functions.


## What are the geometry topologies?

There are 2 types of topologies: 
solid, whose internal space is not part of the fluid, like a solid sphere, 
and membrane, who has no internal space and both sides are wet, like a plate. 
In 3D these are described by closed or open surfaces in 3D coordinates, 
and 2D uses curves in 2D coordinates.


## What geometry presets are available?

3D supports sphere and rectangular plate. 2D supports circle and straight line.
These can be created by functions:
`c.append_sphere`, `c.append_plane`, `c.append_cyl_2d`, `c.append_plane_2d`.
See [functions](#docs/faq/functions.md) for function usages.


## What are the data structures of geometries?

3D geometry is represented by a surface in 3D coordinates, 
and 2D is by a curve in 2D coordinates. 
The generic structure of a 3D surface is wrapped in `TriSurface` class and contains 2 parts: 
point coordinate list and a connectivity list. 
They are shaped in (n_point, 3) float and (n_element, 3) integer. 
The nth row of point coordinate list is the xyz coordinate of the nth point 
and the nth row of the connectivity is the 3 point indexes of the nth triangle element. 
Index starts at 1. 
2D structure is more straightforward and has no wrappers. 
It’s simply a coordinate list shaped in (n_point, 2), 
with its nth row the 2D xy coordinate of the nth point. 
See [How is a geometry created in different ways?](#how-is-a-geometry-created-in-different-ways)
and [functions](#docs/faq/functions.md) for function usages.


## How is a geometry created in different ways?

There are 4 preset geometries provided in `pyvicar` and one can use it without making geometry mesh.
See [What geometry presets are available?](#what-geometry-presets-are-available).
For a 3D geometry surface using mesh data, one can import an STL file using:
`c.append_stl_solid`, `c.append_stl_membrane`.
See [What are the geometry topologies?](#what-are-the-geometry-topologies) 
to know what are the differences between solid and membrane.
When using these functions you don’t typically worry about any data structures -
just import a geometry and place it at a location.
It is also possible to create the surface structure yourself in Python using whatever approaches,
and in the end you will need to assemble the `TriSurface` class object from your data:
`TriSurface.from_xyz_conn`,
but be careful with the indexing and shallow copy.
To set such a generic `TriSurface` object, use: 
`c.append_solid`, `c.append_membrane`.
For a 2D geometry curve using point data, one can import the point list from a csv file using:
`c.append_csv_solid_2d`, `c.append_csv_membrane_2d`,
or from ndarray in an npz file:
`c.append_npz_solid_2d`, `c.append_npz_membrane_2d`.
The 2D counterpart of a 3D `TriSurface` generic data structure is to use
`c.append_solid_2d`, `c.append_membrane_2d`,
which can directly take in `numpy` ndarray of the point coordinates.
See [What are the data structures of geometries](#what-are-the-data-structures-of-geometries)
for its ndarray data structure and
[functions](#docs/faq/functions.md) for function usages.


## Why do I start with motion and substitute geometry but not reversed?

Yes you can, 
but typically to setup the motion data one needs to compute many variables in the script
and write multiple lines of codes to assign the settings,
while setting geometry is only about calling a preset or importing a file in one line,
so substituting geometry would be easier in most cases.


## What is dump post?

Dump post is to postprocess using the dump files, 
which are the `FieldsFiles` for domain fields like velocity and pressure,
`MarkerFiles` for geometry surfaces and distributions of related variables,
`IB2Files` for data in IB2 motion module.
Typical jobs include making isosurface animations of Q, body motion and contours,
animations on slices, etc., and probably at different view angles.
Statistics that requires computation on the domain field or geometry surface data
also need to process these heavy files and is considered a dump post too.
Unlike reports such as drag lift forces that record some lightweight statistic values frequently
(generally every time step by default),
dump files are heavy and generally can be output only at limited number of steps.
Therefore, dump post is discussed separately because it can be resource-consuming.
Reading and processing a lightweight csv report would typically finish instantly,
but might take tens of seconds to complete only one dump frame.
See [functions](#docs/faq/functions.md) for function usages,
and [What is a compact post?](#what-is-a-compact-post) to understand how to make this efficient.


## What is compact post?

When multiple dump post jobs are needed,
simply combining the single jobs would repeat common jobs multiple times, like:
read all frames -> Q calculation -> Q isosurface animation angle 1 -> end ->
read all frames -> Q calculation -> Q isosurface animation angle 2 -> end ->
read all frames -> Q calculation -> Q slice contour animations -> end.
read all frames -> Q calculation -> Q statistics -> end,
where reading the file and Q calculations on a large domain might take 20s for only one frame.
Compact post is to fuse all works needed in one frame, read the file and apply data processing only once,
so the work flow becomes:
read -> Q calculation -> Q isosurface -> angle 1 -> angle 2 -> slice -> statistics -> end.
You will need to assemble a job pipeline using `compact_post` function.
See [functions](functions.md) for function and job usages.


## What is a project and a study?

When you need to run multiple cases governed by a parameter space, you might want to make a project.
A project manages the generation and post processing of multiple cases.
Each case is named as a brief code representing its parameters, 
and the rules of what parameters can be changed and the encoding/decoding formats are called a study.
The typical usage is running these commands in the project directory:
```bash
python run.py <code>
python post.py <job> <code>
python stat.py <job>
```
The details of file structure and roles can be viewed in `examples/04_project/README.md`.


## How to run an example?

First make a folder to run the test.
For a single-case example, you can copy the script as `run.py` or `post.py` there.
For a project, copy the full project directory and `cd` into it.
See [What is the typical layout of an example script?](#what-is-the-typical-layout-of-an-example-script)
to understand the basic structure in a script or project directory.
In a single-case generation in `01_geometry` and `02_motion`,
check the following steps (minimal check is only 1 and 2, 3 thru 5 are more customized run configs):
1. The available python environment should be active, and README.md suggests manage it by conda.
2. A ViCar3D solver should be correctly installed, and modify the `Case` import line to its path. 
3. Decide a case name to generate, or simply use the default tutorial name.
4. Decide whether to run for one step to test or do full simulation, and change the `c.set_tstep`.
5. If running on a server and needs to send SLURM job, modify the job section accordingly.
Keep the `c.bash` or `c.sbatch` commented, and create only the configuration files first and inspect.
After inspection, if you want to directly run the solver at the current shell, activate `c.bash()`.
If you want the current shell to send the SLURM job, activate `c.sbatch()`.
For `03_postprocess`, you will need to specify an existing case folder besides the 1 and 2 above.
Note that a postprocess example does not know the parameters made in case generation,
so you need to check the post function to make them fit your case like the camera target location.
For a project in `04_project`, first understand the coding format in `projmgr/studies.py`,
and the case generation script like the content in a single-case example is in `projmgr/runlib.py`.
A case can then be generated by running `python run.py <code>`.


## What is the typical layout of an example script?

For a project layout, see `examples/04_project/README.md`.
For a single-case script in `01_geometry` and `02_motion`,
the first section in these files is the module import.
```python
import pyvicar
pyvicar.assert_api_version("1.0.1", "1.1.0")
Case = pyvicar.import_case("~/opt/ViCar3D/versions/common")
```
The version assert checks the `pyvicar` version to make sure it supports the features used in the script.
Since ViCar3D has multiple versions with different input file formats and options, 
what `import pyvicar` provides is the config tree structure and higher-level helper functions,
and you need to `import_case` to load the solver configs to generate version-specific files.
The path is the solver install path that should contain:
`lib/pyvicar_addons` for these configs, `bin/ViCar3D` the executable,
`etc/modulefiles` that handles solver environment when executing it.

Then these examples will come with the parameter calculations like setting variable `U` and `dx`.
`02_motion` examples have more variables to define the motion.

The start of setting a case folder is making a `Case` object.
```python
c = Case("casename")
```
Now `c` represents a case folder named `casename`.
Then comes the common settings on grid, geometry, BC, Re number, time stepping, and partitioning:
```python
gm = c.create_grid(l0=d, dx=dx)
body, surf = c.append_sphere(d / 2, dx, gm.center)
c.set_inlet("x1", [U, 0, 0])
c.set_re(re, U=U, L=d)  # U and L are needed since solver uses 1/nu
c.set_tstep(U=Umax, dx=dx, T=T, nT=10, nsteps_unit=10, ndumps=10, step_test=False)
c.set_partition(nproc_node=16, nnode_max=1)
```
See [functions](functions.md) or examples for detail usages.
The last part before writing is the job information:
```python
c.job.enable()
c.job.account = "account"
c.job.partition = "partition"
c.job.condaDeactivate = True
c.job.modulePurge = True
c.job.moduleUse = True
c.job.moduleLoad = True
c.job.logfile = ""
c.job.output = "log.out"
c.job.error = "log.err"
```
These are necessary to create a job file that can manage the runtime environment of ViCar3D solver.
`c.job` represents the `job` file in case folder.
See [settings](#settings.md) for detail usages.
Keep this job section full even though you just need to generate files at first without running, 
because you will still need the job file to run eventually.
The last part is writing and logging:
```python
c.write()
# c.show_grid(gm.center)
c.stat_grid()
c.stat_tstep(
    cfl={"U": Umax, "dx": dx},
    tdt={"T": T},
    ndmp={"T": T},
)
c.stat_viscosity(
    re={"U": U, "L": d},
    yplus={"y": dx, "tau": {"U": U, "L": d}},
)
c.stat_partition()
# c.bash()
# c.sbatch()
```
`c.write` generates the folders using what was set into the `Case` object.
`c.stat_xxx` are logging functions that print diagnose variables.
`c.bash` directly runs the job in the current shell, and `c.sbatch` sends the job file to SLURM.
Keep this section full too because they are likely needed.
3 commands are commented and opt-in:
`c.show_grid` plots the grid and geometry, 
but requires X server, consumes resources on large grid, and is not needed everytime you run the script.
`c.bash` and `c.sbatch` should be activated 
only after you inspect and make sure no issues are in the case scripts and is ready for simulation.
