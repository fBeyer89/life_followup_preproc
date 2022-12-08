import nibabel as nb   
import numpy as np
from pylab import cm
from nipy.labs import viz
import pylab as plt
import pandas as pd
import math
import matplotlib
matplotlib.rcParams['backend'] = "Qt4Agg"


def plot_lesion_seg(flair, LCL, figsize=(11.7,8.3)):
    
    fig = plt.figure(figsize=figsize)
    
    ax = plt.subplot(1,1,1)
 
    print(flair) 
    flair_bl = nb.load(flair).get_data()
    flair_bl_affine = nb.load(flair).get_affine()
           
    #there are nans in some subjects
    flair_bl[np.isnan(flair_bl)]=0
    
    print(LCL)
    LCL_nii = nb.load(LCL)
    LCL_data = LCL_nii.get_data()
    LCL_data[LCL_data >= 1] = 1
    LCL_affine = LCL_nii.get_affine()
    
    slicer = viz.plot_anat(np.asarray(flair_bl), np.asarray(flair_bl_affine), black_bg=True,
                           cmap = cm.Greys_r,  # @UndefinedVariable
                           figure = fig,
                           axes = ax,
                           draw_cross = False)
    slicer.contour_map(np.asarray(LCL_data), np.asarray(flair_bl_affine), linewidths=[0.1], colors=['r',])
    
    return fig
    
    plt.show(fig)
    

def _calc_rows_columns(ratio, n_images_to_plot):
    rows = 1
    for _ in range(100):
        columns = math.floor(ratio * rows)
        total = rows * columns
        if total > n_images_to_plot:
            break
        rows += 1
    return rows, columns    
    
def plot_mosaic(nifti_file, overlay_mask,title=None, figsize=(11.7,8.3)):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_pdf import FigureCanvasPdf as FigureCanvas
    
    nii = nb.load(nifti_file)
    mean_data = nii.get_data()
    mean_data[np.isnan(mean_data)]=0

    n_images = mean_data.shape[2] #show along the z-axis
    #but interesting range is for 100 to 400 approx
    step=20
    range_plot=np.arange(100,400,step)   
    row, col = _calc_rows_columns(figsize[0]/figsize[1], (300)/20)
    row=2
    col=8
    print(row)
    print(col)
    if overlay_mask:
        overlay_data = nb.load(overlay_mask).get_data()
        print(overlay_mask)

    # create figures
    fig = Figure(figsize=figsize)
    FigureCanvas(fig)
        
    ind=0
    for image in range_plot:
        print(image)
        ax = fig.add_subplot(row, col, ind+1)
        data_mask = np.logical_not(np.isnan(mean_data))
        ax.set_rasterized(True)
        ax.imshow(np.fliplr(mean_data[:,:,image].T), vmin=np.percentile(mean_data[data_mask], 0.5),
                  vmax=np.percentile(mean_data[data_mask],99.5), 
                  cmap=cm.Greys_r, interpolation='nearest', origin='lower')  # @UndefinedVariable
        if overlay_mask:    
            cmap = cm.Reds  # @UndefinedVariable
            cmap._init() 
            alphas = np.linspace(0, 0.75, cmap.N+3)
            cmap._lut[:,-1] = alphas
            ax.imshow(np.fliplr(overlay_data[:,:,image].T), vmin=0, vmax=3,
                      cmap=cmap, interpolation='nearest', origin='lower')  # @UndefinedVariable         
        ax.axis('off')
        ind+=1
    fig.subplots_adjust(left = 0.05, right = 0.95, bottom = 0.05, top = 0.95, wspace=0.0, hspace=0.0)
   #fig.tight_layout()
  
   
    return fig

def create_report(subject_list):
    import gc
    import pylab as plt
    from matplotlib.backends.backend_pdf import PdfPages
    
    output_file='/data/pt_life_whm/Results/QA/QA_report_N18.pdf'
    report = PdfPages(output_file)
       
    for subj in subject_list:
        
        flair_bl='/data/pt_life_whm/Data/LST/sub-%s/lmFLAIR_bl.nii.gz' %(subj)
        LCL='/data/pt_life_whm/Data/LST/sub-%s/LCL_ples_lpa_mFLAIR_bl_ples_lpa_mFLAIR_fu.nii.gz' %(subj)
      
    
        #fig = plot_lesion_seg(flair_bl, LCL, figsize=(8.3, 8.3))
        fig = plot_mosaic(flair_bl, LCL, figsize=(10,5))
        plt.show()
        report.savefig(fig, dpi=300)
        fig.clf()
        plt.close()
        
    report.close()
    gc.collect()
    plt.close()
    
    return output_file


#df=pd.read_csv('/data/pt_life_whm/Results/Tables/longvols_w_pseudonym_qa_info.csv')
#subj_list=df['pseudonym'].values

df=pd.read_table('/data/gh_gr_agingandobesity_share/life_shared/Analysis/MRI/LIFE_followup/preprocessing/lesion_segmentation/qa_workflow/run_python_3.txt', header=None)
subj_list=df[0].values
create_report(subj_list)


