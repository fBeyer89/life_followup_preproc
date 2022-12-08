SUBJECTS_DIR="/data/pt_life_freesurfer/freesurfer_all/"


#Usage: bbregister --s <subj> --mov <volid> --reg <regfile> --<contrast>

bbregister --s 15E7897CDD_fu --mov /data/pt_life_whm/Data/Test_dataset_understanding_LST_sub-15E7897CDD/lmFLAIR_bl.nii --t2 --reg reg.lta /data/pt_life_whm/Data/Test_dataset_understanding_LST_sub-15E7897CDD/test_bbregister_with_old_transforms/template.nii


antsApplyTransforms --default-value 0 --dimensionality 3 --float 0 --input /data/pt_life_whm/Data/Test_dataset_understanding_LST_sub-15E7897CDD/tmp.bbregister.157712/template.nii --input-image-type 3 --interpolation Linear --output /data/pt_life_whm/Data/Test_dataset_understanding_LST_sub-15E7897CDD/lmFLAIR_bl_to_MNI.nii --reference-image /afs/cbs.mpg.de/software/fsl/5.0.9/ubuntu-xenial-amd64/share/data/standard/MNI152_T1_2mm_brain.nii.gz --transform /data/pt_life/LIFE_fu/wd_preprocessing/hcp_prep_workflow/anat_preproc/normalize/_subject_LI04142531/antsreg/transform0GenericAffine.mat --transform /data/pt_life/LIFE_fu/wd_preprocessing/hcp_prep_workflow/anat_preproc/normalize/_subject_LI04142531/antsreg/transform1Warp.nii.gz
