# Diffusion MRI preprocessing pipeline for the LIFE-Adult Followup assessment

+ denoise with MRTrix: dwidenoise tool

+ Gibb's ringing removal with MRTrix: mrdegibbs

+ field distortion correction with FSL: topup

	- In the file of *acqparams_dwi.txt*, Total readout time (FSL) = (number of echoes - 1) * echo spacing = (128/2-1)x0.475ms=29.925ms. The reason of number of echoes needed to be devided by two is because LIFE-DWI was acquired with acceleration, partial Fourier=6/8, GRAPPA=2.
		- BW in PE= 16.446999999999999 Hz/pix (DICOM-tag: (0019,1028)
		- Pix in PE= 128, u.a. DICOM-tag: (0051,100b)
		- dwelltime (echo spacing) = 1/(16.45*128)=0.475ms

	- optimised parameters for relatively high resolution of dMRI data
		- `--warpres=20.4,17,13.6,10.2,8.5,6.8,5.1,3.4,1.7`
		- `--estmov=0,0,0,0,0,0,0,0,0` assumed no movement happen during AP and PA scans (they were performed one after another)

+ motion correction and outliner replacement (FSL: eddy)
	- In the file *distor_correct.py*, the setting in *eddy.inputs.num_threads* must be smaller than the global setting (8 as default now), without defining a value here would cause the program only using one cpu, need to change it manually before running the script
	- To Do: add eddy output with 1mm resolution

+ tensor model fitting (FSL: dtifit)

+ use bbregister from FREESURFER to register T1 and FA for ROI analysis
