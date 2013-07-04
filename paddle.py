__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
from settings import *

class Paddle(pygame.sprite.Sprite):

	def __init__(self, x, y, width, height, acceleration, retardation, max_speed, image_path):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		self.velocity_y = 0

		self.acceleration = acceleration

		self.retardation = retardation

		self.max_speed = max_speed

		# Create the image attribute that is drawn to the surface.
		self.image = pygame.image.load(image_path)

		if DEBUG_MODE:
			print("Paddle spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ")")

	def update(self, key_up, key_down):
		if pygame.key.get_pressed()[key_up]:
			self.velocity_y = self.velocity_y - self.acceleration
			if self.velocity_y < -self.max_speed:
				self.velocity_y = -self.max_speed
		elif pygame.key.get_pressed()[key_down]:
			self.velocity_y = self.velocity_y + self.acceleration
			if self.velocity_y > self.max_speed:
				self.velocity_y = self.max_speed
		elif self.velocity_y > 0:
			self.velocity_y = self.velocity_y - self.retardation
			if self.velocity_y < 0:
				self.velocity_y = 0
		elif self.velocity_y < 0:
			self.velocity_y = self.velocity_y + self.retardation
			if self.velocity_y > 0:
				self.velocity_y = 0

		self.y = self.y + self.velocity_y
		self.rect.y = self.y

		# Check collision with y-edges.
		if self.rect.y < 0:
			# Constrain paddle to screen size.
			self.y = 0
			self.rect.y = self.y
		elif self.rect.y + self.rect.height > SCREEN_HEIGHT:
			# Constrain paddle to screen size.
			self.y = SCREEN_HEIGHT - self.rect.height
			self.rect.y = self.y
