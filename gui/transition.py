__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import gui.menu as menu
import settings.settings as settings

"""

This class handles the menu transitions seen in all menus in the game.

The only limit this class works with is that each item given to it has an x and y position (stored as item.x and item.y in each item).
That's all the class needs to know of each item.

You can either add single items or every item in a given menu, and you should only ever need one instance of this class in each screen.
However, there's no harm in having multiple instances if you want to given them different names and/or make update them at different times.

"""

class Transition:

	# The standard speed value, used unless changed for the instance of this class.
	speed = 14 * settings.GAME_FPS * settings.GAME_SCALE

	def __init__(self, main_clock):
		# The speed at which each item moves.
		self.speed = Transition.speed

		# A list of all items registered to this transition object.
		self.items = []

		# This is used to store all the start positions of each item.
		self.start_positions = {}

		# Store the clock to be used when calculating movement.
		self.main_clock = main_clock

	def add_items(self, menu_to_add):
		"""
		Given a menu, adds all the items of that menu to our list of menus EXCEPT for those items that are already in our list of items.
		"""
		for item in menu_to_add.items:
			if not item in self.items:
				self.items.append(item)

	def remove_all_items(self):
		"""
		Simply removes all the items in this Transitions object.
		"""
		del(self.items[:])

	def setup_transition(self, menu_to_setup, left, right, up, down):
		"""
		Given a menu, calls add_items to populate the list of items in this Transition object and then, if the items don't already have
		a given start position, stores the items current positions as the start positions. It then assigns each item a random position
		outside the screen, either to the left or right of the screen, or above / below.
		"""
		choices = self.setup_choices(left, right, up, down)

		# Adds all the items to the list of items (if they already are in the list, they are not added).
		self.add_items(menu_to_setup)

		# We call cleanup to make sure that all the items in the menu is in the right position.
		menu_to_setup.cleanup()

		# For each item in the menu, picks a random position out of the list of available positions and assigns it to that item.
		for item in menu_to_setup.items:
			choice = random.choice(choices)
			if self.start_positions.get(item) == None:
				self.start_positions[item] = (item.x, item.y)
			if choice == "left":
				item.x = -item.get_width()
			elif choice == "right":
				item.x = settings.SCREEN_WIDTH
			elif choice == "up":
				item.y = -item.get_height()
			elif choice == "down":
				item.y = settings.SCREEN_HEIGHT

	def setup_odd_even_transition(self, menu_to_setup, left, right, up, down):
		"""
		Does the same as setup_transition, but when it assign the random positions it first assigns a random position and then alternates
		between assigning that position or the opposite to each item.

		So basically, if the assigned position is to the left of the screen, the next item is positioned to the right of the screen,
		the one after that to the left and so forth.
		"""
		choices = self.setup_choices(left, right, up, down)

		# Adds all the items to the list of items (if they already are in the list, they are not added).
		self.add_items(menu_to_setup)

		# We call cleanup to make sure that all the items in the menu is in the right position.
		menu_to_setup.cleanup()

		# Picks a random position out of the list of available positions, and alternates between assigning that position or the
		# opposite of that position to each item.
		odd = random.choice([True, False])
		choice = random.choice(choices)
		for item in menu_to_setup.items:
			if self.start_positions.get(item) == None:
				self.start_positions[item] = (item.x, item.y)
			if odd:
				if choice == "left":
					item.x = -item.get_width()
				elif choice == "right":
					item.x = settings.SCREEN_WIDTH
				elif choice == "up":
					item.y = -item.get_height()
				elif choice == "down":
					item.y = settings.SCREEN_HEIGHT
			else:
				if choice == "left":
					item.x = settings.SCREEN_WIDTH
				elif choice == "right":
					item.x = -item.get_width()
				elif choice == "up":
					item.y = settings.SCREEN_HEIGHT
				elif choice == "down":
					item.y = -item.get_height()
			odd = not odd

	def setup_single_item_transition(self, item, left, right, up, down):
		"""
		Does the same as setup_transition, but for just a single item.
		"""
		choices = self.setup_choices(left, right, up, down)

		# An alternate to this would be to call self.add_items([item]), but I'm not sure which method is the best. I think(?) this is more efficient...
		if not item in self.items:
			self.items.append(item)

		if self.start_positions.get(item) == None:
			self.start_positions[item] = (item.x, item.y)

		choice = random.choice(choices)
		if choice == "left":
			item.x = -item.get_width()
		elif choice == "right":
			item.x = settings.SCREEN_WIDTH
		elif choice == "up":
			item.y = -item.get_height()
		elif choice == "down":
			item.y = settings.SCREEN_HEIGHT

	def setup_choices(self, left, right, up, down):
		"""
		Simply returns a list the given choices, but mapped as strings instead of True/False values.
		"""
		choices = []
		if left:
			choices.append("left")
		if right:
			choices.append("right")
		if up:
			choices.append("up")
		if down:
			choices.append("down")
		return choices

	def update(self):
		"""
		In order for the actual transition to take place, call this method every frame. It takes care of moving
		each item closer (and eventually to) their start positions.
		"""
		for item in self.items:
			self.move_item_to_position(item, self.start_positions[item])

	def move_item_to_position(self, item, position):
		"""
		This does the actual moving of each item in the list of items. Moves each item with the speed variable,
		which can be changed at any time the user wants.
		"""
		if position[0] < item.x:
			if (item.x - self.speed * self.main_clock.delta_time) < position[0]:
				item.x = position[0]
			else:
				item.x -= self.speed * self.main_clock.delta_time
		elif position[0] > item.x:
			if (item.x + self.speed * self.main_clock.delta_time) > position[0]:
				item.x = position[0]
			else:
				item.x += self.speed * self.main_clock.delta_time

		if position[1] < item.y:
			if (item.y - self.speed * self.main_clock.delta_time) < position[1]:
				item.y = position[1]
			else:
				item.y -= self.speed * self.main_clock.delta_time
		elif position[1] > item.y:
			if (item.y + self.speed * self.main_clock.delta_time) > position[1]:
				item.y = position[1]
			else:
				item.y += self.speed * self.main_clock.delta_time