%% Longitudinal lesion segmentation


%% Settings
addpath("/data/u_fbeyer_software/spm-fbeyer")

spm('Defaults','fMRI');
clear matlabbatch

data_path = '/data/pt_life/LIFE_fu/lesionsegmentation/test/';

%% Load data
% We have to loop over participants as each batch instance only takes
% one participant (with two timepoints)
pfile="/data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/LIFE_followup/preprocessing/lesion_segmentation/subjects_w2tp.txt";
C = readcell(pfile);


for i = 1:length(C(:,7))
char(C(i,7))
clear matlabbatch

f = spm_select('FPList', fullfile(data_path, char(C(i,7))), '^ples_*'); 
f

matlabbatch{1}.spm.tools.LST.long.data_long_tmp = {cellstr(f)};
matlabbatch{1}.spm.tools.LST.long.html_report = 0;

spm_jobman('run', matlabbatch);

end



