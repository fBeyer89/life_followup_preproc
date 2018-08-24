import math
import os
import time
import nibabel as nb
import numpy as np
from misc import plot_vline
from matplotlib.figure import Figure
from pylab import cm
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_pdf import FigureCanvasPdf as FigureCanvas
import pylab as plt
from dipy.io import read_bvals_bvecs

    
def calculate_mean_bo_b_images(dwi_file, bval_file):    
    
    bvals,bvecs = read_bvals_bvecs(bval_file)
    
    dwi = nb.load(dwi_file)
    dwi_data = dwi.get_data()
    
    #create average bo image
    bo_id=[bvals==0]
    mean_bo=np.mean(dwi_data[:,:,:,bo_id],4)    
    b_id=[bvals!=0]
    b_images=dwi_data[:,:,:,b_id]
    
    return mean_bo,b_images

   