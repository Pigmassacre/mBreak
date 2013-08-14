__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import gui.menu as menu
import settings.settings as settings

class Transition:

	speed = 14 * settings.GAME_SCALE

	def __init__(self):
		# The speed at which each item moves.
		self.speed = Transition.speed

		# A list of all items registered to this transition object.
		self.items = []

		# This is used to store all the start positions of each item.
		self.start_positions = {}

	def add_items(self, menu_to_add):
		for item in menu_to_add.items:
			if not item in self.items:
				self.items.append(item)

	def setup_transition(self, menu_to_setup, left, right, up, down):
		choices = self.setup_choices(left, right, up, down)

		self.add_items(menu_to_setup)

		menu_to_setup.cleanup()

		for item in menu_to_setup.items:
			choice = random.choice(choices)
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
		choices = self.setup_choices(left, right, up, down)

		self.add_items(menu_to_setup)

		menu_to_setup.cleanup()

		odd = random.choice([True, False])
		choice = random.choice(choices)
		for item in menu_to_setup.items:
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
		choices = self.setup_choices(left, right, up, down)

		if not item in self.items:
			self.items.append(item)

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
		for item in self.items:
			self.move_item_to_position(item, self.start_positions[item])

	def move_item_to_position(self, item, position):
		if position[0] < item.x:
			if (item.x - self.speed) < position[0]:
				item.x = position[0]
			else:
				item.x -= self.speed
		elif position[0] > item.x:
			if (item.x + self.speed) > position[0]:
				item.x = position[0]
			else:
				item.x += self.speed

		if position[1] < item.y:
			if (item.y - self.speed) < position[1]:
				item.y = position[1]
			else:
				item.y -= self.speed
		elif position[1] > item.y:
			if (item.y + self.speed) > position[1]:
				item.y = position[1]
			else:
				item.y += self.speed