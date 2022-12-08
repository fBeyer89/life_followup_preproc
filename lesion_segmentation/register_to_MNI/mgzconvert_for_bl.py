# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 11:19:21 2015

@author: fbeyer
"""

from nipype.pipeline.engine import Node, Workflow
import nipype.interfaces.utility as util
import nipype.interfaces.io as nio
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.fsl as fsl

'''
Workflow to extract relevant output from freesurfer directory
'''


def create_mgzconvert_pipeline(name='mgzconvert'):
    # workflow
    mgzconvert = Workflow(name='mgzconvert')
    # inputnode
    inputnode = Node(util.IdentityInterface(fields=['fs_subjects_dir', 'fs_subject_id']), name='inputnode')
    # outputnode
    outputnode = Node(util.IdentityInterface(fields=['anat_brain','anat_brain_mask',
                                                     'wmseg']),
                      name='outputnode')
    # import files from freesurfer
    fs_import = Node(interface=nio.FreeSurferSource(),
                     name='fs_import')
    
    # create brain by converting only freesurfer output
    brain_convert = Node(fs.MRIConvert(out_type='niigz',
                                       out_file='brain.nii.gz'),
                         name='brain_convert')


    # connections
    mgzconvert.connect([(inputnode, fs_import, [('fs_subjects_dir', 'subjects_dir'),
                                                ('fs_subject_id', 'subject_id')]),
                        (fs_import, brain_convert, [('brainmask', 'in_file')]),
                        (brain_convert, outputnode, [('out_file', 'anat_brain')]),
                        ])

    return mgzconvert
