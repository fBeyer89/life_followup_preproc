# Coregister LCL maps to MNI space

## To run
- getserver -sL
- start FreeSurfer --version 5.3.0 and ANTSENV 2.3.1 (**starting in 2022**: FREESURFER --version 6.0.0p1 and ANTSENV --version 2.3.5 due to server upgrades)
- start python2.7 environment `miniconda` `source activate agewell_nip1.2`
- update the subject list in `/data/pt_life_whm/Results/Tables/longvols_w_pseudonym.csv` or select a different number of subjects
- run the script `python run_registration_to_MNI.py` 


# Coregister baseline lesion maps to MNI space
## To run
- getserver -sL
- start FreeSurfer --version 5.3.0 and ANTSENV 2.3.1 (**starting in 2022**: FREESURFER --version 6.0.0p1 and ANTSENV --version 2.3.5 due to server upgrades)
- start python2.7 environment `miniconda` `source activate agewell_nip1.2`
- subject list based on processed baseline data with volumes 
- run the script `python run_registration_to_MNI_for_baseline_only.py` 