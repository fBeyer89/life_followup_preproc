# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 13:13:53 2018

@author: zhang
"""
'''
Commands use during diffusion-weighted images preprocessing
=========================================================================
Warp commands dwidenoise & mrdegibbs from MRTrix3.0; eddy-openmp from FSL
-------------------------------------------------------------------------
for unkonwn reason they are not included after loading relavant interface
'''
from nipype import Node, Workflow
from dwi_corr_util import MRdegibbs, DWIdenoise, Eddy
from nipype.interfaces import fsl
#from nipype.interfaces.utility import IdentityInterface


# fsl output type
fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
# initiate workflow
distor_correct=Workflow(name='dwi')


### run dwidenoise:#### 
#noise reduction on all images
denoise = Node(DWIdenoise(noise='noise.nii.gz'), name="denoise")
denoise.inputs.in_file = "/data/pt_life_dti/test/cmrrmbep2ddiffs009a001.nii"


### artefact removal ###
# run unring: remove the ringing artefacts
unring = Node(MRdegibbs(), name="unring")

### topup and eddy ###
# merge AP PA files together
merger = Node(fsl.Merge(), name='merger')
merger.inputs.dimension = 't'
merger.inputs.in_files = ['/data/pt_life_dti/test/cmrrmbep2dseAPunwarpdiffs007a001.nii', '/data/pt_life_dti/test/cmrrmbep2dsePAunwarpdiffs008a001.nii']
merger.inputs.merged_file = 'dwi_appa.nii.gz'

# topup
topup = Node(fsl.TOPUP(), name = 'topup')
topup.inputs.config = "b02b0.cnf"
topup.inputs.encoding_file = '/data/pt_life_dti/test/acqparams_dwi.txt'
topup.inputs.out_base = 'diff_topup'

#skullstrip process using bet
# mean of all b0 unwarped images
maths = Node(fsl.ImageMaths(op_string= '-Tmean'), name="maths")

#create a brain mask from the b0 unwarped
bet = Node(interface=fsl.BET(), name='bet')
bet.inputs.mask = True
bet.inputs.frac = 0.2
bet.inputs.robust = True

#eddy motion correction
eddy = Node(Eddy(), name = "eddy")
#eddy.inputs.num_threads = 32
eddy.inputs.args = '--cnr_maps --residuals -v'
eddy.inputs.repol = True
eddy.inputs.in_acqp = '/data/pt_life_dti/test/acqparams_dwi.txt'
eddy.inputs.in_index = '/data/pt_life_dti/test/index.txt'
eddy.inputs.in_bvec = '/data/pt_life_dti/test/cmrrmbep2ddiffs009a001.bvec'
eddy.inputs.in_bval = '/data/pt_life_dti/test/cmrrmbep2ddiffs009a001.bval'

#connect the nodes
distor_correct.connect([
    
(denoise, unring, [('out_file', 'in_file')]),
(merger, topup, [("merged_file", "in_file")]),
(topup, maths, [('out_corrected', 'in_file')]),
(maths, bet, [("out_file", "in_file")]),
(bet, eddy, [("mask_file", "in_mask")]),
(topup, eddy, [("out_fieldcoef", "in_topup_fieldcoef")]),
(topup, eddy, [("out_movpar", "in_topup_movpar")]),
(unring, eddy, [("out_file", "in_file")])

])

# Specify the base directory for the working directory
distor_correct.base_dir = "/data/pt_life_dti/test"
# Execute the workflow
distor_correct.run()