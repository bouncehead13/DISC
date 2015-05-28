# Distributed Indexed Storage in the Cloud

## Overview of DISC
We improve performance by concurrently processing files and leveraging a multi-storage model. This model allows for various limitations in the current approaches to be improved.

## Installation
Tested with Python 2.7.6

**Note: Installing packages may require `sudo`**

First install a package manager. I recommend using `pip` which can be installed following [these instructions](https://pip.pypa.io/en/stable/installing.html)

Required packages:
- [Google Storage API](https://developers.google.com/api-client-library/python/start/installation) `$ pip install google-api-python-client`
- [Dropbox Core API](https://www.dropbox.com/developers/core/sdks/python) `$ pip install dropbox`
- [skimage](http://scikit-image.org) (version 0.10.1) `$ pip install scikit-image==0.10.1`
- [Pillow](http://pillow.readthedocs.org/) (version 2.4.0) `$ pip install Pillow==2.4.0`
- [MoviePy](http://zulko.github.io/moviepy/) (version 2.2.11) `$ pip install moviepy`

## Commands
- `num_providers`: The number of instances to create with each storage provider
- `--upload` or `--download`: Whether to upload or download the file
- `--million`, `--split`, `--available`, `--scale`, `--low`: User policies

Example command: `python driver.py 2 --upload --split`