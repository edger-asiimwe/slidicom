#
# SLIDICOM - A Python package for constructing DICOMs from Aperio Whole Slide Images
#
# Author:       Asiimwe Edgar
# Copyright:    (c) 2023
#
#
# Module: Splitter - A module for conerting and/or a Whole Slide Images to JEPGs or PNGs
#


import os
import traceback

try:
    OPENSLIDE_BINARIES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'openslide_binaries', 'bin')

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


from openslide.deepzoom import DeepZoomGenerator
from collections import namedtuple

# Defined Data Types
ImageCord = namedtuple('ImageCord', ['image', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 'y4'])

class WSISplitter:
    
    def __init__(self, filename, images):
        self._filename = filename
        self._images = images
        self._slide = openslide.OpenSlide(self.filename)
        self.self._tiles = DeepZoomGenerator(self._slide, tile_size=256, overlap=0, limit_bounds=False)

        self._level_count = self.self._tiles.level_count
        self._level_to_split = self._level_count - 1
        
        self._image_width = self.self._tiles.level_dimensions[self._level_to_split][0]
        self._image_height = self.self._tiles.level_dimensions[self._level_to_split][1]
        
    def __repr__(self):
        return '{0}({1!r}, {2!r})'.format(
            self.__class__.__name__,
            self.filename, 
            self.num_of_images
        )
    
    @property
    def filename(self):
        """ The filename of the Whole Slide Image to split."""
        return self._filename
    
    @property
    def number_of_images(self):
        """ The number of images to split the Whole Slide Image into."""
        return self._images
    
    @property
    def level_count(self):
        """ The number of levels in the DeepZoom pyramid."""
        return self._level_count
    
    @property
    def level_to_split(self):
        """ The level to split the Whole Slide Image at, in the pyramid.
        
        This has been set by default to the last level in the pyramid.
        The images at this level are the highest resolution images.
        """
        return self._level_to_split
    
    @property
    def image_width(self):
        """ The width of the Whole Slide Image to split."""
        return self._image_width
    
    @property
    def image_height(self):
        """ The height of the Whole Slide Image to split."""
        return self._image_height
    
    @property
    def aspect_ratio(self):
        return self._aspect_ratio()
    
    def _aspect_ratio(self):
        """ The aspect ratio of the Whole Slide Image to split."""
        if self._tiles.level_dimensions[self._level_to_splitlevel][0] < self._tiles.level_dimensions[self._level_to_splitlevelevel][1]:
            return (1, round(self._tiles.level_dimensions[self._level_to_splitlevel][1] / self._tiles.level_dimensions[self._level_to_splitlevel][0]))
        return (round(self._tiles.level_dimensions[self._level_to_splitlevel][0] / self._tiles.level_dimensions[self._level_to_splitlevel][1]), 1)