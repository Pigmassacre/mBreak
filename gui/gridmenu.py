__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import gui.menu as menu
from settings.settings import *

class GridMenu(menu.Menu):

	max_number_of_columns = 4
	offset = 9 * GAME_SCALE

	def __init__(self, x, y, position = 0):
		menu.Menu.__init__(self, x, y, position)

		self.max_number_of_columns = GridMenu.max_number_of_columns
		self.offset = GridMenu.offset
		self.current_row_size = 0
		self.current_row_position = self.y

	def add(self, item, function):
		self.items.append(item)	
		if len(self.items) > self.max_number_of_columns:
			self.current_row_size = 0
			self.current_row_position = self.current_row_position + item.get_height() + self.offset 
		elif len(self.items) > 1:
			last_item = self.items[-1]

			item.x = last_item.x + self.offset
			item.y = self.current_row_position
		else:
			item.x = self.x
			item.y = self.y

		self.current_row_size += 1

		self.clicked_outside[item] = False
		self.functions[item] = function

	def cleanup(self):
		for item in self.items:
			item.x = self.x - (item.get_width() / 2)
