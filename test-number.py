from asset import *

asset_init()

# Create a new image
image = NumberGraphicsResources.create_number(-7729, 'red')

# Save the image
image.save('test-text-with-outline.png')
# image.show()