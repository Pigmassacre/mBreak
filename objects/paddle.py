__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import other.useful as useful
import objects.shadow as shadow
import objects.groups as groups
import settings.settings as settings

"""

This is the class that represents the paddles in the game. Paddles take care of their own movement (with the keys they should listen to
provided by the player class). Paddles can only move within the game area, so they also they care of checking for collision with the 
edges of the screen.

"""

def convert():
	Paddle.image.convert()

class Paddle(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/paddle/paddle.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	acceleration = 0.75 * settings.GAME_SCALE
	retardation = 2 * settings.GAME_SCALE
	max_speed = 1.5 * settings.GAME_SCALE

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y, owner):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, Paddle.width, Paddle.height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# The velocity at which the Paddle will be moved when it is updated.
		self.velocity_y = 0

		# These values affect the velocity of the paddle.
		self.acceleration = Paddle.acceleration
		self.retardation = Paddle.retardation
		self.max_speed = Paddle.max_speed

		# The owner is the player that owns the paddle.
		self.owner = owner

		# Store the paddle in the owners paddle_group.
		self.owner.paddle_group.add(self)

		# Create the image attribute that is drawn to the surface.
		self.image = Paddle.image.copy()

		# Colorize the image.
		useful.colorize_image(self.image, self.owner.color)

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

		# Add self to to owners paddle_group and main paddle_group.
		self.owner.paddle_group.add(self)
		groups.Groups.paddle_group.add(self)

		# Create an effect group to handle effects on this paddle.
		self.effect_group = pygame.sprite.Group()

	def update(self, key_up, key_down):
		# Check for key_up or key_down events. If key_up is pressed, the paddle will move up and vice versa for key_down.
		# However, we only move the paddle if max_speed is above zero, since if it is zero the paddle cannot move anyway.
		if self.max_speed > 0:
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
		else:
			# If max_speed is zero, we still want to reduce our velocity.
			if self.velocity_y > 0:
				self.velocity_y = self.velocity_y - self.retardation
				if self.velocity_y < 0:
					self.velocity_y = 0
			elif self.velocity_y < 0:
				self.velocity_y = self.velocity_y + self.retardation
				if self.velocity_y > 0:
					self.velocity_y = 0

		# Move the paddle according to its velocity.
		self.y = self.y + self.velocity_y
		self.rect.y = self.y

		# Move any effects on the paddle.
		for effect in self.effect_group:
			effect.rect.x = self.rect.x
			effect.rect.y = self.rect.y

		# Check collision with y-edges.
		if self.rect.y < settings.LEVEL_Y:
			# Constrain paddle to screen size.
			self.y = settings.LEVEL_Y
			self.rect.y = self.y
		elif self.rect.y + self.rect.height > settings.LEVEL_MAX_Y:
			# Constrain paddle to screen size.
			self.y = settings.LEVEL_MAX_Y - self.rect.height
			self.rect.y = self.y
