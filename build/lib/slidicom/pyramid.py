#
# SLIDICOM - A Python package for constructing DICOMs from Aperio Whole Slide Images
#
# Author:       Asiimwe Edgar
# Copyright:    (c) 2023
#


""" Module: Pyramid TIFF Construction

    This module provides functionalities for Pyrmadial TIFF Construction.
"""

import os

from typing import Union, Dict, Optional
from .preprocessing import SLIDE_METADATA

from tifffile import TiffWriter
from PIL import Image
import numpy as np

Image.MAX_IMAGE_PIXELS = None

TIFF_BASE_METADATA: Dict[str, Optional[Union[int, str, float]]] = {
    'axes': 'YXS',
    'SignificantBits': 8,
}

class PyramidTIFFGenerator(object):
    """ Class: PyramidTIFFGenerator

        This class provides functionalities for Pyrmadial TIFF Construction.
    """

    def __init__(
            self,
            image: Union[str, object, dict],
            format: str,
            metadata_dict: dict = None,
        ):

        self._format = format

        # Process image when a filenmae is provided
        if isinstance(image, str):
            image_name = os.path.splitext(os.path.basename(image))[0]
            self._image = {
                "image_filename": image_name,
                "image_pixel": np.array(Image.open(image))
                }
            self._metadata = None
        
        # Process image when an 'SVSProcessor.pixel_array()' is provided
        elif isinstance(image, dict):
            self._image = image
            self._metadata = metadata_dict

        # Process image when an 'SVSProcessor' object is provided
        elif isinstance(image, object):
            self._image = self._svsprocessor_object(image)
            self._metadata = self._svsprocessor_metadata(image)


    def __repr__(self) -> str:
        return '{0}({1!r}, {2!r})'.format(
            self.__class__.__name__,
            self.image, 
            self._format
        )
    
    @property
    def image(self) -> dict:
        """ 
            This property accesses the image dictionary containing file name
            and the pixel array representation of the image  
        """
        return self._image
    
    @property
    def metadata(self) -> dict:
        """ 
            This property accesses the image dictionary containing file name
            and the pixel array representation of the image  
        """
        return self._metadata
    
    def _svsprocessor_object(self, image: object) -> dict:
        """ Method: _svsprocessor_object

            This method processes the 'SVSProcessor' object and returns the dictonary containing 
            the different images and the pixel array representation.
        """

        try:
            return image.pixel_array()
        except Exception as e:
            raise e
            
    def _svsprocessor_metadata(self, image: object) -> dict:
        """ Method: _svsprocessor_metadata

            This method processes the 'SVSProcessor' object and returns the dictonary containing 
            the image metadata associated with the image object.
        """

        try:
            return image.slide_metadata
        except Exception as e:
            raise e

    def pyramid_file(self, filename, pixel_data, image_metadata):
        """ Method: pyramid_file

            This method generates a single pyramid TIFF file.
        """

        subresolutions = 2
        pixelsize = 0.29

        with TiffWriter(f'{filename}.tiff') as tif:
            metadata = dict()
            
            metadata.update(TIFF_BASE_METADATA)

            for key, value in image_metadata.items():
                if value is None:
                    continue
                metadata.update({key: value})

            options = dict(
                photometric = 'rgb',
                compression='jpeg',

                tile=(
                    int(metadata.get("openslide.level[0].tile-height", 256)),
                    int(metadata.get("openslide.level[0].tile-width", 256))
                    ),

                resolutionunit=metadata.get("tiff.ResolutionUnit", 'CENTIMETER'),
                maxworkers=4,
            )

            print(type(pixel_data))

            tif.write(
                pixel_data,
                subfiletype=subresolutions,
                resolution=(1e4 / pixelsize, 1e4 / pixelsize),
                metadata=metadata,
                **options
            )

            

            

    def generate_pyramid(self):
        """ Method: generate_pyramid

            This method generates a pyramid TIFF file.
        """

        return self.image