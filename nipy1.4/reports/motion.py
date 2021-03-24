import numpy as np
import pylab as plt
import seaborn as sns
from misc import plot_vline
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import FigureCanvasPdf as FigureCanvas
from matplotlib.gridspec import GridSpec

def calc_frame_dispalcement(realignment_parameters_file, parameter_source):
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
    
    return FD_power

def get_mean_frame_displacement_disttribution(realignment_parameters_files, parameter_source):
    mean_FDs = []
    max_FDs = []
    for realignment_parameters_file in realignment_parameters_files:
        FD_power = calc_frame_dispalcement(realignment_parameters_file, parameter_source)
        mean_FDs.append(FD_power.mean())
        max_FDs.append(FD_power.max())
        
    return mean_FDs, max_FDs

def get_st_dvars(dvars_file):
    lines = open(dvars_file, 'r').readlines()
    rows = [[x for x in line.split()] for line in lines] 
    cols = np.array([list(col) for col in zip(*rows)])

    #get standardized DVARS
    st_dvars=cols[0][1:]
    st_dvars.astype(np.float)
    return st_dvars

def plot_frame_displacement(realignment_parameters_file, dvars_file, parameter_source, figsize=(11.7,8.3)):

    FD_power = calc_frame_dispalcement(realignment_parameters_file, parameter_source)
    st_dvars = get_st_dvars(dvars_file)
    print type(st_dvars)
    fig = Figure(figsize=figsize)
    FigureCanvas(fig)

    grid = GridSpec(4, 4)  
    
    ax = fig.add_subplot(grid[0:3,0:3])
    ax.plot(FD_power)
    ax.set_xlim((0, len(FD_power)))
    #plot limit of 0.2 mm (which would be used for scrubbing Power 2012)
    limit=0.2*np.ones(np.shape(FD_power))    
    ax.plot(limit,"red")
    
    mean_FD=np.mean(FD_power)
    maxFD=np.max(FD_power)
    ax.set_ylabel("Frame Displacement [mm]")
    ax.set_xlabel("Frame number")
    ylim = ax.get_ylim()

    ax = fig.add_subplot(grid[3,0:3])  
    ax.plot(st_dvars.astype('float'))
    ax.set_xlim((0, len(st_dvars)))  
    ax.set_ylabel("DVARS [% change BOLD x 10]")
    ax.set_xlabel("Frame number")
    maxdvars=np.max(st_dvars.astype('float'))

    ax = fig.add_subplot(grid[0:3,3])
    sns.distplot(FD_power, vertical=True, axlabel=False, ax=ax)
    ax.set_ylim(ylim)
    ax.set_yticklabels('', fontdict=None, minor=False)
           
    figtitle='motion+signal fluctuations (Power,2012)\n mean FD = %.2fmm (>0.5mm exclusion)\n maxFD = %.2fmm (>3mm exclusion)\n maxDVARS =  %.2f pc-change BOLD (>5 exclusion)' %(mean_FD,maxFD,maxdvars)
    fig.suptitle(figtitle, fontsize='14')
        
    return fig
