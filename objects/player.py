__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import objects.groups as groups
import objects.ball as ball
from pygame.locals import *
from settings.settings import *

class Player(pygame.sprite.Sprite):

	def __init__(self, name, key_up, key_down, color):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		self.name = name
		self.key_up = key_up
		self.key_down = key_down

		# Create and store the paddle.
		self.paddle_group = pygame.sprite.Group()

		# Create a group to store balls in.
		self.ball_group = pygame.sprite.Group()

		# Create a group to store blocks in.
		self.block_group = pygame.sprite.Group()

		# Create a group to store powerups in.
		self.powerup_group = pygame.sprite.Group()

		# Store the player in the main player_group.
		groups.Groups.player_group.add(self)

		# Store the selected color, used to colorize objects that belong to the player.
		self.color = color

	def empty_groups(self):
		self.paddle_group.empty()
		self.ball_group.empty()
		self.block_group.empty()
		self.powerup_group.empty()

	def update(self):
		# Update paddles.
		self.paddle_group.update(self.key_up, self.key_down)
