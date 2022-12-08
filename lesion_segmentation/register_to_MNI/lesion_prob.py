#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  6 15:21:25 2021

@author: fbeyer
"""

from nipype.pipeline.engine import MapNode, Node, Workflow
import nipype.interfaces.utility as util
import nipype.interfaces.fsl as fsl
import nipype.interfaces.ants as ants
import nipype.interfaces.freesurfer as fs


def prepare_lesion_prob(name='lesion_prob'):
    
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    # initiate workflow
    lesion_prob = Workflow(name='lesion_prob')
    # inputnode
    inputnode=Node(util.IdentityInterface(fields=['LCL']),
                                                  name='inputnode')
    
    outputnode=Node(util.IdentityInterface(fields=['lesion_prob_list',
    ]),
    name='outputnode')
    
    binarize=MapNode(fsl.ImageMaths(), name='binarize', iterfield=['args'])
    binarize.inputs.args=['-uthr 1.1 -bin', '-thr 2 -uthr 2.1 -bin', '-thr 3 -bin']
    
    lesion_prob.connect([
                          (inputnode, binarize, [('LCL', 'in_file')]),
                          (binarize, outputnode, [('out_file', 'lesion_prob_list')])
                          ])
    return lesion_prob