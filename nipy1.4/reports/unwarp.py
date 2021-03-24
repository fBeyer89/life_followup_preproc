import nibabel as nb
import numpy as np
from pylab import cm
from nipy.labs import viz
import pylab as plt

def plot_unwarping(mean_epi, mean_epi_uncorrected, figsize=(11.7,8.3),):
       
    fig = plt.figure(figsize=figsize)
    
    ax = plt.subplot(2,1,1)
    
    before_unwarp_data = nb.load(mean_epi_uncorrected).get_data()
    before_unwarp_affine = nb.load(mean_epi_uncorrected).get_affine()
    
    slicer = viz.plot_anat(np.asarray(before_unwarp_data), np.asarray(before_unwarp_affine), black_bg=True,
                           cmap = cm.Greys_r,  # @UndefinedVariable
                           cut_coords = (-8,0,8),
                           slicer='x',
                           figure = fig,
                           axes = ax,
                           draw_cross = False)
    
    ax = plt.subplot(2,1,2)
    
    unwarped_data = nb.load(mean_epi).get_data()
    unwarped_affine = nb.load(mean_epi).get_affine()
    
    slicer = viz.plot_anat(np.asarray(unwarped_data), np.asarray(unwarped_affine), black_bg=True,
                           cmap = cm.Greys_r,  # @UndefinedVariable
                           cut_coords = (-8,0,8),
                           slicer='x',
                           figure = fig,
                           axes = ax,
                           draw_cross = False)
    
    fig.suptitle('fieldmap correction', fontsize='14')
    
    return fig