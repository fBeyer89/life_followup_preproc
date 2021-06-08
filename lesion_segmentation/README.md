# Lesion segmentation in LIFE-Adult

## Baseline

White matter lesion segmentation has been performed with LesionTOADS in the baseline assessment.
The script and instructions how to run the LesionTOADS software is in `/data/pt_life/lampe/How_to_run_LesionTOADS_2020`
The data is in `/data/pt_life/lampe/Alle_zusammengefasst`
For information on Lampe et al. 2019 see `/data/p_life_results/2019_lampe_WMH_WHR/`
Summarized lesion data is in `/data/gh_gr_agingandobesity_share/life_shared/Data/Preprocessed/derivatives/WML_segmentation_data/wmh_deep_periventricular_lesions.csv`


## Followup
In order to perform longitudinal lesion segmentation, the LesionSegmentation Toolbox in SPM is used.
There are two algorithms available: LGA (lesion growth algorithm, needs T1w and FLAIR image + individual threshold) and LPA (lesion prediction algorithm, only needs FLAIR image + no threshold)
Based on a [current report](https://www.sciencedirect.com/science/article/pii/S2213158220302825#!) where LPA outperformed LGA for all thresholds, and unpublished results from Wulms & Minnerup (`/data/pt_life/LIFE_Cooperations/LesionTOADS_Münster/Overview_Figures_Niklas/overview_final_april2021`) LPA perfoms really well and we therefore decided to use it.

1. first cross-sectional lesion segmentation has to be run (for all participants with baseline & followup data)

2. longitudinal comparison of lesion segmentation can be run.
