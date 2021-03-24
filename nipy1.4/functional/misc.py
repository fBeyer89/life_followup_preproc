# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 11:34:05 2018

@author: fbeyer
"""

def compute_dvars(in_file,
                  in_mask,
                  remove_zerovariance=False,
                  intensity_normalization=1000):
    """
    Compute the :abbr:`DVARS (D referring to temporal
    derivative of timecourses, VARS referring to RMS variance over voxels)`
    [Power2012]_.
    Particularly, the *standardized* :abbr:`DVARS (D referring to temporal
    derivative of timecourses, VARS referring to RMS variance over voxels)`
    [Nichols2013]_ are computed.
    .. [Nichols2013] Nichols T, `Notes on creating a standardized version of
         DVARS <http://www2.warwick.ac.uk/fac/sci/statistics/staff/academic-\
research/nichols/scripts/fsl/standardizeddvars.pdf>`_, 2013.
    .. note:: Implementation details
      Uses the implementation of the `Yule-Walker equations
      from nitime
      <http://nipy.org/nitime/api/generated/nitime.algorithms.autoregressive.html\
#nitime.algorithms.autoregressive.AR_est_YW>`_
      for the :abbr:`AR (auto-regressive)` filtering of the fMRI signal.
    :param numpy.ndarray func: functional data, after head-motion-correction.
    :param numpy.ndarray mask: a 3D mask of the brain
    :param bool output_all: write out all dvars
    :param str out_file: a path to which the standardized dvars should be saved.
    :return: the standardized DVARS
    """
    import numpy as np
    import nibabel as nb
    from nitime.algorithms import AR_est_YW
    import warnings

    func = nb.load(in_file).get_data().astype(np.float32)
    mask = nb.load(in_mask).get_data().astype(np.uint8)

    if len(func.shape) != 4:
        raise RuntimeError("Input fMRI dataset should be 4-dimensional")

    idx = np.where(mask > 0)
    mfunc = func[idx[0], idx[1], idx[2], :]

    if intensity_normalization != 0:
        mfunc = (mfunc / np.median(mfunc)) * intensity_normalization

    # Robust standard deviation (we are using "lower" interpolation
    # because this is what FSL is doing
    func_sd = (np.percentile(mfunc, 75, axis=1, interpolation="lower") -
               np.percentile(mfunc, 25, axis=1, interpolation="lower")) / 1.349

    if remove_zerovariance:
        mfunc = mfunc[func_sd != 0, :]
        func_sd = func_sd[func_sd != 0]

    # Compute (non-robust) estimate of lag-1 autocorrelation
    ar1 = np.apply_along_axis(AR_est_YW, 1,
                              regress_poly(0, mfunc,
                                           remove_mean=True)[0].astype(
                                               np.float32), 1)[:, 0]

    # Compute (predicted) standard deviation of temporal difference time series
    diff_sdhat = np.squeeze(np.sqrt(((1 - ar1) * 2).tolist())) * func_sd
    diff_sd_mean = diff_sdhat.mean()

    # Compute temporal difference time series
    func_diff = np.diff(mfunc, axis=1)

    # DVARS (no standardization)
    dvars_nstd = np.sqrt(np.square(func_diff).mean(axis=0))

    # standardization
    dvars_stdz = dvars_nstd / diff_sd_mean

    with warnings.catch_warnings():  # catch, e.g., divide by zero errors
        warnings.filterwarnings('error')

        # voxelwise standardization
        diff_vx_stdz = np.square(
            func_diff / np.array([diff_sdhat] * func_diff.shape[-1]).T)
        dvars_vx_stdz = np.sqrt(diff_vx_stdz.mean(axis=0))

return (dvars_stdz, dvars_nstd, dvars_vx_stdz)