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
import nipype.interfaces.afni as afni
import nipype.interfaces.utility as util
import nipype.interfaces.io as nio    
from nipype.algorithms.confounds import FramewiseDisplacement
from utils import make_the_plot, calc_frame_displacement, get_aseg, plot_fft
import numpy as np 
import nibabel as nb
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd




def create_rs_qc(subjectlist):
    # main workflow for extended qc of diffusion/rsfmri data
    # fsl output type
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    # some hard coded things
    fd_thres=0.2
    tr=2

    # Specify the location of the preprocessed data    
    data_dir="/data/pt_life/LIFE_fu/wd_preprocessing/hcp_prep_workflow/resting/"
    working_dir="/data/pt_life/LIFE_fu/wd_preprocessing/" #MODIFY
    freesurfer_dir="/data/pt_life_freesurfer/freesurfer_all"
   
    qc = Workflow(name="qc")
    qc.base_dir = working_dir + '/' 
    qc.config['execution']['crashdump_dir'] = qc.base_dir + "/crash_files"
    qc.config['execution']={'hash_method':'content'}
    #first get all data needed
    identitynode = Node(util.IdentityInterface(fields=['subject']),
                    name='identitynode')
    identitynode.iterables = ('subject', subjectlist)
    
    info = dict(
       func=[['transform_timeseries/','_subject_','subj','/merge/rest2anat.nii.gz']],
       dvars=[['transform_timeseries/','_subject_','subj','/dvars/rest2anat_dvars.tsv']],
       motpars=[['/motion_correction/','_subject_','subj','/mcflirt/rest_realigned.nii.gz.par']],
       brainmask=[['transform_timeseries/','_subject_','subj','/resample_brain/T1_brain_mask_lowres.nii.gz']])  
    
    ds_rs = Node(
    interface=nio.DataGrabber(infields=['subj'], outfields=['func', 'dvars','motpars','brainmask']),
    name='ds_rs')    
    ds_rs.inputs.base_directory = data_dir
    ds_rs.inputs.template = '%s%s%s%s' 
    ds_rs.inputs.template_args = info
    ds_rs.inputs.sort_filelist = True   

    def juggle_subj(input_id):
        import pandas as pd
        from datetime import datetime as dt
        import os
        import random, string
        
        sic_pseudo=pd.read_csv("/data/gh_gr_agingandobesity_share/life_shared/Data/Preprocessed/derivatives/pseudo_mrt_20201214.csv")
        tmp=sic_pseudo.loc[sic_pseudo.sic == input_id,'pseudonym']
        pseudo = tmp.get_values()[0]+"_fu"
        return pseudo

    rename=Node(util.Function(input_names=['input_id'],
                            output_names=['output_id'],
                            function = juggle_subj), name="rename")

    get_fs=Node(nio.FreeSurferSource(), name="get_fs")
    get_fs.inputs.subjects_dir=freesurfer_dir
    
    
    get_correct_aseg=Node (util.Function(
            input_names=['in_list'],
            output_names=['out_aseg'],
            function=get_aseg), name="get_correct_aseg")
    
    convert=Node(fs.MRIConvert(), name="convert")
    convert.inputs.out_type="niigz"
    
    downsample= Node(afni.Resample(resample_mode='NN',
        outputtype='NIFTI_GZ',
        out_file='aparcaseg_lowres.nii.gz'),
        name = 'downsample')
        
    
    calc_fd_official=Node(FramewiseDisplacement(parameter_source='FSL'), name='calc_fd_official')
    
    calc_fd = Node(util.Function(
            input_names=['realignment_parameters_file', 'parameter_source'],
            output_names=['FD_power','fn'],
            function=calc_frame_displacement), name="calc_fd")
    calc_fd.inputs.parameter_source='FSL'
    
    outliers = Node(afni.OutlierCount(fraction=True, out_file='outliers.out'),
                       name='outliers', mem_gb=1 * 2.5)
    
    bigplot = Node(util.Function(
        input_names=['func', 'seg', 'tr', 'fd_thres', 'outliers', 'dvars', 'fd', 'subj','outfile'],
        output_names=['fn', 'dataframe'],
        function=make_the_plot), name="bigplot")
    bigplot.inputs.tr=tr
    bigplot.inputs.fd_thres=fd_thres
    bigplot.inputs.outfile="summary_fmriplot.png"
    
    fftplot= Node(util.Function(
        input_names=['fn_pd', 'tr'],
        output_names=['fn'],
        function=plot_fft), name="fftplot")
    fftplot.inputs.tr=tr

    
    datasink =Node(name="datasink", interface=nio.DataSink())
    datasink.inputs.base_directory="/data/pt_life_restingstate_followup/Results/QA"
    datasink.inputs.substitutions=[('_subject_', '')]
    
    qc.connect([(identitynode, rename,[('subject', 'input_id')]),
		       (rename, get_fs, [('output_id', 'subject_id')]),
                (identitynode, ds_rs, [('subject', 'subj')]),
                (identitynode, bigplot, [('subject', 'subj')]),
                (get_fs, get_correct_aseg, [('aparc_aseg', 'in_list')]),
                (get_correct_aseg, convert,[('out_aseg', 'in_file')]),
                (convert, downsample, [('out_file', 'in_file')]),
                (ds_rs, downsample, [('func', 'master')]),
                (downsample, bigplot, [('out_file', 'seg')]),
                (ds_rs, calc_fd, [('motpars', 'realignment_parameters_file')]),
		(ds_rs, calc_fd_official, [('motpars','in_file')]),
                (ds_rs, bigplot, [('func', 'func')]),
                (ds_rs, bigplot, [('dvars', 'dvars')]),
                (calc_fd, bigplot, [('fn', 'fd')]),#FD_power
                (ds_rs, outliers, [('func', 'in_file')]),
                (ds_rs, outliers, [('brainmask', 'mask')]),
                (outliers, bigplot, [('out_file', 'outliers')]),
                (bigplot, datasink, [('fn','detailedQA.@bigplot')]),  
                (bigplot, fftplot, [('dataframe', 'fn_pd')]),
                (bigplot, datasink, [('dataframe', 'detailedQA.metrics.@dataframe')]),
                (fftplot, datasink, [('fn', 'detailedQA.@fftplot')]),
                (calc_fd, datasink, [('fn', 'detailedQA.metrics.@fd')]),
		(calc_fd_official, datasink, [('out_file', 'detailedQA.metrics.@fd_official')])
                ])    


    qc.run(plugin="MultiProc", plugin_args={"n_procs" : 16, "non_daemon" : True})
    

 
    return qc


df=pd.read_table('/data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/LIFE_followup/preprocessing/qa/resting/qa_pipeline/all_for_rerun_qa_test.txt',header=None)

subj=df[0].values
print(subj)

#rerun dvars: LI0057625X
#errors: LI01530759
#subj_cleaned=np.delete(subj, [np.where(subj == 'LI01530759'), np.where(subj== 'LI0057625X') ])

subj=(['LI02554637','LI01213470','LI00807691','LI0067249X', 'LI00272497', 'LI02373153', 'LI03398139', 'LI02657370'])
qc=create_rs_qc(subj)
qc.run()    
   





