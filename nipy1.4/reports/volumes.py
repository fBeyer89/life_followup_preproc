import math
import os
import time
import nibabel as nb
import numpy as np
import seaborn as sns
from misc import plot_vline
from matplotlib.figure import Figure
from pylab import cm
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_pdf import FigureCanvasPdf as FigureCanvas
from matplotlib.pyplot import text,axis


def _calc_rows_columns(ratio, n_images):
    rows = 1
    for _ in range(100):
        columns = math.floor(ratio * rows)
        total = rows * columns
        if total > n_images:
            break

        columns = math.ceil(ratio * rows)
        total = rows * columns
        if total > n_images:
            break
        rows += 1
    return rows, columns

def plot_mosaic(nifti_file, image_type, overlay_mask = None,title=None, figsize=(11.7,8.3)):
    if isinstance(nifti_file,str):
        nii = nb.load(nifti_file)
        mean_data = nii.get_data()
    elif isinstance(nifti_file, unicode):
        nii = nb.load(nifti_file)
        mean_data = nii.get_data()
    else:
        mean_data = nifti_file
   
    if image_type=='flair':
            n_images = mean_data.shape[2]
            step=8
            range_plot=np.arange(8,n_images-8,step)   
            row, col = _calc_rows_columns(figsize[0]/figsize[1], (n_images-16)/step)
            #z-direction in flair image is in y-dimension
    elif image_type=='t1':
        n_images=mean_data.shape[2]
        step=4
        range_plot=np.arange(0,n_images-56,step)
        row, col = _calc_rows_columns(figsize[0]/figsize[1], (n_images-56)/step)
        #z-direction is in z-dimension
    else:
        n_images=mean_data.shape[2]
        step=1
        row, col = _calc_rows_columns(figsize[0]/figsize[1], n_images/step)
        range_plot=np.arange(0,n_images,step)
  
    if overlay_mask:
        overlay_data = nb.load(overlay_mask).get_data()

    # create figures
    fig = Figure(figsize=figsize)
    FigureCanvas(fig)
    
    fig.subplots_adjust(top=0.85)
    
    ind=0
    for image in range_plot:
        ax = fig.add_subplot(row, col, ind+1)
        data_mask = np.logical_not(np.isnan(mean_data))
        if overlay_mask:
            ax.set_rasterized(True)
        if image_type=="flair":
            ax.imshow(np.fliplr(mean_data[100:480,100:480,image].T), vmin=np.percentile(mean_data[data_mask], 0.5), 
                      vmax=np.percentile(mean_data[data_mask],99.5), 
                      cmap=cm.Greys_r, interpolation='nearest', origin='lower')  # @UndefinedVariable
        elif image_type=="t1":
            ax.imshow(np.flipud(mean_data[:,:,image].T), vmin=np.percentile(mean_data[data_mask], 0.5), 
                      vmax=np.percentile(mean_data[data_mask],99.5), 
                      cmap=cm.Greys_r, interpolation='nearest', origin='lower')  # @UndefinedVariable
            if overlay_mask:
                cmap = cm.Reds  # @UndefinedVariable
                cmap._init() 
                alphas = np.linspace(0, 0.75, cmap.N+3)
                cmap._lut[:,-1] = alphas
                ax.imshow(np.flipud(overlay_data[:,:,image].T), vmin=0, vmax=1,
                          cmap=cmap, interpolation='nearest', origin='lower')  # @UndefinedVariable
        else: 
            ax.imshow(np.fliplr(mean_data[:,:,image].T), vmin=np.percentile(mean_data[data_mask], 0.5), 
                      vmax=np.percentile(mean_data[data_mask],99.5), 
                      cmap=cm.Greys_r, interpolation='nearest', origin='lower')  # @UndefinedVariable
            if overlay_mask:
                cmap = cm.Reds  # @UndefinedVariable
                cmap._init() 
                alphas = np.linspace(0, 0.75, cmap.N+3)
                cmap._lut[:,-1] = alphas
                ax.imshow(np.fliplr(overlay_data[:,:,image].T), vmin=0, vmax=1,
                          cmap=cmap, interpolation='nearest', origin='lower')  # @UndefinedVariable
            
        ax.axis('off')
        ind+=1
    fig.subplots_adjust(left = 0.05, right = 0.95, bottom = 0.05, top = 0.95, wspace=0.01, hspace=0.1)
    
    if not title:
        _, title = os.path.split(nifti_file)
        title += " (last modified: %s)"%time.ctime(os.path.getmtime(nifti_file))
    fig.suptitle(title, fontsize='14')
    
    return fig
 
