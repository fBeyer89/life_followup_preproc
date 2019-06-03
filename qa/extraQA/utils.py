#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 09:25:57 2019

@author: fbeyer
"""
def spectrum_mask(size):
    """Creates a mask to filter the image of size size"""
    import numpy as np
    from scipy.ndimage.morphology import distance_transform_edt as distance

    ftmask = np.ones(size)

    # Set zeros on corners
    # ftmask[0, 0] = 0
    # ftmask[size[0] - 1, size[1] - 1] = 0
    # ftmask[0, size[1] - 1] = 0
    # ftmask[size[0] - 1, 0] = 0
    ftmask[size[0] // 2, size[1] // 2] = 0

    # Distance transform
    ftmask = distance(ftmask)
    ftmask /= ftmask.max()

    # Keep this just in case we want to switch to the opposite filter
    ftmask *= -1.0
    ftmask += 1.0

    ftmask[ftmask >= 0.4] = 1
    ftmask[ftmask < 1] = 0
    return ftmask



def slice_wise_fft(in_file, ftmask=None, spike_thres=3., out_prefix=None):
    """Search for spikes in slices using the 2D FFT"""
    import os.path as op
    import numpy as np
    import nibabel as nb
    from utils import spectrum_mask
    from scipy.ndimage.filters import median_filter
    from scipy.ndimage import generate_binary_structure, binary_erosion
    from statsmodels.robust.scale import mad

    if out_prefix is None:
        fname, ext = op.splitext(op.basename(in_file))
        if ext == '.gz':
            fname, _ = op.splitext(fname)
        out_prefix = op.abspath(fname)

    func_data = nb.load(in_file).get_data()

    if ftmask is None:
        ftmask = spectrum_mask(tuple(func_data.shape[:2]))

    fft_data = []
    for t in range(func_data.shape[-1]):
        func_frame = func_data[..., t]
        fft_slices = []
        for z in range(func_frame.shape[2]):
            sl = func_frame[..., z]
            fftsl = median_filter(np.real(np.fft.fft2(sl)).astype(np.float32),
                                  size=(5, 5), mode='constant') * ftmask
            fft_slices.append(fftsl)
        fft_data.append(np.stack(fft_slices, axis=-1))

    # Recompose the 4D FFT timeseries
    fft_data = np.stack(fft_data, -1)

    # Z-score across t, using robust statistics
    mu = np.median(fft_data, axis=3)
    sigma = np.stack([mad(fft_data, axis=3)] * fft_data.shape[-1], -1)
    idxs = np.where(np.abs(sigma) > 1e-4)
    fft_zscored = fft_data - mu[..., np.newaxis]
    fft_zscored[idxs] /= sigma[idxs]

    # save fft z-scored
    out_fft = op.abspath(out_prefix + '_zsfft.nii.gz')
    nii = nb.Nifti1Image(fft_zscored.astype(np.float32), np.eye(4), None)
    nii.to_filename(out_fft)

    # Find peaks
    spikes_list = []
    for t in range(fft_zscored.shape[-1]):
        fft_frame = fft_zscored[..., t]

        for z in range(fft_frame.shape[-1]):
            sl = fft_frame[..., z]
            if np.all(sl < spike_thres):
                continue

            # Any zscore over spike_thres will be called a spike
            sl[sl <= spike_thres] = 0
            sl[sl > 0] = 1

            # Erode peaks and see how many survive
            struc = generate_binary_structure(2, 2)
            sl = binary_erosion(sl.astype(np.uint8), structure=struc).astype(np.uint8)

            if sl.sum() > 10:
                spikes_list.append((t, z))

    out_spikes = op.abspath(out_prefix + '_spikes.tsv')
    np.savetxt(out_spikes, spikes_list, fmt=b'%d', delimiter=b'\t', header='TR\tZ')

    return len(spikes_list), out_spikes, out_fft

def calc_frame_displacement(realignment_parameters_file, parameter_source):
    import numpy as np
    import os
    lines = open(realignment_parameters_file, 'r').readlines()
    rows = [[float(x) for x in line.split()] for line in lines]
    cols = np.array([list(col) for col in zip(*rows)])

    if parameter_source == 'AFNI':
        translations = np.transpose(np.abs(np.diff(cols[0:3, :])))
        rotations = np.transpose(np.abs(np.diff(cols[3:6, :])))
    
    elif parameter_source == 'FSL':
        translations = np.transpose(np.abs(np.diff(cols[3:6, :])))
        rotations = np.transpose(np.abs(np.diff(cols[0:3, :])))

    FD_power = np.sum(translations, axis = 1) + (50*3.141/180)*np.sum(rotations, axis =1)

    #FD is zero for the first time point
    FD_power = np.insert(FD_power, 0, 0)
    fn=os.getcwd()+'/fd.txt'
    np.savetxt(fn, FD_power)
    
    print(np.shape(FD_power))
    print(fn)
    return FD_power, fn



def make_the_plot(func, seg, tr, fd_thres, outliers, dvars, fd, subj, outfile):
    import nibabel as nb
    import scipy.io as sio
    import numpy as np
    import pandas as pd
    from matplotlib import gridspec as mgs
    import seaborn as sns
    from seaborn import color_palette
    import pandas as pd
    from niworkflows.viz.plots import plot_carpet, confoundplot
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    import os
    import scipy.fftpack

    seg_file=nb.load(seg)
    seg_data=seg_file.get_data()

      
    dataframe = pd.DataFrame({
    'outliers': np.loadtxt(outliers, usecols=[0]).tolist(),
    # Pick standardized dvars (col 0 in my case)
    # First timepoint is NaN (difference)
    'DVARS': [np.nan] + np.loadtxt(dvars, skiprows=1, usecols=[0]).tolist(),
    # First timepoint is zero (reference volume)
    'FD': [0.0] + np.loadtxt(fd, skiprows=1, usecols=[0]).tolist(),
    })

    if os.path.isfile('/data/pt_life_restingstate_followup/physio/%s_resp.mat' %(subj)):
        print("respiration file is present")
        resp=sio.loadmat('/data/pt_life_restingstate_followup/physio/%s_resp.mat' %(subj))
        r=resp.get('r')
        r=r.flatten()
        r=r[4:]
        dataframe['resp']=r.tolist()
    
    fn_pd=os.getcwd()+'/confounds.csv'
    dataframe.to_csv(fn_pd, sep=',',index_col=False)
    
    confounds = {}
    units={'outliers': '%', 'FD': 'mm'}
    vlines={'FD': [fd_thres]}
    for name in dataframe.columns.ravel():
         confounds[name] = {
        'values': dataframe[[name]].values.ravel().tolist(),
        'units': units.get(name),
        'cutoff': vlines.get(name)
    }

    ##lut for freesurfer's aparc+aseg segmentation
    lut=np.zeros((2036,),dtype="int")
    lut[2]=2
    lut[7]=2
    lut[41]=2
    lut[46]=2
    lut[251:255]=2
    lut[2]=2
    lut[7]=2
    lut[4]=3
    lut[43]=3
    lut[14]=3
    lut[1000:2035]=1
    lut[17:18]=1
    lut[53:54]=1
    lut[47]=4
    lut[8]=4
    
 
    nconfounds=len(confounds)
    nrows=1+nconfounds #number of confounds + carpet plot
    
    # Create grid
    grid = mgs.GridSpec(nrows, 1, wspace=0.0, hspace=0.05,
                        height_ratios=[1] * (nrows - 1) + [5])
    
    grid_id = 0
    
    
    if nconfounds:
        palette = color_palette("husl", nconfounds)
    
    for i, (name, kwargs) in enumerate(confounds.items()):
        tseries = kwargs.pop('values')
        confoundplot(
            tseries, grid[grid_id], hide_x=True, tr=tr, color=palette[i],
            name=name, **kwargs)
        grid_id += 1
        
          
    
    plot_carpet(func, seg_data, lut=lut, subplot=grid[-1], tr=2)
    
    

    fn=os.getcwd()+'/'+outfile
    figure = plt.gcf()
    #plt.show()
    figure.savefig(fn, bbox_inches='tight')
    plt.close(figure)
    return fn, fn_pd

def get_aseg(in_list):
    import re
    r = re.compile('.*aparc(?!.a2009s).*')
    sel=list(filter(r.match,in_list))  

    return sel[0]



def plot_fft(fn_pd, tr):
    import pandas as pd
    import numpy as np
    import scipy.fftpack
    import matplotlib.pyplot as plt
    #import matplotlib
    #matplotlib.use("TkAgg")
    from matplotlib import gridspec as mgs
    import os
    from seaborn import color_palette
    
    #read confounds file
    confounds=pd.read_csv(fn_pd)
    
    ##plot FFT of FD and RESP
    palette = color_palette("husl", 2)
    
    #parameters to plot
    if ('resp' in confounds.columns.values):
        resp=confounds.resp.values
        resp_t= scipy.fftpack.fft(resp)
    fd=confounds.FD.values
    
  
    # Number of samplepoints is identical for both measures.
    N = fd.size
    
    # sample spacing
    T = tr
      
    #perform FFT and calculate frequency space.
    fd_t= scipy.fftpack.fft(fd)
    xf = np.linspace(0.0, 1.0/(2.0*T), N/2)
    grid = mgs.GridSpec(1, 1, wspace=0.0, hspace=0.05)
    
    ax = plt.subplot(grid[0])
    ax.grid(False)
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.set_xlabel('frequency (Hz)')
    for side in ["top", "right", "left"]:
        ax.spines[side].set_color('none')
        ax.spines[side].set_visible(False)
    ax.plot(xf[1:], 2.0/N*np.abs(fd_t[0:N//2])[1:],linewidth=.8, color=palette[0], label='fd')
    if ('resp' in confounds.columns.values):
        ax.plot(xf[1:], 2.0/N*np.abs(resp_t[0:N//2])[1:],linewidth=.8, color=palette[1], label='resp')
    ax.legend(loc='upper left')
    
    fn=os.getcwd()+'/freqplot.png'
    figure = plt.gcf()
    
    #plt.show()
    figure.savefig(fn, bbox_inches='tight')
    plt.close(figure)
    return fn