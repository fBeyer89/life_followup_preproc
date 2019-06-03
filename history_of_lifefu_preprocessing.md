##History of preprocessing LIFE FOLLOWUP

- beginning of data acquisition for followup in june 2018
  basic environment: MRICRON AFNI --version '17.2.17' ANTSENV --version '2.2.0' FSL --version 5.0.9 FREESURFER --version 5.3.0
  nipype versions 0.13.0-geb8a930.dev or 1.1.2
  
  **structural**
	- Freesurfer v. 5.3.0 was selected for compatibility with baseline data
  **DWI**
  eddy_openmp wrapped for nipype with an in-house implementation 
  (which used /data/pt_life_dti/scripts/life2018/eddy_openmp-5.0.11 but did not allow  all output files). 
  eddy options:
  repol -> to interpolate slices with signal loss due to head motion
  slice-to-volume correction -> not implemented because the data is single-banded.
  **rs**
	- preprocessing steps are according to fMRIprep's minimal preprocessing.

- 17.12.2018: rerun all participants because of wrong acquisition time in DWI preprocessing. 
	      previous: total acquisition time = 0.029925
	      corrected: total acquisition time = 0.05985

- 21.05.2019: updated EDDY DWI correction to nipype implementation of FSL 5.0.11 (nipype 1.2.0)
	      should not change the results but just enable saving all outputs.
	      allow to run eddy_quad quality control (from FSL 6.0.1)
	      rerun all participants until now with run_workflow_redo_eddy.py to re-generate outputs (which only reruns diffusion pipeline)



