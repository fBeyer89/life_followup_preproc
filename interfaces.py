import os
import sys
import math

from nipype.interfaces.traits_extension import isdefined
from nipype.interfaces.base import BaseInterface, InputMultiPath,\
    OutputMultiPath, BaseInterfaceInputSpec, traits, File, TraitedSpec,\
    CommandLineInputSpec, CommandLine, Directory
from traits.trait_errors import TraitError
import nipype.interfaces.dcm2nii as d2n
from nipype.utils.filemanip import split_filename
#from duke_siemens.util_dicom_siemens import read as read_siemens_shadow

from util import *
#from hcpre.config import *


class HCDcm2nii(d2n.Dcm2nii):
    """ We override to fix a bug in output listing... """
    def _parse_stdout(self, stdout):
        import re
        import os
        files = []
        reoriented_files = []
        reoriented_and_cropped_files = []
        bvecs = []
        bvals = []
        skip = False
        last_added_file = None
        for line in stdout.split("\n"):
            if not skip:
                file = None
                if line.startswith("Saving "):
                    file = line[len("Saving "):]
                elif line.startswith("GZip..."):
                    #for gzipped outpus files are not absolute
                    if isdefined(self.inputs.output_dir):
                        output_dir = self.inputs.output_dir
                        print output_dir
                    else:
                        output_dir = self._gen_filename('output_dir')
                    file = os.path.abspath(os.path.join(output_dir,
                                                        line[len("GZip..."):]))
                elif line.startswith("Number of diffusion directions "):
                    if last_added_file:
                        base, filename, ext = split_filename(last_added_file)
                        bvecs.append(os.path.join(base,filename + ".bvec"))
                        bvals.append(os.path.join(base,filename + ".bval"))
                        
                elif re.search('.*->(.*)', line):
                    val = re.search('.*->(.*)', line)
                    val = val.groups()[0]
                    if isdefined(self.inputs.output_dir):
                        output_dir = self.inputs.output_dir
                    else:
                        output_dir = self._gen_filename('output_dir')
                    val = os.path.join(output_dir, val)
                    file = val

                if file:
                    if last_added_file and os.path.exists(file) and not last_added_file in file:
                        files.append(file)
                    last_added_file = file
                    continue

                if line.startswith("Reorienting as "):
                    reoriented_files.append(line[len("Reorienting as "):])
                    skip = True
                    continue
                elif line.startswith("Cropping NIfTI/Analyze image "):
                    base, filename = os.path.split(line[len("Cropping NIfTI/Analyze image "):])
                    filename = "c" + filename
                    reoriented_and_cropped_files.append(os.path.join(base, filename))
                    skip = True
                    continue
            skip = False
        return files, reoriented_files, reoriented_and_cropped_files, bvecs, bvals

class DicomInfoInputSpec(BaseInterfaceInputSpec):
    files = InputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=True,
            desc="a list of dicom files from which to extract data",
            copyfile=False)

class DicomInfoOutputSpec(TraitedSpec):
    info = traits.List(traits.Dict(),
            desc="an ordered list of dicts, all in the same directory.")

