# Diffusion MRI preprocessing pipeline for the LIFE-Adult Followup assessment

+ denoise with MRTrix: dwidenoise tool 

+ Gibb's ringing removal with MRTrix: mrdegibbs 

+ field distortion correction with FSL: topup
	- optimised parameters for relatively high resolution of dMRI data
	- `--warpres=20.4,17,13.6,10.2,8.5,6.8,5.1,3.4,1.7` 
	- `--estmov=0,0,0,0,0,0,0,0,0` assumed no movement happen during AP and PA scans (they were performed one after another)

+ motion correction and outliner replacement (FSL: eddy)
	- to do: add eddy output with 1mm resolution

+ tensor model fitting (FSL: dtifit)

+ (To do) use bbregister from FREESURFER to register T1 and FA for ROI analysis

