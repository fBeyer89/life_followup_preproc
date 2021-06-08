# life_followup_preproc

Preprocessing pipelines for the LIFE-Adult Followup assessment (based on [HCP pipeline]((https://github.com/beOn/hcpre)))

+ BIDS conversion: copies NIFTI & corresponding .json files into `/data/p_life_raw/bids` (functions and subworkflows in: `bids`)

+ Structural preprocessing: with Freesurfer + registration to MNI152 1mm space (functions and subworkflows in: `structural`)

+ Functional (rsfMRI) preprocessing: removal of first 4 volumes, motion correction (MCFlirt), coregistration to anatomical (BBREGISTER), unwarping (FUGUE) applied in a single step, removal of linear trend. (functions and subworkflows in: `functional`)

+ Diffusion MRI preprocessing: artefacts correction including denoising (MRTrix: dwidenoise) and Gibb's ringing removal (MRTrix: mrdegibbs); field distortion correction (FSL: topup); motion correction and outliner replacement (FSL: eddy); tensor model fitting (FSL: dtifit)(functions and subworkflows in: `diffusion`)

+ Creating a report for quick overview of the data.(functions and subworkflows in: `reports`)

### Other folders
`workflow_redo_eddy`: modules to rerun workflow with other eddy settings (was previously used, now eddy settings in the main workflow are adapted)

`conf_files`: previously used config files.

## How to run the preprocessing workflow

### Prerequisite:
- python2.7 environment with all packages listed in `/data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/LIFE_followup/preprocessing/nipy1.4/requirements.txt`

- The environment may be installed in different ways:
1. use `virtualenv` to create a virtual environment. This is a most basic version control tool for Python 2.7. Detailed instructions can be found [here](https://packaging.python.org/tutorials/installing-packages/).

    - create a directory where your virtualenv should live `/home/user/myvirtualenv`
    - test that you have `pip` installed in your python version by typing `python -m pip --version` (should say `pip 9.0.1 from /usr/lib/python2.7/dist-packages (python 2.7)`)
    - install virtualenv to your default institute python 2.7 version by typing `python -m pip install virtualenv`
    - create your own virualenvironment by typing `python -m virtualenv /home/user/myvirtualenv`
    - activate this environment by typing `source /home/user/myvirtualenv/bin/activate`
    - now you are using python with this environment and may install all desired packages into it
    - `/data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/LIFE_followup/preprocessing/nipy1.4/requirements.txt` tells you which packages you need
    - run `python -m pip install -r requirements.txt`
    - now you can use this virtual environment in any session after **activating** it with `source /home/user/myvirtualenv/bin/activate`



  2. use `miniconda` for version control.
    - install `miniconda` into a local directory. For detailed instructions see [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)
    - create a Python 2.7 environment using `conda create -y --name myenv python=2.7`. This environment will be located in your local conda directory
    - now add the required packages using `conda install --force-reinstall -y -q --name myenv -c conda-forge --file requirements.txt`
    - if not everything can be installed via `conda install`, activate your environment `source activate myenv` and use `pip install -r /data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/LIFE_followup/preprocessing/nipy1.4/requirements.txt ` to install the missing packages
    - now you can use this virtual environment in any session after **activating** it with `source activate myenv`



### Step-by-step

1. Connect to generation 5 server  (if still available)   
`getserver -sL -g5`

2. Load software packages using `./environment_FSL5.0.11.sh`
   which will load `MRICRON AFNI --version '17.2.17' ANTSENV --version '2.2.0' FSL --version 5.0.11 FREESURFER --version 5.3.0`
3. activate the virtual Python environment (see above)

*if generation 5 is not available*
 1. Connect to generation 6 server `getserver -sL -g6`
 2. Load software packages using `./environment_FSL5.0.11_g6servers.sh`
    which will load `MRICRON AFNI --version '19.1.05' ANTSENV --version '2.3.1' FSL --version 5.0.11 FREESURFER --version 5.3.0` (a different ANTS and AFNI version)
 3. activate the virtual Python environment (see above)

4. To run the workflow:
  - modify the subjects you want to run in `/data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/LIFE_followup/preprocessing/nipy1.4/conf_for_LIFE_FU_*.conf` (first line)
  - working directory is defined in `run_workflow_hcplike.py`, ll.76: `working_dir=/data/pt_life/LIFE_fu/wd_preprocessing/` (don't change, unless directory is full). Here, all intermediate steps are saved, this is why when rerunning the workflow it will only re-run steps for which the script has been altered.
  - run the workflow in the terminal you set up above with `python run_workflow_hcplike.py --run -n 8 --config conf_for_LIFE_FU.conf `
  - if there is more than one file `*.conf` you will be prompted to select the file on the keyboard. It may take a while until all available files are identified.
  - now everything runs :)      


5.  After the workflow has finished
  - check for error logfiles (`*.pklz`) and try to solve issues
  - check regularly whether
      - subjects were scanned at followup who did not have a baseline assessment (table: `/data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/lifebids/new_pseudos.csv`) and add them to the BIDS participants file, if necessary (`/data/p_life_raw/bids/participants.ods`)
      - there is enough space in working directory, freesurfer directory and bids directory, otherwise ask IT for more disk space.
  - *optionally*: check the output report files in `/data/p_life_raw/documents/fu_reports/` for a quick glance on data quality
  - create extensive QA files for resting-state and DWI data (see `/data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/LIFE_followup/preprocessing/qa/` for HowTos)
  - bidsify Physio data (see `bids/physio2bids/` for HowTo)