class DicomInfo(BaseInterface):
    input_spec = DicomInfoInputSpec
    output_spec = DicomInfoOutputSpec

    def __init__(self, *args, **kwargs):
        super(DicomInfo, self).__init__(*args, **kwargs)
        self.info = []

    def _run_interface(self, runtime):
        import dicom
        files = self.inputs.files
        by_series = {}
        self.info = []
        for f in files:
            d = dicom.read_file(f)
            try: 
                s_num = d.SeriesNumber
                s_num = int(s_num)
            except Exception, e:
                raise e
            
            if not s_num in by_series:
                by_series[s_num] = {
                    "series_num": s_num,
                    "series_desc": getattr(d,"SeriesDescription",None),
                    "protocol_name": getattr(d,"ProtocolName",None),
                }
                if [0x19,0x1018] in d and \
                        "description" in dir(d[0x19,0x1018]) and \
                        "RealDwellTime" in d[0x19,0x1018].description():
                    try:
                        by_series[s_num]["RealDwellTime"] = float(d[0x19,0x1018].value)
                    except Exception, e:
                        pass # don't die
                it = getattr(d,"ImageType",None)
                if it:
                    if not isinstance(it,str):
                        it = list(it)
                    by_series[s_num]["image_type"] = it
                ipped = getattr(d,"InPlanePhaseEncodingDirection", None)
                if ipped:
                    by_series[s_num]["ipp_encoding_direction"] = ipped
                
                # ep repetition time
                rep = d.get((0x0018,0x0080), None)
                if rep:
                    try:
                        rep = float(rep.value)/1000 #to get it in seconds
                    except Exception, e:
                        pass
                    else:
                        by_series[s_num]["TR"] = rep 
                        
                # ep echo spacing ingredients
                bpppe = d.get((0x0019,0x1028), None)
                if bpppe:
                    try:
                        bpppe = float(bpppe.value)
                    except Exception, e:
                        pass
                    else:
                        by_series[s_num]["bw_per_pix_phase_encode"] = bpppe 
                        
                acq_mat = getattr(d, "AcquisitionMatrix", None)
                if acq_mat and len(acq_mat) == 4:
                    # acq mat text gets turned into this struct.
                    # n will be in 0/1 (other index will == 0), m will be in 2/3
                    by_series[s_num]["acq_matrix_n"] = acq_mat[0] or acq_mat[1]
                    by_series[s_num]["acq_matrix_m"] = acq_mat[2] or acq_mat[3]
                # try to get orientation from header
                orient = orientation_from_dcm_header(d)
                if orient:
                    by_series[s_num]["orientation"] = orient
                # try to get siemens shadow header
                #try:
                #    ss = read_siemens_shadow(f)[0]
                #except Exception, e:
                #    pass
                #else:
                #    siemens_keys = ["in_plane_rotation", "polarity_swap"]
                #    by_series[s_num].update(dict([(k,v) for k,v in ss.iteritems() if k in siemens_keys]))
            bs = by_series[s_num]
            # collect all of the unique EchoTimes per series
            try:
                et = getattr(d,"EchoTime",None)
                if et:
                    et = float(et)
                    if not "echo_times" in bs:
                        bs["echo_times"] = []
                    if not et in bs["echo_times"]:
                        bs["echo_times"].append(et)
            except Exception, e:
                pass # don't die.
        for s_num, s_info in by_series.iteritems():
            # find delta_te, collapse to echo time if needed
            if "echo_times" in s_info:
                etc = len(s_info["echo_times"])
                if etc == 0:
                    del s_info["echo_times"]
                elif etc == 1:
                    s_info["echo_time"] = s_info["echo_times"][0]
                    del s_info["echo_times"]
                elif etc == 2:
                    s_info["delta_te"] = abs(s_info["echo_times"][0] - s_info["echo_times"][1])
        for k in sorted(by_series.keys()):
            self.info.append(by_series[k])
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs["info"] = self.info
        return outputs

class NiiWranglerInputSpec(BaseInterfaceInputSpec):
    nii_files = InputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=True,
            desc="a list of nifti files to be categorized, matched up, etc.",
            copyfile=False)
    series_map = traits.Dict(
            key_trait=traits.Str(),
            value_trait=traits.List(),
            value = {},
            mandatory=False,
            usedefault=True,
            desc="keys are any member of SCAN_TYPES, values are lists of series\
                  descriptions as recorded in DICOM headers.")
    dicom_info = traits.List(
            mandatory=True,
            desc="one dict for each series in the session, in the order they were\
                  run. each dict should contain at least the series_num (int) and\
                  the series_desc (str).")
    ep_TR=  traits.Either(traits.Enum("NONE"), traits.Float(),
            desc="rsfmri TR or 'NONE' if not used.")   
    ep_rsfmri_echo_spacings = traits.Either(traits.Enum("NONE"), traits.Float(),
            desc="""
            The effective echo spacing of your BOLD images. Already accounts
            for whether or not iPAT (acceleration in the phase direction) was
            used. If you're using acceleration, then the EES is not going to
            match the 'Echo Spacing' that Siemen's reports in the console.
            Setting this value will prevent any attempt to derive it.""")   
    ep_dwi_echo_spacings = traits.Either(traits.Enum("NONE"), traits.Float(),
            desc="""
            The effective echo spacing of your BOLD images. Already accounts
            for whether or not iPAT (acceleration in the phase direction) was
            used. If you're using acceleration, then the EES is not going to
            match the 'Echo Spacing' that Siemen's reports in the console.
            Setting this value will prevent any attempt to derive it.""")
    ep_unwarp_dir = traits.Enum("x", "x-", "-x", "y", "y-", "-y", "z", "z-", "-z",
            desc="Setting this value will prevent any attempt to derive it.")
            

