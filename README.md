# life_followup_preproc

Preprocessing pipelines for the LIFE-Adult Followup assessment (based on HCP pipeline)

+ Structural preprocessing: with Freesurfer + registration to MNI152 1mm space

+ Functional (rsfMRI) preprocessing: removal of first 4 volumes, motion correction (MCFlirt), coregistration to anatomical (BBREGISTER)
, unwarping (FUGUE) applied in a single step, removal of linear trend.

+ Creating a report for quick overview of the data.

Based on the implementation of HCP pipelines for nipype (https://github.com/beOn/hcpre)
