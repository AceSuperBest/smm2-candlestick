from asset import *

asset_init()

# Create a new image
image = NumberGraphicsResources.create_number(-7729, 'red')

print(image.width, image.height)

# Save the image
image.save('test-number.png')
# image.show()