class NiiWranglerOutputSpec(TraitedSpec):
    t1 = OutputMultiPath(
            traits.List(File(exists=True)),
            mandatory=True,
            desc="anatomical t1 nifti (list in chronological order  if repeated)")
    rsfmri = OutputMultiPath(
            traits.List(File(exists=True)),
            mandatory=True,
            desc="rsfmri nifti (list in chronological order  if repeated)")
    mag_fieldmap = traits.Either(traits.Enum("NONE"), traits.File(exists=True),
            default="NONE", mandatory=False, usedefault=True,
            desc="magnitude fieldmap image for structural images. first matching image will be used.")
    phase_fieldmap = traits.Either(traits.Enum("NONE"), traits.File(exists=True),
            default="NONE", mandatory=False, usedefault=True,
            desc="phase fieldmap image for structural images. first matching image will be used.")
    dwi      = traits.List(traits.Str(),
            mandatory=True,
            desc="dwi nifti (list in chronological order  if repeated).")
    dwi_ap  = traits.List(traits.Str(),
            mandatory=True,
            desc="dwi ap nifti for topup (list in chronological order  if repeated).")
    dwi_pa  = traits.List(traits.Str(),
            mandatory=True,
            desc="dwi pa nifti for topup (list in chronological order  if repeated).")
    flair   = traits.List(traits.Str(),
            mandatory=True,
            desc="flair nifti (list in chronological order  if repeated).")
    fieldmap_te = traits.Either(traits.Enum("NONE"), traits.Float(),
            default="NONE", mandatory=False, usedefault=True,
            desc="delta TE in ms for magnitude fieldmap or 'NONE' if not used.")
    ep_TR=  traits.Either(traits.Enum("NONE"), traits.Float(),
            value=["NONE"], mandatory=False, usedefault=True,
            desc="rsfmri TR or 'NONE' if not used.")
    ep_rsfmri_echo_spacings = traits.Either(traits.Enum("NONE"), traits.Float(),
            value=["NONE"], mandatory=False, usedefault=True,
            desc="""
            The effective echo spacing of your rsfmri images. Already accounts
            for whether or not iPAT (acceleration in the phase direction) was
            used. If you're using acceleration, then the EES is not going to
            match the 'Echo Spacing' that Siemen's reports in the console.
            This value will be derived, if not overridden by the input of the
            same name. Please inspect the value after your initial run of the
            pipeline to ensure that it's sane.
            """)
    ep_dwi_echo_spacings = traits.Either(traits.Enum("NONE"), traits.Float(),
            value=["NONE"], mandatory=False, usedefault=True,
            desc="""
            The effective echo spacing of your BOLD images. Already accounts
            for whether or not iPAT (acceleration in the phase direction) was
            used. If you're using acceleration, then the EES is not going to
            match the 'Echo Spacing' that Siemen's reports in the console.
            This value will be derived, if not overridden by the input of the
            same name. Please inspect the value after your initial run of the
            pipeline to ensure that it's sane.
            Length must match number of bold images.""")
    ep_unwarp_dirs = traits.List(traits.Enum("x", "x-", "-x", "y", "y-", "-y", "z", "z-", "-z",),
            mandatory=True,
            desc="Length must match number of bold images.")

