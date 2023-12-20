#
# SLIDICOM - A Python package for constructing DICOMs from Aperio Whole Slide Images
#
# Author:       Asiimwe Edgar
# Copyright:    (c) 2023
#


""" Module: Preprocessing

    This module provides functionalities for preprocessing WSL e.g. SVS
    before use in Pyrmadial TIFF Construction and DICOM Construction.
"""


import os
import traceback
import concurrent.futures
from typing import Dict, Optional, Union
from collections import namedtuple

try:
    #OPENSLIDE_BINARIES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'openslide_binaries', 'bin')
    OPENSLIDE_BINARIES_PATH = os.path.join(os.path.dirname(__file__), 'openslide_binaries', 'bin')

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
import numpy as np
import csv

# Defined Custom Data Types
ImageCord = namedtuple(
    'ImageCord', 
    ['image', 'x1', 'y1', 'x2', 'y2', 'x3', 'y3', 'x4', 'y4']
)

TileCordinate = namedtuple(
    'TileCordinate', 
    ['image_filename', 'tile_cordinates']
)

SLIDE_METADATA: Dict[str, Optional[Union[int, str, float]]] = {
    'aperio.AppMag': int | None,
    'aperio.Date': str | None,
    'aperio.DisplayColor': int | None,
    'aperio.Exposure Scale': float | None,
    'aperio.Exposure Time': str | None,
    'aperio.Filename': str | None,
    'aperio.Focus Offset': float | None,
    'aperio.ICC Profile': str | None,
    'aperio.ImageID': str | None,
    'aperio.Left': float | None,
    'aperio.LineAreaXOffset': float | None,
    'aperio.LineAreaYOffset': float | None,
    'aperio.LineCameraSkew': float | None,
    'aperio.MPP': float | None,
    'aperio.OriginalHeight': int | None,
    'aperio.OriginalWidth': int | None,
    'aperio.ScanScope ID': str | None,
    'aperio.StripeWidth': int | None,
    'aperio.Time': str | None,
    'aperio.Time Zone': str | None,
    'aperio.Top': float | None,
    'aperio.User': str | None,
    'openslide.associated.label.height': int | None,
    'openslide.associated.label.width': int | None,
    'openslide.associated.macro.height': int | None,
    'openslide.associated.macro.width': int | None,
    'openslide.associated.thumbnail.height': int | None,
    'openslide.associated.thumbnail.width': int | None,
    'openslide.comment': str | None,
    'openslide.icc-size': int | None,
    'openslide.level-count': int | None,
    'openslide.level[0].downsample': float | None,
    'openslide.level[0].height': int | None,
    'openslide.level[0].tile-height': int | None,
    'openslide.level[0].tile-width': int | None,
    'openslide.level[0].width': int | None,
    'openslide.level[1].downsample': float | None,
    'openslide.level[1].height': int | None,
    'openslide.level[1].tile-height': int | None,
    'openslide.level[1].tile-width': int | None,
    'openslide.level[1].width': int | None,
    'openslide.level[2].downsample': float | None,
    'openslide.level[2].height': int | None,
    'openslide.level[2].tile-height': int | None,
    'openslide.level[2].tile-width': int | None,
    'openslide.level[2].width': int | None,
    'openslide.level[3].downsample': float | None,
    'openslide.level[3].height': int | None,
    'openslide.level[3].tile-height': int | None,
    'openslide.level[3].tile-width': int | None,
    'openslide.level[3].width': int | None,
    'openslide.mpp-x': float | None,
    'openslide.mpp-y': float | None,
    'openslide.objective-power': int | None,
    'openslide.quickhash-1': str | None,
    'openslide.vendor': str | None,
    'tiff.ImageDescription': str | None,
    'tiff.ResolutionUnit': str | None,
}


class ImageCordinates:    
    def __init__(self, imageCord, parent_filename):
        self._imageCord = imageCord
        self._parent_filename = os.path.basename(parent_filename)
        self.image_filename = self._image_filename()
        self.tile_cordinates = self._tile_image_index()

    def _image_filename(self):
        return "{0}_{1}_{2}".format(
            self._parent_filename, 
            self._imageCord.image[0], 
            self._imageCord.image[1]
        )
    
    def image_width(self):
        return (self._imageCord.x2 - self._imageCord.x1) * 256

    def image_height(self):
        return (self._imageCord.y3 - self._imageCord.y1) * 256
    
    def _tile_image_index(self):
        return [ (x, y) for y in range(self._imageCord.y1, self._imageCord.y3) for x in range(self._imageCord.x1, self._imageCord.x2)]
    
    def _tile_cordinates(self):
        return TileCordinate(self._image_filename(), self._tile_image_index())
    

