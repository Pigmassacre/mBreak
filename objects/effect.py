__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import objects.groups as groups
from settings.settings import *

class Effect(pygame.sprite.Sprite):

	def __init__(self, parent):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Store the parent.
		self.parent = parent

		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(self.parent.rect.x, self.parent.rect.y, self.parent.rect.width, self.parent.rect.height)

		# Store self in the main effect_group.
		groups.Groups.effect_group.add(self)

	def on_hit_ball(self, entity):
		print(str(entity) + " hit ball " + str(entity))

	def on_hit_block(self, entity):
		print(str(entity) + " hit block " + str(entity))
		
	def on_hit_wall(self, entity):
		print(str(entity) + " hit a wall.")

	def update(self):
		self.rect.x = self.parent.rect.x
		self.rect.y = self.parent.rect.y
		self.rect.width = self.parent.rect.width
		self.rect.height = self.parent.rect.height
		
		print("Updating effect " + str(self))
