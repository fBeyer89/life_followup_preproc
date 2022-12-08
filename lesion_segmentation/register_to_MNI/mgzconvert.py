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
    
    # create brainmask from aparc+aseg with single dilation
    def get_aparc_aseg(files):
        for name in files:
            if 'aparc+aseg' in name:
                return name

    # create brain by converting only freesurfer output
    brain_convert = Node(fs.MRIConvert(out_type='niigz',
                                       out_file='brain.nii.gz'),
                         name='brain_convert')

    brain_binarize = Node(fsl.ImageMaths(op_string='-bin -fillh', out_file='T1_brain_mask.nii.gz'), name='brain_binarize')

    # cortical and cerebellar white matter volumes to construct wm edge
    # [lh cerebral wm, lh cerebellar wm, rh cerebral wm, rh cerebellar wm, brain stem]
    wmseg = Node(fs.Binarize(out_type='nii.gz',
                             match=[2, 7, 41, 46, 16],#3,42
                             binary_file='T1_brain_wmseg.nii.gz'),
                 name='wmseg')

    # connections
    mgzconvert.connect([(inputnode, fs_import, [('fs_subjects_dir', 'subjects_dir'),
                                                ('fs_subject_id', 'subject_id')]),
                        (fs_import, wmseg, [(('aparc_aseg', get_aparc_aseg), 'in_file')]),
                        (fs_import, brain_convert, [('brainmask', 'in_file')]),
                        (brain_convert, outputnode, [('out_file', 'anat_brain')]),
                        (brain_convert, brain_binarize, [('out_file', 'in_file')]),
                        (brain_binarize, outputnode, [('out_file', 'anat_brain_mask')]),
                        (wmseg, outputnode, [('binary_file', 'wmseg')]),
                        ])

    return mgzconvert
