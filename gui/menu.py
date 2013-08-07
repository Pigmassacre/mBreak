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

		# This is the amount of items the menu will display in a row before generating a new column.
		self.max_number_of_rows = 3

		# Setup a dictionary that contains the functions that each item will call when activated.
		self.functions = {}

		# Store the last clicked button, so if we click a button and then hold down the mouse button it only registers as one click.
		self.last_clicked_item = None

		# We keep track if we clicked outside a button until we release the mouse button.
		self.clicked_outside = {}

		# Store the current position in the menu.
		self.position = 0
		
		# Store the coordinates so we know where to position the menu.
		self.x = x
		self.y = y

	def get_width(self):
		max_size = 0
		for item in self.items:
			if item.get_width() > max_size:
				max_size = item.get_width()
		return max_size

	def get_height(self):
		max_size = 0
		for item in self.items:
			if item.get_height() > max_size:
				max_size = item.get_height()
		return max_size

	def add(self, item, function):
		if len(self.items) > 0:
			last_item = self.items[-1]

			self.items.append(item)
			item.x = self.x - (item.get_width() / 2)
			item.y = last_item.y + (last_item.get_height() * 2)
		else:
			self.items.append(item)
			item.x = self.x - (item.get_width() / 2)
			item.y = self.y

		self.clicked_outside[item] = False
		self.functions[item] = function

	def cleanup(self):
		for item in self.items:
			item.x = self.x - (item.get_width() / 2)

	def remove(self, item):
		self.items.remove(item)

	def update(self):
		mouse_pos = pygame.mouse.get_pos()
		pressed_buttons = pygame.mouse.get_pressed()

		for item in self.items:
			item.selected = False

			# We want to ignore any "clicks" that occur if we hold the mouse button down and then move the cursor on top of the item.
			if pressed_buttons[0]:
				if not self.clicked_outside[item]:
					self.clicked_outside[item] = not self.is_mouse_over_item(item, mouse_pos)
			else:
				self.clicked_outside[item] = False
			
			if self.is_mouse_over_item(item, mouse_pos):
				item.selected = True
				if pressed_buttons[0] and not self.clicked_outside[item]:
					if not self.last_clicked_item == item:
						self.functions[item](item)
						self.last_clicked_item = item
				else:
					self.last_clicked_item = None

	def is_mouse_over_item(self, item, mouse_pos):
		x = mouse_pos[0]
		y = mouse_pos[1]

		return x >= item.x and x <= item.x + item.get_width() and y >= item.y and y <= item.y + item.get_height()

	def draw(self, surface):
		for item in self.items:
			item.draw(surface)