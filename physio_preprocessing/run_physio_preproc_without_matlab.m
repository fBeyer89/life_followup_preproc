%add tapas toolbox to path
addpath(genpath('/data/u_fbeyer_software/spm-fbeyer'))



%Specify variables
subjects_file='/data/gh_gr_agingandobesity_share/life_shared/Results/External_coops/PV240_Dagher_Scholz_headmotion_gwas/Amendment2021/Analysis/all_data_final_30.06.21.txt';

subjID = fopen(subjects_file);
subjects=textscan(subjID,'%s');

%create output file
res=ones(length(subjects{:}),2);

physio_in.log_files.vendor="Siemens";
physio_in.log_files.sampling_interval=[];
physio_in.log_files.align_scan='last';
physio_in.log_files.relative_start_acquisition=0;

physio_in.scan_timing.sqpar.Nslices           = 30;   % number of slices per volume in fMRI scan
physio_in.scan_timing.sqpar.NslicesPerBeat    = 30;   % usually equals Nslices, unless you trigger with the heart beat
physio_in.scan_timing.sqpar.TR                = 2;   % volume repetition time in seconds
physio_in.scan_timing.sqpar.Ndummies          = 0;   % number of dummy volumes
    
physio_in.scan_timing.sqpar.Nscans            = 300;
physio_in.scan_timing.sqpar.Nprep             = 0;
physio_in.scan_timing.sqpar.time_slice_to_slice  = 0.067;
physio_in.scan_timing.sqpar.onset_slice       =  1;
physio_in.scan_timing.sync.method = 'nominal';

physio_in.preproc.cardiac.modality = 'PPU';
physio_in.preproc.cardiac.initial_cpulse_select.method = 'auto'; %automated detection works better than reading from log-file.
physio_in.preproc.cardiac.initial_cpulse_select.file = '';
physio_in.preproc.cardiac.initial_cpulse_select.min = 1;
physio_in.preproc.cardiac.initial_cpulse_select.kRpeak = [];
physio_in.preproc.cardiac.posthoc_cpulse_select.method = 'on'; %manual correction can be an option.
physio_in.preproc.cardiac.posthoc_cpulse_select.file='';
physio_in.preproc.cardiac.posthoc_cpulse_select.percentile = 80; %percentile of 
                                                                 %beat-2-beat interval histogram 
                                                                 %that constitutes the "average heart beat duration" 
                                                                 %in the session
physio_in.preproc.cardiac.posthoc_cpulse_select.upper_thresh = 60; % minimum exceedance (in %) 
                                                                   %from average heartbeat duration 
                                                                   %to be classified as missing heartbeat
physio_in.preproc.cardiac.posthoc_cpulse_select.lower_thresh = 60; % minimum reduction (in %) 
                                                                   %from average heartbeat duration
                                                                   %to be classified an abundant heartbeat
  
physio_in.model.orthogonalise = 'none';  
physio_in.model.retroicor.include = 1; % 1 = included; 0 = not used
physio_in.model.retroicor.order.c = 3;
physio_in.model.retroicor.order.r = 4;
physio_in.model.retroicor.order.cr = 1; 
physio_in.model.output_multiple_regressors = 'multiple_regressors.txt';
physio_in.model.movement.include = 0;
physio_in.model.movement.file_realignment_parameters = '';
physio_in.model.hrv.include=1;
physio_in.model.hrv.delays = 0;
physio_in.model.other.include = 0;
physio_in.model.other.input_multiple_regressors = '';
physio_in.model.output_physio='';
physio_in.model.rvt.include=1;
physio_in.model.rvt.delays = 0;
physio_in.model.noise_rois.include=0;
physio_in.model.movement.include=0;

physio_in.ons_secs = [];
physio_in.verbose.level = 2;
physio_in.verbose.process_log = cell(0,1); 
                                % stores text outputs of PhysIO Toolbox
                                % processing, e.g. warnings about missed
                                % slice triggers, peak height etc.
physio_in.verbose.fig_handles = zeros(0,1);  


