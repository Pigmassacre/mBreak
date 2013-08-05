__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import other.useful as useful
import objects.powerup as powerup
import objects.shadow as shadow
import objects.ball as ball
import objects.groups as groups
from settings.settings import *

def convert():
	Multiball.image.convert_alpha()

class Multiball(powerup.Powerup):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/multiball.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * GAME_SCALE
	height = image.get_height() * GAME_SCALE
	width = 8 * GAME_SCALE
	height = 8 * GAME_SCALE

	# Scale image to game_scale.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, Multiball.width, Multiball.height)

		# Load the image file.
		self.image = Multiball.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

		if DEBUG_MODE:
			print("Multiball spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ")")

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()

		x = entity.x
		y = entity.y
		speed = entity.speed
		angle = entity.angle
		damage = entity.damage
		owner = entity.owner

		amount_to_spawn = 3

		for i in range(0, amount_to_spawn):
			print("Angle: " + str(angle))
			angle = angle + ((2 * math.pi) / amount_to_spawn)
			x = x + math.cos(angle)
			y = y + math.sin(angle)
			groups.Groups.ball_group.add(ball.Ball(x, y, angle, speed, owner))
