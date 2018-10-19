import os
import sys
from multiprocessing import Pool, cpu_count
from configobj import ConfigObj

from util import *

SCAN_TYPES = [
    "t1",
    "rsfmri",
    "fieldmap_magnitude",
    "fieldmap_phase",
    "dwi",
    "fieldmap_pa",
    "fieldmap_ap",
    "flair",
    "swi",
    "tof_angio"]

RSPREPROC_KEYS = ["epi_resolution","vol_to_remove", "ep_unwarp_dir"]

TEMPL_KEYS = [
    "t1_template_2mm",
    "t1_template_epi_resolution"
    ]

CONF_FILE_KEYS = [
    "fnirt_config",
    "top_up_config",]

CONF_FILE_DEFAULTS = [
    "%(xxx)s/global/config/T1_2_MNI152_2mm.cnf",
    "%(xxx)s/global/config/b02b0.cnf",]
    
YES_WORDS = [1,"1","y","Y","yes","Yes","YES", "True", "true"]
NO_WORDS = [0,"0","n","N","no","No","NO", "False", "false"]


def setup_conf():
    import os
    # get name for conf file
    name = raw_input("New config file name [hcp.conf]: ")
    name = name.strip()
    name = name if name else "hcp.conf"
    name = name if (len(name) > 5 and name[-5:] == ".conf") else name + ".conf"
    # make sure that file doesn't already exist
    if os.path.exists(name):
        print "File already exists."
        return
    # get the directory containing all data for all subjects
    print "\nThe subjects directory should contain all raw data for all subjects."
    subs_dir = raw_input("Subjects Directory [/afs/cbs.mpg.de/projects/life/patients/]: ")
    subs_dir = subs_dir.strip()
    subs_dir = subs_dir if subs_dir else "/afs/cbs.mpg.de/projects/life/patients/"
    subs_dir = os.path.abspath(subs_dir)
    # get the template used for getting form the subject dir to the dicoms
    print "\nThe DICOM template should be a format string for a glob which, " + \
          "when combined with an individual subject ID, will get us all of " + \
          "the subject's DICOM files."
    dcm_temp = raw_input("DICOM template [%s/*_2018*/DICOM/]: ")
    dcm_temp = dcm_temp.strip()
    #using LI00513253 as a default participant.LI00513253
    dcm_temp = dcm_temp if dcm_temp else "%s/*_2018*/DICOM/*"
    #don't add .dcm to path
    #dcm_temp = dcm_temp if ".dcm" in dcm_temp else os.path.join(dcm_temp, "*.dcm")
    # get a list of subjects
    print "\nSubjects should be a comma separated list of subject ids."
    subs = raw_input("Subject list ['']: ")
    subs = subs.strip()
    # set up config obj
    config = ConfigObj(name, unrepr=True)
    # get the basics
    config["general"] = {}
    config["general"]["subjects"] = [s.strip() for s in subs.split(",")]
    config["general"]["subject_dir"] = subs_dir
    config["general"]["dicom_template"] = dcm_temp
    
    fs_dir = raw_input("fs directory [/data/pt_life_freesurfer/freesurfer_all]: ")
    fs_dir = fs_dir if fs_dir else "/data/pt_life_freesurfer/freesurfer_all"
    config["general"]["fs_dir"]=fs_dir
      
    #output for results
    config["general"]["outdir_dir"]="/data/pt_life/data_fbeyer/testing_LIFE_fu/outdir"
    #output for niftis
    config["general"]["nifti_dir"]="/data/pt_life/data_fbeyer/testing_LIFE_fu/outdir"
    
    #some info for resting state preprocessing
    config["rspreproc"] = {}
    config["rspreproc"]["epi_resolution"]=3
    config["rspreproc"]["vol_to_remove"]=4
    config["rspreproc"]["ep_unwarp_dir"]='y-'

    #config the templates
    config["templates"]={}
    config["templates"]["t1_template_2mm"]='/afs/cbs.mpg.de/software/fsl/5.0.9/ubuntu-xenial-amd64/share/data/standard/MNI152_T1_2mm_brain.nii.gz'    
    config["templates"]["t1_template_epi_resolution"]='/home/raid1/fbeyer/Documents/Scripts/ICA_RSN_analysis/MNI/MNI_resampled.nii'
 
    # write the config file
    config.write()
    print "updating config"
    update_conf(name)
    

def get_series_desc(dicom_path):
    import dicom
    d = dicom.read_file(dicom_path, stop_before_pixels=True, force=True)
    sd = getattr(d, "SeriesDescription", None)
    return sd

