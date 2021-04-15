# life_followup_preproc

Preprocessing pipelines for the LIFE-Adult Followup assessment (based on HCP pipeline)

+ Structural preprocessing: with Freesurfer + registration to MNI152 1mm space

+ Functional (rsfMRI) preprocessing: removal of first 4 volumes, motion correction (MCFlirt), coregistration to anatomical (BBREGISTER)
, unwarping (FUGUE) applied in a single step, removal of linear trend.

+ Diffusion MRI preprocessing: artefacts correction including denoising (MRTrix: dwidenoise) and Gibb's ringing removal (MRTrix: mrdegibbs); field distortion correction (FSL: topup); motion correction and outliner replacement (FSL: eddy); tensor model fitting (FSL: dtifit)

+ Creating a report for quick overview of the data.

Based on the implementation of HCP pipelines for nipype (https://github.com/beOn/hcpre)

**How to run**

1. Connect to generation 5 server**  (if still available)   
`getserver -sL -g5`

2. Load software packages using `./environment_FSL5.0.11.sh`
   which will load `MRICRON AFNI --version '17.2.17' ANTSENV --version '2.2.0' FSL --version 5.0.11 FREESURFER --version 5.3.0`
3. activate Python 2.7 with nipype version 1.2.0 (and other packages) in
`source activate agewell_nip1.2`

*if generation 5 is not available*
 1. Connect to generation 6 server `getserver -sL -g6`
 2. Load software packages using `./environment_FSL5.0.11_g6server.sh`
    which will load `MRICRON AFNI --version '19.1.05' ANTSENV --version '2.3.1' FSL --version 5.0.11 FREESURFER --version 5.3.0` (a different ANTS and AFNI version)
 3. activate Python 2.7 with nipype version 1.2.0 (and other packages) in
 `source activate agewell_nip1.2`

4. To run the workflow:
`python run_workflow_hcplike.py --run -n 8 --config conf_for_LIFE_FU.conf `

working directory is defined in "run_workflow_hcplike.py", ll.76: working_dir="/data/pt_life/LIFE_fu_wd/" (don't change, unless directory is full)

For DWI QC FSL --version 6.0.1 is needed.
