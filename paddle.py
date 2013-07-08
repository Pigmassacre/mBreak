__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import useful
import shadow
import groupholder
from settings import *

class Paddle(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/paddle/paddle.png")
	# Scale it to game_scale.
	image = pygame.transform.scale(image, (image.get_width() * GAME_SCALE, image.get_height() * GAME_SCALE))

	def __init__(self, x, y, width, height, acceleration, retardation, max_speed, owner):
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

		# Store the owner.
		self.owner = owner

		# Store the paddle in the owners paddle_group.
		self.owner.paddle_group.add(self)

		# Create the image attribute that is drawn to the surface.
		self.image = Paddle.image.copy()

		# Colorize the image.
		useful.colorize_image(self.image, self.owner.color)

		# Add self to to owners paddle_group and main paddle_group.
		self.owner.paddle_group.add(self)
		groupholder.paddle_group.add(self)

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

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
		if self.rect.y < LEVEL_Y:
			# Constrain paddle to screen size.
			self.y = LEVEL_Y
			self.rect.y = self.y
		elif self.rect.y + self.rect.height > LEVEL_MAX_Y:
			# Constrain paddle to screen size.
			self.y = LEVEL_MAX_Y - self.rect.height
			self.rect.y = self.y
