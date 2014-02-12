__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import settings.settings as settings

class Item():

	def __init__(self):
		self.y_nudge = 0
		self.time_passed = 0
		
	def update(self, main_clock):
		if self.selected:
			self.y_nudge = -((math.sin(self.time_passed * 0.0075) + 1) / 2.0) * 1.5 * settings.GAME_SCALE
			self.time_passed += main_clock.get_time()
		else:
			self.time_passed = 0
			self.y_nudge = 0
			
	def draw(self, surface):
		pass