class NiiWrangler(BaseInterface):
    input_spec = NiiWranglerInputSpec
    output_spec = NiiWranglerOutputSpec

    def __init__(self, *args, **kwargs):
        super(NiiWrangler, self).__init__(*args, **kwargs)
        self.t1_files = []
        self.rsfmri_files = []
        self.dwi_files = []
        self.dwi_ap_files = []
        self.dwi_pa_files = []
        self.flair_files = []
        self.fieldmap_mag = []
        self.fieldmap_ph = []
        self.bval = []
        self.bvec = []
        self.ep_TR= None
        self.fieldmap_mag_delta_te = "NONE"
        self.t1_sample_spacing = 0.
        self.ep_dwi_echo_spacings = None
        self.ep_rsfmri_echo_spacings = None
        self.ep_unwarp_dirs = None

    def _run_interface(self, runtime):
        import re
        import operator
        
        print "starting NII wrangler"
        nii_files = self.inputs.nii_files
        smap = self.inputs.series_map
        dinfo = self.inputs.dicom_info
        #block_averaging = self.inputs.block_struct_averaging
        s_num_reg = re.compile(".*s(\d+)a(?!.*/)") # sux to use filename. make more robust if needed.
        nii_by_series = {}
        fails = []
        extras = []
        for fn in nii_files:
            try:
                # we only want the first nii for each series
                # TODO: find out what those others (A/B) are all about. fix this as needed.
                sn = int(s_num_reg.match(fn).groups()[0])
                if sn in nii_by_series:
                    extras.append(fn)
                    continue
                nii_by_series[sn] = fn
            except Exception, e:
                fails.append(fn)
        if fails:
            raise ValueError("Could not derive series number from file names: %s." % str(fails))
        if extras:
            print >> sys.stderr, "\nWARNING: Ignoring extra niftis: %s\n" % str(extras)
        # add nifti names to the dicts
        m_count = 0
        for sn, fn in nii_by_series.iteritems():
            m = filter(lambda x: x.get("series_num",-1) == sn, dinfo)
            if not m:
                continue
            m_count += 1
            m[0]["nifti_file"] = fn
        if not m_count == len(dinfo):
            raise ValueError("incorrect number of nifti->series matches (%d/%d)" % (m_count, len(dinfo)))
        
        # time for some data wrangling
        nf = "nifti_file"
        sd = "series_desc"
        it = "image_type"
        t1fs = [d for d in filter(lambda x: sd in x and x[sd] in smap.get("t1",[]), dinfo) if nf in d]
        #if block_averaging:
        #    t1fs = [t1fs[0]]
        #    t2fs = [t2fs[0]]
        self.t1_files = [d[nf] for d in t1fs]
        #get rsfmri, if no "resting state return default file"
        bs = [d for d in filter(lambda x: sd in x and x[sd] in smap.get("rsfmri",[]), dinfo) if nf in d]
        self.rsfmri_files = [d[nf] for d in bs]
        #get dwi
        dwi = [d for d in filter(lambda x: sd in x and x[sd] in smap.get("dwi",[]), dinfo) if nf in d]
        
        if len(dwi)==0:
            print "no DTI acquired"
            self.dwi_files=['nothing to proceed']
            self.dwi_pa_files=['nothing to proceed']
            self.dwi_ap_files=['nothing to proceed']        
        else:
            self.dwi_files = [d[nf] for d in dwi]
            dwi_pa = [d for d in filter(lambda x: sd in x and x[sd] in smap.get("fieldmap_pa",[]), dinfo) if nf in d]
            self.dwi_pa_files = [d[nf] for d in dwi_pa]    
            dwi_ap = [d for d in filter(lambda x: sd in x and x[sd] in smap.get("fieldmap_ap",[]), dinfo) if nf in d]
            self.dwi_ap_files = [d[nf] for d in dwi_ap] 
 
        flair = [d for d in filter(lambda x: sd in x and x[sd] in smap.get("flair",[]), dinfo) if nf in d]
        if len(flair)==0:
            print "no FLAIR acquired"
            self.flair_files=['nothing to proceed']
        else:
            self.flair_files = [d[nf] for d in flair]
               
        # we have to do some extra looking at the headers for the mag and phase fieldmaps too
        mag_fs = filter(lambda x: sd in x and
                x[sd] in smap.get("fieldmap_magnitude",[]) and
                it in x and
                isinstance(x[it], list) and
                len(x[it]) > 2 and
                x[it][2].strip().lower() == "m", dinfo) # we want the 3rd field of image type to be 'm'
        phase_fs = filter(lambda x: sd in x and
                x[sd] in smap.get("fieldmap_phase",[]) and
                it in x and
                isinstance(x[it], list) and
                len(x[it]) > 2 and
                x[it][2].strip().lower() == "p", dinfo) # we want the 3rd field of image type to be 'p'
        self.fieldmap_mag = [d[nf] for d in mag_fs if nf in d]
        self.fieldmap_ph = [d[nf] for d in phase_fs if nf in d]
        
        # calculate echo spacing for rsfmri:   
        #if more than one resting state scan was acquired:
        ep_rsfmri_echo_fail = False
        ep_TR_fail=False
        if len(bs)>1:
            print "two or more resting-state scans"
            if isdefined(self.inputs.ep_rsfmri_echo_spacings):
                self.ep_rsfmri_echo_spacings = [self.inputs.ep_rsfmri_echo_spacings for n in self.rsfmri_files]
            elif bs and any(["bw_per_pix_phase_encode" in d and "acq_matrix_n" in d for d in bs]):
                if not all(["bw_per_pix_phase_encode" in d and "acq_matrix_n" in d for d in bs]):
                    ep_rsfmri_echo_fail = True
                else:
                    self.ep_rsfmri_echo_spacings = [1/(d["bw_per_pix_phase_encode"] * d["acq_matrix_n"]) for d in bs]
            else:
                self.ep_rsfmri_echo_spacings = ["NONE" for n in self.rsfmri_files]
            
            if isdefined(self.inputs.ep_TR):
                self.ep_TR=[self.inputs.ep_TR for n in self.rsfmri_files]
            elif bs and any(["TR" in d for d in bs]):
                if not all(["TR" in d for d in bs]):
                    ep_TR_fail = True
                else: 
                    self.ep_TR=[d["TR"] for d in bs]
            else:
                 self.ep_TR= ["NONE" for n in self.rsfmri_files]
        else:
            print "one resting-state scan"
            if isdefined(self.inputs.ep_rsfmri_echo_spacings):
                self.ep_rsfmri_echo_spacings = self.inputs.ep_rsfmri_echo_spacings
            elif bs and "bw_per_pix_phase_encode" in bs[0] and "acq_matrix_n" in bs[0]:
                if not "bw_per_pix_phase_encode" in bs[0] and "acq_matrix_n" in bs[0]:
                    ep_rsfmri_echo_fail = True
                else:
                    self.ep_rsfmri_echo_spacings = 1/(bs[0]["bw_per_pix_phase_encode"] * bs[0]["acq_matrix_n"])
            else:
                self.ep_rsfmri_echo_spacings = "NONE" 
            
            if isdefined(self.inputs.ep_TR):
                self.ep_TR=self.inputs.ep_TR
            elif bs and "TR" in bs[0]:
                if not "TR" in bs[0]:
                    ep_TR_fail = True
                else: 
                    self.ep_TR=bs[0]["TR"]
            else:
                 self.ep_TR= "NONE"

            
        ep_dwi_echo_fail = False
        if len(dwi)>1:
            print "more than one dwi scan"
            if isdefined(self.inputs.ep_dwi_echo_spacings):
                self.ep_dwi_echo_spacings = [self.inputs.ep_dwi_echo_spacings for n in self.dwi_files]
            elif bs and any(["bw_per_pix_phase_encode" in d and "acq_matrix_n" in d for d in dwi]):
                if not all(["bw_per_pix_phase_encode" in d and "acq_matrix_n" in d for d in dwi]):
                    ep_dwi_echo_fail = True
                else:
                    self.ep_dwi_echo_spacings = [1/(d["bw_per_pix_phase_encode"] * d["acq_matrix_n"]) for d in dwi]
            else:
                self.ep_dwi_echo_spacings = ["NONE" for n in self.dwi_files]       
        else:
            print "one dwi scan"
            if isdefined(self.inputs.ep_dwi_echo_spacings):
                self.ep_dwi_echo_spacings = self.inputs.ep_dwi_echo_spacings
            elif bs and "bw_per_pix_phase_encode" in bs[0] and "acq_matrix_n" in bs[0]:
                if not "bw_per_pix_phase_encode" in bs[0] and "acq_matrix_n" in bs[0]:
                    ep_dwi_echo_fail = True
                else:
                    self.ep_dwi_echo_spacings = 1/(bs[0]["bw_per_pix_phase_encode"] * bs[0]["acq_matrix_n"])
            else:
                self.ep_dwi_echo_spacings = "NONE"
         
        # output delta te for magnitude fieldmap if available
        if mag_fs and self.fieldmap_mag and self.fieldmap_ph:
            self.fieldmap_mag_delta_te = mag_fs[0].get("delta_te","NONE")
        else:
            self.fieldmap_mag_delta_te = "NONE"
