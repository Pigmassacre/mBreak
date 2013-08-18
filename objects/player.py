__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import objects.groups as groups
import objects.ball as ball
import objects.powerups.powerup as powerup
from pygame.locals import *
import settings.settings as settings

class Player(pygame.sprite.Sprite):

	def __init__(self, x, y, name, key_up, key_down, color):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Store the x and y position. This is used to display the list of powerups the player currently has.
		self.x = x
		self.y = y

		# The name is dislayed at the end of each match/game.
		self.name = name

		# Key up and down are, ofcourse, the keys that any paddles connected to this player will respond to.
		self.key_up = key_up
		self.key_down = key_down

		# Create and store the paddle.
		self.paddle_group = pygame.sprite.Group()

		# Create a group to store balls in.
		self.ball_group = pygame.sprite.Group()

		# Create a group to store blocks in.
		self.block_group = pygame.sprite.Group()

		# Create a group to store effects in.
		self.effect_group = pygame.sprite.Group()

		# Store the player in the main player_group.
		groups.Groups.player_group.add(self)

		# Create a OrdereredUpdates group used to store and display the powerups currently on this player.
		self.powerup_group = pygame.sprite.OrderedUpdates()

		# This is used to determine if an item has been added or removed from the group.
		self.last_powerup_group_size = len(self.powerup_group)

		# The offset between each powerup.
		self.powerup_offset = 2 * settings.GAME_SCALE

		# Store the selected color, used to colorize objects that belong to the player.
		self.color = color

	def empty_groups(self):
		# Empty all the groups.
		self.paddle_group.empty()
		self.ball_group.empty()
		self.block_group.empty()
		self.powerup_group.empty()
		self.effect_group.empty()
		
	def add_powerup(self, classname, effect):
		# Determine what position to place the powerup at.
		if self.x <= settings.SCREEN_WIDTH / 2:
			# If position is on the left half of the screen, place the powerup after the item with the highest x value in the powerup group.
			max_x = self.x
			for a_powerup in self.powerup_group:
				if a_powerup.x + a_powerup.width > max_x:
					max_x = a_powerup.x + a_powerup.width + self.powerup_offset
			x = max_x
			y = self.y
		else:
			# If position is on the right half of the screen, place the powerup before the item with the lowest x value in the powerup group.
			min_x = self.x
			for a_powerup in self.powerup_group:
				if a_powerup.x - self.powerup_offset - powerup.Powerup.width < min_x:
					min_x = a_powerup.x - self.powerup_offset - powerup.Powerup.width
			x = min_x
			y = self.y

		# Stores a powerup in our powerup group, and connects it to the effect so the powerup can be killed when the effect is killed.
		temp_powerup = classname(x, y)
		effect.displayed_powerups.append(temp_powerup)
		self.powerup_group.add(temp_powerup)

		# Change the last_powerup_group_size to match the current size of the group.
		self.last_powerup_group_size = len(self.powerup_group)

	def update(self):
		# We check if any object has been removed from the powerup group.
		if len(self.powerup_group) < self.last_powerup_group_size:
			# We use this to position the powerups.
			previous_powerup = None

			# If an object has been removed, we update the position of all items in the list.
			for a_powerup in self.powerup_group:
				# Determine how to place the powerups.
				if previous_powerup == None:
					# If the previous powerup is none, we can just place the powerup at our position.
					a_powerup.x = self.x
				else:
					# Otherwise, we place the powerup next to the previous powerup.
					if self.x <= settings.SCREEN_WIDTH / 2:
						# To the left of the previous powerup.
						a_powerup.x = previous_powerup.x + previous_powerup.width + self.powerup_offset
					else:
						# To the right of the previous powerup.
						a_powerup.x = previous_powerup.x - a_powerup.width - self.powerup_offset
					
				# Set this powerup as the previous one.
				previous_powerup = a_powerup

			# Finally, change the last_powerup_group_size to match the current size.
			self.last_powerup_group_size = len(self.powerup_group)

		# Update paddles. The player takes care of this in order to send correct keys to the it's own paddles.
		self.paddle_group.update(self.key_up, self.key_down)
