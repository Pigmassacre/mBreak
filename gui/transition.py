__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import gui.menu as menu
from settings.settings import *

class Transition():

	def __init__(self, speed = 44):
		self.speed = speed
		
	def setup_all_sides_transition(self, menu_to_setup):
		self.start_positions = {}
		menu_to_setup.cleanup()
		for item in menu_to_setup.items:
			self.start_positions[item] = (item.x, item.y)
			if random.choice([True, False]):
				if random.choice([True, False]):
					item.x = SCREEN_WIDTH
				else:
					item.x = -item.get_width()
			else:
				item.y = SCREEN_HEIGHT

	def setup_left_right_transition(self, menu_to_setup):
		self.start_positions = {}
		menu_to_setup.cleanup()
		odd = random.choice([True, False])
		for item in menu_to_setup.items:
			self.start_positions[item] = (item.x, item.y)
			if odd:
				item.x = SCREEN_WIDTH
			else:
				item.x = -item.get_width()
			odd = not odd

	def handle_menu_transition(self, menu_to_handle):
		for item in menu_to_handle.items:
			self.move_item_to_position(item, self.start_positions[item])

	def move_item_to_position(self, item, position):
		if position[0] < item.x:
			if (item.x - self.speed) < position[0]:
				item.x = position[0]
			else:
				item.x -= self.speed
		elif position[0] > item.x:
			if (item.x + self.speed) > position[0]:
				item.x = position[0]
			else:
				item.x += self.speed

		if position[1] < item.y:
			if (item.y - self.speed) < position[1]:
				item.y = position[1]
			else:
				item.y -= self.speed
		elif position[1] > item.y:
			if (item.y + self.speed) > position[1]:
				item.y = position[1]
			else:
				item.y += self.speed