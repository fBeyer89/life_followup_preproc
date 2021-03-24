#!/bin/bash


#run eddy qc for agewell.de-MRI

#Usage: eddy_quad <eddyBase> -idx <eddyIndex> -par <eddyParams> -m <mask> -b <bvals> [options]
   
   
#Compulsory arguments:
#       eddyBase             Basename (including path) specified when running EDDY
#       -idx, --eddyIdx      File containing indices for all volumes into acquisition parameters
#       -par, --eddyParams   File containing acquisition parameters
#       -m, --mask           Binary mask file
#       -b, --bvals          b-values file
   
#Optional arguments:
#       -g, --bvecs          b-vectors file - only used when <eddyBase>.eddy_residuals file is present
#       -o, --output-dir     Output directory - default = '<eddyBase>.qc' 
#       -f, --field          TOPUP estimated field (in Hz)
#       -s, --slspec         Text file specifying slice/group acquisition
#       -v, --verbose        Display debug messages



for subj in LI0026893X
do

eddy_quad /data/pt_life_dti_followup/diffusion/${subj}/eddy_corrected --eddyIdx /home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/index.txt --eddyParams /home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/acqparams_dwi.txt --mask /data/pt_life_dti_followup/diffusion/${subj}/dwi_appa_corrected_maths_brain_mask.nii.gz --bvals /data/pt_life_dti_followup/diffusion/${subj}/cmrrmbep2ddiffs*.bval -g /data/pt_life_dti_followup/diffusion/${subj}/cmrrmbep2ddiffs*.bvec -f /data/pt_life_dti_followup/diffusion/${subj}/dwi_appa_field.nii.gz

done

#eddy_quad /data/pt_life/LIFE_fu/wd_preprocessing/redo_eddy/hcp_prep_workflow/dwi_preproc/distor_correct/_subject_LI0026893X/eddy/eddy_corrected -idx /home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/index.txt -par /home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/acqparams_dwi.txt -m /data/pt_life/LIFE_fu/wd_preprocessing/redo_eddy/hcp_prep_workflow/dwi_preproc/distor_correct/_subject_LI0026893X/bet/dwi_appa_corrected_maths_brain_mask.nii.gz -b /data/pt_life/LIFE_fu/wd_preprocessing/redo_eddy/hcp_prep_workflow/_subject_LI0026893X/dicom_convert/cmrrmbep2ddiffs009a001.bval --bvecs /data/pt_life/LIFE_fu/wd_preprocessing/redo_eddy/hcp_prep_workflow/_subject_LI0026893X/dicom_convert/cmrrmbep2ddiffs009a001.bvec -f /data/pt_life/LIFE_fu/wd_preprocessing/redo_eddy/hcp_prep_workflow/dwi_preproc/distor_correct/_subject_LI0026893X/topup/dwi_appa_field.nii.gz


#works:
#eddy_quad /data/pt_life_dti_followup/diffusion/LI0026893X/eddy_corrected --eddyIdx /home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/index.txt --eddyParams /home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/acqparams_dwi.txt --mask /data/pt_life_dti_followup/diffusion/LI0026893X/dwi_appa_corrected_maths_brain_mask.nii.gz --bvals /data/pt_life_dti_followup/diffusion/LI0026893X/cmrrmbep2ddiffs009a001.bval

#doesnt work
#eddy_quad /data/pt_life_dti_followup/diffusion/LI0026893X/eddy_corrected --eddyIdx=/home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/index.txt --eddyParams=/home/raid1/fbeyer/Documents/Scripts/LIFE_followup/preprocessing/nipy1.4/diffusion/acqparams_dwi.txt --mask=/data/pt_life_dti_followup/diffusion/LI0026893X/dwi_appa_corrected_maths_brain_mask.nii.gz --bvals=/data/pt_life_dti_followup/diffusion/LI0026893X/cmrrmbep2ddiffs009a001.bval

rm -rf /data/pt_life_dti_followup/squad
eddy_squad -o /data/pt_life_dti_followup/squad /data/pt_life_dti_followup/squad_tst.txt


