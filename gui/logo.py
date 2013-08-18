__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
from libs import pyganim
import settings.settings as settings

"""

This class is used to create and display the animated mBreak logo. It can be positioned anywhere, played, stopped, paused
and anything you could possibly want. It's mostly a wrapper around the nice pyganim library (credits and license and
stuff like that are in the readme.txt).

"""

class Logo:

	# Scale the actual logo image by this value.
	scale = 2

	# Sets the default position to the top-left corner.
	x = 0
	y = 0

	# Creates a pyganim object from the logo images. 
	logo = pyganim.PygAnimation([("res/logo/mBreakTitle_01.png", 1.55),
								("res/logo/mBreakTitle_02.png", 0.075),
								("res/logo/mBreakTitle_03.png", 0.075),
								("res/logo/mBreakTitle_04.png", 0.075),
								("res/logo/mBreakTitle_05.png", 0.075),
								("res/logo/mBreakTitle_06.png", 0.075),
								("res/logo/mBreakTitle_07.png", 0.075),
								("res/logo/mBreakTitle_01.png", 1.55),
								("res/logo/mBreakTitle_07.png", 0.075),
								("res/logo/mBreakTitle_06.png", 0.075),
								("res/logo/mBreakTitle_05.png", 0.075),
								("res/logo/mBreakTitle_04.png", 0.075),
								("res/logo/mBreakTitle_03.png", 0.075),
								("res/logo/mBreakTitle_02.png", 0.075)])

	def __init__(self):
		# Store a copy of the pyganim object.
		self.logo = Logo.logo.getCopy()

		# Set the current scale of the object to the standard scale (also scaled by settings.GAME_SCALE).
		self.current_scale = Logo.scale * settings.GAME_SCALE

		# Store the default position values.
		self.x = Logo.x
		self.y = Logo.y

	def play(self):
		# Wraps to pyganims play function.
		self.logo.play()

	def pause(self):
		# Wraps to pyganims pause function.
		self.logo.pause()

	def stop(self):
		# Wraps to pyganims stop function.
		self.logo.stop()

	def get_width(self):
		# Returns the maximum width of the logo, scaled by the current scale.
		return self.logo.getMaxSize()[0] * self.current_scale

	def get_height(self):
		# Returns the maximum height of the logo, scaled by the current scale.
		return self.logo.getMaxSize()[1] * self.current_scale

	def draw(self, window_surface):
		# Position the logo. We also scale the current frame to the current scale every time draw is called.
		# Arguably this is performance hog, but it works pretty good so...
		temp_logo = pygame.transform.scale(self.logo.getCurrentFrame(), (self.get_width(), self.get_height()))
		temp_logo_x = self.x
		temp_logo_y = self.y

		# Draw the logo.
		window_surface.blit(temp_logo, (temp_logo_x, temp_logo_y))