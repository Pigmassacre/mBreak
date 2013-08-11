__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
from libs import pyganim
import settings.settings as settings

class Logo:

	# Scale the actual logo image by this value.
	scale = 2

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
		self.logo = Logo.logo.getCopy()

		self.current_scale = Logo.scale * settings.GAME_SCALE

		self.x = 0
		self.y = 0

	def play(self):
		self.logo.play()

	def pause(self):
		self.logo.pause()

	def stop(self):
		self.logo.stop()

	def get_width(self):
		return self.logo.getMaxSize()[0] * self.current_scale

	def get_height(self):
		return self.logo.getMaxSize()[1] * self.current_scale

	def draw(self, window_surface):
		# Position the logo.
		temp_logo = pygame.transform.scale(self.logo.getCurrentFrame(), (self.get_width(), self.get_height()))
		temp_logo_x = self.x
		temp_logo_y = self.y

		# Draw the logo.
		window_surface.blit(temp_logo, (temp_logo_x, temp_logo_y))