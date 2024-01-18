from slidicom.preprocessing import SVSProcessor

# Specify the image location
IMAGE_FILE_PATH = "C:/Users/edger/OneDrive/Desktop/SVS158.svs"

# Create `SVSProcessor` object
wsi = SVSProcessor(IMAGE_FILE_PATH, 1)

# Image Height
print(f"Image height - {wsi.image_height}")

# Image Width
print(f"Image width - {wsi.image_width}")

# Getting the image pixel data
pixel_data = wsi.pixel_array()

# Checking to see the images that have been split
print(pixel_data.keys())

# Getting the image metadata
image_metadata = wsi.slide_metadata
print(image_metadata)

# Saving JPEG images to local disk
wsi.pixel_array(save=True)





