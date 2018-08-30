# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 12:30:27 2015

@author: fbeyer
"""


def strip_rois_func(in_file, t_min):
    '''
    Removing intial volumes from a time series
    '''
    import numpy as np
    import nibabel as nb
    import os
    from nipype.utils.filemanip import split_filename
    #transform list to file (strip the list) or cheap workaround
    in_file=in_file[0]
    nii = nb.load(in_file)
    new_nii = nb.Nifti1Image(nii.get_data()[:,:,:,t_min:], nii.get_affine(), nii.get_header())
    new_nii.set_data_dtype(np.float32)
    _, base, _ = split_filename(in_file)
    nb.save(new_nii, base + "_roi.nii.gz")
    print base + "_roi.nii.gz"
    return os.path.abspath(base + "_roi.nii.gz")