__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *
from settings import *

class Player(pygame.sprite.Sprite):

	def __init__(self, name, key_up, key_down, color):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		self.name = name
		self.key_up = key_up
		self.key_down = key_down
		
		# Create a group to store paddles in.
		self.paddle_group = pygame.sprite.Group()

		# Create a group to store balls in.
		self.ball_group = pygame.sprite.Group()

		# Create a group to store blocks in.
		self.block_group = pygame.sprite.Group()

		# Create a group to store powerups in.
		self.powerup_group = pygame.sprite.Group()

		# Store the selected color, used to colorize objects that belong to the player.
		self.color = color

	def update(self):
		self.paddle_group.update(self.key_up, self.key_down)