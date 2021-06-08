# Lesion segmentation in LIFE-Adult

## Baseline

White matter lesion segmentation has been performed with LesionTOADS in the baseline assessment.
The script and instructions how to run the LesionTOADS software is in `/data/pt_life/lampe/How_to_run_LesionTOADS_2020`
The data is in `/data/pt_life/lampe/Alle_zusammengefasst`
For information on Lampe et al. 2019 see `/data/p_life_results/2019_lampe_WMH_WHR/`
Summarized lesion data is in `/data/gh_gr_agingandobesity_share/life_shared/Data/Preprocessed/derivatives/WML_segmentation_data/wmh_deep_periventricular_lesions.csv`


## Followup
In order to perform longitudinal lesion segmentation, the LesionSegmentation Toolbox (version 3.0.0) in SPM12 is used.
There are two algorithms available: LGA (lesion growth algorithm, needs T1w and FLAIR image + individual threshold) and LPA (lesion prediction algorithm, only needs FLAIR image + no threshold)
Based on a [current report](https://www.sciencedirect.com/science/article/pii/S2213158220302825#!) where LPA outperformed LGA for all thresholds, and unpublished results from Wulms & Minnerup (`/data/pt_life/LIFE_Cooperations/LesionTOADS_Münster/Overview_Figures_Niklas/overview_final_april2021`) LPA perfoms really well and we therefore decided to use it.

1. copy baseline and followup data into working directory with `copy_flair_data.sh`. <br/> This script generates the file `/data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/LIFE_followup/preprocessing/lesion_segmentation/subjects_w2tp.txt` which lists all subjects eligible for longitudinal processing. Subjects are copied into single subject folders in ``.

2. Start SPM12 and add path to private matlab (`addpath("/data/u_fbeyer_software/spm-fbeyer")`). Then type `cd cross-sectional; run cross_batch.m` in Matlab console or terminal. Outputs are lesion probability masks *ples_lpa_mFLAIR.nii* for each participant.

3. Start SPM12 and add path to private matlab. Then type `cd longitudinal; run long_batch.m` in Matlab console or terminal. Outputs are longitudinal lesion probability masks (lples_lpa_msub-FLAIR.nii) and lesion change labels (LCL_[nam_ples_t]_[nam_ples_t+1].nii) which indicate decrease, no change and increase with the numbers 1, 2,and 3, respectively

4. Postprocessing: extraction of lesion volumes (bl, fu and change) based on longitudinal subjects, and on cross-sectional subjects for those without followup. 
