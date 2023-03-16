from __future__ import division, unicode_literals

from nipype.interfaces.utility import (IdentityInterface, Merge)
from nipype.interfaces import (fsl, ants, afni)
from nipype.interfaces.base import CommandLine
from nipype.interfaces.io import DataSink
from nipype import Workflow, Node

from os.path import join as opj

from ..interfaces.hdbet import HDBet

CommandLine.set_default_terminal_output('allatonce')
fsl.FSLCommand.set_default_output_type('NIFTI_GZ')


def pet_preprocessing_workflow(participant_id: str, 
                               scratch_folder: str,
                               perform_smoothing: bool, 
                               name='coreg_and_norm_wf'):
    """
    Build PET brain coregistration and normalization pipeline.

    This workflow performs image croppiong, brain extraction, coregistration
    in two separate stages, and normalization. 


    Parameters
    ----------
    participant_id : string
        participant label for this single-participant workflow.

        base_dir : string, optional
            path to workflow storage

    """
    
    # Route input files
    inputnode = Node(interface=IdentityInterface(
        fields=['results_folder',
                'pet_image', 
                'participant_id', 
                'template', 
                'T1', 
                'T1_mask', 
                'T1_resampled_template', 
                'transform',
                'smooth_fwhm',
                'num_threads']), 
        name='input_files')

    # Crop PET image
    crop = Node(afni.Autobox(), name='crop_image')
    crop.inputs.outputtype='NIFTI_GZ'
    crop.inputs.padding = 10

    # Skull strip PET image
    hdbet = Node(HDBet(), name = "skull_strip")
    hdbet.inputs.device = 'cpu'
    hdbet.inputs.mode = 'fast'
    hdbet.inputs.tta = '0'

    # Rigister cropped PET to MR space, first pass
    coregister_first_pass = Node(ants.Registration(), name='coreg_first_pass')
    coregister_first_pass.inputs.output_transform_prefix = 'petmask2anatmask'
    coregister_first_pass.inputs.output_warped_image = 'petmask2anatmask.nii.gz'
    coregister_first_pass.inputs.transforms = ['Rigid']
    coregister_first_pass.inputs.transform_parameters = [(0.3,), (0.3,)]
    coregister_first_pass.inputs.number_of_iterations = [[1000, 100]]*3 
    coregister_first_pass.inputs.dimension = 3
    coregister_first_pass.inputs.write_composite_transform = True
    coregister_first_pass.inputs.collapse_output_transforms = False
    coregister_first_pass.inputs.metric = ['Mattes'] 
    coregister_first_pass.inputs.metric_weight = [1] 
    coregister_first_pass.inputs.radius_or_number_of_bins = [32] 
    coregister_first_pass.inputs.sampling_strategy = ['Regular']
    coregister_first_pass.inputs.sampling_percentage = [0.3] 
    coregister_first_pass.inputs.convergence_threshold = [1.e-12] 
    coregister_first_pass.inputs.convergence_window_size = [20] 
    coregister_first_pass.inputs.smoothing_sigmas = [[4, 2]]
    coregister_first_pass.inputs.sigma_units = ['vox'] 
    coregister_first_pass.inputs.shrink_factors = [[15, 8]] 
    coregister_first_pass.inputs.use_estimate_learning_rate_once = [True] 
    coregister_first_pass.inputs.use_histogram_matching = [False] 
    coregister_first_pass.inputs.initial_moving_transform_com = 0

    # Rigister cropped PET to MR space, second pass
    coregister_second_pass = Node(ants.Registration(), name='coreg_second_pass')
    coregister_second_pass.inputs.output_transform_prefix = 'pet2anat'
    coregister_second_pass.inputs.output_warped_image = 'pet2anat.nii.gz'
    coregister_second_pass.inputs.transforms = ['Rigid']
    coregister_second_pass.inputs.transform_parameters = [(0.3,), (0.3,)]
    coregister_second_pass.inputs.number_of_iterations = [[1000, 100]]*3 
    coregister_second_pass.inputs.dimension = 3
    coregister_second_pass.inputs.write_composite_transform = True
    coregister_second_pass.inputs.collapse_output_transforms = False
    coregister_second_pass.inputs.metric = ['Mattes'] 
    coregister_second_pass.inputs.metric_weight = [1] 
    coregister_second_pass.inputs.radius_or_number_of_bins = [32] 
    coregister_second_pass.inputs.sampling_strategy = ['Regular']
    coregister_second_pass.inputs.sampling_percentage = [0.3] 
    coregister_second_pass.inputs.convergence_threshold = [1.e-12] 
    coregister_second_pass.inputs.convergence_window_size = [20] 
    coregister_second_pass.inputs.smoothing_sigmas = [[4, 2]]
    coregister_second_pass.inputs.sigma_units = ['vox'] 
    coregister_second_pass.inputs.shrink_factors = [[15, 8]] 
    coregister_second_pass.inputs.use_estimate_learning_rate_once = [True] 
    coregister_second_pass.inputs.use_histogram_matching = [False] 

    # Merge transformation files
    coregister_merge = Node(Merge(2), iterfield=['in'], name='merge_coreg_transformations')

    # Merge all transformations
    merge = Node(Merge(3), iterfield=['in'], name='merge_transformations')

    # Apply mask coregistration to pet
    apply_first_pass = Node(ants.ApplyTransforms(), name='apply_coreg_first_pass')
    apply_first_pass.inputs.args = '--float'
    apply_first_pass.inputs.input_image_type = 3
    apply_first_pass.inputs.interpolation = 'Linear'
    apply_first_pass.inputs.invert_transform_flags = [False]
    apply_first_pass.inputs.num_threads = 1
    apply_first_pass.terminal_output = 'file'

    # Apply final coreg to PET image for native space analysis
    apply_second_pass = Node(ants.ApplyTransforms(), name='apply_final_coreg')
    apply_second_pass.inputs.args = '--float'
    apply_second_pass.inputs.input_image_type = 3
    apply_second_pass.inputs.interpolation = 'Linear'
    apply_second_pass.inputs.invert_transform_flags = [False, False]
    apply_second_pass.inputs.num_threads = 1
    apply_second_pass.terminal_output = 'file'

    # Apply Transformation - applies the normalization matrix to the mean image
    apply_coregistration_and_normalization = Node(ants.ApplyTransforms(), name='apply_coreg_and_norm')
    apply_coregistration_and_normalization.inputs.args = '--float'
    apply_coregistration_and_normalization.inputs.input_image_type = 3
    apply_coregistration_and_normalization.inputs.interpolation = 'Linear'
    apply_coregistration_and_normalization.inputs.invert_transform_flags = [False, False, False]
    apply_coregistration_and_normalization.inputs.num_threads = 1
    apply_coregistration_and_normalization.terminal_output = 'file'

    # Smoothing
    if perform_smoothing:
        smooth = Node(fsl.Smooth(), name='fwhm_smoothing')

    # Datasink
    datasink = Node(DataSink(), name="output_files")

    # Set subject scratch folder if defined
    if scratch_folder:
        scratch_folder = opj(scratch_folder, participant_id)

    # Connect nodes
    workflow = Workflow(name=name, base_dir=scratch_folder)

    # Crop PET image
    workflow.connect(inputnode, 'pet_image', crop, 'in_file')

    # Skull strip PET image
    workflow.connect(crop, 'out_file', hdbet, 'in_file')
    workflow.connect(inputnode, 'num_threads', hdbet, 'num_threads')

    # Register masks
    workflow.connect(inputnode, 'T1_mask', coregister_first_pass, 'fixed_image')
    workflow.connect(hdbet, 'mask_file', coregister_first_pass, 'moving_image')
    workflow.connect(inputnode, 'num_threads', coregister_first_pass, 'num_threads')
    
    # Apply mask rotation to pet image
    workflow.connect(inputnode, 'pet_image', apply_first_pass, 'input_image')
    workflow.connect(inputnode, 'template', apply_first_pass, 'reference_image')
    workflow.connect(coregister_first_pass, 'composite_transform', apply_first_pass, 'transforms')

    # Register cropped PET to MR
    workflow.connect(apply_first_pass, 'output_image', coregister_second_pass, 'moving_image')
    workflow.connect(inputnode, 'T1', coregister_second_pass, 'fixed_image')
    workflow.connect(inputnode, 'num_threads', coregister_second_pass, 'num_threads')

    # Merge coregistrations for native space output
    workflow.connect(coregister_second_pass, 'composite_transform', coregister_merge, 'in1')
    workflow.connect(coregister_first_pass, 'composite_transform', coregister_merge, 'in2')

    # Coregistration, Normalization -> merge transformations
    workflow.connect(inputnode, 'transform', merge, 'in1')
    workflow.connect(coregister_second_pass, 'composite_transform', merge, 'in2')
    workflow.connect(coregister_first_pass, 'composite_transform', merge, 'in3')

    # Transformations -> apply final coregistration
    workflow.connect(inputnode, 'pet_image', apply_second_pass, 'input_image')
    workflow.connect(inputnode, 'T1_resampled_template', apply_second_pass, 'reference_image')
    workflow.connect(coregister_merge, 'out', apply_second_pass, 'transforms')

    # Transformations -> apply coregistration and normalization to pet image
    workflow.connect(inputnode, 'pet_image', apply_coregistration_and_normalization, 'input_image')
    workflow.connect(inputnode, 'template', apply_coregistration_and_normalization, 'reference_image')
    workflow.connect(merge, 'out', apply_coregistration_and_normalization, 'transforms')

    # Smooth PET image
    if perform_smoothing:
        workflow.connect(apply_coregistration_and_normalization, 'output_image', smooth, 'in_file')
        workflow.connect(inputnode, 'smooth_fwhm', smooth, 'fwhm')

    # Route results files to output folders
    workflow.connect(inputnode, 'results_folder', datasink, 'base_directory')
    workflow.connect(inputnode, 'participant_id', datasink, 'container')
    workflow.connect(crop, 'out_file', datasink, 'convert.pet_crop')
    workflow.connect(hdbet, 'out_file', datasink, 'convert.pet_skullstrip')
    workflow.connect(coregister_first_pass, 'warped_image', datasink, 'coreg.mask')
    workflow.connect(coregister_second_pass, 'warped_image', datasink, 'coreg.pet')
    workflow.connect(inputnode, 'T1_resampled_template', datasink, 'coreg.T1_resampled')
    workflow.connect(apply_second_pass, 'output_image', datasink, 'coreg.pet_final')
    workflow.connect(coregister_first_pass, 'composite_transform', datasink, 'transforms.cocoregister_first_pass')
    workflow.connect(coregister_second_pass, 'composite_transform', datasink, 'transforms.cocoregister_second_pass')
    workflow.connect(apply_coregistration_and_normalization, 'output_image', datasink, 'norm.pet')

    if perform_smoothing:
        workflow.connect(smooth, 'smoothed_file', datasink, 'smooth')

    return workflow

