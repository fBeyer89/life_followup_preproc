from glob import glob
from base_reports import create_report, read_dists, check
import pandas as pd
from nipype.pipeline.engine import Workflow, Node
from nipype.interfaces.utility import Function, IdentityInterface
from nipype.interfaces.io import SelectFiles
from dwi_util import calculate_mean_bo_b_images

def create_base_report():
 
    # main workflow
    create_base_report = Workflow(name='base_report')  
    
    
    inputnode=Node(IdentityInterface(fields=
    ['subject',
    'tsnr_file',
    'realignment_parameters_file',
    'mean_epi_file',
    'mean_epi_file_unwarped',
    'brain_mask',
    'T1',
    'dwi_file',
    'bvals',
    'bvecs',
    'FA_file',
    'reg_file_dwi',
    'flair_file',
    'out_dir',
    'freesurfer_dir',
    'wm_file',
    'reg_file',
    'dvars_file'
    ]),
    name='inputnode') 

    outputnode=Node(IdentityInterface(fields=['report']),
    name='outputnode')    
       
     
    prep_dwi_calc = Node(Function(input_names=["dwi_file", "bval_file", "bvec_file"],
                              output_names=["dti_available","mean_bo", "bimages"],
                              function = calculate_mean_bo_b_images), name="prep_bo")     
    
    def make_out(out_dir, subject_id):
        f = out_dir+"%s_report.pdf"%(subject_id)
        return f
    
    
    make_outfile = Node(Function(input_names=['out_dir',
                                              'subject_id',
                                             ],
                                 output_names=['output_file'], 
                                 function = make_out),
                        name='make_outfile')
    
        
    report = Node(Function(input_names=['subject_id', 
                                         'tsnr_file', 
                                         'realignment_parameters_file', 
                                         'parameter_source',
                                         'mean_epi_file',
                                         'mean_epi_uncorrected_file',
                                         'T1_file',
                                         'mask_file',
                                         'dti_available',
                                         'mean_bo',
                                         'b_images',
				         'FA_file',
					 'reg_file_dwi',
                                         'flair_file',
                                         'wm_file', 
                                         'reg_file',
                                         'fssubjects_dir',           
                                         'output_file',
                                         'dvars_file'
                                         ], 
                                                                                
                            output_names=['out', 'subject_id'],
                            function = create_report), name="report")
    report.inputs.parameter_source = 'FSL'

    
    
    create_base_report.connect([(inputnode, make_outfile, [('subject', 'subject_id')]),
                                (inputnode, make_outfile, [('out_dir', 'out_dir')]),
                                (inputnode, prep_dwi_calc, [('dwi_file', 'dwi_file'),
                                                            ('bvals', 'bval_file'),
                                                            ('bvecs', 'bvec_file')]),
                                (prep_dwi_calc, report, [('dti_available', 'dti_available'),
                                                         ('mean_bo', 'mean_bo'),
                                                         ('bimages', 'b_images')]),
                                (inputnode, report, [('subject', 'subject_id'),
                                                     ('tsnr_file', 'tsnr_file'),
                                                     ('FA_file','FA_file'),
                                                     ('reg_file_dwi','reg_file_dwi'),
                                                     ('realignment_parameters_file', 'realignment_parameters_file'),
                                                     ('dvars_file','dvars_file'),
                                                     ('mean_epi_file', 'mean_epi_uncorrected_file'), 
                                                     ('mean_epi_file_unwarped', 'mean_epi_file'),        
                                                     ('brain_mask', 'mask_file'), 
                                                     ('T1', 'T1_file'),                                                
                                                     ('flair_file', 'flair_file'), 
                                                     ('freesurfer_dir', 'fssubjects_dir'),                                  
                                                     ('wm_file', 'wm_file'),
                                                     ('reg_file', 'reg_file')
                                  ]),
                                 (make_outfile, report, [('output_file', 'output_file')]),
                                 (report, outputnode, [('out', 'report')])
                                  #check_report, [('subject_id', 'subject_id')])
                ])
                
    return create_base_report #plugin='MultiProc', plugin_args={'n_procs' : 20})
         
