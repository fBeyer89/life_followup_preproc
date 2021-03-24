## LIFE Adult Followup physiological data processing
@author: fBeyer89

Physiological data was acquired with a breathing belt and pulse oximetry (with SIEMENS devices).

Preprocessing is based on the  [PhysIO toolbox](https://www.sciencedirect.com/science/article/pii/S016502701630259X) implemented in MATLAB.

1. Check file size to see whether physio data is complete
* run `check_filesize_physio_data.sh` in the shell (.resp should be 154 KB, .puls should be 240 KB)
* creates `overview_filesize.tsv` in `/data/pt_life_restingstate_followup/results/` for further analysis
* add subjects with incomplete files to exclusion list in ll. 91 in `run_physio_preproc_without_matlab.m`

2. To run preprocessing
- start MATLAB --version 9.3
- open MATLAB GUI or terminal with command matlab (-nojvm; then graphical display will be disabled)
- open the script `run_physio_preproc_without_matlab.m`
- change subjects to be included in l.7 (subject list) and l.77
- run script (run "run_physio_preproc_without_matlab.m" in terminal)
- this scripts saves the output from the Physio Toolbox, i.e. downsampled resp and PPU traces, resp./cardiac cycles, RVT and HR, into /data/pt_life_restingstate_followup/physio/%s.mat
- this script gives an error if files are incomplete -> check the case manually.

3. To create table with information on resting-state head motion, BOLD fluctuations and physiological timecourses for further analysis 
- start MATLAB as before
- run `plotting_physio_motion_dvars.m`  
- change subjects to be included in l.7 (subject list) and l.77
- this script saves a table in `/data/pt_life_restingstate_followup/results/results_rs_motion_physio.csv` with
	* Column 1,2: mean and maximal framewise displacement at followup (meanFD,maxFD)
  * Column 3,4: mean and maximal framewise displacement at baseline (meanFD_BL,maxFD_BL)
  * Column 5,6,7: mean and maximal DVARS at followup (meanstdDVARS, maxstdDVARS) and correlation with meanFD (corr_FD_stdDVARS)
  * Column 8,9,10,11: correlation of mean FD and respiratory and PPU traces, HR, RVT (corr_FD_resp,corr_FD_oxy,corr_FD_RVT,corr_FD_HR)
  * Column 12,13,14,15: correlation of DVARS and respiratory and PPU traces, HR, RVT (corr_dvars_resp,corr_dvars_oxy,corr_dvars_RVT,corr_dvars_HR)

- additionally it saves the SIC into `/data/pt_life_restingstate_followup/results/SIC.csv`

