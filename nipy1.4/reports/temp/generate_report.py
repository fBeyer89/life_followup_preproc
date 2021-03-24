from glob import glob
from correlation import get_similarity_distribution
from motion import get_mean_frame_displacement_disttribution
from volumes import get_median_distribution
from reports import create_report
import pandas as pd
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import Function


if __name__ == '__main__':
   # data_dir = "/afs/cbs.mpg.de/projects/mar004_lsd-lemon-preproc/probands/"
    data_dir = "/data/pt_nro148/3T/restingstate_and_freesurfer/preprocessing/preprocessed/"
    
    #out_dir= "/afs/cbs.mpg.de/projects/mar004_lsd-lemon-preproc/results/reports/lsd/"
    out_dir= "/data/pt_nro148/3T/restingstate_and_freesurfer/quality_reports/Julias_reports/"
    
    #fs_dir= "/afs/cbs.mpg.de/projects/mar004_lsd-lemon-preproc/freesurfer/"
    #fs_dir= "/afs/cbs.mpg.de/projects/mar004_lsd-lemon-preproc/freesurfer/"
    
    
    #scans =  ['rest1', 'rest2', 'rest3', 'rest4', 'rest5', 'rest6'] 
    wf = Workflow("reports")
    wf.base_dir = "/data/pt_nro148/3T/restingstate_and_freesurfer/quality_reports/wd/"
    wf.config['execution']['crashdump_dir'] = wf.base_dir + "crash_files/"
    
    
    with open('/data/pt_nro148/3T/restingstate_and_freesurfer/Lists/RSV_3T_FU_all_available_subjects.txt', 'r') as f:
        subjects = [line.strip() for line in f]
    #subjects.sort()
    subjects= ['RSV143', 'RSV150'] 
    #generating distributions
    print 'generating similarity'
    mincost_files = [data_dir + "%s/resting_state/coregister/rest2anat.dat.mincost"%(subject) for subject in subjects]
    similarity_distribution = get_similarity_distribution(mincost_files)
    
                             
    print 'generating mean fd'
    realignment_parameters_files = [data_dir + "%s/resting_state/realign/rest_realigned.par"%(subject) for subject in subjects]
    mean_FD_distribution, max_FD_distribution = get_mean_frame_displacement_disttribution(realignment_parameters_files, 'FSL')
      
    print 'generating tsnr'
    tsnr_files = [data_dir + "%s/resting_state/realign/tsnr.nii.gz"%(subject) for subject in subjects]
    mask_files = [data_dir + "%s/resting_state/denoise/mask/T1_brain_mask2epi.nii.gz"%(subject) for subject in subjects]
    tsnr_distributions = get_median_distribution(tsnr_files, mask_files)
     
    df = pd.DataFrame(zip(subjects, similarity_distribution, mean_FD_distribution, max_FD_distribution, tsnr_distributions), columns = ["subject_id", "coregistration quality", "Mean FD", "Max FD", "Median tSNR"])
    df.to_csv(out_dir+"summary_FU.csv")
    
#        similarity_distribution = dict(zip(subjects, similarity_distribution))
    
#         for subject in subjects:
#             #setting paths for this subject
#             tsnr_file = data_dir + "%s/preprocessed/lsd_resting/%s/realign/rest_realigned_tsnr.nii.gz"%(subject, scan)
#             
#             timeseries_file = data_dir + "%s/preprocessed/lsd_resting/%s/rest_preprocessed.nii.gz"%(subject, scan)
#             realignment_parameters_file = data_dir + "%s/preprocessed/lsd_resting/%s/realign/rest_realigned.par"%(subject, scan)
#     
#             wm_file = data_dir + "%s/preprocessed/anat/T1_brain_wmedge.nii.gz"%(subject)
#             mean_epi_file = data_dir + "%s/preprocessed/lsd_resting/%s/coregister/rest_mean2fmap_unwarped.nii.gz"%(subject, scan)
#             mean_epi_uncorrected_file = data_dir + "%s/preprocessed/lsd_resting/%s/coregister/rest_mean2fmap.nii.gz"%(subject, scan)
#             mask_file = data_dir + "%s/preprocessed/lsd_resting/%s/denoise/mask/T1_brain_mask2epi.nii.gz"%(subject, scan)
#             reg_file = data_dir + "%s/preprocessed/lsd_resting/%s/coregister/transforms2anat/rest2anat.dat"%(subject, scan)
#             fssubjects_dir = fs_dir
#     
#             mincost_file = data_dir + "%s/preprocessed/lsd_resting/%s/coregister/rest2anat.dat.mincost"%(subject, scan)
#             
#             output_file = out_dir+"%s_%s_report.pdf"%(subject, scan)
#             
#             report = Node(Function(input_names=['subject_id', 
#                                                  'tsnr_file', 
#                                                  'realignment_parameters_file', 
#                                                  'parameter_source',
#                                                  'mean_epi_file',
#                                                  'mean_epi_uncorrected_file',
#                                                  'wm_file', 
#                                                  'mask_file', 
#                                                  'reg_file', 
#                                                  'fssubjects_dir', 
#                                                  'similarity_distribution', 
#                                                  'mean_FD_distribution', 
#                                                  'tsnr_distributions', 
#                                                  'output_file'], 
#                                     output_names=['out'],
#                                     function = create_report), name="report_%s_%s"%(scan,subject))
#             report.inputs.subject_id = subject
#             report.inputs.tsnr_file = tsnr_file
#             report.inputs.realignment_parameters_file = realignment_parameters_file
#             report.inputs.parameter_source = 'FSL'
#             report.inputs.mean_epi_file = mean_epi_file
#             report.inputs.mean_epi_uncorrected_file = mean_epi_uncorrected_file
#             report.inputs.wm_file = wm_file
#             report.inputs.mask_file = mask_file
#             report.inputs.reg_file = reg_file
#             report.inputs.fssubjects_dir = fssubjects_dir
#             report.inputs.similarity_distribution = similarity_distribution
#             report.inputs.mean_FD_distribution = mean_FD_distribution
#             report.inputs.tsnr_distributions = tsnr_distributions
#             report.inputs.output_file = output_file
#             report.plugin_args={'override_specs': 'request_memory = 8000'}
#             wf.add_nodes([report])
          
#wf.run(plugin='MultiProc', plugin_args={'n_procs' : 10})
wf.run()
     
