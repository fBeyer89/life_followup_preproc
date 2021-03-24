# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 16:23:14 2018

@author: fbeyer
"""
import matplotlib.pyplot as plt
import nibabel as nb
import numpy as np
from nipype.interfaces.freesurfer.preprocess import ApplyVolTransform
from nipy.labs import viz
import nibabel as nb   
import numpy as np
import seaborn as sns
from pylab import cm


#def get_st_dvars(dvars_file):
#    import numpy as np
#    print "XXXXXXXXXXXXX\nXXXXXXXXXXXX\nXXXXXXXXXX"
#    print "read dvars file"
#    lines = open(dvars_file, 'r').readlines()
#    rows = [[x for x in line.split()] for line in lines] 
#    cols = np.array([list(col) for col in zip(*rows)])

    #get standardized DVARS
#    st_dvars=cols[0][1:]
#    st_dvars.astype(np.float)
#    return st_dvars

#res=get_st_dvars("/data/pt_life/LIFE_fu/wd_test/hcp_prep_workflow/resting/transform_timeseries/_subject_LI00334118/dvars/rest2anat_dvars.tsv")
#print len(res)

#
#import numpy as np
#print type(res[0])
#print res.astype('float')
#plt.plot(res.astype('float'))
#plt.show()


def plot_FA_T1_coregistration(FA_file, wm_file, reg_file, fssubjects_dir, subject_id, figsize=(11.7,8.3)):
    
    fig = plt.figure(figsize=figsize)
    
    ax = plt.subplot(1,1,1) 
    
    res = ApplyVolTransform(source_file = FA_file,
                            reg_file = reg_file,
                            fs_target = True,
                            subjects_dir = fssubjects_dir,
                            terminal_output = "none").run()

    FA = nb.load(res.outputs.transformed_file).get_data()
    print np.shape(FA)
    FA_affine = nb.load(res.outputs.transformed_file).get_affine()
    
#     ribbon_file = "%s/%s/mri/ribbon.mgz"%(fssubjects_dir, subject_id)
#     ribbon_nii = nb.load(ribbon_file)
#     ribbon_data = ribbon_nii.get_data()
#     ribbon_data[ribbon_data > 1] = 1
#     ribbon_affine = ribbon_nii.get_affine()
    
    wm_nii = nb.load(wm_file)
    wm_data = wm_nii.get_data()
    wm_data[wm_data > 1] = 1
    wm_affine = wm_nii.get_affine()
    print np.shape(wm_nii)
    
    slicer = viz.plot_anat(np.asarray(FA), np.asarray(FA_affine), black_bg=True,
                           cmap = cm.Greys_r,  # @UndefinedVariable
                           figure = fig,
                           axes = ax,
                           draw_cross = False)
    slicer.contour_map(np.asarray(wm_data), np.asarray(wm_affine), linewidths=[0.1], colors=['r',])
    
    fig.suptitle('coregistration', fontsize='14')
    plt.show(fig)
    return fig
    
    

plot_FA_T1_coregistration('/data/pt_life_dti_followup/diffusion/LI00528196/dtifit__FA.nii.gz', '/data/pt_life/LIFE_fu/wd_preprocessing/hcp_prep_workflow/anat_preproc/mgzconvert/_subject_LI00528196/wmseg/T1_brain_wmseg.nii.gz', '/data/pt_life/LIFE_fu/wd_preprocessing/hcp_prep_workflow/dwi_preproc/_subject_LI00528196/bbregister/fa2anat.dat', '/data/pt_life_freesurfer/freesurfer_all', 'LI00528196')
