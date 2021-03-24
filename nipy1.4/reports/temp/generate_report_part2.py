from glob import glob
from correlation import get_similarity_distribution
from motion import get_mean_frame_displacement_disttribution
from volumes import get_median_distribution
from reports import create_report, read_dists, check
import pandas as pd
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import Function, IdentityInterface
from nipype.interfaces.io import SelectFiles


if __name__ == '__main__':
    
    data_dir = "/data/pt_nro148/3T/restingstate_and_freesurfer/"
    out_dir= "/data/pt_nro148/3T/restingstate_and_freesurfer/quality_reports/Julias_reports/"
    fs_dir= "/data/pt_nro148/3T/restingstate_and_freesurfer/preprocessing/freesurfer"    
    
    
    subjects_file = '/data/pt_nro148/3T/restingstate_and_freesurfer/Lists/RSV_3T_FU_all_available_subjects.txt'
    stats_file = out_dir+"summary_FU.csv"
    check_file = out_dir+'checklist_FU.txt'
    

    wf = Workflow("reports_part2")
    wf.base_dir = "/data/pt_nro148/3T/restingstate_and_freesurfer/quality_reports/wd/"
    wf.config['execution']['crashdump_dir'] = wf.base_dir + "crash_files/"

    with open(subjects_file, 'r') as f: # can be made dependent on scan
        subjects = [line.strip() for line in f]

    #subjects=['RSV001']    
    #subjects.sort()
    #subjects.remove('26858')
    #subjects.remove('26435')
    #subjects.remove('27062')
    
    
    subjects = [x for x in subjects]
    subjects = ['RSV143', 'RSV150']
    
    
    def make_stats(template):
        return template
    
    make_statsfile = Node(Function(input_names=['template'],
                                    output_names=['fname'],
                                    function=make_stats),
                           name='make_statsfile')
    make_statsfile.inputs.template = stats_file
    
    
    read_distributions = Node(Function(input_names=['csv_file'],
                                       output_names=['similarity_distribution',
                                                     'mean_FD_distribution',
                                                     'tsnr_distributions'],
                                       function=read_dists),
                              name='read_distributions')
    
    
    subject_infosource = Node(IdentityInterface(fields=['subject_id']), 
                              name='subject_infosource')
    subject_infosource.iterables=('subject_id', subjects)
    
    
    # select files
    templates={'stats_file' : "quality_reports/Julias_reports/summary_FU.csv",
                'tsnr_file' : "preprocessing/preprocessed/{subject_id}/resting_state/realign/tsnr.nii.gz",
                'timeseries_file' : "preprocessing/preprocessed/{subject_id}/resting_state/denoise/rest_preprocessed_nativespace.nii.gz",
                'realignment_parameters_file' : "preprocessing/preprocessed/{subject_id}/resting_state/realign/rest_realigned.par",
                'mean_epi_file' : "preprocessing/preprocessed/{subject_id}/resting_state/coregister/rest_mean2fmap_unwarped.nii.gz",
                'mean_epi_uncorrected_file' :"preprocessing/preprocessed/{subject_id}/resting_state/coregister/rest_mean2fmap.nii.gz",
                'mask_file' : "preprocessing/preprocessed/{subject_id}/resting_state/denoise/mask/T1_brain_mask2epi.nii.gz",
                'reg_file' : "preprocessing/preprocessed/{subject_id}/resting_state/coregister/transforms2anat/rest2anat.dat",
                'mincost_file' : "preprocessing/preprocessed/{subject_id}/resting_state/coregister/rest2anat.dat.mincost",
                'wm_file' : "preprocessing/preprocessed/{subject_id}/structural/T1_brain_wmedge.nii.gz"         
               }
    selectfiles = Node(SelectFiles(templates, base_directory=data_dir),
                       name="selectfiles")
       
    
    def make_out(out_dir, subject_id):
        f = out_dir+"%s_report.pdf"%(subject_id)
        return f
    
    
    make_outfile = Node(Function(input_names=['out_dir',
                                              'subject_id',
                                             ],
                                 output_names=['output_file'], 
                                 function = make_out),
                        name='make_outfile')
    make_outfile.inputs.out_dir = out_dir
    
        
    report = Node(Function(input_names=['subject_id', 
                                         'tsnr_file', 
                                         'realignment_parameters_file', 
                                         'parameter_source',
                                         'mean_epi_file',
                                         'mean_epi_uncorrected_file',
                                         'wm_file', 
                                         'mask_file', 
                                         'reg_file', 
                                         'fssubjects_dir', 
                                         'similarity_distribution', 
                                         'mean_FD_distribution', 
                                         'tsnr_distributions', 
                                         'output_file'], 
                            output_names=['out', 'subject_id'],
                            function = create_report), name="report")
    report.inputs.parameter_source = 'FSL'
    report.inputs.fssubjects_dir = fs_dir
    
    check_report = Node(Function(input_names=['subject_id', 'checklist'],
                                 output_names=['checklist'],
                                 function=check),
                        name='check_report')
    check_report.inputs.checklist = check_file
    
    
    
    wf.connect([(subject_infosource, selectfiles, [('subject_id', 'subject_id')]),
                (subject_infosource, make_outfile, [('subject_id', 'subject_id')]),
                (subject_infosource, report, [('subject_id', 'subject_id')]),
                (selectfiles, report, [('tsnr_file', 'tsnr_file'),
                                        ('realignment_parameters_file', 'realignment_parameters_file'),
                                        ('mean_epi_file', 'mean_epi_file'),
                                        ('mean_epi_uncorrected_file', 'mean_epi_uncorrected_file'),                                        
                                        ('mask_file', 'mask_file'),
                                        ('reg_file', 'reg_file'),
                                        ('wm_file', 'wm_file')
                                        ]),
                (make_statsfile, read_distributions, [('fname', 'csv_file')]),
                (read_distributions, report, [('similarity_distribution', 'similarity_distribution'),
                                              ('mean_FD_distribution', 'mean_FD_distribution'),
                                              ('tsnr_distributions', 'tsnr_distributions')]),
                (make_outfile, report, [('output_file', 'output_file')]),
                (report, check_report, [('subject_id', 'subject_id')])
                ])
                
    wf.run() #plugin='MultiProc', plugin_args={'n_procs' : 20})
         
