__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import copy
import other.useful as useful
import objects.powerup as powerup
import objects.charged as charged
import objects.shadow as shadow
import objects.ball as ball
import objects.groups as groups
import objects.timeout as timeout
import objects.speed as speed
import settings.settings as settings

def convert():
	Multiball.image.convert_alpha()

class Multiball(powerup.Powerup):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/multiball.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE

	# The amount of time the effect will last.
	duration = 10000

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, Multiball.width, Multiball.height)

		# Load the image file.
		self.image = Multiball.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()

		for paddle in entity.owner.paddle_group:
			if paddle.x < (settings.SCREEN_WIDTH / 2):
				# If the paddle is on the left side, spawn ball on the right side of the paddle. 
				x = paddle.x + paddle.width + 1
				angle = 0
			else:
				# Otherwise spawn on the left side of the paddle.
				x = paddle.x - paddle.width - 1
				angle = math.pi

			# Create a ball and store it temporarily.
			temp_ball = ball.Ball(x, paddle.y + (paddle.height / 2), angle, entity.owner)

			# Add all the players effects to the ball.
			#temp_effect = None
			for effect in entity.owner.effect_group:
				# Add this effect to the ball. Make sure we don't spread the charged effect.
				# We want to make sure that the added effects ends exactly when the parent effect ends, so we set its duration to duration - time_passed.
				if effect.__class__ != charged.Charged:
					effect.__class__(temp_ball, effect.duration - effect.time_passed)

			# Create a timeout effect which is added to the ball.
			timeout_effect = timeout.Timeout(temp_ball, Multiball.duration)

		# Store a powerup of this type in entity owners powerup group, so we can display the powerups collected by a player.
		entity.owner.add_powerup(Multiball, timeout_effect)