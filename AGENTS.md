# Using pyvicar

These instructions help a fresh agent write Python scripts that use `pyvicar` to configure, run, or postprocess ViCar3D cases. They focus on using the package, not developing it.

## 1. Understand the task and find a matching example

Before writing a script, identify the requested case or study, its output directory, the ViCar3D installation, and the simulation details supplied by the user. Depending on the task, these may include dimensionality, body geometry and motion, flow conditions, grid resolution, time horizon, processor layout, cluster account and partition, and desired outputs. Ask about missing details that materially affect the setup rather than silently inventing them.

Read the relevant parts of `README.md` and adapt the closest example. Examples are grouped by task:

- `examples/01_geometry/`: geometry, imported surfaces, and grid setup.
- `examples/02_motion/`: moving bodies and motion settings.
- `examples/03_postprocess/`: analysis of solver results, plots, reports, videos, and compact data.
- `examples/04_project/`: parameterized studies, per-case processing, and cross-case statistics.

## 2. Set up the Python and solver environments

The Python environment needs `pyvicar` and the dependencies listed in `README.md`. The README recommends managing Python and these dependencies with Conda; identify the user's environment and activate the appropriate Conda environment before running a script.

The ViCar3D solver is installed separately. Its installation root contains `bin/ViCar3D` and `lib/pyvicar_addons`. A commonly used location is `~/opt/ViCar3D/versions/<version>`. Treat that as a candidate default: confirm the directory exists and the intended version before relying on it. Do not assume paths in examples match the user's machine.

For a solver-backed script, import the `Case` class from the selected installation:

```python
import pyvicar

Case = pyvicar.import_case("/path/to/ViCar3D/installation")
```

Importing checks the installation and compatibility between its add-ons and the installed `pyvicar` API. Examples may assert a compatible API range with `pyvicar.assert_api_version(minimum, maximum)`; follow the range used by the closest example when the script relies on version-specific behavior.

`from pyvicar.case import Case` gives the built-in configuration layout without connecting to an installed solver. Use it to inspect or generate basic configuration files, not to run a solver-backed case or depend on an installation-specific job setup. For solver execution and installation-specific features, use the imported `Case`.

Different ViCar3D installations may expose different options and defaults, especially for numerical schemes. The `c.input.misc` section holds settings specific to some solver versions. Do not assume a setting found in one version's `c.input.misc` is valid in another. Use one built-in or installation-specific `Case` layout per Python process.

## 3. Configure a case

A typical setup uses high-level helpers to build the grid, add geometry, set physical conditions, and choose the processor partition. For example:

```python
c = Case("case_directory")
gm = c.create_grid(l0=length_scale, dx=grid_spacing)
body, surface = c.append_sphere(radius, grid_spacing, gm.center)
c.set_inlet("x1", [velocity, 0, 0])
c.set_re(reynolds_number, U=velocity, L=length_scale)
c.set_tstep(U=velocity, dx=grid_spacing, T=time_scale, nT=number_of_periods)
c.set_partition()
c.write()
```

This is a pattern, not a complete physical setup. Choose geometry, flow direction, scales, time-step controls, and boundary conditions from the task and a matching example. For 2D cases, use the 2D grid and geometry helpers; they differ from their 3D counterparts.

### Prefer helpers; use direct fields when needed

High-level helpers perform calculations or conversions and set multiple low-level fields. Use them when they cover the requested setup. Body helpers are usually sufficient for typical cases and avoid manual edits to the nested canonical-body tree.

For settings without a matching helper, `Case` exposes low-level fields through nested attributes. For example:

- `c.input.parallel.npx` sets the `parallel` section's `npx` value in `input.dat`.
- `c.canonicalBody.bodies[1].general.bodyTypes` accesses the first body's `bodyTypes` setting in `canonical_body_in.dat`.

The body-list index starts at **1**. Inspect the matching example and generated files for expected defaults and valid values. If a setting is not covered, the available fields can be inspected from the object's structure or an informative invalid-attribute error. A temporary case generated with the imported `Case` can also show the complete input files and their defaults.

The usual helpers configure the essentials for a case; other settings, such as numerical schemes, may come from the solver installation's defaults. This is often appropriate. If the user specifically requests one of those settings, first check the examples, then use the relevant low-level field if needed and supported by the selected installation.

### Job setup and writing

`c.write()` creates the case directory structure and writes solver input, grid, and body files. If a SLURM job is needed, configure `c.job` as shown in the examples before writing. Job fields include task layout, partition, account, QoS/GRES/extra flags, and optional Conda or environment-module setup.

Do not submit or launch a solver job unless the user asks for execution and the required installation and cluster details are known.

## 4. Read and postprocess results

For an existing case, follow the relevant `examples/03_postprocess/` pattern. For example, `c.draglift.read()` and `c.draglift.proc()` load and process force series. Other examples cover plots, JSON/CSV reports, isosurfaces, slice contours, body animation, recording, and data compaction. Managed postprocessing artifacts are written under the case's `Post` directory. Use the `Case` class corresponding to the existing case and verify that the required solver outputs are available.

For postprocessing on a cluster, the Python environment may need a headless/off-screen VTK build and MPI linked to the target platform. See the dependency notes in `README.md`.

## 5. Manage a multi-case study

`examples/04_project/` demonstrates a project-level manager that converts parameter codes to case settings, generates and runs individual cases, performs per-case post jobs, and computes statistics across cases. Study-specific parameter encoding and orchestration belong in the user's project scripts; do not assume `pyvicar` provides that manager as part of its package API.

## Practical limits

- `pyvicar` prepares and processes cases; the ViCar3D solver distribution is separate.
- Do not assume a solver installation, cluster account, partition, geometry input, or output dataset from an example exists in the user's environment.
- For a distribution-specific feature, consult the selected installation's bundled `pyvicar_addons` examples or confirm the relevant version and installation details with the user.