for i=[36,137,150,442,559,885,965,597] %size(subjects{1},1) 
    %test subjects:
    % low FD, highRR: 36, 137, 150, 442
    % high FD, low RR: 559, 885, 965, 597
    
    sprintf("Subject number: %i and ID: %s", i,subjects{1}{i})

    
    %%exclude participants with faulty data based on file size/error during
    %%processing (not used as input is only "clean data")
    if subjects{1}{i}=="LI02271832"||subjects{1}{i}=="LI00143114"||subjects{1}{i}=="LI00706330"||...
        subjects{1}{i}=="LI00552556"||subjects{1}{i}=="LI00605658"||subjects{1}{i}=="LI00752733"||...
        subjects{1}{i}=="LI0127843X"||subjects{1}{i}=="LI02692576"||subjects{1}{i}=="LI03736172"||...
        subjects{1}{i}=="LI03436577"||subjects{1}{i}=="LI03403894"||subjects{1}{i}=="LI00647018"||...
        subjects{1}{i}=="LI02478671"||subjects{1}{i}=="LI0353619X"||subjects{1}{i}=="LI02550372"||...
        subjects{1}{i}=="LI00640890"||subjects{1}{i}=="LI00958910"||subjects{1}{i}=="LI03413232"||...
        subjects{1}{i}=="LI02002716"
       continue
    else
    %subject dependent saving options
    mkdir(sprintf('/data/pt_life_restingstate_followup/Data/physio/%s', subjects{1}{i}));
    physio_in.save_dir = sprintf('/data/pt_life_restingstate_followup/Data/physio/%s', subjects{1}{i});
    sprintf('/data/pt_life_restingstate_followup/Data/physio/%s/results.jpg', subjects{1}{i})
    physio_in.verbose.fig_output_file = sprintf('/data/pt_life_restingstate_followup/Data/physio/%s/results.jpg', subjects{1}{i}); 
    %physio_in.verbose.fig_output_file = sprintf('/data/pt_life/data_fbeyer/testing_LIFE_fu/preprocessed/physio/%s/results.jpg', subjects{i}); 

    %Define variables for individual subjects MRI data
    files=dir(sprintf('/data/p_life_raw/patients/%s/%s_20*/Scans.txt', subjects{1}{i},subjects{1}{i}));
    %always select last folder (most current)
    files=files(end);
    
    %find last rsfMRI scan volume:    
    fileID = fopen(sprintf("%s/%s",files.folder,files.name),'r');
    formatSpec = '%s %s';
    A = fscanf(fileID,formatSpec);
    %find index where cmrr_mbep2d_resting starts
    index=strfind(A,'cmrr_mbep2d_resting');
    %dicom index is used to find right dicom for timing information
    dicom_number=A(index-4:index-1);
    last_epi_volume=sprintf('%s%s%s', dicom_number,'0300');
    files=dir(sprintf('/data/p_life_raw/patients/%s/%s_20*/DICOM/%s', subjects{1}{i},subjects{1}{i}, last_epi_volume));
    files=files(end);
    physio_in.log_files.scan_timing = sprintf("%s/%s",files.folder,files.name); 
  
    %find resp and cardiac files
    files=dir(sprintf('/data/p_life_raw/patients/%s/%s_20*/PHYS_%s/%s/Physio_log_*.resp', subjects{1}{i},subjects{1}{i},subjects{1}{i},subjects{1}{i}));
    
    if isempty(files)
        res(i,1)=0;
    else    
        if length(files)>1
            %find which one is the resting state scan (eg the earlier one)
            if datetime(files(1).date)<datetime(files(2).date)
                sprintf("the first data point is the earlier one")
                physio_in.log_files.respiration=sprintf("%s/%s",files(1).folder,files(1).name);
            else
                sprintf("the last data point is the earlier one") 
                physio_in.log_files.respiration=sprintf("%s/%s",files(2).folder,files(2).name);
            end
        else
            physio_in.log_files.respiration=sprintf("%s/%s",files(1).folder,files(1).name);
        end
    end
       
    files=dir(sprintf('/data/p_life_raw/patients/%s/%s_20*/PHYS_%s/%s/Physio_log_*.puls', subjects{1}{i},subjects{1}{i},subjects{1}{i},subjects{1}{i}));
    if isempty(files)
        res(i,2)=0;
    else   
        if length(files)>1
            %find which one is the resting state scan (eg the earlier one)
            if datetime(files(1).date)<datetime(files(2).date)
                %sprintf("the first data point is the earlier one")
                physio_in.log_files.cardiac=sprintf("%s/%s",files(1).folder,files(1).name);
            else
                %sprintf("the last data point is the earlier one") 
                physio_in.log_files.cardiac=sprintf("%s/%s",files(2).folder,files(2).name);
            end 
       else
            physio_in.log_files.cardiac=sprintf("%s/%s",files(1).folder,files(1).name);
        end
        

    end
    
    %doesNeedPhyslogFilesonly if both physio files are available run analysis.
    if (res(i,1)~=0&&res(i,2)~=0)
       %create & run physio file
       physio = tapas_physio_new('empty', physio_in);
       [physio_out, R, ons_secs, resp] = tapas_physio_main_create_regressors(physio);

       %saving resp and oxy trace to later visually compare to fMRI and
       %head motion
       r=physio_out.trace.resp;
       save(sprintf('/data/pt_life_restingstate_followup/Data/physio/%s_resp.mat', subjects{1}{i}),'r','-v7')  	
       rvt=physio_out.ons_secs.rvt;
       save(sprintf('/data/pt_life_restingstate_followup/Data/physio/%s_rvt.mat', subjects{1}{i}),'rvt','-v7') 
       hr=physio_out.ons_secs.hr;
       save(sprintf('/data/pt_life_restingstate_followup/Data/physio/%s_hr.mat', subjects{1}{i}),'hr','-v7')
       c=physio_out.trace.oxy; 
       save(sprintf('/data/pt_life_restingstate_followup/Data/physio/%s_oxy.mat', subjects{1}{i}),'c','-v7') 
       
       %save physio params in separate text file
       phys_params=[resp,mean(ons_secs.hr)];
       save(sprintf('/data/pt_life_restingstate_followup/Data/physio/%s_RVT_RR_HR.txt', subjects{1}{i}),'phys_params', '-ascii', '-double', '-tabs');  
	
    else
        fileID = fopen('/data/pt_life_restingstate_followup/Data/physio/missing.txt','a');
        fprintf(fileID,'%s\n',subjects{1}{i});
        fclose(fileID);
        %save(sprintf('/data/pt_life_restingstate_followup/Data/physio/missing.txt', subjects{1}{i}, 'append', '-ascii')
    end
    end


end
