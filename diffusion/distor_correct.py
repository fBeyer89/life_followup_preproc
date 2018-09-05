# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 13:13:53 2018

@author: Rui Zhang
"""
'''
Commands use during diffusion-weighted images preprocessing
=========================================================================
Warp commands dwidenoise & mrdegibbs from MRTrix3.0; eddy-openmp from FSL
-------------------------------------------------------------------------
for unkonwn reason they are not included after loading relavant interface
'''
from nipype import Node, Workflow
from dwi_corr_util import (MRdegibbs, DWIdenoise, Eddy)
from nipype.interfaces import fsl
from nipype.interfaces import utility as util



def create_distortion_correct():
    # fsl output type
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    # initiate workflow
    distor_correct = Workflow(name='distor_correct')
    # input node
    inputnode = Node(util.IdentityInterface(fields=[
        'dwi',
        'dwi_ap',
        'dwi_pa',
        'bvals',
        'bvecs',
        'echo_space'
    ]),
        name='inputnode')
    # output node
    outputnode = Node(util.IdentityInterface(fields=[
        'bo_brain',
        "bo_brainmask",
        'noise',
        'dwi_denoised',
        "dwi_unringed",
        "dwi_appa",
        "topup_bo",
        "topup_corr",
        "topup_field",
        "topup_fieldcoef",
        "eddy_corr",
        "rotated_bvecs"
    ]),
        name='outputnode')

    ''
    # noise reduction on all images
    ''
    denoise = Node(DWIdenoise(noise='noise.nii.gz'), name="denoise")

    ''
    # artefact removal
    ''
    # run unring: remove the ringing artefacts
    unring = Node(MRdegibbs(), name="unring")

    ''
    # topup and eddy #TODO: make acqparams and index files
    ''
    # merge AP PA files together

    b0_comb = Node(util.Merge(2), name='b0_comb')
    merger = Node(fsl.Merge(), name='merger')
    merger.inputs.dimension = 't'
    merger.inputs.merged_file = 'dwi_appa.nii.gz'
    distor_correct.connect([
        (inputnode, b0_comb, [('dwi_ap', 'in1')]),
        (inputnode, b0_comb, [('dwi_pa', 'in2')]),
        (b0_comb, merger, [('out', 'in_files')])
    ])

    # topup
    topup = Node(fsl.TOPUP(), name='topup')
    topup.inputs.config = "/data/pt_life_dti/scripts/life_FU/b02b0.cnf" #use optimised parameters
    topup.inputs.encoding_file = '/data/pt_life_dti/test/acqparams_dwi.txt'
    # topup.inputs.out_base = 'diff_topup'
    # --> Total readout time (FSL) = (number of echoes - 1) * echo spacing = (64-1)*0.78ms=49.14 ms #bcuz of GRAPPA

    # skullstrip process using bet
    # mean of all b0 unwarped images
    maths = Node(fsl.ImageMaths(op_string='-Tmean'), name="maths")

    # create a brain mask from the b0 unwarped
    bet = Node(interface=fsl.BET(), name='bet')
    bet.inputs.mask = True
    bet.inputs.frac = 0.2
    bet.inputs.robust = True

    # eddy motion correction
    eddy = Node(Eddy(), name="eddy")
    eddy.inputs.num_threads = 8 #TODO: does not work for more than 8, but without defining here would only use one cpu, a fix?
    eddy.inputs.args = '--cnr_maps --residuals'
    eddy.inputs.repol = True
    eddy.inputs.in_acqp = '/data/pt_life_dti/test/acqparams_dwi.txt'
    eddy.inputs.in_index = '/data/pt_life_dti/test/index.txt'

    ''
    # connect the nodes
    ''
    distor_correct.connect([

        (merger, topup, [("merged_file", "in_file")]),
        (topup, outputnode, [('out_corrected', 'topup_bo')]),
        (topup, outputnode, [('out_fieldcoef', 'topup_fieldcoef')]),
        (topup, outputnode, [('out_field', 'topup_field')]),
        (topup, maths, [('out_corrected', 'in_file')]),
        (maths, outputnode, [('out_file', 'dwi_appa')]),
        (maths, bet, [("out_file", "in_file")]),
        (bet, outputnode, [("mask_file", "bo_brainmask")]),
        (bet, outputnode, [("out_file", "bo_brain")]),
        (bet, eddy, [("mask_file", "in_mask")]),
        (inputnode, eddy, [("bvecs", "in_bvec")]),
        (inputnode, eddy, [("bvals", "in_bval")]),
        (topup, eddy, [("out_fieldcoef", "in_topup_fieldcoef")]),
        (topup, eddy, [("out_movpar", "in_topup_movpar")]),
        (inputnode, denoise, [('dwi', 'in_file')]),
        (denoise, outputnode, [('out_file', 'dwi_denoised')]),
        (denoise, unring, [('out_file', 'in_file')]),
        (unring, outputnode, [('out_file', 'dwi_unringed')]),
        (unring, eddy, [("out_file", "in_file")]),
        (eddy, outputnode, [("out_corrected", "eddy_corr")]),
        (eddy, outputnode, [("out_rotated_bvecs", "rotated_bvecs")])

    ])

    return distor_correct
