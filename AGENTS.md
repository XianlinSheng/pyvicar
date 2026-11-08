# Using pyvicar

## Purpose
Help the user create runnable Python scripts that use `pyvicar` to configure ViCar3D cases, generate their input files, and, when requested, process existing results. Package development is outside this guide's scope.

## Understand the requested deliverable
Unless the user explicitly asks for a project parameter or case code, interpret a request for “code” as a runnable Python script that uses `pyvicar`. Do not confuse that script with a study identifier from `examples/04_project/`. If the intended deliverable remains unclear, ask briefly.

Before writing the script, identify the requested case or study, its output location, and the simulation details that materially affect it. These may include dimensionality, geometry and motion, flow conditions, grid resolution, time horizon, processor layout, cluster account and partition, and desired outputs. Ask about missing important values instead of silently inventing them.

## Workflow

1. Find the closest example in `examples/` and use it as the starting point. Combine patterns from multiple examples when needed.
2. Consult the relevant topics in [the FAQ index](docs/faq/INDEX.md) for example selection, settings, and helper functions.
3. Adapt the example into a Python script for the requested case. Preserve applicable case-writing, job-configuration, and diagnostic code. Leave `c.bash()` and `c.sbatch()` commented so the user can decide whether to run or submit the generated job.
4. Check that the script uses values and paths supported by the user's request. Do not assume an example's solver installation, cluster account, partition, geometry, or output data is available. Ask when a missing detail materially changes the script.

The FAQ is organized into three sections:

- [Examples](docs/faq/examples.md): choosing and adapting example scripts.
- [Settings](docs/faq/settings.md): the Case configuration tree, available options, runtime environments, and solver versions.
- [Functions](docs/faq/functions.md): high-level helpers, case writing, job hooks, diagnostics, and postprocessing.
