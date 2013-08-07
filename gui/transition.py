__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import gui.menu as menu
from settings.settings import *

class Transition():

	def __init__(self, speed):
		self.speed = speed

	def setup_menu_transition(self, menu_to_setup):
		self.start_positions = {}
		menu_to_setup.cleanup()
		for item in menu_to_setup.items:
			self.start_positions[item] = item.x
			if random.choice([True, False]):
				item.x = SCREEN_WIDTH
			else:
				item.x = -item.get_width()

	def handle_menu_transition(self, menu_to_handle):
		for item in menu_to_handle.items:
			if self.start_positions[item] < item.x:
				if (item.x - self.speed) < self.start_positions[item]:
					item.x = self.start_positions[item]
				else:
					item.x -= self.speed
			elif self.start_positions[item] > item.x:
				if (item.x + self.speed) > self.start_positions[item]:
					item.x = self.start_positions[item]
				else:
					item.x += self.speed