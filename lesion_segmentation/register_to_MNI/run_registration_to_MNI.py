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
from mgzconvert import create_mgzconvert_pipeline
from ants import create_normalize_pipeline
from apply_ants import create_ants_registration_pipeline
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
    working_dir="/data/pt_life/LIFE_fu/wd_flair_reg/" #MODIFY
    freesurfer_dir="/data/pt_life_freesurfer/freesurfer_all"
   
    flair_reg = Workflow(name="flair_reg")
    flair_reg.base_dir = working_dir + '/' 
    flair_reg.config['execution']['crashdump_dir'] = flair_reg.base_dir + "/crash_files"
    flair_reg.config['execution']={'hash_method':'content'}
    #first get all data needed
    identitynode = Node(util.IdentityInterface(fields=['subject']),
                    name='identitynode')
    identitynode.iterables = ('subject', subjectlist)
    
    info = dict(
       flair_nat=[['sub-','subj','/lmFLAIR_bl.nii.gz']],
       lesion_change=[['sub-','subj','/LCL_ples_lpa_mFLAIR_bl_ples_lpa_mFLAIR_fu.nii.gz']])  

    data_grab = Node(
    interface=nio.DataGrabber(infields=['subj'], outfields=['flair_nat']),
    name='data_grab')    
    data_grab.inputs.base_directory = data_dir
    data_grab.inputs.template = '%s%s%s' 
    data_grab.inputs.template_args = info
    data_grab.inputs.sort_filelist = True   

    def fs_temp_name(input_id):
        fs_temp = input_id+".long."+input_id+'_temp'
        return fs_temp

    fs_temp=Node(util.Function(input_names=['input_id'],
                            output_names=['output_id'],
                            function = fs_temp_name), name="fs_temp")

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
       
    lesion_prob=prepare_lesion_prob()
    
    normalize = create_normalize_pipeline()
    normalize.inputs.inputnode.standard=mni_template
    
    apply_ants=create_ants_registration_pipeline()
    apply_ants.inputs.inputnode.ref=mni_template 
    
  
    datasink =Node(name="datasink", interface=nio.DataSink())
    datasink.inputs.base_directory="/data/pt_life_whm/Results/flair2MNI/"
    datasink.inputs.substitutions=[('_subject_', ''),
                                   ('_ants_reg0', 'flair2MNI'),
                                   ('_ants_reg1', 'decrease2MNI'),
                                   ('_ants_reg2', 'stable2MNI'),
                                   ('_ants_reg3', 'incrase2MNI')]

    # connecting the nodes
    flair_reg.connect([

        (identitynode, data_grab,[('subject', 'subj')]),
        (identitynode, fs_temp,[('subject', 'input_id')]),
        (fs_temp, bbreg, [('output_id', 'subject_id')]),
        (data_grab, bbreg, [("flair_nat", "source_file")]),
        (fs_temp, mgzconvert,  [('output_id', 'inputnode.fs_subject_id')]),  
        (mgzconvert, normalize, [('outputnode.anat_brain', 'inputnode.anat')]),
        (bbreg, apply_ants, [('out_fsl_file', 'inputnode.flair2anat')]),
        (normalize, apply_ants, [('outputnode.anat2std_transforms', 'inputnode.transforms_anat2MNI')] ),
        (data_grab, apply_ants, [('flair_nat', 'inputnode.flair_native')]),
        (data_grab, lesion_prob, [('lesion_change', 'inputnode.LCL')]),
        (lesion_prob, apply_ants, [('outputnode.lesion_prob_list','inputnode.LCL')]),
        (mgzconvert, apply_ants, [('outputnode.anat_brain', 'inputnode.brain')]),
        (apply_ants, datasink, [('outputnode.flair2MNI', 'flair2MNI')]),
        (bbreg, datasink, [('out_fsl_file', 'bbreg.out_fsl'),
                             ('out_reg_file', 'bbreg.out_reg'),
                             ('registered_file', 'bbreg.reg_file')]),
        (normalize, datasink, [('outputnode.anat2std', 'ants.anat2std'),
                               ('outputnode.anat2std_transforms', 'ants.anat2std_transforms'),
                               ('outputnode.std2anat_transforms', 'ants.std2anat_transforms')]),
        (mgzconvert, datasink, [('outputnode.anat_brain', 'bbreg.brain')]),
        (mgzconvert, datasink, [('outputnode.wmseg', 'bbreg.wmseg')])])
    
    flair_reg.run(plugin="MultiProc", plugin_args={"n_procs" : 16, "non_daemon" : True})
    
    return flair_reg


df=pd.read_csv('/data/pt_life_whm/Results/Tables/longvols_w_pseudonym_qa.csv')
df_fs=pd.read_csv("/data/gh_gr_agingandobesity_share/life_shared/Data/Preprocessed/derivatives/FreeSurfer/QA_followup/freesurfer_qa_baseline_and_followup.csv")

#Merge
merged_df=pd.merge(
    df,
    df_fs,
    how="left",
    left_on="pseudonym",
    right_on="pseudonym")

#Exclude everyone with quality issues in FLAIR or no template in FS
tmp=merged_df[merged_df["qa_check"]!=1]
tmp=tmp[tmp["qa_check"]!=3]

df_quality_ok=tmp[tmp["FU_usable"]!="0"]

subj=df_quality_ok['pseudonym'].values
#print(subj)
subj=subj[701:]

flair_reg=create_flair_reg(subj)
flair_reg.run(plugin='MultiProc', plugin_args={'n_procs' : 16})    
   





