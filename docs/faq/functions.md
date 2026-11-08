# Functions FAQ

## What is a high-level helper function?

A high-level helper performs common calculations or conversions, then sets several lower-level Case fields for you. Use one when it covers the requested operation; use direct settings for options without a matching helper. The helpers are attached to the `Case` interface, so scripts usually call them as methods such as `c.create_grid(...)` or `c.set_re(...)`.

## What does `c.set_re()` do?

`c.set_re(re, U, L)` converts the requested Reynolds number to the solver's stored inverse kinematic viscosity value by setting:

```python
c.input.timeStep.re = re / (U * L)
```

Pass the Reynolds number and the characteristic velocity `U` and length `L` that match the physical case. Related `c.stat_viscosity(...)` diagnostics can calculate and print Reynolds-number or wall-unit estimates using the supplied scales.

## Which helpers configure flow, time stepping, grids, and geometry?

### Flow, timestep, and partition

- `c.set_inlet(inlet, velocity)` sets a Dirichlet velocity condition at the named inlet and initializes the domain velocity from that vector.
- `c.set_tstep(U, dx, T, ...)` chooses a timestep, step count, dump interval, restart interval, and Poisson residual tolerance using velocity, minimum grid spacing, and the time scale. Use the matching example for optional controls such as CFL limit, dump count, or one-step test mode.
- `c.set_partition(...)` estimates processor and node counts from the grid size and requested per-node/per-processor limits, sets the parallel decomposition, and configures the job task layout.
- `c.set_partition_total(nproc)` sets the parallel decomposition for a specified total process count.

### Grid and geometry

- `c.create_grid(...)` creates and applies a `GridModel`; it returns that model, which includes the grid center and dimensions. `c.apply_grid_model(...)` applies an existing model.
- Grid helpers such as `c.refine_grid(...)`, `c.uniform_grid_n(...)`, `c.uniform_grid_dx(...)`, and `c.grid_2d(...)` configure grid spacing and dimensionality. See the geometry and motion examples for 2D/3D differences.
- Geometry helpers such as `c.append_sphere(...)`, `c.append_cyl_2d(...)`, `c.append_plane(...)`, and the STL/CSV/NPZ helpers create or load geometry and attach a solid or membrane body. For example, `c.append_sphere(radius, dx, gm.center)` returns body and surface objects.

Body helpers are usually sufficient for typical cases and avoid manual edits to the nested canonical-body tree. Use low-level body settings only when a requested option is not covered by a helper.

Choose parameters from the user's case and the nearest example; the helper call signatures and appropriate geometry differ by dimension and object type.

## How do I write a case and leave job submission to the user?

Call `c.write()` after configuring the case. It creates the case directory structure and writes solver input, grid, body, and enabled job files. Keep SLURM settings in the script when needed; do not remove them just because execution is disabled.

A typical ending, adapted from the selected example, retains job configuration, writing, relevant diagnostics, and commented run/submission hooks:

```python
# Job settings adapted to the user's cluster and task
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

c.write()

# Optional grid preview
# c.show_grid(gm.center)

# Keep applicable diagnostics from the example, using this script's values.
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

# The user can uncomment one when ready:
# c.bash()
# c.sbatch()
```

The diagnostic values `Umax`, `dx`, `T`, `U`, and `d` are from an example workflow. Define or substitute them using the new script's physical parameters; do not copy example variable names blindly. `c.bash()` runs the generated job script locally, while `c.sbatch()` submits it to SLURM. Keep both commented by default and do not execute either hook unless the user explicitly asks you to run or submit the job.

## How do I inspect a case and its configuration?

- `c.stat_grid()`, `c.stat_tstep(...)`, `c.stat_viscosity(...)`, and `c.stat_partition()` print setup diagnostics. Some diagnostics need physical values not stored in the case, so pass the relevant values from the script. Keep only diagnostics useful for the requested case.
- `c.show_grid(...)` can preview the grid when supported by the environment; examples commonly leave this call commented.
- Read the generated input files to review the actual settings and defaults used by the selected installation.

## How do I read and postprocess solver results?

For an existing case, use the `Case` class corresponding to that case and verify that required solver outputs exist. For example, `c.draglift.read()` loads force data and `c.draglift.proc()` processes force series. The postprocessing examples also cover plots, JSON/CSV reports, isosurfaces, slice contours, body animation, recording, compression, and compact datasets. Managed postprocessing artifacts are written under the case's `Post` directory.

For a parameterized collection of cases, `examples/04_project/` demonstrates an external project manager that converts parameter codes to settings, creates and runs cases, performs per-case post jobs, transfers selected files, and computes cross-case statistics. This study-specific orchestration is not a built-in `pyvicar` function.
