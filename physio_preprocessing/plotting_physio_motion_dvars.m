%%plotting physio and motion data and dvars together.

%add tapas toolbox to path
addpath(genpath('/data/pt_life/data_fbeyer/spm-fbeyer'))
%create physio_in file
%Specify variables
subjects_file='/data/pt_life_restingstate_followup/Results/Summaries/qa_check2021/all_physio_data.txt';
%'/data/pt_life/data_fbeyer/genetics/analysis/young_and_old/connectome_project/old/794subjects.txt'

subjID = fopen(subjects_file);
subjects=textscan(subjID,'%s');

all_res=zeros(size(subjects{1},1),15);
subjects={"LI05095916"}
for i=1:1%size(subjects{1},1)
    
    %if subjects{1}{i}=="LI01273319"%for looking at plots of individual subjects

        %RESTING STATE scan needs to be processed
        if isfile(sprintf('/data/pt_life_restingstate_followup/resting/moco/%s/rest_realigned.nii.gz.par', subjects{1}{i}))
            fileID = fopen(sprintf('/data/pt_life_restingstate_followup/resting/moco/%s/rest_realigned.nii.gz.par', subjects{1}{i}),'r');
            formatSpec = '%f %f %f %f %f %f';
            motion_data = fscanf(fileID,formatSpec);

            %reshape and remove first 5 volums
            motion_data=transpose(reshape(motion_data,[6,296]));

            %calculate mean FD
            %parameter_source == 'FSL':
            translations = abs(diff(motion_data(:,4:6)));
            rotations = abs(diff(motion_data(:,1:3)));

            FD_power = sum(translations,2) + sum((50*rotations),2);
            all_res(i,1)=mean([0;sum(translations,2) + sum((50*rotations),2)]);
            all_res(i,2)=max([0;sum(translations,2) + sum((50*rotations),2)]);
            
        
            %DVARS data (standardized BOLD signal in entire brain mask)
            if isfile(sprintf(['/data/pt_life/LIFE_fu/wd_preprocessing/hcp_prep_workflow/resting/'...
                                  'transform_timeseries/_subject_%s/dvars/rest2anat_dvars.tsv'], subjects{1}{i}))

                dvars=tdfread(sprintf(['/data/pt_life/LIFE_fu/wd_preprocessing/hcp_prep_workflow/resting/'...
                                  'transform_timeseries/_subject_%s/dvars/rest2anat_dvars.tsv'], subjects{1}{i}));
                dvars_std=dvars.std_DVARS;   

                %results head motion & DVARS

                all_res(i,5)=mean(dvars_std);
                all_res(i,6)=max(dvars_std);
                all_res(i,7)=corr(dvars_std,FD_power);
            end
        end
        
        %write baseline motion (if available)
        if isfile(sprintf('/data/pt_life_restingstate/LIFE/preprocessed/%s/resting_state/realign/rest_realigned.par', subjects{1}{i}))
            fileID = fopen(sprintf('/data/pt_life_restingstate/LIFE/preprocessed/%s/resting_state/realign/rest_realigned.par', subjects{1}{i}),'r');
            formatSpec = '%f %f %f %f %f %f';
            motion_data = fscanf(fileID,formatSpec);

            
            if length(motion_data)<1770
                continue
            else
            %reshape and remove first 5 volums
            motion_data=transpose(reshape(motion_data,[6,295]));

            %calculate mean FD
            %parameter_source == 'FSL':
            translations = abs(diff(motion_data(:,4:6)));
            rotations = abs(diff(motion_data(:,1:3)));

            FD_power_BL = [0;sum(translations,2) + sum((50*rotations),2)];
            all_res(i,3)=mean(FD_power_BL);
            all_res(i,4)=max(FD_power_BL);
            end
        end
        
        %PHYSIOLOGICAL data
        if isfile(sprintf("/data/pt_life_restingstate_followup/Data/physio/%s.mat", subjects{1}{i}))
                phys_data=load(sprintf("/data/pt_life_restingstate_followup/Data/physio/%s.mat", subjects{1}{i}));

                %use respiratory and PPU traces resampled to volume acquisitions.
                resp=phys_data.physio.trace.resp;
                oxy=phys_data.physio.trace.oxy;

                %remove first 5 volumes.
                resp=resp(6:300);
                oxy=oxy(6:300);

                all_res(i,8)=corr(FD_power,resp);
                all_res(i,9)=corr(FD_power,oxy);
                all_res(i,10)=corr(FD_power,phys_data.physio.ons_secs.rvt(6:end));
                all_res(i,11)=corr(FD_power,phys_data.physio.ons_secs.hr(6:end)); 
		if isfile(sprintf(['/data/pt_life/LIFE_fu/wd_preprocessing/hcp_prep_workflow/resting/'...
                                  'transform_timeseries/_subject_%s/dvars/rest2anat_dvars.tsv'], subjects{1}{i}))
                	all_res(i,12)=corr(dvars_std,resp);
                	all_res(i,13)=corr(dvars_std,oxy);
                	all_res(i,14)=corr(dvars_std,phys_data.physio.ons_secs.rvt(6:end));
                	all_res(i,15)=corr(dvars_std,phys_data.physio.ons_secs.hr(6:end)); 
		end

        else 
            continue
        end
    %end
      
