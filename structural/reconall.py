# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 11:12:37 2015

@author: fbeyer
"""

from nipype.pipeline.engine import Workflow, Node
import nipype.interfaces.utility as util
import nipype.interfaces.freesurfer as fs
'''
Workflow to run freesurfer recon-all -all and collect original output
'''
def create_reconall_pipeline(name='reconall'):
    reconall=Workflow(name='reconall')
    #inputnode
    inputnode=Node(util.IdentityInterface(fields=['anat',
    'fs_subjects_dir',
    'fs_subject_id'
    ]),
    name='inputnode')
    outputnode=Node(util.IdentityInterface(fields=['fs_subjects_dir',
    'fs_subject_id']),
    name='outputnode')
    
    def rename_subject_for_fu(input_id):
        output_id=input_id+"_fu"
        return output_id
       
    #modify subject name so it can be saved in the same folder as other LIFE- freesurfer data
    rename=Node(util.Function(input_names=['input_id'], 
                            output_names=['output_id'],
                            function = rename_subject_for_fu), name="rename")  
    
    # run reconall
    recon_all = Node(fs.ReconAll(args='-all -hippo-subfields -no-isrunning', openmp=8), #FS version 6.0: -hippocampal-subfields-T1, version 5.3.. -hippo-subfields
    name="recon_all")
    #recon_all.inputs.directive= 'autorecon2-wm' # -autorecon3
    recon_all.plugin_args={'submit_specs': 'request_memory = 9000'}
    reconall.connect([
    (inputnode, rename, [('fs_subject_id', 'input_id')]),
    (rename, recon_all, [('output_id', 'subject_id')]),
    (inputnode, recon_all, [('fs_subjects_dir', 'subjects_dir'),
                            ('anat', 'T1_files')]),
    (recon_all, outputnode, [('subject_id', 'fs_subject_id'),
    ('subjects_dir', 'fs_subjects_dir')])
    ])
    return reconall
