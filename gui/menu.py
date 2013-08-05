__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
from settings.settings import *

class Menu:

	def __init__(self, x, y, position = 0):
		# Setup a list to contain all the menu items.
		self.items = []

		# Setup a dictionary that contains the functions that each item will call when activated.
		self.functions = {}

		# Store the current position in the menu.
		self.position = 0
		
		# Store the coordinates so we know where to position the menu.
		self.x = x
		self.y = y

	def add(self, item, function):
		if len(self.items) > 0:
			last_item = self.items[len(self.items) - 1]

			self.items.append(item)
			item.x = self.x - (item.get_width() / 2)
			item.y = last_item.y + (last_item.get_height() * 2)
		else:
			self.items.append(item)
			item.x = self.x - (item.get_width() / 2)
			item.y = self.y

		self.functions[item] = function

	def remove(self, item):
		self.items.remove(item)

	def update(self):
		mouse_pos = pygame.mouse.get_pos()
		pressed_buttons = pygame.mouse.get_pressed()

		for item in self.items:
			if self.is_mouse_over_item(item, mouse_pos):
				if pressed_buttons[0]:
					self.functions[item]()

	def is_mouse_over_item(self, item, mouse_pos):
		x = mouse_pos[0]
		y = mouse_pos[1]

		return x >= item.x and x <= item.x + item.get_width() and y >= item.y and y <= item.y + item.get_height()

	def draw(self, surface):
		for item in self.items:
			item.draw(surface)