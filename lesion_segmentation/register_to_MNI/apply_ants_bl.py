# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 14:00:12 2015

@author: fbeyer
"""
from nipype.pipeline.engine import MapNode, Node, Workflow
import nipype.interfaces.utility as util
import nipype.interfaces.fsl as fsl
import nipype.interfaces.ants as ants
import nipype.interfaces.freesurfer as fs


def create_ants_registration_pipeline(name='ants_registration'):
    # set fsl output type
    fsl.FSLCommand.set_default_output_type('NIFTI_GZ')
    # initiate workflow
    ants_registration = Workflow(name='ants_registration')
    # inputnode
    inputnode=Node(util.IdentityInterface(fields=['flair_native', 'LCL',
                                                  'brain',
                                                  'flair2anat',
                                                  'transforms_anat2MNI_lin',
                                                  'transforms_anat2MNI_warp',
                                                  'ref'
                                                  ]),
                                                  name='inputnode')
    # outputnode
    outputnode=Node(util.IdentityInterface(fields=['flair2MNI',
    ]),
    name='outputnode')

    
    
    collect_inputs_applyTf = Node(interface = util.Merge(2),name='collect_inputs_applyTf')  
    
    applyreg = MapNode(fs.ApplyVolTransform(), name='applyreg',iterfield='source_file')
    
            
    def make_list(lin, warp):
        transforms=[warp,lin]
        return transforms
        
    create_transforms=Node(util.Function(input_names=['lin', 'warp'],
                            output_names=['transforms'],
                            function = make_list), name="create_transforms")
    
    #ants_reg = Node(ants.ApplyTransforms(input_image_type = 3, dimension = 3, interpolation = 'Linear'), name='ants_reg')
    ants_reg = MapNode(ants.ApplyTransforms(input_image_type = 3, dimension = 3, interpolation = 'Linear'), name='ants_reg', iterfield='input_image')
    
    
    ants_registration.connect([
                          (inputnode, collect_inputs_applyTf, [('flair_native', 'in1')]),
                          (inputnode, collect_inputs_applyTf, [('LCL', 'in2')]),
                          (collect_inputs_applyTf, applyreg, [('out', 'source_file')]),
                          (inputnode, applyreg, [('flair2anat', 'fsl_reg_file')]),
                          (inputnode, applyreg, [('brain', 'target_file')]),
                          (applyreg, ants_reg, [('transformed_file', 'input_image')]),
                          (inputnode, ants_reg, [('ref', 'reference_image')]), 
                          (inputnode, create_transforms,  [('transforms_anat2MNI_lin', 'lin')]),
                          (inputnode, create_transforms,  [('transforms_anat2MNI_warp', 'warp')]),
                          (create_transforms, ants_reg,  [('transforms', 'transforms')]),
                          (ants_reg, outputnode, [('output_image', 'flair2MNI')])
                          ])
                          
    return ants_registration
    
    
