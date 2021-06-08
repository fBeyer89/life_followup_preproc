%% Cross-sectional lesion segmentation

%% Settings
addpath("/data/u_fbeyer_software/spm-fbeyer")

spm('defaults', 'FMRI');
base_data="/data/pt_life/LIFE_fu/lesionsegmentation/test/";

%% Data
f = spm_select('FPListRec', fullfile(base_data), '^FLAIR*') ;

%% Prepare batch
matlabbatch{1}.spm.tools.LST.lpa.data_F2 = cellstr(f);
matlabbatch{1}.spm.tools.LST.lpa.data_coreg = {''};
matlabbatch{1}.spm.tools.LST.lpa.html_report = 0;

%% Run batch
spm_jobman('run', matlabbatch);


