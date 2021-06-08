## History of preprocessing LIFE FOLLOWUP

- beginning of data acquisition for followup in June 2018
  basic environment: MRICRON AFNI --version '17.2.17' ANTSENV --version '2.2.0' FSL --version 5.0.9 FREESURFER --version 5.3.0
  nipype versions 0.13.0-geb8a930.dev or 1.1.2

### Explanation of this pipeline:

  **structural**  
	Freesurfer v. 5.3.0 was selected for compatibility with baseline data

  **DWI**  
  Eddy_openmp wrapped for nipype with an in-house implementation
  (which used `/data/pt_life_dti/scripts/life2018/eddy_openmp-5.0.11` but did not allow  all output files).  
  eddy options:
        - repol -> to interpolate slices with signal loss due to head motion
        - slice-to-volume correction -> not implemented because the data is single-banded  

  **rs**  
	Preprocessing steps are according to fMRIprep's minimal preprocessing.


### Changes to this pipeline:
- 17.12.2018: rerun all participants because of wrong acquisition time in DWI preprocessing.
	Previous: total acquisition time = 0.029925, corrected: total acquisition time = 0.05985

- 21.05.2019: updated EDDY DWI correction to nipype implementation of FSL 5.0.11 (nipype 1.2.0)   
	This should not change the results but just enable saving all outputs, to run eddy_quad quality control (from FSL 6.0.1. At this point all participants assessed until now were rerun with `run_workflow_redo_eddy.py` to re-generate outputs (which only reruns diffusion pipeline)

- 15.04.2021: modified workflow to use new IDs for FreeSurfer processing and BIDS conversion included in the workflow.

- 21.04.2021: modified dimension along which images are selected in `reports` because of differences in conversion between dcm2nii and dcm2niix
