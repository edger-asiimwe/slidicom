from slidicom.preprocessing import TileCordinate

class ImageCordinates:
    def __init__(self, imageCord, parent_filename):
        self._imageCord = imageCord
        self._parent_filename = parent_filename
        self.image_filename = self._image_filename()
        self.tile_cordinates = self._tile_image_index()

    def _image_filename(self):
        return "{0}_{1}_{2}".format(self._parent_filename, self._imageCord.image[0], self._imageCord.image[1])
    
    def image_width(self):
        return (self._imageCord.x2 - self._imageCord.x1) * 256

    def image_height(self):
        return (self._imageCord.y3 - self._imageCord.y1) * 256
    
    def _tile_image_index(self):
        return [ (x, y) for y in range(self._imageCord.y1, self._imageCord.y3) for x in range(self._imageCord.x1, self._imageCord.x2)]
    
    def _tile_cordinates(self):
        return TileCordinate(self._image_filename(), self._tile_image_index())