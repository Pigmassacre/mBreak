__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

# Store various useful classes in here, for now atleast.
import pygame
from libs import pyganim

class TextItem:

	def __init__(self, text_value, font_path, font_size, font_color, alpha_value):
		self.text_value = text_value
		self.font = pygame.font.Font(font_path, font_size)
		self.surface = self.font.render(text_value, False, font_color)
		self.surface.set_alpha(alpha_value)

	def get_width(self):
		return self.font.size(self.text_value)[0]

	def get_height(self):
		return self.font.size(self.text_value)[1]

	def blink(self, time_passed, blink_rate):
		"""
		If called once per loop, switches the target surface alpha value between 255 and 0 every blink_rate.
		The surface spends 2/3s of the time with alpha value 0 as with 255.
		"""
		if time_passed > blink_rate:
			if self.surface.get_alpha() == 255:
				self.surface.set_alpha(0)
				return blink_rate // 3
			else:
				self.surface.set_alpha(255)
				return 0
		else:
			return time_passed

class Logo:

	def __init__(self):
		self.logo = pyganim.PygAnimation([("res/mBreakTitle_01.png", 1.00),
											("res/mBreakTitle_02.png", 0.075),
											("res/mBreakTitle_03.png", 0.075),
											("res/mBreakTitle_04.png", 0.075),
											("res/mBreakTitle_05.png", 0.075),
											("res/mBreakTitle_06.png", 0.075),
											("res/mBreakTitle_07.png", 0.075),
											("res/mBreakTitle_01.png", 1.00),
											("res/mBreakTitle_07.png", 0.075),
											("res/mBreakTitle_06.png", 0.075),
											("res/mBreakTitle_05.png", 0.075),
											("res/mBreakTitle_04.png", 0.075),
											("res/mBreakTitle_03.png", 0.075),
											("res/mBreakTitle_02.png", 0.075)])

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