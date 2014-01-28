__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import objects.powerups.powerup as powerup
import objects.effects.reduced as reduced
import objects.shadow as shadow
import objects.groups as groups
import settings.settings as settings

"""

This is the Reducer powerup. When picked up by a ball, it applies a "reduced" effect to the paddles of the current owner of that ball.

"""

def convert():
	# We put this here so the game-class can call this method to "preload" the image used for this powerup.
	# I could probably put this in the constructor of the powerup, but I worry about performance so I make sure to only do it once.
	Reducer.image.convert_alpha()

class Reducer(powerup.Powerup):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/reducer.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	
	# The amount of time the effect will last.
	duration = 7500

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, Reducer.width, Reducer.height, False)

		# Load the image file.
		self.image = Reducer.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

	def create_effect(self, entity):
		return reduced.Reduced(entity, Reducer.duration)

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()

		# Create a reduced effect to be added to the paddles of the owner of the entity.
		for paddle in entity.owner.paddle_group:
			created_effect = self.create_effect(paddle)

		# Add this effect to the owner of the entity.
		entity.owner.effect_group.add(created_effect)

		# Store a powerup of this type in entity owners powerup group, so we can display the powerups collected by a player.
		entity.owner.add_powerup(self.__class__, created_effect)