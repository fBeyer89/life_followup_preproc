import os
import sys
import math

from nipype.interfaces.base import isdefined
from nipype.interfaces.base import BaseInterface, InputMultiPath,\
    OutputMultiPath, BaseInterfaceInputSpec, traits, File, TraitedSpec,\
    CommandLineInputSpec, CommandLine, Directory
from traits.trait_errors import TraitError
import nipype.interfaces.dcm2nii as d2n
from nipype.utils.filemanip import split_filename
import numpy as np

class BidsConvertInputSpec(BaseInterfaceInputSpec):

    bids_info = traits.List(
            mandatory=True,
            desc="List of json files (str) corresponding to each session in the scan.")
    dicom_info = traits.List(
            mandatory=True,
            desc="one dict for each series in the session, in the order they were\
                  run. each dict should contain at least the series_num (int), \
                  the series_desc (str). and the corresponding nifti (str)")
    bids_outputdir = traits.Str(
            mandatory=True,
            desc="a directory used for bids_output")
    subj = traits.String(
            mandatory=True,
            desc="a subject and time of scan identifier")
    bvals = InputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=False,
            desc="List of bval files (str) corresponding to the DWI scans.")
    bvecs = InputMultiPath(
            traits.Either(traits.List(File(exists=True)),File(exists=True)),
            mandatory=False,
            desc="List of bvecs files (str) corresponding to the DWI scans.")

class BidsConvertOutputSpec(TraitedSpec):
    bids_outputs = traits.List(traits.Str(), desc="an list of files saved in bids format")
    pseudo = traits.String(
            mandatory=True,
            desc="the new subject pseudonym replacing LI...")

class BidsConvert(BaseInterface):
    input_spec = BidsConvertInputSpec
    output_spec = BidsConvertOutputSpec

    def __init__(self, *args, **kwargs):
        super(BidsConvert, self).__init__(*args, **kwargs)
        self.bids_outputs = []

    def _run_interface(self, runtime):
        from bids_conversion import *
        self.bids_outputs = []
        bids_outputdir = self.inputs.bids_outputdir
        subj = self.inputs.subj
        dicom_info = self.inputs.dicom_info
        bids_info = self.inputs.bids_info
        bvals=self.inputs.bvals
        bvecs=self.inputs.bvecs

        [bids_outputs,pseudo]=create_bids(dicom_info, bids_info, bids_outputdir, subj, bvals, bvecs)
        self.bids_outputs=bids_outputs
        self.pseudo = pseudo

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs["bids_outputs"] = self.bids_outputs
        outputs["pseudo"] = self.pseudo
        return outputs