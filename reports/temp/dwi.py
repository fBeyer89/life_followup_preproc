import nibabel as nb
import numpy as np
#import seaborn as sns
#from pylab import cm
#from nipype.interfaces.freesurfer.preprocess import ApplyVolTransform
from nipy.labs import viz
#from misc import plot_vline
#from matplotlib.figure import Figure
#from matplotlib.backends.backend_pdf import FigureCanvasPdf as FigureCanvas
#from matplotlib.gridspec import GridSpec
#import pylab as plt
import matplotlib.pyplot as plt 

def get_similarity_distribution(mincost_files):
    similarities = []
    for mincost_file in mincost_files:
        similarity = float(open(mincost_file, 'r').readlines()[0].split()[0])
        similarities.append(similarity)
    return similarities
    
    
def plot_dwi_corregistration(dwi_file):#, similarity_distribution=None, figsize=(11.7,8.3)):    
    print "hello"  

def test(input):
    print "hello"     
     
     
     #fig = plt.figure(figsize=figsize)
    #dwi = nb.load(dwi_file)
    #dwi_data = dwi.get_data()
#    wm_data[wm_data > 1] = 1
#    wm_affine = wm_nii.get_affine()
#    
#    slicer = viz.plot_anat(np.asarray(func), np.asarray(func_affine), black_bg=True,
#                           cmap = cm.Greys_r,  # @UndefinedVariable
#                           figure = fig,
#                           axes = ax,
#                           draw_cross = False)
#    slicer.contour_map(np.asarray(wm_data), np.asarray(wm_affine), linewidths=[0.1], colors=['r',])
#    
#    fig.suptitle('coregistration', fontsize='14')
#    
#    return fig
#    
#    plt.show(fig)