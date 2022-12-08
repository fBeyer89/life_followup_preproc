#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 21 10:16:37 2019
#eddy quality control
@author: fbeyer
"""
from nipype import Node, Workflow, Function
from nipype.interfaces import fsl
from nipype.interfaces.utility import IdentityInterface
import nipype.interfaces.freesurfer as fs
import nipype.interfaces.utility as util
import nipype.interfaces.io as nio    
from mgzconvert_for_bl import create_mgzconvert_pipeline
from apply_ants_bl import create_ants_registration_pipeline
from lesion_prob import prepare_lesion_prob
import numpy as np 
import nibabel as nb
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd




def create_flair_reg(subjectlist):
    # main workflow to coregister long FLAIR, long FreeSurfer and MNI space.
    # fsl output type
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    # some hard coded things
    mni_template="/afs/cbs.mpg.de/software/fsl/5.0.11/ubuntu-bionic-amd64/data/standard/MNI152_T1_1mm_brain.nii.gz"

    # Specify the location of the preprocessed data    
    data_dir="/data/pt_life_whm/Data/LST/"
    coreg_dir="/data/pt_life_restingstate/LIFE/preprocessed/"
    working_dir="/data/pt_life/LIFE_fu/wd_flair_reg_bl/" #MODIFY
    freesurfer_dir="/data/pt_life_freesurfer/freesurfer_all"
   
    flair_reg = Workflow(name="flair_reg")
    flair_reg.base_dir = working_dir + '/' 
    flair_reg.config['execution']['crashdump_dir'] = flair_reg.base_dir + "/crash_files"
    flair_reg.config['execution']={'hash_method':'content'}
   
    #first get all data needed
    identitynode = Node(util.IdentityInterface(fields=['subject']),
                    name='identitynode')
    identitynode.iterables = ('subject', subjectlist)

    #for the registration files need to use old SIC
    def juggle_subj(pseudo):
        import pandas as pd
        sic_pseudo=pd.read_csv("/data/gh_gr_agingandobesity_share/life_shared/Data/Preprocessed/derivatives/pseudo_mrt_20201214.csv")
        tmp=sic_pseudo.loc[sic_pseudo.pseudonym == pseudo,'sic']
        sic = tmp.get_values()[0]
        return sic
    
    extract_sic=Node(util.Function(input_names=['pseudo'],
                        output_names=['sic'],
                        function = juggle_subj), name="extract_sic")

    
    info = dict(
       flair_nat=[['sub-','subj','/mFLAIR_bl.nii.gz']],
       lesion_change=[['sub-','subj','/ples_lpa_mFLAIR_bl.nii.gz']])

    data_grab = Node(
    interface=nio.DataGrabber(infields=['subj'], outfields=['flair_nat', "lesion_change"]),
    name='data_grab')    
    data_grab.inputs.base_directory = data_dir
    data_grab.inputs.template = '%s%s%s' 
    data_grab.inputs.template_args = info
    data_grab.inputs.sort_filelist = True   

    info = dict(
       reg_lin=[['subj','/structural/transforms2mni/transform0GenericAffine.mat']],
       reg_warp=[['subj','/structural/transforms2mni/transform1Warp.nii.gz']])

    data_grab2 = Node(
    interface=nio.DataGrabber(infields=['subj'], outfields=['reg_lin', "reg_warp"]),
    name='data_grab2')    
    data_grab2.inputs.base_directory = coreg_dir
    data_grab2.inputs.template = '%s%s' 
    data_grab2.inputs.template_args = info
    data_grab2.inputs.sort_filelist = True   

    #Do not use template but raw FS
    get_fs=Node(nio.FreeSurferSource(), name="get_fs")
    get_fs.inputs.subjects_dir=freesurfer_dir
    
    
    bbreg = Node(fs.BBRegister(contrast_type='t2',
                               subjects_dir=freesurfer_dir,
                               out_fsl_file='flair2anat.mat',
                               out_reg_file='flair2anat.dat',
                               registered_file='flair2anat_bbreg.nii.gz',
                               init='fsl'
                               ),
                               name='bbregister')
    
    
    mgzconvert = create_mgzconvert_pipeline()
    mgzconvert.inputs.inputnode.fs_subjects_dir=freesurfer_dir
         
    
    apply_ants=create_ants_registration_pipeline()
    apply_ants.inputs.inputnode.ref=mni_template 
    
  
    datasink =Node(name="datasink", interface=nio.DataSink())
    datasink.inputs.base_directory="/data/pt_life_whm/Results/flair2MNI/"
    datasink.inputs.substitutions=[('_subject_', ''),
                                   ('_ants_reg0', 'flair2MNI'),
                                   ('_ants_reg1', 'lesion2MNI')]


    # connecting the nodes
    flair_reg.connect([

        (identitynode, data_grab,[('subject', 'subj')]),
        (identitynode, bbreg, [('subject', 'subject_id')]),
        (data_grab, bbreg, [("flair_nat", "source_file")]),
        (identitynode, mgzconvert,  [('subject', 'inputnode.fs_subject_id')]),  
        (bbreg, apply_ants, [('out_fsl_file', 'inputnode.flair2anat')]),
        (identitynode, extract_sic, [('subject', 'pseudo')]),
        (extract_sic, data_grab2, [('sic', "subj")]),
        (data_grab2, apply_ants, [('reg_lin', 'inputnode.transforms_anat2MNI_lin'),
                                 ('reg_warp', 'inputnode.transforms_anat2MNI_warp')]),
        (data_grab, apply_ants, [('flair_nat', 'inputnode.flair_native'), 
                                 ('lesion_change','inputnode.LCL')]),
        (mgzconvert, apply_ants, [('outputnode.anat_brain', 'inputnode.brain')]),
        (apply_ants, datasink, [('outputnode.flair2MNI', 'flair2MNI')]),
        (bbreg, datasink, [('out_fsl_file', 'bbreg.out_fsl'),
                             ('out_reg_file', 'bbreg.out_reg'),
                             ('registered_file', 'bbreg.reg_file')]),
        (mgzconvert, datasink, [('outputnode.anat_brain', 'bbreg.brain')]),
        ])
    
    
    return flair_reg


df=pd.read_csv('/data/pt_life_whm/Results/Tables/cross_vols.txt', sep=' ')
df_fs=pd.read_csv("/data/gh_gr_agingandobesity_share/life_shared/Data/Preprocessed/derivatives/FreeSurfer/QA_followup/freesurfer_qa_baseline_and_followup.csv")
info=pd.read_csv("/data/gh_gr_agingandobesity_share/life_shared/Data/Preprocessed/derivatives/PV168_A1_Pilot_subject_list_inclusion_exclusion29.1.19.csv")

#Merge
merged_df=pd.merge(
    df,
    df_fs,
    how="left",
    left_on="pseudonym",
    right_on="pseudonym")

#Exclude everyone with quality issues in FS
df_quality_ok=merged_df[merged_df["BL_usable"]!="0"]

subj=df_quality_ok['pseudonym'].values
print(len(subj))

subj=subj[6:700] #first run
#subj=subj[1:5]
#subj=['00A27F1CA0']

flair_reg=create_flair_reg(subj)
flair_reg.run(plugin='MultiProc', plugin_args={'n_procs' : 16})    
   
#plugin='Linear'




