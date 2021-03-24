def create_report(subject_id, tsnr_file, realignment_parameters_file, parameter_source, mean_epi_file, mean_epi_uncorrected_file, wm_file, 
                  mask_file, reg_file, fssubjects_dir, similarity_distribution, mean_FD_distribution, tsnr_distributions, output_file):
    import gc
    import pylab as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from volumes import plot_mosaic, plot_distrbution_of_values
    from correlation import plot_epi_T1_corregistration
    from motion import plot_frame_displacement
    from unwarp import plot_unwarping
    
    
    report = PdfPages(output_file)
    
    fig = plot_mosaic(mean_epi_file, title="Mean EPI", figsize=(8.3, 11.7))
    report.savefig(fig, dpi=300)
    fig.clf()
    
    fig = plot_mosaic(mean_epi_file, "Brain mask", mask_file, figsize=(8.3, 11.7))
    report.savefig(fig, dpi=600)
    fig.clf()
    
    fig = plot_mosaic(tsnr_file, title="tSNR", figsize=(8.3, 11.7))
    report.savefig(fig, dpi=300)
    fig.clf()
    
    fig = plot_distrbution_of_values(tsnr_file, mask_file, 
        "Subject %s tSNR inside the mask" % subject_id, 
        tsnr_distributions, 
        "Median tSNR (over all subjects)", 
        figsize=(8.3, 8.3))
    report.savefig(fig, dpi=300)
    fig.clf()
    plt.close()
    
    fig = plot_frame_displacement(realignment_parameters_file, parameter_source, mean_FD_distribution, figsize=(8.3, 8.3))
    report.savefig(fig, dpi=300)
    fig.clf()
    plt.close()
    
    fig = plot_unwarping(mean_epi_file, mean_epi_uncorrected_file, figsize=(8.3, 5))
    report.savefig(fig, dpi=300)
    fig.clf()
    plt.close()
    
    fig = plot_epi_T1_corregistration(mean_epi_file, wm_file, 
                                      reg_file, fssubjects_dir, subject_id, 
                                      similarity_distribution, figsize=(8.3, 8.3))
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
