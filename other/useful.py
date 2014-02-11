__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *
import math
from itertools import chain

"""

This module contains a few useful methods to deal with colors.

"""

def create_frames_from_sheet(sheet, frame_width, frame_height, frame_duration = None):
	frames = []
	for i in range(0, sheet.get_height(), frame_height):
		frame_surface = pygame.surface.Surface((frame_width, frame_height), SRCALPHA)
		frame_surface.blit(sheet, (0, -i))
		if frame_duration is None:
			frames.append(frame_surface)
		else:
			frames.append((frame_surface, frame_duration))
	return frames
 
 # Shamelessly stolen from http://www.pygame.org/wiki/TextWrapping
 # It doesn't say who the author is, so, eh, thanks to her/him for
 # saving me some headache!
def truncline(text, font, maxwidth):
    real=len(text)       
    stext=text           
    l=font.size(text)[0]
    cut=0
    a=0                  
    done=1
    old = None
    while l > maxwidth:
        a=a+1
        n=text.rsplit(None, a)[0]
        if stext == n:
            cut += 1
            stext= n[:-cut]
        else:
            stext = n
        l=font.size(stext)[0]
        real=len(stext)               
        done=0                        
    return real, done, stext             
        
def wrapline(text, font, maxwidth): 
    done=0                      
    wrapped=[]                  
                               
    while not done:             
        nl, done, stext=truncline(text, font, maxwidth) 
        wrapped.append(stext.strip())                  
        text=text[nl:]                                 
    return wrapped
 
def wrap_multi_line(text, font, maxwidth):
    """
    Returns text taking new lines into account.
    """
    lines = chain(*(wrapline(line, font, maxwidth) for line in text.splitlines()))
    return list(lines)

def tint_surface(surface):
	"""
	Given a surface, returns the same surface tinted a bit darker.
	"""
	tint_color = pygame.Color(0, 0, 0, 200)
	tint_surface = pygame.Surface((surface.get_width(), surface.get_height()), SRCALPHA)
	tint_surface.fill(tint_color)
	surface.blit(tint_surface, (0, 0))

def blend_colors(old_color, blend_color, blend_alpha = False):
	"""
	Given two colors, an old_color and a blend_color, this returns a new color that is the old_color blended
	with the blend_color. If the optional blend_alpha parameter is set to True, the alpha value of both colors
	is also blended.
	"""
	new_r = int(old_color.r * (blend_color.r / 255.0))
	new_g = int(old_color.g * (blend_color.g / 255.0))
	new_b = int(old_color.b * (blend_color.b / 255.0))

	if blend_alpha:
		new_a = int(old_color.a * (blend_color.a / 255.0))
	else:
		new_a = old_color.a

	return pygame.Color(new_r, new_g, new_b, new_a)

def colorize_image(image, new_color, blend_alpha = False, bgr = True):
	"""
	Given an image and a new_color, this method colors the image with the new_color.
	If the optional parameter blend_alpha is True, the alpha value is blended too.
	"""
	# Lock the surface so we can colorize it.
	image.lock()

	# Work through the pixelarray.
	pixelarray = pygame.PixelArray(image)
	for x in range(0, image.get_size()[0]):
		for y in range(0, image.get_size()[1]):
			# Get the current color.
			current_color = image.unmap_rgb(pixelarray[x, y])

			# Blend the colors.
			after_blend_color = blend_colors(current_color, new_color, blend_alpha)

			# Map the new color the the pixelarray.
			if bgr:
				# For some reason, pixelarray apparently reverses the color after colorizing.
				# So we reverse the color order before adding it to the current pixel. (BGRA, instead of RGBA as it should be...)
				final_color = pygame.Color(after_blend_color.b, after_blend_color.g, after_blend_color.r, after_blend_color.a)
			else:
				final_color = pygame.Color(after_blend_color.r, after_blend_color.g, after_blend_color.b, after_blend_color.a)	
			pixelarray[x, y] = final_color

	# We're done, so unlock the surface again.
	image.unlock()
