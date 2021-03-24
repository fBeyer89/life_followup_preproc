import nibabel as nb   
import numpy as np
import seaborn as sns
from pylab import cm
from nipype.interfaces.freesurfer.preprocess import ApplyVolTransform
from nipy.labs import viz
from misc import plot_vline
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import FigureCanvasPdf as FigureCanvas
from matplotlib.gridspec import GridSpec 
import pylab as plt


def get_similarity_distribution(mincost_files):
    similarities = []
    for mincost_file in mincost_files:
        similarity = float(open(mincost_file, 'r').readlines()[0].split()[0])
        similarities.append(similarity)
    return similarities
    
    
def plot_epi_T1_corregistration(mean_epi_file, wm_file, reg_file, fssubjects_dir, subject_id, figsize=(11.7,8.3)):
    
    fig = plt.figure(figsize=figsize)
    
    ax = plt.subplot(1,1,1)
    print ax    
    
    res = ApplyVolTransform(source_file = mean_epi_file,
                            reg_file = reg_file,
                            fs_target = True,
                            subjects_dir = fssubjects_dir,
                            terminal_output = "none").run()

    func = nb.load(res.outputs.transformed_file).get_data()
    func_affine = nb.load(res.outputs.transformed_file).get_affine()
    
#     ribbon_file = "%s/%s/mri/ribbon.mgz"%(fssubjects_dir, subject_id)
#     ribbon_nii = nb.load(ribbon_file)
#     ribbon_data = ribbon_nii.get_data()
#     ribbon_data[ribbon_data > 1] = 1
#     ribbon_affine = ribbon_nii.get_affine()
    
    wm_nii = nb.load(wm_file)
    wm_data = wm_nii.get_data()
    wm_data[wm_data > 1] = 1
    wm_affine = wm_nii.get_affine()
    
    slicer = viz.plot_anat(np.asarray(func), np.asarray(func_affine), black_bg=True,
                           cmap = cm.Greys_r,  # @UndefinedVariable
                           figure = fig,
                           axes = ax,
                           draw_cross = False)
    slicer.contour_map(np.asarray(wm_data), np.asarray(wm_affine), linewidths=[0.1], colors=['r',])
    
    fig.suptitle('coregistration EPI-T1', fontsize='14')
    
    return fig
    
    plt.show(fig)

def plot_FA_T1_corregistration(FA_file, wm_file, reg_file, fssubjects_dir, subject_id, figsize=(11.7,8.3)):
    
    fig = plt.figure(figsize=figsize)
    
    ax = plt.subplot(1,1,1) 
    
    res = ApplyVolTransform(source_file = FA_file,
                            reg_file = reg_file,
                            fs_target = True,
                            subjects_dir = fssubjects_dir,
                            terminal_output = "none").run()

    FA = nb.load(res.outputs.transformed_file).get_data()
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
    
    slicer = viz.plot_anat(np.asarray(FA), np.asarray(FA_affine), black_bg=True,
                           cmap = cm.Greys_r,  # @UndefinedVariable
                           figure = fig,
                           axes = ax,
                           draw_cross = False)
    slicer.contour_map(np.asarray(wm_data), np.asarray(wm_affine), linewidths=[0.1], colors=['r',])
    
    fig.suptitle('coregistration FA-T1', fontsize='14')
    
    return fig
    
    plt.show(fig)
    

def plot_T1_brainmask(T1, brainmask, figsize=(11.7,8.3)):

    
    
    fig = plt.figure(figsize=figsize)
    ax = plt.subplot(1,1,1)
    T1_data = nb.load(T1).get_data()
    T1_affine = nb.load(T1).get_affine()
       
    brain_nii = nb.load(brainmask)
    brain_data = brain_nii.get_data()
    #brain_data[wm_data > 1] = 1
    brain_affine = brain_nii.get_affine()
    
    slicer = viz.plot_anat(np.asarray(T1_data), np.asarray(T1_affine), black_bg=True,
                           cmap = cm.Greys_r,  # @UndefinedVariable
                           figure = fig,
                           axes = ax,
                           draw_cross = False)
    slicer.contour_map(np.asarray(brain_data), np.asarray(brain_affine), linewidths=[0.1], colors=['r',])
    
    fig.suptitle('FS brain extraction', fontsize='14')
    
    return fig
    
    plt.show(fig)
 
