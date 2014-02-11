__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import settings.settings as settings

class Item():

	def __init__(self):
		self.y_nudge = 0

	def draw(self, surface):
		if self.selected:
			#self.y_nudge = -2 * settings.GAME_SCALE
			self.y_nudge = -((math.sin(pygame.time.get_ticks() * 0.0075) + 1) / 2.0) * 1.5 * settings.GAME_SCALE
		else:
			self.y_nudge = 0