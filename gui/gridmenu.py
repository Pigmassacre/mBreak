__author__ = "Olof Karlsson"
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
		self.cleanup()
		min_x = 99999
		max_x = 0
		for item in self.items:
			if item.x < min_x:
				min_x = item.x
			if item.x + item.get_width() > max_x:
				max_x = item.x + item.get_width()
		return max_x - min_x

	def get_height(self):
		self.cleanup()
		min_y = 99999
		max_y = 0
		for item in self.items:
			if item.y < min_y:
				min_y = item.y
			if item.y + item.get_height() > max_y:
				max_y = item.y + item.get_height()
		return max_y - min_y

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