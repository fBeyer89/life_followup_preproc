%% Longitudinal lesion segmentation


%% Settings
addpath("/data/u_fbeyer_software/spm-fbeyer")

spm('Defaults','fMRI');
clear matlabbatch

data_path = '/data/pt_life_whm/Data/LST/';

%% Load data
% We have to loop over participants as each batch instance only takes
% one participant (with two timepoints)

f = fopen('run_final.txt','r');
tmp = textscan(f, '%s', 'Delimiter', ',');
fclose(f);

fu_data=tmp{1}
test=fu_data(1:end,1)

%run only those who have been run completely until here.

bl_cs = strrep(test,'_fu','_bl');%only use those with followup MRI, and modify the path to change to baseline


{bl_cs,test}



matlabbatch{1}.spm.tools.LST.long.data_long_tmp = {bl_cs,test};
matlabbatch{1}.spm.tools.LST.long.html_report = 1;

spm_jobman('run', matlabbatch);