class SVSProcessor(object):
    
    def __init__(
            self, 
            filename: str, 
            images: int
        ):

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

        self._slide_metadata = self._slide_metadata_dict()


        
    def __repr__(self) -> str:
        return '{0}({1!r}, {2!r})'.format(
            self.__class__.__name__,
            self.filename, 
            self.number_of_images
        )
    
    @property
    def filename(self) -> str:
        """ The filename of the Whole Slide Image to split."""
        return self._filename
    
    @property
    def number_of_images(self) -> int:
        """ The number of images to split the Whole Slide Image into."""
        return self._images
    
    @property
    def level_count(self) -> int:
        """ The number of levels in the DeepZoom pyramid."""
        return self._level_count
    
    @property
    def level_to_split(self) -> int:
        """ The level to split the Whole Slide Image at, in the pyramid.
        
        This has been set by default to the last level in the pyramid.
        The images at this level are the highest resolution images.
        """
        return self._level_to_split
    
    @property
    def image_width(self) -> int:
        """ The width of the Whole Slide Image to split."""
        return self._image_width
    
    @property
    def image_height(self) -> int:
        """ The height of the Whole Slide Image to split."""
        return self._image_height
    
    @property
    def aspect_ratio(self) -> tuple:
        return self._aspect_ratio()
    
    @property
    def slide_metadata(self) -> Dict[str, Optional[Union[int, str, float]]]:
        """ The metadata of the Whole Slide Image to split."""
        return self._slide_metadata
    
    def _aspect_ratio(self) -> tuple:
        """ The aspect ratio of the Whole Slide Image to split."""
        if self._tiles.level_dimensions[self._level_to_split][0] < self._tiles.level_dimensions[self._level_to_split][1]:
            return (1, round(self._tiles.level_dimensions[self._level_to_split][1] / self._tiles.level_dimensions[self._level_to_split][0]))
        return (round(self._tiles.level_dimensions[self._level_to_split][0] / self._tiles.level_dimensions[self._level_to_split][1]), 1)
    
    def _slide_metadata_dict(self) -> Dict[str, Optional[Union[int, str, float]]]:
        """ Return the slide metadata in the Whole Slide Image """
        return {
            key: self._slide.properties.get(key, None)
            for key in SLIDE_METADATA
        }
    
    def _save_metadata_to_file(self) -> None:
        if self._save:
            metadata = self._slide_metadata
            save_path = os.path.join(os.path.dirname(self._filename), "{0}.csv".format(self._filename))

            with open(save_path, 'w', newline='') as csvfile:
                fieldnames = ['Property', 'Value']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)

                writer.writeheader()

                for property_name, value in metadata.items():
                    writer.writerow({'Property': property_name, 'Value': value})

        
    # TODO: Change to make the images, in range of 1, 2, 4, 8
    def _split_per_image(self) -> tuple:
        image_ratio = self._aspect_ratio()

        if self._images % 2 == 0:
            if image_ratio[0] == 2 and image_ratio[1] == 1:
                images_on_X = self._images // 2
                images_on_Y = self._images // images_on_X
        elif self._images == 1:
            images_on_X, images_on_Y = 1, 1

        return (images_on_X, images_on_Y)
    
    def _image_split_cordinates(self) -> list:
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


    def _process_image(self, image_coord, save, format) -> Dict[str, np.ndarray]:

        image = ImageCordinates(
            image_coord, 
            self._filename
        )
        
        full_image = Image.new('RGB', 
                               (
                                   image.image_width(), 
                                   image.image_height()
                                )
                            )

        for tile in image.tile_cordinates:
            tile_image = self._tiles.get_tile(self._level_to_split, tile)

            x = (tile[0] - image._imageCord.x1) * 256
            y = (tile[1] - image._imageCord.y1) * 256

            full_image.paste(tile_image, (x, y))

        if save:
            save_path = os.path.join(os.path.dirname(self._filename), "{0}.{1}".format(image.image_filename, format))
            full_image.save(save_path)

        image_pixel = np.array(full_image)

        return {'image_filename': image.image_filename, 'image_pixel': image_pixel}


    def pixel_array(self, save=False, format='jpeg') -> Dict[str, np.ndarray]:
        """ Return the pixel array of the split images as a numpy array
        from the Whole Slide Image.

        Returns:
            Dict[str, np.ndarray]: A dictionary of the split images as numpy arrays.

        """
        images = {}

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self._process_image, image_coord, save, format): image_coord 
                for image_coord in self._image_split_cordinates()
            }

            concurrent.futures.wait(futures)

            for future in concurrent.futures.as_completed(futures):
                image_coord = futures[future]
                try:
                    result = future.result()
                    images[result['image_filename']] = result['image_pixel']
                except Exception as e:
                    print(f"Error processing image at coordinates {image_coord}: {e}")

        return images