#        # a BOLD image by any other name...
#        self.bold_names = ["bold_%d" % n for n in xrange(len(self.bolds))]
#        # we'll derive the ep unwarp dir in the future... for now, just set it in config
        if isdefined(self.inputs.ep_unwarp_dir):
            self.ep_unwarp_dirs = [self.inputs.ep_unwarp_dir for n in self.rsfmri_files]
            # if you have any polarity swapped series, apply that now
            pswaps = smap.get("polarity_swapped", [])
            if pswaps:
                for b_idx, uw_dir in enumerate(self.ep_unwarp_dirs):
                    if bs[b_idx].get("series_desc",None) in pswaps:
                        raw_dir = uw_dir.replace("-","")
                        self.ep_unwarp_dirs[b_idx] = "-"+raw_dir if not "-" in uw_dir else raw_dir
        else:
            # fail. we can do better!
            raise ValueError("We can't derive ep_unwarp_dir yet. Please set it in the nii wrangler config section.")
        ### and let's do some sanity checking
        # warn if you're going to ignore field or magnitude phase maps
        if not (len(self.fieldmap_mag) and len(self.fieldmap_ph)):
            print >> sys.stderr, "\nWARNING: found %d magnitude fieldmaps and %d phase fieldmaps.\n" % (len(self.fieldmap_mag), len(self.fieldmap_ph))

        ### derive the derived values
        # t1_sample_spacing
        if t1fs and "RealDwellTime" in t1fs[0].keys():
            self.t1_sample_spacing = t1fs[0]["RealDwellTime"] * math.pow(10,-9)
        else:
            self.t1_sample_spacing = "NONE"
        # don't continue if there was screwiness around calculating ep echo spacing
        if ep_rsfmri_echo_fail:
            raise ValueError("Unabel to calculate fmri ep echo spacing. Try specifying manually in nii wrangler config section.")
        if ep_dwi_echo_fail:
            raise ValueError("Unabel to calculate dwi ep echo spacing. Try specifying manually in nii wrangler config section.")
        if ep_TR_fail:
            raise ValueError("Unabel to derive TR. Try specifying manually in nii wrangler config section.")
        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs["t1"] = self.t1_files
        outputs["rsfmri"] = self.rsfmri_files
        outputs["dwi"] = self.dwi_files
        outputs["dwi_ap"] = self.dwi_ap_files
        outputs["dwi_pa"] = self.dwi_pa_files
        outputs["flair"] = self.flair_files
        fm = self.fieldmap_mag
        fp = self.fieldmap_ph
        outputs["mag_fieldmap"] = fm[0] if fm and fp else "NONE"
        outputs["phase_fieldmap"] = fp[0] if fm and fp else "NONE"
        if not (fm and fp):
            print >> sys.stderr, "\nWARNING: not using magnitude or phase fieldmaps.\n"
        outputs["fieldmap_te"] = self.fieldmap_mag_delta_te
        outputs["ep_TR"] = self.ep_TR
        outputs["ep_dwi_echo_spacings"] = self.ep_dwi_echo_spacings
        outputs["ep_rsfmri_echo_spacings"] = self.ep_rsfmri_echo_spacings
        outputs["ep_unwarp_dirs"] = self.ep_unwarp_dirs
        return outputs
        
