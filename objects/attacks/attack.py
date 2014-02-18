__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame

"""

Base class of all attacks.

"""

class Attack(pygame.sprite.Sprite):

	def __init__(self, owner):
		self.owner = owner

	def reset(self):
		pass

	def attack(self):
		pass

	def update(self, main_clock):
		pass
