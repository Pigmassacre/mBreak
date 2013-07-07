__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import shadow
from libs import pyganim
from settings import *

class Logo:

	def __init__(self):
		self.logo = pyganim.PygAnimation([("res/logo/mBreakTitle_01.png", 1.00),
											("res/logo/mBreakTitle_02.png", 0.075),
											("res/logo/mBreakTitle_03.png", 0.075),
											("res/logo/mBreakTitle_04.png", 0.075),
											("res/logo/mBreakTitle_05.png", 0.075),
											("res/logo/mBreakTitle_06.png", 0.075),
											("res/logo/mBreakTitle_07.png", 0.075),
											("res/logo/mBreakTitle_01.png", 1.00),
											("res/logo/mBreakTitle_07.png", 0.075),
											("res/logo/mBreakTitle_06.png", 0.075),
											("res/logo/mBreakTitle_05.png", 0.075),
											("res/logo/mBreakTitle_04.png", 0.075),
											("res/logo/mBreakTitle_03.png", 0.075),
											("res/logo/mBreakTitle_02.png", 0.075)])
		self.x = 0
		self.y = 0

		# These are used for rotation the logo.
		self.current_angle = 0
		self.max_angle = 15
		self.min_angle = -15
		self.rotate_step = 0.40
		self.rotate_up = True
		self.current_scale = 8
		self.max_scale = 8.25
		self.min_scale = 7.75
		self.scale_by = 0.01
		self.scale_up = True

	def play(self):
		self.logo.play()

	def pause(self):
		self.logo.pause()

	def stop(self):
		self.logo.stop()

	def get_width(self):
		return self.logo.getMaxSize()[0]

	def get_height(self):
		return self.logo.getMaxSize()[1]

	def draw(self, window_surface):
		temp_logo_width = int(self.logo.getRect().width * self.current_scale)
		temp_logo_height = int(self.logo.getRect().height * self.current_scale)
		temp_logo = pygame.transform.scale(self.logo.getCurrentFrame(), (temp_logo_width, temp_logo_height))
		temp_logo = pygame.transform.rotate(temp_logo, self.current_angle)
		temp_logo_x = (SCREEN_WIDTH - temp_logo.get_width()) // 2
		temp_logo_y = ((SCREEN_HEIGHT - temp_logo.get_height()) // 2) - 30
		window_surface.blit(temp_logo, (temp_logo_x, temp_logo_y))
		
		if self.rotate_up:
			self.current_angle = self.current_angle + self.rotate_step
		else:
			self.current_angle = self.current_angle - self.rotate_step

		if self.current_angle > self.max_angle:
			self.current_angle = self.max_angle
			self.rotate_up = False
		elif self.current_angle < self.min_angle:
			self.current_angle = self.min_angle
			self.rotate_up = True

		if self.scale_up:
			self.current_scale = self.current_scale + self.scale_by
		else:
			self.current_scale = self.current_scale - self.scale_by

		if self.current_scale > self.max_scale:
			self.current_scale = self.max_scale
			self.scale_up = False
		elif self.current_scale < self.min_scale:
			self.current_scale = self.min_scale
			self.scale_up = True