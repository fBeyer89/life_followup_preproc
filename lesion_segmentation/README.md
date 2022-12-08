# Lesion segmentation in LIFE-Adult

## Baseline

White matter lesion segmentation has been performed with LesionTOADS in the baseline assessment.
The script and instructions how to run the LesionTOADS software is in `/data/pt_life/lampe/How_to_run_LesionTOADS_2020`
The data is in `/data/pt_life/lampe/Alle_zusammengefasst`
For information on Lampe et al. 2019 see `/data/p_life_results/2019_lampe_WMH_WHR/`
Summarized lesion data is in `/data/gh_gr_agingandobesity_share/life_shared/Data/Preprocessed/derivatives/WML_segmentation_data/wmh_deep_periventricular_lesions.csv`


## Followup
In order to perform longitudinal lesion segmentation, the LesionSegmentation Toolbox (version 3.0.0) in SPM12 is used (with a private SPM version in `/data/u_fbeyer_software/spm-fbeyer`). For details on the algorithm see [Schmidt, 2019](https://www.sciencedirect.com/science/article/pii/S2213158219301998).
There are two algorithms available: LGA (lesion growth algorithm, needs T1w and FLAIR image + individual threshold) and LPA (lesion prediction algorithm, only needs FLAIR image + no threshold)
Based on a [current report](https://www.sciencedirect.com/science/article/pii/S2213158220302825#!) where LPA outperformed LGA for all thresholds, and unpublished results from Wulms & Minnerup (`/data/pt_life/LIFE_Cooperations/LesionTOADS_Münster/Overview_Figures_Niklas/overview_final_april2021`) LPA perfoms really well and we therefore decided to use it.

1. copy baseline and followup data into working directory with `copy_flair_data.sh`. <br/> This script generates the file `/data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/LIFE_followup/preprocessing/lesion_segmentation/subjects_w2tp.txt` which lists all subjects eligible for longitudinal processing. Subjects are copied into single subject folders in `/data/pt_life_whm/Data/LST/`. FLAIR files need to be unzipped before processing.

2. Start SPM12 and add path to private matlab (`addpath("/data/u_fbeyer_software/spm-fbeyer")`). Then type `cd cross-sectional; run cross_batch.m` in Matlab console or terminal. `cross_batch.m` runs all subjects in (e.g.) `cross-sectional/last_to_run.txt` Outputs are bias-corrected FLAIR images *mFLAIR.nii* and lesion probability masks *ples_lpa_mFLAIR.nii* for each participant.


3. For longitudinal processing, create a text file listing all *ples_lpa_mFLAIR_fu.nii* files you want to process, separated by commas like in `longitudinal/run_final.txt`. You can use the script `longitudinal/long_script.m` to create such a file (need to put commas manually). Then, start SPM12 and add path to private matlab. Type `cd longitudinal; run run_long_script.m` in Matlab console or terminal. Outputs are longitudinal lesion probability masks (lples_lpa_msub-FLAIR.nii) and lesion change labels (LCL_[nam_ples_t][nam_ples_t+1].nii) which indicate decrease, no change and increase with the numbers 1, 2,and 3, respectively. These files are in mid-way space between both timepoints, which was estimated using longitudinal rigid registration. They ca be overlaid with `lmFLAIR_bl.nii` and `lmFLAIR_fu.nii`. `rlm_FLAIR_bl` and `rlm_FLAIR_fu` are in the same space as the original FLAIRs, but resliced.

4. Cleaning up: Use scripts in `gzipping/` to gzip irrelevant files after cross-sectional processing, and all files after longitudinal processing. Also deletes intermediate results in `LST*`.     

5. Postprocessing:
- Scripts for extraction of lesion volumes in `extract_lesion_volume`.  
For longitudinal subjects the script returns the voxel number and volume for decrease (1), stable (2) and increase (3) in lesion volume based on the LCL maps in `/data/pt_life_whm/Results/Tables/longvols.txt`. On the 5.8.21 1059 participants, eight had no baseline/followup FLAIR scan and for eight the processing did not work, leaving us with 1043 usable datasets before QA, more info see in `/data/pt_life_whm/Results/QA/LST_processing.ods`.
For cross-sectional analysis, we extracted voxel number and volume of all lesions with a lesion probability > 0.8. Because of internal correction of lesion volume in the longitudinal stream, cross-sectional and longitudinal volumes are not directly comparable. **Usage case and usability of this cross-sectional lesion data has to be clarified**

6. Quality control of lesion maps.
We performed quality control using `slicesdir` and a custom script plotting those with NAs in the upper row of the image into a PDF (see `lesion_segmentation/qa_workflow`). If we suspected issues, we looked into the data with `fsleyes`. QA results are in `/data/pt_life_whm/Results/QA/qa_info_safetycopy.ods`. The images were classified into 3 categories ('1': MRI quality issues baseline or followup, '2': ventricular expansion (slight/strong) which led to false estimation of lesion reduction, '3': brain pathology, e.g. stroke or extremely large ventricles making lesion estimation unreliable). One should exclude those with either 1 or 3 to make sure these issues don't confound results.
Table with complete information on MRI acquisition, preprocessing and QA is generated by  `/data/pt_life_whm/Results/Tables/Overview_subjects.R` and saved in `/data/pt_life_whm/Results/Tables/longvols_w_pseudonym_qa.csv`.

7. Transformation of LCL lesion maps into MNI space for statistical Analysis
We use a two-step approach: first, *lmFLAIR_bl* images are co-registered via `bbregister` with the FreeSurfer longitudinal template of this subject `subj.long.subj_temp` from `data/pt_life_freesurfer/freesurfer_all`. Then, `antsRegistration` is used to bring the templates `brainmask.nii.gz` into 1mm MNI space (`/afs/cbs.mpg.de/software/fsl/5.0.11/ubuntu-bionic-amd64/data/standard/MNI152_T1_1mm_brain.nii.gz`). Both transforms are then applied to *lmFLAIR_bl* and *LCL_* maps.
To run the workflow, activate ANTSENV, FREESURFER --version 5.3.0 and `py3` conda environment. Then run `lesion_segmentation/register_to_MNI/run_registration_to_MNI.py`.