end
% 
% T = array2table(all_res, 'VariableNames',{'meanFD','maxFD','meanFD_BL','maxFD_BL','meanstdDVARS', 'maxstdDVARS', 'corr_FD_stdDVARS'...
%                                            'corr_FD_resp','corr_FD_oxy','corr_FD_RVT','corr_FD_HR',...
%                                            'corr_dvars_resp','corr_dvars_oxy','corr_dvars_RVT','corr_dvars_HR'})
%  
% T_final=[cell2table(subjects{1}),T];
% writetable(T,'/data/pt_life_restingstate_followup/results/results_rs_motion_physio.csv')
% 
% writetable(cell2table(subjects{1}),'/data/pt_life_restingstate_followup/results/SIC.csv')



%%PLOT: compare downsampled DVARS/FD and physioparams.
figure()
subplot(4,1,1)
plot(dvars_std, 'y','LineWidth',2)
title("DVARS")
subplot(4,1,2)
plot(FD_power, 'g','LineWidth',2)
title("FD displacement")
subplot(4,1,3)
%plot(phys_data.physio.ons_secs.t,phys_data.physio.ons_secs.fr, 'g','LineWidth',2)
%hold on
plot(resp, 'blue','LineWidth',2)
title("respiratory trace (a.u.), downsampled")
subplot(4,1,4)
%plot(phys_data.physio.ons_secs.t,phys_data.physio.ons_secs.c, 'blue','LineWidth',2)
%hold on
plot(oxy, 'b','LineWidth',2)
title("PPU trace (a.u.), downsampled")

%%PLOT original data compared to downsampled data
figure()
subplot(4,1,1)
plot(phys_data.physio.ons_secs.fr, 'g','LineWidth',2)
title("resp data, original time resolution, filtered, cropped to acquisition window")
subplot(4,1,2)
plot(resp, 'blue','LineWidth',2)
title("resp data, resampled to TR, filtered")
subplot(4,1,3)
plot(phys_data.physio.ons_secs.c, 'blue','LineWidth',2)
title("cardiac data, original time resolution, filtered, cropped to acquisition window")
subplot(4,1,4)
plot(oxy, 'b','LineWidth',2)
title("cardiac data, resampled to TR, filtered")

%%PLOT HRV and RVT and mean FD and DVARS
figure()
subplot(4,1,1)
plot(phys_data.physio.ons_secs.hr(6:end), 'r','LineWidth',2)
title("HR")
subplot(4,1,2)
plot(phys_data.physio.ons_secs.rvt(6:end), 'r','LineWidth',2)
title("RVR")
subplot(4,1,3)
plot(FD_power, 'g','LineWidth',2)
title("FD displacement")
subplot(4,1,4)
plot(dvars_std, 'y','LineWidth',2)
title("DVARS")

