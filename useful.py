__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

# Store various useful classes in here, for now atleast.
import pygame
import math

def colorize_image(image, new_color):
	# Unlock the surface so we can colorize it.
	image.lock()

	# Work through the pixelarray.
	pixelarray = pygame.PixelArray(image)
	for x in range(0, image.get_size()[0]):
		for y in range(0, image.get_size()[1]):
			# Get the current color.
			current_color = image.unmap_rgb(pixelarray[x, y])

			# Colorize R
			current_color.r = current_color.r * (new_color.r / 255)

			# Colorize G
			current_color.g = current_color.g * (new_color.g / 255)

			# Colorize B
			current_color.b = current_color.b * (new_color.b / 255)

			# Map the new color the the pixelarray. For some reason, pixelarray apparently reverses the color after colorizing.
			# So we reverse the color order before adding it to the current pixel. (BGRA, instead of RGBA as it should be...)
			final_color = pygame.Color(current_color.b, current_color.g, current_color.r, current_color.a)
			pixelarray[x, y] = final_color

	# We're done, so lock the surface again.
	image.unlock()
