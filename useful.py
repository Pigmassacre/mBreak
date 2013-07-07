__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

# Store various useful classes in here, for now atleast.
import pygame
import math

def blend_colors(old_color, blend_color, blend_alpha=False):
	new_r = int(old_color.r * (blend_color.r / 255.0))
	new_g = int(old_color.g * (blend_color.g / 255.0))
	new_b = int(old_color.b * (blend_color.b / 255.0))

	if blend_alpha:
		new_a = old_color.a * (blend_color.a / 255.0)
	else:
		new_a = old_color.a

	return pygame.Color(new_r, new_g, new_b, new_a)

def colorize_image(image, new_color):
	# Unlock the surface so we can colorize it.
	image.lock()

	# Work through the pixelarray.
	pixelarray = pygame.PixelArray(image)
	for x in range(0, image.get_size()[0]):
		for y in range(0, image.get_size()[1]):
			# Get the current color.
			current_color = image.unmap_rgb(pixelarray[x, y])

			# Blend the colors.
			after_blend_color = blend_colors(current_color, new_color)

			# Map the new color the the pixelarray. For some reason, pixelarray apparently reverses the color after colorizing.
			# So we reverse the color order before adding it to the current pixel. (BGRA, instead of RGBA as it should be...)
			final_color = pygame.Color(after_blend_color.b, after_blend_color.g, after_blend_color.r, after_blend_color.a)
			pixelarray[x, y] = final_color

	# We're done, so lock the surface again.
	image.unlock()
