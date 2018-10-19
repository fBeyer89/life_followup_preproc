import math

import time
from misc import plot_vline
from matplotlib.figure import Figure
from pylab import cm
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_pdf import FigureCanvasPdf as FigureCanvas
import pylab as plt


    
def calculate_mean_bo_b_images(dwi_file, bval_file=False, bvec_file=False):    
    from dipy.io import read_bvals_bvecs
    from nipype.utils.filemanip import split_filename
    import nibabel as nb
    import numpy as np
    import os
    
    print len(dwi_file)
    print bval_file
    if (len(dwi_file)==1 and os.path.isfile(dwi_file[0])):
        bvals,bvecs = read_bvals_bvecs(bval_file,bvec_file)
        print dwi_file[0]
        dwi = nb.load(dwi_file[0])
        print dwi.get_affine()
        dwi_data = dwi.get_data()
        
        #create average bo image
        bo_id=bvals==0
        print np.shape(dwi_data[:,:,:,bo_id])
        if np.shape(dwi_data[:,:,:,bo_id])[3] != 7:
            print "why there are not 7 B0s"
        mean_bo=np.mean(dwi_data[:,:,:,bo_id],3)    
        b_id=bvals!=0
        b_images=dwi_data[:,:,:,b_id]
        print np.shape(b_images)
        if np.shape(b_images)[3]!=60:
           print "why there are not 60 directions?"
        
        mean_bo_nii = nb.Nifti1Image(mean_bo, dwi.get_affine(), dwi.get_header())
        mean_bo_nii.set_data_dtype(np.float32)
        _, base, _ = split_filename(dwi_file[0])
        nb.save(mean_bo_nii, base + "_mean_bo.nii.gz")
        
        b_images_nii = nb.Nifti1Image(b_images, dwi.get_affine(), dwi.get_header())
        b_images_nii.set_data_dtype(np.float32)
        _, base, _ = split_filename(dwi_file[0])
        print base
        nb.save(b_images_nii, base + "_b_images.nii.gz")
        print os.path.abspath(base + "_mean_bo.nii.gz")
        return True, str(os.path.abspath(base + "_mean_bo.nii.gz")), str(os.path.abspath(base + "_b_images.nii.gz"))
    else:
        print "no dti or more than 1 dti acquired"
        return False, str('not acquired'), str('not acquired')

   