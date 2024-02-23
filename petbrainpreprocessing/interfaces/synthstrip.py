import os
import warnings
import os.path as op
from nipype.interfaces.fsl.base import FSLCommand, FSLCommandInputSpec

from nipype.interfaces.base import (
    TraitedSpec,
    File,
    traits,
    isdefined
)

warnings.filterwarnings("always", category=UserWarning)


class SynthstripInputSpec(FSLCommandInputSpec):
    in_file = File(
        desc="input image to skullstrip",
        exists=True,
        argstr="-i %s",
        position=0,
        mandatory=True,
        copyfile=False
    )
    out_file = File(
        desc="save stripped image to file",
        argstr="-o %s",
        exists=False,
        position=1,
        hash_files=False,
        genfile=True
    )
    mask_file = File(
        desc="save binary brain mask to file",
        argstr="-m %s",
        position=2,
        mandatory=False,
        hash_files=False,
        genfile=True
    )
    dt_file = File(
        desc="save distance transform to file",
        argstr="-d %s",
        position=3,
        mandatory=False,
        hash_files=False,
        genfile=True
    )
    use_gpu = traits.Bool(
        desc="use the GPU",
        argstr="-g",
        mandatory=False
    )
    border = traits.Float(
        desc="mask border threshold in mm, defaults to 1",
        argstr="-b %f",
        mandatory=False
    )
    no_csf = traits.Bool(
        desc="exclude CSF from brain border",
        argstr="--no-csf",
        mandatory=False
    )
    model_file = File(
        exists=True,
        desc="alternative model weights",
        argstr="--model %s",
        copyfile=False
    )

class SynthstripOutputSpec(TraitedSpec):
    out_file = File(desc="output file", exists=True)
    mask_file = File(desc="mask file", exists=True)
    dt_file = File(desc="distance transform file", exists=True)
    

class Synthstrip(FSLCommand):
    """
    Brain Extraction using synthstrip-docker.
    Examples
    --------
    from nipype_custom.synthstrip import Synthstrip
    >>> synthstrip = Synthstrip()
    >>> synthstrip.inputs.in_file = 'file.nii.gz'
    >>> synthstrip.inputs.out_file = 'file_bet.nii.gz'
    >>> synthstrip.inputs.mask_file = 'mask.nii.gz'
    >>> synthstrip.inputs.dt_file = 'dt.nii.gz'
    >>> synthstrip.inputs.use_gpu = True
    >>> synthstrip.inputs.border = 1
    >>> synthstrip.inputs.no_csf = True
    >>> synthstrip.inputs.model_file = 'model.pth'
    >>> synthstrip.cmdline
    >>> synthstrip.run()
    """

    input_spec = SynthstripInputSpec
    output_spec = SynthstripOutputSpec
    _cmd = "synthstrip-docker"


    def _run_interface(self, runtime):
        runtime = super()._run_interface(runtime)
        if runtime.stderr:
            self.raise_exception(runtime)
        return runtime


    def _format_arg(self, name, spec, value):
        formatted = super()._format_arg(name, spec, value)
        if name == "in_file":
            # Convert to relative path
            return op.relpath(formatted, start=os.getcwd())
        return formatted


    def _gen_outfilename(self):
        out_file = self.inputs.out_file
        # Generate default output filename if non specified.
        if not isdefined(out_file) and isdefined(self.inputs.in_file):
            out_file = self._gen_fname(self.inputs.in_file, suffix="_brain")
        return out_file


    def _gen_maskfilename(self):
        mask_file = self.inputs.mask_file
        # Generate default output filename if non specified.
        if not isdefined(mask_file) and isdefined(self.inputs.in_file):
            mask_file = self._gen_fname(self.inputs.in_file, suffix="_brain_mask")
            return mask_file
        return mask_file


    def _gen_dtfilename(self):
        dt_file = self.inputs.dt_file
        # Generate default output filename if non specified.
        if not isdefined(dt_file) and isdefined(self.inputs.in_file):
            dt_file = self._gen_fname(self.inputs.in_file, suffix="_brain_dt")
            return dt_file
        return dt_file


    def _gen_filename(self, name):
        if name == "out_file":
            return self._gen_outfilename()
        if name == "mask_file":
            return self._gen_maskfilename()
        if name == "dt_file":
            return self._gen_dtfilename()
        return None


    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["out_file"] = os.path.abspath(self._gen_outfilename())

        basename = os.path.basename(outputs["out_file"])
        cwd = os.path.dirname(outputs["out_file"])
        kwargs = {"basename": basename, "cwd": cwd}

        if isdefined(self.inputs.mask_file):
            outputs['mask_file'] = self.inputs.mask_file
        else:
            outputs['mask_file'] = self._gen_fname(suffix="_mask", **kwargs)

        if isdefined(self.inputs.dt_file):
            outputs['dt_file'] = self.inputs.dt_file
        else:
            outputs['dt_file'] = self._gen_fname(suffix="_dt", **kwargs)

        return outputs
    
