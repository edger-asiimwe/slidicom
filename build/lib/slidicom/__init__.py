#
# SLIDICOM - A Python package for constructing DICOMs from Aperio Whole Slide Images
#
# Author:       Asiimwe Edgar
# Copyright:    (c) 2023
#

__doc__ = """ 
    SLIDICOM - A Python package for constructing DICOMs from Aperio Whole Slide Images 
    =====================================================================================

    This package is a wrapper around the openslide-python and libdicom library. 
    It provides a simple interface for constructing DICOMs from Aperio Whole Slide Images.
"""

import os
import traceback

try:
    OPENSLIDE_BINARIES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'openslide_binaries', 'bin'))

    if hasattr(os, 'add_dll_directory'):
        # Python 3.8+ on Windows
        with os.add_dll_directory(OPENSLIDE_BINARIES_PATH):
            import openslide
    else:
        import openslide
except ImportError:
    raise ImportError(
        "Unable to load openslide libraries."
    ).with_traceback(traceback.format_exc())

import pandas as pd
from openslide.deepzoom import DeepZoomGenerator


class AbstractSlidicom:
    """ The base class of a slidicom object."""

    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class Slidicom(AbstractSlidicom):
    """ A slide object that can be used to construct a DICOM from an Aperio Whole Slide Image. 

        This class depends on the openslide-python library. If an OpenSlideError is raised,
        that means that the file that you are trying to read is not a valid WSI image. Or 
        possibly, there is an issue with the openslide binary files. 
    """

    def __init__(self, filename, data_path):
        """ Initialize a slidicom object. """

        AbstractSlidicom.__init__(self)
        self._osr = openslide.open_slide(filename)
        self._data = pd.read_csv(data_path)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._osr._filename})'