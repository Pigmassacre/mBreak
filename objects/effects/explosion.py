__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import other.useful as useful
from libs import pyganim
import objects.camera as camera
import objects.groups as groups
import objects.effects.effect as effect
import settings.settings as settings

"""

Simple on-hit effect.

"""

def convert():
	# We put this here so the game-class can call this method to "preload" the image used for this powerup.
	# I could probably put this in the constructor of the powerup, but I worry about performance so I make sure to only do it once.
	Explosion.image_sheet.convert_alpha()

class Explosion(effect.Effect):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image_sheet = pygame.image.load("res/effect/explosion.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image_sheet.get_width() * (settings.GAME_SCALE + 1)
	height = image_sheet.get_height() * (settings.GAME_SCALE + 1)
	frame_width = width
	frame_height = width

	# Scale image to settings.GAME_SCALE.
	image_sheet = pygame.transform.scale(image_sheet, (width, height))

	def __init__(self, parent, duration = 1000):
		# We start by calling the superconstructor.
		effect.Effect.__init__(self, parent, duration)

		# Generate the animation frames.
		frames = useful.create_frames_from_sheet(Explosion.image_sheet, Explosion.frame_width, Explosion.frame_height, 0.06)

		# Create the pyganim object.
		self.animation = pyganim.PygAnimation(frames, False)

		# Start playing the animation!
		self.animation.play()

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		# Update the playback rate of the animation.
		self.animation.rate = main_clock.time_scale

		# If the animation is finished, we destroy ourselves.
		if self.animation.isFinished():
			self.destroy()

	def draw(self, surface):
		# Draw the current frame of the animation.
		self.animation.blit(surface, (self.parent.rect.x - camera.CAMERA.x, self.parent.rect.y - camera.CAMERA.y))