def update_conf(conf_path):
    import os
    import sys
    from glob import glob
    import dicom
    from time import sleep
    from numpy import unique
    # TODO: make sure conf is there
    print "starting to update config"
    config = ConfigObj(conf_path, unrepr=True)
    # update the series map if needed or desired
    needs_smap = "series" not in config
    if not needs_smap:
        needs_smap = raw_input("Do you want to re-map the series descriptions y/[n]? ").strip() in YES_WORDS
    if needs_smap:
        # get list of all sequence descriptions
        print "needing smap"        
        s = config["general"]["subject_dir"]
        print s
        t = config["general"]["dicom_template"] % "*"
        print t
        print "searching for dicoms"
        print os.path.join(s,t)
        dicoms = glob(os.path.join(s,t))
        message = "\rChecking series names (this may several minutes) %s"
        dcm_count = len(dicoms)
        pool = Pool(processes=min(15, int(round(cpu_count() * .75))))
        result = pool.map_async(get_series_desc, dicoms)
        print result.get()
        while not result.ready():
            sleep(.5)
            # perc = float(dcm_count - result._number_left) / float(dcm_count)
            # perc = "(%d%%)..." % int(round(perc * 100))
            perc = "(%d chunks remaining)..." % result._number_left
            m = message % perc
            sys.stdout.write(m)
            sys.stdout.flush()
        series = unique(result.get()).tolist()
        if None in series:
            series.remove(None)
        found = "\nFound %d unique series descriptions.\n" % len(series)
        sys.stdout.write(found)
        # message if we didn't find anything
        if not series:
            raise ValueError("couldn't find any dicoms! please double check your paths and templates...")
        # update the series confg
        series.sort()
        print "-------\nSeries:\n-------"
        print "\n".join(["%d:\t%s" % (i, ser) for i,ser in enumerate(series)]) + "\n"
        type_matches = dict(zip(SCAN_TYPES, [[] for s in SCAN_TYPES]))
        i = 0
        series_count = len(series)
        while i < len(SCAN_TYPES):
            ft = SCAN_TYPES[i]
            m = raw_input("\nWhich series do you use for '%s'?\n[None] or comma separated values 0-%d: " % (ft, len(series)-1)).strip()
            if not m:
                i += 1
                continue
            try:
                m = [int(n) for n in m.split(",")]
                if any([n < 0 or n >= series_count for n in m]):
                    raise ValueError()
            except Exception, e:
                print "Invalid Selection..."
                continue
            i += 1
            for n in m:
                type_matches[ft].append(series[n])
        config["series"] = {}
        for key in sorted(type_matches.keys()):
            config["series"][key] = type_matches[key]
    config["DEFAULT"] = {}
    # freesurfer home (defaults)
    d_val = os.environ.get("FREESURFER_HOME", "")
    print d_val
    fsh = raw_input("\nPath for FREESURFER_HOME [%s]: " % d_val).strip()
    fsh = fsh if fsh else d_val
    config["DEFAULT"]["freesurfer_home"] = fsh
    # fsl dir (defaults)
    d_val = os.environ.get("FSLDIR", "")
    fslh = raw_input("\nPath for FSLDIR [%s]: " % d_val).strip()
    fslh = fslh if fslh else d_val
    config["DEFAULT"]["fsl_dir"] = fslh

    
    # config file locations (config_files)
    def_c = raw_input("\nUse default config files [y]/n?").strip() not in NO_WORDS
    c_vals = CONF_FILE_DEFAULTS if def_c else ['' for k in CONF_FILE_KEYS]
    config["config_files"] = {}
    for i, key in enumerate(CONF_FILE_KEYS):
        config["config_files"][key] = c_vals[i]
    if not def_c:
        print "\nWhen finished, please open your config file to set the other config file locations manually.\n"
        
    # write the file!
    config.write()

def select_conf():
    # if there"s only one conf around, select it. otherwise, offer a choice.
    from glob import glob
    confs = glob("./*.conf")
    if not confs:
        raise ValueError("Could not find any .conf files in current directory.")
    if len(confs) == 1:
        return confs[0]
    return numbered_choice(confs, prompt = "There were multiple config files. Please choose.")

def validate_config(conf_dict):
    """ validates the config dict
    return: True if it passes, False if it fails
    """
    # TODO: more of this
    # make sure we can get an env out of it
    try:
        get_env_for_config(conf_dict)
    except Exception, e:
        return False
    return True

def numbered_choice(choices, prompt=None, allow_multiple=False, allow_none=False):
    import numpy as np
    # TODO: print a choice, return the chosen value
    if not prompt:
        prompt = "Options:\n" + "-"*len("Options:")
    print prompt + "\n"
    for i, val in enumerate(choices):
        print "%d: %s" % (i, val)
    # print "\n"
    nstr = "[None] or " if allow_none else ""
    mstr = "comma separated values " if allow_multiple else ""
    selection = None
    done = False
    while not done:
        try:
            m = raw_input("\nSelect %s%s0-%d: " % (nstr, mstr, len(choices)-1)).strip()
            if not m:
                if allow_none:
                    selection = None
                    done = True
                else:
                    raise ValueError()
            else:
                m = [int(n) for n in m.split(",")]
                if len(m) > 1 and not allow_multiple:
                    raise ValueError()
                if any([n < 0 or n >= len(choices) for n in m]):
                    raise ValueError()
                m = np.unique(m)
                selection = [choices[n] for n in m]
                if not allow_multiple:
                    selection = selection[0]
                done = True
        except ValueError, e:
            print "Invalid Selection..."
            continue
    return selection

def get_config_dict(conf_path):
    config = ConfigObj(conf_path, unrepr=True)
    return config

def get_env_for_config(conf_dict):
    # exceptions will be raised if config isn't good.
    # hint: we call this from the validation method!
    d = conf_dict["DEFAULT"]
    new_d = {
        "FSLDIR":d["fsl_dir"],
        "FREESURFER":d["freesurfer_home"],
        }
    new_d.update(conf_dict.get("env",{}))
    return new_d


def apply_dict_to_obj(the_d, obj, skip_names=[]):
    if not the_d:
        return
    for name, val in the_d.iteritems():
        if name in skip_names or "traits" not in dir(obj) or name not in obj.traits().keys():
            continue
    setattr(obj, name, val)