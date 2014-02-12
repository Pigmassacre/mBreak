__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import settings.settings as settings

class Item():

	def __init__(self):
		self.y_nudge = 0
		self.y_nudge_retreat_speed = 0.1 * settings.GAME_FPS * settings.GAME_SCALE
		self.time_passed = 0
		
	def update(self, main_clock):
		if self.selected:
			self.y_nudge = -((math.sin(self.time_passed * 0.0075) + 1) / 2.0) * 2 * settings.GAME_SCALE
			self.time_passed += main_clock.get_time()
		else:
			self.time_passed = 0
			if self.y_nudge < 0:
				self.y_nudge += self.y_nudge_retreat_speed * main_clock.delta_time
				if self.y_nudge > 0:
					self.y_nudge = 0
			elif self.y_nudge > 0:
				self.y_nudge -= self.y_nudge_retreat_speed * main_clock.delta_time
				if self.y_nudge < 0:
					self.y_nudge = 0
			
	def draw(self, surface):
		pass