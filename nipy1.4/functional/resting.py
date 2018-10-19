# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 12:26:20 2015

@author: fbeyer
"""

from nipype.pipeline.engine import Node, Workflow
import nipype.interfaces.utility as util
import nipype.interfaces.io as nio
import nipype.interfaces.fsl as fsl
import nipype.interfaces.afni as afni
from strip_rois import strip_rois_func
from moco import create_moco_pipeline
from fieldmap_coreg import create_fmap_coreg_pipeline
from transform_timeseries import create_transform_pipeline

'''
Main workflow for resting state preprocessing.
====================================================
Uses basic preprocessing steps as described in Parkes, 2018
1) removal of 4 initial volumes
2) distortion correction
3) realignment of volumes to first MCFLIRT
4) demeaning and removing of linear & quadratic trends
5) co-registration to structural
#not performed 6) temporal filtering 
'''
def create_resting():

    # main workflow
    func_preproc = Workflow(name='resting')
    
    inputnode=Node(util.IdentityInterface(fields=
    ['subject_id',
    'out_dir',
    'freesurfer_dir',
    'func',
    'fmap_mag',
    'fmap_phase',
    'anat_head',
    'anat_brain',
    'anat_brain_mask',
    'vol_to_remove', 
    'TR',
    'epi_resolution',
    'echo_space', 
    'te_diff',
    'pe_dir'     
    ]),
    name='inputnode')   
           
    # node to remove first volumes
    remove_vol = Node(util.Function(input_names=['in_file','t_min'],
    output_names=["out_file"],
    function=strip_rois_func),
    name='remove_vol')
       
    # workflow for motion correction
    moco=create_moco_pipeline()
    # workflow for fieldmap correction and coregistration
    #have to rename subject for fu
    def rename_subject_for_fu(input_id):
        output_id=input_id+"_fu"
        return output_id
       
    #modify subject name so it can be saved in the same folder as other LIFE- freesurfer data
    #rename=Node(util.Function(input_names=['input_id'], 
    #                        output_names=['output_id'],
    #                        function = rename_subject_for_fu), name="rename")      
    
    
    fmap_coreg=create_fmap_coreg_pipeline()
    
    # workflow for applying transformations to timeseries
    transform_ts = create_transform_pipeline()
    
   
    #detrending
    detrend = Node(afni.Detrend(),name="detrend")
    detrend.inputs.args = '-polort 2'
    detrend.inputs.outputtype = "NIFTI"
    
    
    #outputnode
    outputnode=Node(util.IdentityInterface(fields=['par','rms','mean_epi','tsnr','fmap','unwarped_mean_epi2fmap',
                                                   'coregistered_epi2fmap', 'fmap_fullwarp', 'epi2anat', 'epi2anat_mat',
                                                   'epi2anat_dat','epi2anat_mincost','full_transform_ts',
                                                   'full_transform_mean', 'resamp_brain','detrended_epi',
                                                   'dvars_file']),
    name='outputnode')  
        
    # connections
    func_preproc.connect([
    
    #remove the first volumes    
    (inputnode, remove_vol, [('func', 'in_file')]),
    (inputnode, remove_vol, [('vol_to_remove', 't_min')]),
    (inputnode, moco, [('anat_brain_mask', 'inputnode.brainmask')]),
    #align volumes and motion correction
    (remove_vol, moco, [('out_file', 'inputnode.epi')]),
    
    #prepare field map 
    (inputnode, fmap_coreg,[('subject_id','inputnode.fs_subject_id')]),
    (inputnode, fmap_coreg, [('fmap_phase', 'inputnode.phase'),
                             ('freesurfer_dir','inputnode.fs_subjects_dir'),                             
                             ('echo_space','inputnode.echo_space'),
                             ('te_diff','inputnode.te_diff'),
                             ('pe_dir','inputnode.pe_dir'),
                             ('fmap_mag', 'inputnode.mag'),
                             ('anat_head', 'inputnode.anat_head'),
                             ('anat_brain', 'inputnode.anat_brain')
                             ]),
    (moco, fmap_coreg, [('outputnode.epi_mean', 'inputnode.epi_mean')]),
    #transform ts
    (remove_vol, transform_ts, [('out_file', 'inputnode.orig_ts')]),
    (inputnode, transform_ts, [('anat_head', 'inputnode.anat_head')]),
    (inputnode, transform_ts, [('anat_brain_mask', 'inputnode.brain_mask')]),
    (inputnode, transform_ts, [('epi_resolution','inputnode.resolution')]),
    (moco, transform_ts, [('outputnode.mat_moco', 'inputnode.mat_moco')]),
    (fmap_coreg, transform_ts, [('outputnode.fmap_fullwarp', 'inputnode.fullwarp')]),
    (transform_ts, detrend, [('outputnode.trans_ts', 'in_file')]),
    ##all the output
    (moco, outputnode, [#('outputnode.epi_moco', 'realign.@realigned_ts'),
    ('outputnode.par_moco', 'par'),
    ('outputnode.rms_moco', 'rms'),
    ('outputnode.epi_mean', 'mean_epi'),
    ('outputnode.tsnr_file', 'tsnr')
    ]),
    (fmap_coreg, outputnode, [('outputnode.fmap','fmap'),
    ('outputnode.unwarped_mean_epi2fmap', 'unwarped_mean_epi2fmap'),
    ('outputnode.epi2fmap', 'coregistered_epi2fmap'),
    ('outputnode.fmap_fullwarp', 'fmap_fullwarp'),
    ('outputnode.epi2anat', 'epi2anat'),
    ('outputnode.epi2anat_mat', 'epi2anat_mat'),
    ('outputnode.epi2anat_dat', 'epi2anat_dat'),
    ('outputnode.epi2anat_mincost', 'epi2anat_mincost')
    ]),
    (transform_ts, outputnode, [('outputnode.trans_ts', 'full_transform_ts'),
    ('outputnode.trans_ts_mean', 'full_transform_mean'),
    ('outputnode.resamp_brain', 'resamp_brain'),
    ('outputnode.out_dvars', 'dvars_file')]),
    (detrend, outputnode, [('out_file','detrended_epi')])
    ])
    
    
    return func_preproc
