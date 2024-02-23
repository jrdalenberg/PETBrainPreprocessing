# PET Brain Preprocessing
Robust Nipype workflow for preprocessing PET BIDS brain data. Initially developed for 18F FDG PET brain images acquired by project NEMO at the Department of Neurology, University Medical Center Groningen. https://www.movementdisordersgroningen.com/nl/nemo. This workflow was also successfully tested on 18F FEOBV PET brain images.

# About
Since existing preprocessing pipelines for FDG PET brain data may require many manual correctons, we set up this a preprocessing pipeline for PET Brain Preprocessing. This preprocessing pipeline is currently built for static PET brain images stored in [BIDS format](https://bids-specification.readthedocs.io/en/stable/04-modality-specific-files/09-positron-emission-tomography.html). The goal of the pipeline was for it to be robust, easy-to-use, and minimal. 

Minimal preprocessing includes (1) _coregistration_ and (2) _normalization_ of PET brain images. This pipeline complements `--anat-only` preprocessing of T1w anatomical images by [fMRIPrep](https://fmriprep.org/en/stable/).

![Pipeline Graph](docs/_static/analysis_pipeline.png)

# Requirements
- [fMRIPrep](https://fmriprep.org/en/stable/)
- [FSL 6.0](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation)
- [AFNI 21.3.04 'Trajan'](https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/index.html)
- [ANTs 2.3.5](http://stnava.github.io/ANTs/)
- [Synthstrip-docker](https://surfer.nmr.mgh.harvard.edu/docs/synthstrip/). Also see [(Hoopes, et al., 2022)](https://doi.org/10.1016/j.neuroimage.2022.119474).


# TODO
- Make outputs BIDS compatible.
- Make participant label optional.
- Make docker image.
- Add support for dynamic scans.
- Add motion correction for dynamic scans.
- Add pharmakinetic modeling for dynamic scans.
- Add optional atlas-based segmentation.
- Add optional small volume correction.

# License information
## License
Copyright (c) 2023, the PET Brain preprocessing developers.

PET Brain preprocessing is licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

# Acknowledgements
This work was supported by ZonMw TOP 2019.