from setuptools import setup

setup(
    name='PET Brain Preprocessing',
    version='0.1.1',    
    description='Robust Nipype pipeline for preprocessing PET BIDS brain \
                 data. Initially developed for 18F FDG PET brain images \
                 acquired by project NEMO at the Dep of Neurology, \
                 University Medical Center Groningen. \
                 https://www.movementdisordersgroningen.com/nl/nemo',
    url='https://github.com/jrdalenberg/pet-brain-preprocessing',
    author='Jelle R. Dalenberg',
    author_email='j.r.dalenberg@gmail.com',
    license='Apache License 2.0',
    packages=['petbrainpreprocessing'],
    install_requires=['nipype>=1.8.5',
                      'bids',
                      'templateflow>=23.0.0',
                      'docopt>=0.6.2',
                      'nibabel>=5.0.1',
                      'NetworkX==2.6',
                      ],
    scripts=['petbrainpreprocessing/pet_brain_preprocessing.py'],
    classifiers=[
        'Development Status :: 1 - Concept',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache License 2.0',  
        'Operating System :: Unix',        
        'Programming Language :: Python :: 3.9',
    ],
)