__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import settings.settings as settings

"""

This is the base menu class. It can be placed anywhere in the game screen, and if items (textitems, imageitems, coloritems, choiceitems etc)
are added to it those items are displayed in a top to bottom fashion. It can also register a function to each item so that when that item is
clicked the corresponding function is called.

"""

class Menu:

	# Initialize the mixer (so we can load a sound) and load the sound effect.
	pygame.mixer.init(44100, -16, 2, 2048)
	sound_effect = pygame.mixer.Sound("res/sounds/select.ogg")

	def __init__(self, x = 0, y = 0, position = 0):
		# Setup a list to contain all the menu items.
		self.items = []

		# We use this list to make sure that only one menu ever has a selected item.
		self.other_menus = []

		# This is the amount of items the menu will display in a row before generating a new column.
		self.max_number_of_rows = 3

		#self.current_row_size = 0

		# Setup a dictionary that contains the functions that each item will call when activated.
		self.functions = {}

		# We keep track of the previously selected item so we know when to play a sound effect.
		self.previous_selected_item = None

		# Store the last clicked button, so if we click a button and then hold down the mouse button it only registers as one click.
		self.last_clicked_item = None

		# We keep track of if we clicked outside a button until we release the mouse button.
		self.clicked_outside = {}

		# Store the current position in the menu.
		self.position = 0
		
		# Store the coordinates so we know where to position the menu.
		self.x = x
		self.y = y

	def get_width(self):
		# Returns the distance between the lowest x-value and the highest x-value out of all items in the menu.
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
		# Returns the distance between the lowest y-value and the highest y-value out of all items in the menu.
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
		# Given an item and a function, this adds that item to this menu and registers a function to our
		# function dictionary with that item as the key.
		if len(self.items) > 0:
			# If the added item is anything but the first item, place it below the last item in the menu.
			last_item = self.items[-1]

			self.items.append(item)
			item.x = self.x - (item.get_width() / 2)
			item.y = last_item.y + (last_item.get_height() * 2)
		else:
			# If it is the first item in the menu, place it at the top of the menu.
			self.items.append(item)
			item.x = self.x - (item.get_width() / 2)
			item.y = self.y

		# Register the item to the clicked_outside and functions dictionaries.
		self.clicked_outside[item] = False
		self.functions[item] = function

	def remove(self, item):
		# Remves the given item from the menu.
		self.items.remove(item)

	def cleanup(self):
		# Repositions all the items in the menu.
		for item in self.items:
			item.x = self.x - (item.get_width() / 2)
			item.y = self.y + ((item.get_height() * 2) * self.items.index(item))

	def register_other_menus(self, other_menus):
		# Register the other menus into our own list of other menus.
		if not other_menus in self.other_menus:
			# We don't want to register ourself, so we filter ourself out with an anonymous function.
			self.other_menus.extend(filter(lambda x: x != self, other_menus))

	def update(self, main_clock):
		# We store the current mouse position and the state of the mouse buttons in order to figure out if an item
		# is selected / clicked on by the mouse.
		mouse_pos = pygame.mouse.get_pos()
		pressed_buttons = pygame.mouse.get_pressed()

		# We use this list to figure out if no items are selected
		selected_items = []

		for item in self.items:
			# Call the items update method.
			item.update(main_clock)
		
			# We want to ignore any "clicks" that occur if we hold the mouse button down and then move the cursor on top of the item.
			if pressed_buttons[0]:
				# If the left mouse button is clicked...
				if not self.clicked_outside[item]:
					# And we haven't clicked outside this item, we set the clicked_outside value for this item
					# to either True if the mouse is outside this item, or False otherwise.
					self.clicked_outside[item] = not self.is_mouse_over_item(item, mouse_pos)
			else:
				# If the left mouse button isn't clicked, well then there surely wasn't a click outside this item, so we set the
				# clicked outside value for this item to False.
				self.clicked_outside[item] = False

			if self.is_mouse_over_item(item, mouse_pos):
				# If the mouse cursor is over this item...
				for another_item in self.items:
					# We unselect all the other items.
					another_item.selected = False
				# And set this item to be selected.
				item.selected = True
				if pressed_buttons[0] and not self.clicked_outside[item]:
					# If the left mouse button is clicked, and we haven't clicked outside the item and then moved the mouse cursor
					# on top of the item without letting go of the mouse button...
					if not self.last_clicked_item == item:
						# We call the matching function, and set this item as the last clicked item.
						self.functions[item](item)
						self.last_clicked_item = item
				else:
					# If the mouse cursor isn't over any item, we set the last clicked item to be None.
					self.last_clicked_item = None

			# If the item is selected but we still haven't played a sound effect, do so.
			if item.selected:
				# Unselect all other items in the other menus.
				for other_menu in self.other_menus:
					for an_item in other_menu.items:
						an_item.selected = False
				selected_items.append(item)
				if item != self.previous_selected_item:
					# If the item differs from the previously selected item, it must mean it's a newly selected item.
					# So, we play a sound effect and then set this item as the previously selected item, so we won't play
					# a sound effect again unless a new item is selected.
					Menu.sound_effect.play()
					self.previous_selected_item = item

		# If there is no selected item in this menu, reset the previous selected item.
		if len(selected_items) == 0:
			self.previous_selected_item = None

	def is_mouse_over_item(self, item, mouse_pos):
		# Returns True if the given mouse_pos is inside the given item.
		x = mouse_pos[0]
		y = mouse_pos[1]
		return x >= item.x and x <= item.x + item.get_width() and y >= item.y and y <= item.y + item.get_height()

	def draw(self, surface):
		# Simply draws all the items of this menu to the given surface.
		for item in self.items:
			item.draw(surface)