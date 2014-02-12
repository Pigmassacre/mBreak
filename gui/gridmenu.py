__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import gui.menu as menu
import settings.settings as settings

"""

This is a subclass of Menu that positions it's items in a grid (table) like fashion, instead of a vertical list like in Menu.
The user can specify the max number of columns, and the GridMenu takes care of positioning each of its items accordingly.

Other than that, it's a subclass of menu so it works pretty much like menu.

"""

class GridMenu(menu.Menu):

	offset = 2 * settings.GAME_SCALE

	def __init__(self, max_number_of_columns = 3, x = 0, y = 0, position = 0):
		# We call the superconstructor, ofcourse.
		menu.Menu.__init__(self, x, y, position)

		# This is the max number of items that are displayed next to each other before a new row is added.
		self.max_number_of_columns = max_number_of_columns

		# This is the offset between each item in the menu.
		self.offset = GridMenu.offset

		# We setup a few default variables.
		self.current_row_size = 0
		self.current_row_position = self.y

	def add(self, item, function):
		# This works almost exactly like the Menu function, but it positions the added items in a grid-like fashion. 
		self.items.append(item)
		self.current_row_size += 1

		# Populate the grid with the item, and store the new current row size and current row position.
		temp_size_pos = self.populate_grid(item, self.current_row_size, self.current_row_position)
		self.current_row_size = temp_size_pos[0]
		self.current_row_position = temp_size_pos[1]

		# Store the function for this item.
		self.functions[item] = function

	def populate_grid(self, item, row_size, row_position):
		# Populates the grid according to the max_number_of_columns.
		if row_size > self.max_number_of_columns:
			# If the row size is larger than the max number of columns, we position the item below the last row and at the beginning of the new row.
			row_size = 1
			row_position = row_position + item.get_height() + self.offset

		if row_size > 1:
			# If the row size is larger than one, we position the item to the right of the last item in the last row.
			item.x = self.x + (row_size - 1) * item.get_width() + (row_size - 1) * self.offset
			item.y = row_position
		else:
			# Otherwise, we position the item to the beginning of the row.
			item.x = self.x
			item.y = row_position

		# We return the changed row_size and row_position.
		return (row_size, row_position)

	def cleanup(self):
		# Repositions all the items in the gridmenu.
		temp_row_size = 0
		temp_row_position = self.y

		for item in self.items:
			temp_row_size += 1
			temp_size_pos = self.populate_grid(item, temp_row_size, temp_row_position)
			temp_row_size = temp_size_pos[0]
			temp_row_position = temp_size_pos[1]
				