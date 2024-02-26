from petbrainpreprocessing.workflows.preprocessing_workflow import \
    pet_preprocessing_workflow
from templateflow import api as tflow
import argparse
from os import makedirs
from os.path import exists, isfile
from os.path import join as opj
from nibabel.processing import resample_to_output
from nibabel import load, save
from multiprocessing import cpu_count


def main():
    parser = argparse.ArgumentParser(
        description="Function that handles the inputs for preprocessing pet images."
    )
    parser.add_argument("bids_dir", 
                        help="Path to the BIDS dataset directory.")
    parser.add_argument("output_dir", 
                        help="Output directory.")
    parser.add_argument("anat_derivatives_dir", 
                        help="fMRIPrep Anatomical derivatives directory.")
    parser.add_argument("--participant-label",
                        required=True,
                        help="A space delimited list of participant identifiers or \
                            a single identifier (the sub- prefix can be removed).",
    )
    parser.add_argument("--nprocs",
                        type=int,
                        help="Maximum number of threads across all processes.",
    )
    parser.add_argument("--fwhm",
                        type=float,
                        help="The full width at half maximum smoothing kernel.",
    )
    parser.add_argument("--work-dir",
                        help="Path where intermediate results should be stored.",
    )
    args = parser.parse_args()

    # Check arguments
    participant = f"sub-{args.participant_label}"
    if not exists(args.anat_derivatives_dir):
        raise FileNotFoundError(f"ERROR. Cannot find fMRIPrep derivatives \
            folder {args.anat_derivatives_dir}.")

    participant_fmriprep_anat_folder = \
        opj(args.anat_derivatives_dir, participant, "anat")
    
    if not exists(participant_fmriprep_anat_folder):
        raise FileNotFoundError(f"ERROR. Cannot find fMRIPrep derivatives \
            participant_folder {participant_fmriprep_anat_folder}.")

    participant_bids_folder = opj(args.bids_dir, participant)

    if not exists(participant_bids_folder):
        raise FileNotFoundError(f"ERROR. Cannot find BIDS participant_folder \
            {participant_bids_folder}.")

    # Make sure the workdir exists
    if args.work_dir is not None:
        makedirs(args.work_dir, exist_ok=True)

    # Make sure the output dir exists
    makedirs(args.output_dir, exist_ok=True)

    # Fetch files
    anat_file_path = opj(participant_fmriprep_anat_folder,
        f"{participant}_desc-preproc_T1w.nii.gz")
    anat_mask_file_path = opj(participant_fmriprep_anat_folder,
        f"{participant}_desc-brain_mask.nii.gz")
    anat2mni_matrix = opj(participant_fmriprep_anat_folder,
        f"{participant}_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5")
    pet_file_path = opj(participant_bids_folder, "pet",
        f"{participant}_pet.nii.gz")

    # Check for missing input data
    missing_files = []
    for file_path in [anat_file_path, anat_mask_file_path, anat2mni_matrix, pet_file_path]:
        if not isfile(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        raise FileNotFoundError(f"ERROR. The following files are missing: {', '.join(missing_files)}")

    # Fetch MNI template
    template = tflow.get('MNI152NLin2009cAsym', desc=None, resolution=2,
                          suffix='T1w', extension='nii.gz')

    # Resample T1w to PET voxel dimensions (needed as reference image for ANTs)
    pet_file_img = load(pet_file_path)
    anat_file_img = load(anat_file_path)
    resample_size = abs(pet_file_img.affine.diagonal()[0:3])
    T1w_resampled_img = resample_to_output(anat_file_img, resample_size)
    T1w_resampled_path = opj(participant_fmriprep_anat_folder, 
        f'{participant}_desc-preproc_resampled-to-PET_T1w.nii.gz')
    save(T1w_resampled_img, T1w_resampled_path)
    
    # Set nprocs to max if not specified
    if args.nprocs == None:
        args.nprocs = cpu_count()

    # Set up coregistration + normalization pipeline
    wf = pet_preprocessing_workflow(participant,  args.work_dir, args.fwhm != None)
    wf.inputs.input_files.results_folder = args.output_dir
    wf.inputs.input_files.T1 = anat_file_path
    wf.inputs.input_files.T1_mask = anat_mask_file_path
    wf.inputs.input_files.T1_resampled_template = T1w_resampled_path
    wf.inputs.input_files.participant_id = participant
    wf.inputs.input_files.template = template
    wf.inputs.input_files.pet_image =  pet_file_path
    wf.inputs.input_files.num_threads = int(args.nprocs)
    wf.inputs.input_files.transform = anat2mni_matrix

    # Optional smoothing
    if args.fwhm is not None:
        wf.inputs.input_files.smooth_fwhm = int(args.fwhm)

    # Write pipeline graph
    wf.write_graph(graph2use='flat', simple_form=True)

    # Run pipeline
    wf.run('MultiProc', plugin_args={'n_procs': int(args.nprocs)})


if __name__ == '__main__':
    main()
