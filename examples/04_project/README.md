## Project
Project is a managed system of many cases that needs to control parameter space, 
configuration coupling, batch processing, remote transfer, comprehensive statistics, etc..
Each case is named with a unique brief code that represents its parameters, 
and a small project manager system is responsible for defining the code format, encode/decode, 
creating parameters set, generating case files, and scheduling processings for a given code in the command.
Several commands are provided in the project root path, 
and the implementations or configurations are put in the projmgr folder.
A typical file layout for a project is
<pre>
- project
 |- run.py  : start/restart a case, python run.py &ltcode&gt
 |- post.py : postprocess cases, python post.py &ltjob&gt &ltcode1&gt ...
 |- stat.py : run statistics, python stat.py &ltjob1&gt ...
 |- sbatch_job_post : sbatch projmgr/job_post script for a case, sbatch_job_post &ltcode&gt
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
</pre>
