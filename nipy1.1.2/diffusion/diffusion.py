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


def create_dti():
    # main workflow for preprocessing diffusion data
    # fsl output type
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    # Initiation of a workflow
    dwi_preproc = Workflow(name="dwi_preproc")
    # inputnode
    inputnode = Node(IdentityInterface(fields=[
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
    # workflow to run distortion correction
    ''
    distor_corr = create_distortion_correct()

    #''
    ## upsampling #TODO: upsample with eddy directly, waiting for Alfred for the method
    #''
    #flirt = Node(fsl.FLIRT(), name='flirt')
    #flirt.inputs.apply_isoxfm = 1
    #TODO: to use this for dtifit, needed to creat another brain mask

    ''
    # tensor fitting
    ''
    dti = Node(fsl.DTIFit(), name='dti')

    # registration of FA to T1 FREESURFER output (BBregister)?

    ''
    # connecting the nodes
    ''
    dwi_preproc.connect([

        (inputnode, distor_corr, [('dwi', 'inputnode.dwi')]),
        (inputnode, distor_corr, [('dwi_ap', 'inputnode.dwi_ap')]),
        (inputnode, distor_corr, [('dwi_pa', 'inputnode.dwi_pa')]),
        (inputnode, distor_corr, [("bvals", "inputnode.bvals")]),
        (inputnode, distor_corr, [("bvecs", "inputnode.bvecs")]),
        (inputnode, dti, [("bvals", "bvals")]),
        (distor_corr, outputnode, [('outputnode.bo_brain', 'bo_brain')]),
        (distor_corr, outputnode, [('outputnode.bo_brainmask', 'bo_brainmask')]),
        (distor_corr, outputnode, [('outputnode.noise', 'noise')]),
        (distor_corr, outputnode, [('outputnode.dwi_denoised', 'dwi_denoised')]),
        (distor_corr, outputnode, [('outputnode.dwi_unringed', 'dwi_unringed')]),
        (distor_corr, outputnode, [('outputnode.topup_corr', 'topup_corr')]),
        (distor_corr, outputnode, [('outputnode.topup_field', 'topup_field')]),
        (distor_corr, outputnode, [('outputnode.topup_fieldcoef', 'topup_fieldcoef')]),
        (distor_corr, outputnode, [('outputnode.eddy_corr', 'eddy_corr')]),
        (distor_corr, outputnode, [('outputnode.rotated_bvecs', 'rotated_bvecs')]),
        (distor_corr, dti, [("outputnode.rotated_bvecs", "bvecs")]),
        (distor_corr, dti, [('outputnode.bo_brainmask', 'mask')]),
        #(distor_corr, flirt, [('outputnode.eddy_corr', 'in_file')]),
        #(distor_corr, flirt, [('outputnode.eddy_corr', 'reference')]),
        #(flirt, dti, [('out_file', 'dwi')]),
        (distor_corr, dti, [('outputnode.eddy_corr', 'dwi')]),
        (dti, outputnode, [('FA', 'dti_fa')]),
        (dti, outputnode, [('MD', 'dti_md')]),
        (dti, outputnode, [('L1', 'dti_l1')]),
        (dti, outputnode, [('L2', 'dti_l2')]),
        (dti, outputnode, [('L3', 'dti_l3')]),
        (dti, outputnode, [('V1', 'dti_v1')]),
        (dti, outputnode, [('V2', 'dti_v2')]),
        (dti, outputnode, [('V3', 'dti_v3')])

    ])

    return dwi_preproc
