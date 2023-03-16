import warnings
from pathlib import Path

from nipype.interfaces.base import (
    TraitedSpec,
    CommandLineInputSpec,
    CommandLine,
    File,
    traits,
    isdefined
)

warnings.filterwarnings("always", category=UserWarning)

class HDBetInputSpec(CommandLineInputSpec):
    in_file = File(
        exists=True,
        desc="Input. Can be either a single file name or an input folder. \
              In file: must be nifti (.nii.gz) and can only be 3D. No support for 4d images, use fslsplit to split \
              4d sequences into 3d images. In folder: all files ending with .nii.gz within that folder will be brain extracted.",
        argstr="-i %s",
        position=0,
        mandatory=True,
        copyfile=False
    )

    out_file = File(
        desc="Output. Can be either a filename or a folder. If it does not exist, the folder will be created",
        argstr="-o %s",
        position=1,
        hash_files=False
    )

    mode = traits.Str(
        desc="Mode can be either 'fast' or 'accurate'. Fast will use only one set of parameters whereas accurate \
              will use the five sets of parameters that resulted from our cross-validation as an ensemble. Default: accurate",
        argstr="-mode %s",
        position=2
    )

    device = traits.Str(
        desc="Used to set on which device the prediction will run. Must be either int or str. Use int for GPU id or 'cpu' \
              to run on CPU. When using CPU you should consider disabling tta. Default for -device is: 0",
        argstr="-device %s",
        position=3,
    )

    num_threads = traits.Int(
        desc="Used to set the number of cpu threads. Must be either int or str. Use 0 for max available cpus. \
              Default for -threads is: 0",
        argstr="-threads %i",
        position=4,
    )

    tta = traits.Str(
        desc="Used to set on which device the prediction will run. Must be either int or str. Use int for GPU id or 'cpu' \
              to run on CPU. When using CPU you should consider disabling tta. Default for -device is: 0",
        argstr="-tta %s",
        position=5,
    )

    pp = traits.Enum(
        0,
        1,
        desc="Set to 0 to disabe postprocessing (remove all but the largest connected component in the prediction. Default: 1",
        argstr="-pp %d",
        position=6,
    )

    s = traits.Enum(
        0,
        1,
        desc="Set to 0 to disabe postprocessing (remove all but the largest connected component in the prediction. Default: 1",
        argstr="-s %d",
        position=7,
    )


class HDBetOutputSpec(TraitedSpec):
    out_file = File(desc="output file", exists=True)
    mask_file = File(desc="mask file", exists=True)


class HDBet(CommandLine):
    """
    Brain Extraction using hd-bet.
    Examples
    --------
    from nipype_custom.hdbet import HDBet
    >>> hdbet = HDBet()
    >>> hdbet.inputs.in_file = 'file.nii.gz'
    >>> hdbet.inputs.out_file = 'file_bet.nii.gz'
    >>> hdbet.inputs.device = 'cpu'
    >>> hdbet.inputs.mode = 'fast'
    >>> hdbet.inputs.num_threads = 0
    >>> hdbet.inputs.tta = 0
    >>> hdbet.cmdline
    >>> hdbet.run()
    """

    input_spec = HDBetInputSpec
    output_spec = HDBetOutputSpec
    _cmd = "hd-bet"


    def _list_outputs(self):
        outputs = self.output_spec().get()

        if isdefined(self.inputs.out_file):
            outputs['out_file'] = self.inputs.out_file

            file_name = Path(self.inputs.out_file)
            base, first_dot, extension = file_name.name.partition('.')
            file_name = file_name.with_name(base)
            outputs['mask_file'] = f'{file_name}_mask.{extension}'

        else:
            file_name = Path(self.inputs.in_file)
            base, first_dot, extension = file_name.name.partition('.')
            file_name = file_name.with_name(base)

            outputs['out_file'] = f'{file_name}_bet.{extension}'
            outputs['mask_file'] = f'{file_name}_bet_mask.{extension}'

        return outputs