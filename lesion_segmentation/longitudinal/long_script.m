%% Longitudinal lesion segmentation


%% Settings
addpath("/data/u_fbeyer_software/spm-fbeyer")

spm('Defaults','fMRI');
clear matlabbatch

data_path = '/data/pt_life_whm/Data/LST/';

%% Load data
% We have to loop over participants as each batch instance only takes
% one participant (with two timepoints)

fu = spm_select('FPListRec', fullfile(data_path), '^ples\w*(?=fu\.).*nii$'); 

fid = fopen('all_to_run_19.7','wt');
for rows = 1:size(fu)
fprintf(fid,'%s\n',fu(rows,:));
end
fclose(fid)

%fu_cs=cellstr(fu);

%run only those who have been run completely until here.

%bl_cs = strrep(fu_cs(103:150,:),'_fu','_bl');%only use those with followup MRI, and modify the path to change to baseline


%{bl_cs,fu_cs(103:150,:)}



%matlabbatch{1}.spm.tools.LST.long.data_long_tmp = {bl_cs,fu_cs(103:150,:)};
%matlabbatch{1}.spm.tools.LST.long.html_report = 0;

%spm_jobman('run', matlabbatch);







