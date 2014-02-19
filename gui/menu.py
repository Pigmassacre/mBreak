__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import settings.settings as settings

"""

This is the base menu class. It can be placed anywhere in the game screen, and if items (textitems, imageitems, coloritems, choiceitems etc)
are added to it those items are displayed in a top to bottom fashion. It can also register a function to each item so that when that item is
clicked the corresponding function is called.

"""

class Menu(object):

	# Initialize the mixer (so we can load a sound) and load the sound effect.
	pygame.mixer.init(44100, -16, 2, 2048)
	sound_effect = pygame.mixer.Sound("res/sounds/select.ogg")

	def __init__(self, x = 0, y = 0, position = 0):
		# Setup a list to contain all the menu items.
		self.items = []

		# We use this list to make sure that only one menu ever has a selected item.
		self.other_menus = []

		# Setup a dictionary that contains the functions that each item will call when activated.
		self.functions = {}

		# We keep track of the previously selected item so we know when to play a sound effect.
		self.previous_selected_item = None

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
		# Add the item to our list of items.
		self.items.append(item)

		# Register the item with the given function to the functions dictionary.
		self.functions[item] = function

		self.position_item(item)

	def position_item(self, item):
		pass

	def remove(self, item):
		# Remves the given item from the menu.
		self.items.remove(item)

	def cleanup(self):
		# Repositions all the items in the menu.
		for item in self.items:
			self.position_item(item)

	def register_other_menus(self, other_menus):
		# Register the other menus into our own list of other menus.
		if not other_menus in self.other_menus:
			# We don't want to register ourself, so we filter ourself out with an anonymous function.
			self.other_menus.extend(filter(lambda x: x != self, other_menus))

	def is_mouse_over_item(self, item, mouse_pos):
		# Returns True if the given mouse_pos is inside the given item.
		x = mouse_pos[0]
		y = mouse_pos[1]
		return x >= item.x and x <= item.x + item.get_width() and y >= item.y and y <= item.y + item.get_height()

	def update(self, main_clock):
		# We use this list to figure out if no items are selected
		selected_items = []

		for item in self.items:
			# Call the items update method.
			item.update(main_clock)

			# If the item is selected but we still haven't played a sound effect, do so.
			if item.selected:
				selected_items.append(item)
				if item != self.previous_selected_item:
					# If the item differs from the previously selected item, it must mean it's a newly selected item.
					# So, we play a sound effect and then set this item as the previously selected item, so we won't play
					# a sound effect again unless a new item is selected.
					sound = Menu.sound_effect.play()
					if not sound is None:
						sound.set_volume(settings.SOUND_VOLUME)
					self.previous_selected_item = item

		# If there is no selected item in this menu, reset the previous selected item.
		if len(selected_items) == 0:
			self.previous_selected_item = None

	def draw(self, surface):
		# Simply draws all the items of this menu to the given surface.
		for item in self.items:
			item.draw(surface)