def plot_diffusion_directions(b_images,title=None, overlay_mask = None, figsize=(11.7,8.3)):  
    if isinstance(b_images,str): 
        nii = nb.load(b_images)
        data = nii.get_data()
    else:
        data = b_images
   
    #number of diffusion weighted images
    n_images=np.shape(data)[3]
    #plotting the middle slice for each diffusion direction
    axial_middle = np.shape(data)[2] // 2
    row, col = _calc_rows_columns(figsize[0]/figsize[1], n_images)
    if overlay_mask:
        overlay_data = nb.load(overlay_mask).get_data()

    # create figures
    fig = Figure(figsize=figsize)
    FigureCanvas(fig)
    
    fig.subplots_adjust(top=0.85)
    for image in (range(n_images)):
        ax = fig.add_subplot(row, col, image+1)
        data_mask = np.logical_not(np.isnan(data))
        if overlay_mask:
            ax.set_rasterized(True)
        ax.imshow(np.fliplr(data[:,:,axial_middle,image].T), vmin=np.percentile(data[data_mask], 0.6),#0.5 
                   vmax=np.percentile(data[data_mask],99.5), #99.5
                   cmap=cm.Greys_r, interpolation='nearest', origin='lower')  # @UndefinedVariable
        if overlay_mask:
            cmap = cm.Reds  # @UndefinedVariable
            cmap._init() 
            alphas = np.linspace(0, 0.75, cmap.N+3)
            cmap._lut[:,-1] = alphas
            ax.imshow(np.fliplr(overlay_data[:,:,image].T), vmin=0, vmax=1,
                   cmap=cmap, interpolation='nearest', origin='lower')  # @UndefinedVariable
            
        ax.axis('off')
    fig.subplots_adjust(left = 0.05, right = 0.95, bottom = 0.05, top = 0.95, wspace=0.01, hspace=0.1)
    
    #if not title:
    #    _, title = os.path.split(b_images)
    #    title += " (last modified: %s)"%time.ctime(os.path.getmtime(b_images))
    #fig.suptitle(title, fontsize='14')
    
    return fig, n_images    
    
def _get_values_inside_a_mask(main_file, mask_file):
    main_nii = nb.load(main_file)
    main_data = main_nii.get_data()
    nan_mask = np.logical_not(np.isnan(main_data))
    mask = nb.load(mask_file).get_data() > 0
    
    data = main_data[np.logical_and(nan_mask, mask)]
    return data

def get_median_distribution(main_files, mask_files):
    medians = []
    for main_file, mask_file in zip(main_files, mask_files):
	#print main_file
        med = np.median(_get_values_inside_a_mask(main_file, mask_file))
        medians.append(med)
    return medians


def plot_distrbution_of_values(main_file, mask_file, xlabel, distribution=None, xlabel2=None, figsize=(11.7,8.3)):
    data = _get_values_inside_a_mask(main_file, mask_file)

    fig = Figure(figsize=figsize)
    FigureCanvas(fig)
    
    gs = GridSpec(2, 1)
    ax = fig.add_subplot(gs[0, 0])
    sns.distplot(np.array(data, dtype=np.double), kde=False, bins=100, ax=ax) #sns.distplot(data.astype(np.double), kde=False, bins=100, ax=ax)
    ax.set_xlabel(xlabel)
    
    ax = fig.add_subplot(gs[1, 0])
    sns.distplot(np.array(distribution, dtype=np.double), ax=ax) 
    #sns.distplot(np.array(distribution).astype(np.double), ax=ax)    
    cur_val = np.median(data)
    label = "%g"%cur_val
    plot_vline(cur_val, label, ax=ax)
    ax.set_xlabel(xlabel2)
    
    return fig
    
def plot_textbox(print_text, figsize=(11.7,8.3)):
    font = {'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 18,
        }
    fig = Figure(figsize=figsize)
    FigureCanvas(fig)
    grid = GridSpec(1, 1)
    ax = fig.add_subplot(grid[0,0])
    ax.text(0.5, 0.5, print_text, horizontalalignment='center', verticalalignment='center', fontdict=font)
    axis('off')
    return fig
