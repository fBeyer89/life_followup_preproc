def create_report(subject_id, 
                  tsnr_file, realignment_parameters_file, dvars_file, parameter_source,
                  dti_available, mean_bo, b_images, FA_file,reg_file_dwi,
                  mean_epi_file,  mean_epi_uncorrected_file, 
                  wm_file, T1_file, mask_file, reg_file, fssubjects_dir, 
                  flair_file,
                  output_file):
    import gc
    import os
    import pylab as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from reports.volumes import plot_mosaic, plot_diffusion_directions, plot_textbox
    from reports.unwarp import plot_unwarping
    from reports.correlation import plot_epi_T1_corregistration,plot_T1_brainmask, plot_FA_T1_corregistration
    from reports.motion import plot_frame_displacement
    
    
    report = PdfPages(output_file)
       
    #plot general brain extraction
    print "creating T1/mask"
    fig = plot_mosaic(T1_file, image_type="t1", overlay_mask = mask_file, figsize=(8.3, 11.7))
    report.savefig(fig, dpi=600)
    fig.clf()     
        
    #first plot FLAIR
    if os.path.isfile(flair_file[0]):
        fig = plot_mosaic(str(flair_file[0]), image_type="flair", title="FLAIR image", figsize=(8.3, 11.7))
    else:
        fig=plot_textbox(print_text="no FLAIR image acquired", figsize=(8.3,11.7))
    
    report.savefig(fig, dpi=300)
    fig.clf() 
    plt.close()
        
    #first plot all diffusion weighted imaging     
    if dti_available==True:    
        fig = plot_mosaic(mean_bo, image_type="else", title = "Mean B0", figsize=(8.3, 11.7))
        report.savefig(fig, dpi=300)
        fig.clf()
        
        fig,n_diff=plot_diffusion_directions(b_images,title="60 diffusion directions", overlay_mask = None, figsize=(11.7,8.3))
        report.savefig(fig, dpi=300)
        fig.clf()

        fig=plot_FA_T1_corregistration(FA_file, wm_file, reg_file_dwi, fssubjects_dir, subject_id, figsize=(8.3, 8.3))
        fig.clf()
    else:
        fig=plot_textbox(print_text="no DTI image acquired", figsize=(8.3,11.7))
        report.savefig(fig, dpi=300)
        fig.clf() 

      
    plt.close()
   
   #now everything resting-state related
    fig = plot_mosaic(mean_epi_file,image_type="else", title="Mean EPI", figsize=(8.3, 11.7))
    report.savefig(fig, dpi=300)
    fig.clf()
           
    fig = plot_mosaic(tsnr_file, image_type="else",title="tSNR", figsize=(8.3, 11.7))
    report.savefig(fig, dpi=300)
    fig.clf()
       
    fig = plot_frame_displacement(realignment_parameters_file, dvars_file, parameter_source, figsize=(8.3, 8.3))
    report.savefig(fig, dpi=300)
    fig.clf()
    plt.close()
    
    fig = plot_unwarping(mean_epi_file, mean_epi_uncorrected_file, figsize=(8.3, 5))
    report.savefig(fig, dpi=300)
    fig.clf()
    plt.close()
    
    fig = plot_epi_T1_corregistration(mean_epi_file, wm_file, 
                                      reg_file, fssubjects_dir, subject_id, figsize=(8.3, 8.3))
    report.savefig(fig, dpi=300)
    fig.clf()
    plt.close()
    
    report.close()
    gc.collect()
    plt.close()
    
    return output_file, subject_id



def read_dists(csv_file):
    
    import pandas as pd
    import numpy as np
    df = pd.read_csv(csv_file, dtype=object)
    sim = dict(zip(df['subject_id'], list(np.asarray(df['coregistration quality'], dtype='float64'))))
    mfd = list(np.asarray(df['Mean FD'], dtype='float64'))
    tsnr = list(np.asarray(df['Median tSNR'], dtype='float64'))
    
    return sim, mfd, tsnr


def check(subject_id,checklist):
    
    with open(checklist, 'a') as f:
        f.write(subject_id+'\n')
    return checklist
