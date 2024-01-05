from slidicom.preprocessing import SVSProcessor
from slidicom.pyramid import PyramidTIFFGenerator
import timeit

start = timeit.default_timer()
image = SVSProcessor("C:/Users/edger/OneDrive/Desktop/SVS158.svs", 1)

pixel = image.pixel_array()

pyramid = PyramidTIFFGenerator(pixel, 'svs')



images = pyramid.generate_pyramid()

for filename, im in images.items():
    pyramid.pyramid_file(filename, im, image.slide_metadata)

stop = timeit.default_timer()
print('Time: ', stop - start)