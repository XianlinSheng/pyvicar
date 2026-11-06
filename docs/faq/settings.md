# Settings FAQ

## How are settings organized?

A `Case` exposes a structured tree of settings. Nested attributes generally correspond to sections and fields in ViCar3D input files. For example:

- `c.input.parallel.npx` is the `npx` setting in the `parallel` section of `input.dat`.
- `c.canonicalBody.bodies[1].general.bodyTypes` accesses the `bodyTypes` setting in the first body's `general` section in `canonical_body_in.dat`.

The body-list index starts at **1**. The main top-level groups are:

- `input`: solver input sections such as parallelization, domain, boundary conditions, timestep, and Poisson settings.
- `probe`: probe input configuration.
- `canonicalBody`: body definitions and their settings.
- `unstrucSurface`: unstructured surface geometry.
- `srj` and `om2edge`: specialized solver input sections.
- `xgrid`, `ygrid`, and `zgrid`: coordinate grid files.
- `job`: optional job-script settings.
- `draglift`, `dump`, `restart`, `report`, and `post`: solver outputs, restart data, reports, and postprocessing management.

Input and geometry groups are primarily written when `c.write()` is called; output-oriented groups are used to read or process solver results.

## How do I find available settings and valid options?

First inspect a matching example and the generated input files for the selected solver installation. Helpers set common combinations of low-level values, but installations can have different fields and defaults.

For a setting not covered by an example, inspect the available children on the relevant Case object or use the informative error from an invalid attribute to discover valid names. A case generated with the imported `Case` class can show the complete input files and defaults for that installation. Do not create a temporary case in a user directory unless the task calls for it; use an appropriate scratch/output path.

## Which Case class and solver installation should I use?

For a solver-backed script, import the `Case` class from the ViCar3D installation:

```python
import pyvicar

Case = pyvicar.import_case("/path/to/ViCar3D/installation")
```

The installation root contains `bin/ViCar3D` and `lib/pyvicar_addons`. A commonly used location is `~/opt/ViCar3D/versions/<version>`; treat it as a candidate and confirm that the directory exists and contains the intended version. Do not assume paths in examples match the user's machine.

`from pyvicar.case import Case` gives the built-in configuration layout without connecting to an installed solver. It can be used to inspect or generate basic configuration files. For solver-backed job generation, execution, and installation-specific features, use the imported `Case`.

Use one built-in or installation-specific `Case` layout per Python process. Examples may use `pyvicar.assert_api_version(minimum, maximum)` to check compatibility; follow the range used by the closest example when relying on version-specific behavior.

## How do solver versions affect settings?

Different ViCar3D installations may expose different options and defaults, especially for numerical schemes. The `c.input.misc` section contains settings specific to some solver versions. Do not assume a field found in one version is supported by another. If the user requests a solver-specific setting, confirm the selected installation/version and inspect its bundled `pyvicar_addons` examples.

The higher-level helpers usually configure essentials, while other settings may be provided by installation defaults. This is often intended. Use direct fields for a requested setting only when the selected installation supports it.

## Which Python environment should I use?

Use a Python environment where `pyvicar` and its runtime dependencies are installed. The package dependency list is in `pyproject.toml`. Conda is commonly used; identify the environment the user intends to use and do not assume its name.

For postprocessing on a cluster, the Python environment may need a headless/off-screen VTK build and MPI linked to the target platform. Check the active environment and platform-specific installation details when this matters.

## What job settings can I configure?

When a SLURM job is needed, `c.job` settings commonly cover job name, partition, time, nodes, tasks per node, GRES, QoS, account, output/error logs, and additional SLURM flags. Optional environment fields can add Conda deactivation and environment-module purge/use/load commands. Available values and defaults can depend on the imported solver installation and example; inspect those before filling them in.

Job settings belong in the generated Python script so `c.write()` can produce the job file. See [writing and job hooks](functions.md#how-do-i-write-a-case-and-leave-job-submission-to-the-user) for the expected script pattern.
