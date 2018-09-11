# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 13:41:03 2018

@author: Rui Zhang
"""

'''
Main workflow for preprocessing of diffusion-weighted data
==========================================================
Uses file structure set up by conversion
'''
from nipype import Node, Workflow
from distor_correct import create_distortion_correct
from nipype.interfaces import fsl
from nipype.interfaces.utility import IdentityInterface
import nipype.interfaces.freesurfer as fs

def coreg_fa():
    # main workflow for preprocessing diffusion data
    # fsl output type
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    # Initiation of a workflow
    coreg = Workflow(name="coreg")
    # inputnode
    inputnode = Node(IdentityInterface(fields=[
        'subject_id',
        'freesurfer_dir',
        'dwi',
        'dwi_ap',
        'dwi_pa',
        'bvals',
        'bvecs',
        'echo_space'
    ]),
        name='inputnode')
    # output node
    outputnode = Node(IdentityInterface(fields=[
        'dwi_denoised',
        "dwi_unringed",
        "topup_corr",
        "topup_field",
        "topup_fieldcoef",
        "eddy_corr",
        "rotated_bvecs",
        'dti_fa',
        'dti_md',
        'dti_l1',
        'dti_l2',
        'dti_l3',
        'dti_v1',
        'dti_v2',
        'dti_v3'
        
    ]),
        name='outputnode')

    ''
    # registration of FA to T1 FREESURFER output
    ''
    # linear registration with bbregister
    bbreg = Node(fs.BBRegister(contrast_type='t1',
    out_fsl_file='dti2anat.mat',
    out_reg_file='dti2anat.dat',
    registered_file='dti2anat_bbreg.nii.gz',
    init='fsl'
    ),
    name='bbregister')
    
    # echo " - apply the inverse of the matrix from aseg.mgz to diffusion"
# mri_vol2vol --mov  $results_dir/$subj/${subj}_fa.nii.gz --targ ${free_dir}/$subj/mri/aseg.mgz --o $results_dir/$subj/rois/aseg.nii.gz --reg $results_dir/$subj/rois/bbregister_fa_2_orig_bbr.dat --inv --nearest
    applyreg = fs.ApplyVolTransform()
    applyreg.inputs.source_file = 'structural.nii'
    applyreg.inputs.reg_file = 'register.dat'
    applyreg.inputs.transformed_file = 'struct_warped.nii'
    applyreg.inputs.fs_target = True

    coreg.connect([
		(dti, bbreg, [('FA', 'source_file')]),
        (inputnode, bbreg, [('freesurfer_dir', 'subjects_dir'),
                            ('subject_id', 'subject_id')]),
        (bbreg, outputnode, [('out_fsl_file', 'epi2anat_mat'),
                             ('out_reg_file', 'epi2anat_dat'),
                             ('registered_file', 'epi2anat'),
                             ('min_cost_file', 'epi2anat_mincost')
                            ])
    ])

    return coreg
