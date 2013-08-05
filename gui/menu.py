__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
from settings.settings import *

class Menu:

	def __init__(self, x, y, position = 0):
		# Setup a list to contain all the menu items.
		self.menu_list = []

		# Store the current position in the menu.
		self.position = 0
		
		# Store the coordinates so we know where to position the menu.
		self.x = x
		self.y = y

	def add(self, item):
		if len(self.menu_list) > 0:
			last_item = self.menu_list[len(self.menu_list) - 1]
			print(str(len(self.menu_list) - 1))
			self.menu_list.append(item)
			item.x = self.x - (item.get_width() / 2)
			item.y = last_item.y + (last_item.get_height() * 2)
		else:
			self.menu_list.append(item)
			item.x = self.x - (item.get_width() / 2)
			item.y = self.y

	def remove(self, item):
		self.menu_list.remove(item)

	#def update(self):


	def draw(self, surface):
		for item in self.menu_list:
			item.draw(surface)