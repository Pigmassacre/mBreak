__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import gui.menu as menu
from settings.settings import *

class GridMenu(menu.Menu):

	max_number_of_columns = 3
	offset = 2 * GAME_SCALE

	def __init__(self, x, y, position = 0):
		menu.Menu.__init__(self, x, y, position)

		self.max_number_of_columns = GridMenu.max_number_of_columns
		self.offset = GridMenu.offset
		self.current_row_size = 0
		self.current_row_position = self.y

	def get_width(self):
		max_x = 0
		for item in self.items:
			if item.x > max_x:
				max_x = item.x + item.get_width()
		return max_x - self.x

	def get_height(self):
		max_y = 0
		for item in self.items:
			if item.y > max_y:
				max_y = item.y + item.get_width()
		return max_y - self.y

	def add(self, item, function):
		self.items.append(item)
		self.current_row_size += 1

		temp_size_pos = self.populate_grid(item, self.current_row_size, self.current_row_position)
		self.current_row_size = temp_size_pos[0]
		self.current_row_position = temp_size_pos[1]

		self.clicked_outside[item] = False
		self.functions[item] = function

	def populate_grid(self, item, row_size, row_position):
		if row_size > self.max_number_of_columns:
			row_size = 1
			row_position = row_position + item.get_height() + self.offset

		if row_size > 1:
			item.x = self.x + (row_size - 1) * item.get_width() + (row_size - 1) * self.offset
			item.y = row_position
		else:
			item.x = self.x
			item.y = row_position

		return (row_size, row_position)

	def cleanup(self):
		temp_row_size = 0
		temp_row_position = self.y

		for item in self.items:
			temp_row_size += 1
			temp_size_pos = self.populate_grid(item, temp_row_size, temp_row_position)
			temp_row_size = temp_size_pos[0]
			temp_row_position = temp_size_pos[1]