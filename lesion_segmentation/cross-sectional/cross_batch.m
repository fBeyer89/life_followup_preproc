%% Cross-sectional lesion segmentation

%% Settings
addpath("/data/u_fbeyer_software/spm-fbeyer")

spm('defaults', 'FMRI');
base_data="/data/pt_life_whm/Data/LST/";

%% Data
%f = spm_select('FPListRec', fullfile(base_data), '^FLAIR.*\.nii$') %'^FLAIR*')
%fid = fopen('last_to_run.txt','wt');
%for rows = 1:size(f)
%fprintf(fid,'%s\n',f(rows,:));
%end
%fclose(fid)


f = fopen('last_to_run.txt','r');
tmp = textscan(f, '%s', 'Delimiter', ',');
fclose(f);
data=tmp{1}
run_data=data(1:end,1)

%% Prepare batch
matlabbatch{1}.spm.tools.LST.lpa.data_F2 = run_data;
matlabbatch{1}.spm.tools.LST.lpa.data_coreg = {''};
matlabbatch{1}.spm.tools.LST.lpa.html_report = 0;

%% Run batch
spm_jobman('run', matlabbatch);


