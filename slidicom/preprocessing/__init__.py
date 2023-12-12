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
        # Python 3.12+ on Windows
        with os.add_dll_directory(OPENSLIDE_BINARIES_PATH):
            import openslide
    else:
        import openslide
except ImportError:
    raise ImportError(
        "Unable to load openslide libraries."
    ).with_traceback(traceback.format_exc())


from openslide.deepzoom import DeepZoomGenerator
from PIL import Image
from collections import namedtuple 
import numpy as np

# Defined Data Types
ImageCord = namedtuple(
    'ImageCord', 
    ['image', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 'y4']
)

TileCordinate = namedtuple(
    'TileCordinate', 
    ['image_filename', 'tile_cordinates']
)

from .cordinates import ImageCordinates
#from cordinates import ImageCordinates
#from . import cordinates


class SVSProcessor:
    
    def __init__(self, filename, images):
        self._filename = filename
        self._images = images
        
        self._slide = openslide.OpenSlide(self.filename)

        self._tiles = DeepZoomGenerator(self._slide, 
                                        tile_size=256, 
                                        overlap=0, 
                                        limit_bounds=False
                                    )

        self._level_count = self._tiles.level_count
        self._level_to_split = self._level_count - 1
        
        self._image_width = self._tiles.level_dimensions[self._level_to_split][0]
        self._image_height = self._tiles.level_dimensions[self._level_to_split][1]
        
    def __repr__(self):
        return '{0}({1!r}, {2!r})'.format(
            self.__class__.__name__,
            self.filename, 
            self.number_of_images
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
        if self._tiles.level_dimensions[self._level_to_split][0] < self._tiles.level_dimensions[self._level_to_split][1]:
            return (1, round(self._tiles.level_dimensions[self._level_to_split][1] / self._tiles.level_dimensions[self._level_to_split][0]))
        return (round(self._tiles.level_dimensions[self._level_to_split][0] / self._tiles.level_dimensions[self._level_to_split][1]), 1)
    
    def _check_input(self):
        if self._images % self._aspect_ratio()[0] != 0 or self._images % self._aspect_ratio()[1] != 0:
            raise ValueError("Number of images must be divisible by aspect ratio")
        return True
    
    def _split_per_image(self):
        image_ratio = self._aspect_ratio()

        if self._images % 2 == 0:
            if image_ratio[0] == 2 and image_ratio[1] == 1:
                images_on_X = self._images // 2
                images_on_Y = self._images // images_on_X
        elif self._images == 1:
            images_on_X, images_on_Y = 1, 1

        return (images_on_X, images_on_Y)
    
    def _image_split_cordinates(self):
        image_splits_on_X, image_splits_on_Y = self._split_per_image()

        tiles_on_X = self._tiles.level_tiles[self._level_to_split][0] // image_splits_on_X
        tiles_on_Y = self._tiles.level_tiles[self._level_to_split][1] // image_splits_on_Y

        remainder_X = self._tiles.level_tiles[self._level_to_split][0] % image_splits_on_X
        remainder_Y = self._tiles.level_tiles[self._level_to_split][1] % image_splits_on_Y

        image_split_cordinates = []

        for y in range(image_splits_on_Y):
            for x in range(image_splits_on_X):
                if x < image_splits_on_X - 1 and y < image_splits_on_Y - 1:
                    """ This statement considers images sections that fully complete
                    E.g section rows and columns at the top and left edge, going beyond.

                    It leaves out sections that are half, or contain extra tiles as a
                    result of the remainder tiles.
                    E.g section row and column that are at the bottom and right edge.

                    ======== TOP LEFT =========
                    
                    """
                    image_cord = ImageCord(
                        image=((x + 1), (y + 1)),
                        x1=x * tiles_on_X, y1=y,
                        x2=x * tiles_on_X + tiles_on_X, y2=y,
                        x3=x * tiles_on_X, y3=tiles_on_Y,
                        x4=x * tiles_on_X + tiles_on_X, y4=tiles_on_Y
                    )
                    image_split_cordinates.append(image_cord)
                elif x == image_splits_on_X - 1 and y < image_splits_on_Y - 1:
                    """ This statement considers images sections on the TOP-RIGHT, that 
                    have the extra remainder tiles. This section contains remainder tiles on the X-plane 
                    direction only

                    ========= TOP RIGHT ==========
                    
                    """
                    image_cord = ImageCord(
                        image=((x + 1), (y + 1)),
                        x1=x * tiles_on_X, y1=y,
                        x2=x * tiles_on_X + tiles_on_X + remainder_X, y2=y,
                        x3=x * tiles_on_X, y3=tiles_on_Y,
                        x4=x * tiles_on_X + tiles_on_X + remainder_X, y4=tiles_on_Y
                    )
                    image_split_cordinates.append(image_cord)
                elif x == image_splits_on_X - 1 and y == image_splits_on_Y - 1:
                    """ This statement considers the 'ONE' images section at the BOTTOM-RIGHT, that 
                    have the extra remainder tiles. This section contains remainder tiles on the X-plane 
                    and Y-plane directions.

                    ========= BOTTOM RIGHT ==========
                    
                    """
                    image_cord = ImageCord(
                        image=((x + 1), (y + 1)),
                        x1=x * tiles_on_X, y1=y * tiles_on_Y,
                        x2=x * tiles_on_X + tiles_on_X + remainder_X, y2=y * tiles_on_Y,
                        x3=x * tiles_on_X, y3=y * tiles_on_Y + tiles_on_Y + remainder_Y,
                        x4=x * tiles_on_X + tiles_on_X + remainder_X, y4=y * tiles_on_Y + tiles_on_Y + remainder_Y
                    )
                    image_split_cordinates.append(image_cord)
                elif x < image_splits_on_X - 1 and y == image_splits_on_Y - 1:
                    """ This statement considers images sections on the BOTTOM-LEFT, that 
                    have the extra remainder tiles. This section contains remainder tiles on the Y-plane
                    direction only

                    ========= BOTTOM LEFT ==========
                    
                    """
                    image_cord = ImageCord(
                        image=((x + 1), (y + 1)),
                        x1=x * tiles_on_X, y1=y * tiles_on_Y,
                        x2=x * tiles_on_X + tiles_on_X + remainder_X, y2=y * tiles_on_Y,
                        x3=x * tiles_on_X, y3=y * tiles_on_Y + tiles_on_Y + remainder_Y,
                        x4=x * tiles_on_X + tiles_on_X + remainder_X, y4=y * tiles_on_Y + tiles_on_Y + remainder_Y
                    )
                    image_split_cordinates.append(image_cord)

        return image_split_cordinates
    
    def process_image(self, save=False):
        image_data = []

        for image_coord in self._image_split_cordinates():
            image = ImageCord(image_coord, self._filename)

            for tile_coord in image.tile_cordinates:
                tile_image = np.array(self._tiles.get_tile(self._level_to_split, tile_coord))
                
                print(f"Processing Image: {image.image_filename}, Tile: {tile_coord}")
                # # Print some information about the current tile
                # print(f"Processing Image: {image.image_filename}, Tile: {tile_coord}")

                # # Access pixel data (assuming tile_image is a NumPy array)
                # pixel_data = tile_image.ravel()

                # # Add pixel data to the image object if needed
                # image.add_pixel_data(pixel_data)

            if save:
                # Save the tile as a JPEG image
                save_path = os.path.join(os.path.dirname(self._filename), "{0}.jpeg".format(image.image_filename))
                Image.fromarray(tile_image, mode='RGB').save(save_path)
                print(f"Tile saved to {save_path}")

            image_data.append(image)

        return image_data
    
