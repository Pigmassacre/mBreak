__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import other.useful as useful
import objects.rocket as rocket
import objects.shadow as shadow
import objects.groups as groups
import settings.settings as settings

def convert():
	HomingRocket.image.convert_alpha()

class HomingRocket(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/homingrocket.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	width = 4 * settings.GAME_SCALE
	height = 8 * settings.GAME_SCALE
	max_speed = 3 * settings.GAME_SCALE
	damage = 10
	homing_angle_strength = 0.12
	particle_spawn_amount = 4

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	# TODO: Add target selection code and chasing code.
	def __init__(self, x, y, speed, owner):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, HomingRocket.width, HomingRocket.height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# Keep track of the HomingRockets position in the previous frame, used for collision handling.
		self.previous = pygame.rect.Rect(self.x, self.y, HomingRocket.width, HomingRocket.height)

		# Set the angle variable.
		self.angle = angle

		# Set maximum speed of the HomingRocket.
		self.max_speed = HomingRocket.max_speed

		# Set the speed variable.
		if speed <= self.max_speed:
			self.speed = speed
		else:
			self.speed = self.max_speed
		
		# Store the owner.
		self.owner = owner

		# Load the image file.
		self.image = Rocket.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

	def update(self, entity):
		# Move the HomingRocket with speed in consideration.
		self.x = self.x + (math.cos(self.angle) * self.speed)
		self.y = self.y + (math.sin(self.angle) * self.speed)
		self.rect.x = self.x
		self.rect.y = self.y

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()
