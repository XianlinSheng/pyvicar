## Project
Project is a managed system of many cases that needs to control parameter space, 
configuration coupling, batch processing, remote transfer, comprehensive statistics, etc..
Each case is named with a unique brief code that represents its parameters, 
and a small project manager system is responsible for defining the code format, encode/decode, 
creating parameters set, generating case files, and scheduling processings for a given code in the command.
Several commands are provided in the project root path, 
and the implementations or configurations are put in the projmgr folder.
A typical file layout for a project is
```
- project
 |- run.py  : start/restart a case, python run.py <code>
 |- post.py : postprocess cases, python post.py <job> <code1> ...
 |- stat.py : run statistics, python stat.py <job1> ...
 |- sbatch_job_post : sbatch projmgr/job_post script for a case, sbatch_job_post <code>
 |- pull    : pull updates from remote server, including scripts, simulation reports (no dump files)
 |- push    : push updates, mainly the scripts
 |- projmgr
   |- filter-pull   : rsync file filter for ./pull
   |- filter-push   : rsync file filter for ./push
   |- host          : remote server project path
   |- job_post      : postprocess script template
   |- __init__.py   : init of the mini projmgr system, simply import the submodules
   |- params.py     : parameters set that defines a case, starting point of the mgr system
   |- studies.py    : coding format and encode/decode from code string to params set
   |- runlib.py     : functions that create case files from params set
   |- postlib
     |- __init__.py : provides runtime import, post job scripts in postlib/ is auto loaded
     |- xxx.py      : defines a post job, simply creates a job.py with post_job(params) func
     |- misc        : all required detail implementations or tools
   |- statlib
     |- ...         : structure same as postlib, but job.py contains stat_job() func
  |- codes ...  : simulation cases
```
Postprocess is to process the output data and generate other datasets within the same case
so each case is independent and one needs to specify the code to run it.
Statistics is analysis across cases, it is highly flexible and depends on the parameter space
and the existing cases, so it does not take arguments and one modifies a script directly in place.

Here are some common modifications after copying a project example.
The unmentioned rest of these can be left untouched if simulating the same physical and numerical settings.
1. projmgr/params.py: solver versions, install paths, platform names
1. projmgr/studies.py: coding of solver versions, platforms
1. projmgr/runlib.py: partitioning settings, version&platform, accounts
1. projmgr/host: remote path
1. projmgr/filter-pull: platform-version suffix pattern, e.g., + [LR][CG]
1. projmgr/job_post: partition, accounts, number of processors (considering memory), and post jobs to run
1. projmgr/statlib/...: job content, statistics jobs depend on the actual jobs that one run

Note that nothing is intended to be hard-coded in the projmgr, 
and this is why it is made completely inside a project not a pyvicar module.
It is completely within the design to temporarily 
comment out or change some implementations in the post scripts for special cases.
