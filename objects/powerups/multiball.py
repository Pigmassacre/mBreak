__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.powerups.powerup as powerup
import objects.effects.charged as charged
import objects.effects.sizechange as sizechange
import objects.effects.timeout as timeout
import objects.effects.flash as flash
import objects.shadow as shadow
import objects.ball as ball
import objects.groups as groups
import settings.settings as settings

"""

This is the Multiball powerup. When this powerup is hit by a ball, it spawns an extra ball for the parent of that ball.

Balls spawned by Multiball get all the effects of the owner of the ball that hit the Multiball, EXCEPT for the Charged effect.
That effect is special. ;)

Balls spawned by Multiball powerups only last for a short amount of time. This is handled by attaching a timeout effect
to the balls that are created by this powerup.

"""

def convert():
	# We put this here so the game-class can call this method to "preload" the image used for this powerup.
	# I could probably put this in the constructor of the powerup, but I worry about performance so I make sure to only do it once.
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

			# Add all the currently active effects to the ball.
			for player in groups.Groups.player_group:
				for effect in player.effect_group:
					# Add this effect to the ball. Make sure we don't spread the charged, sizechange, flash or timeout effect.
					if effect.__class__ != charged.Charged and effect.__class__ != sizechange.SizeChange and effect.__class__ != flash.Flash and effect.__class__ != timeout.Timeout:
						# We want to make sure that the added effects ends exactly when the parent effect ends, so we set its duration to duration - time_passed.
						copied_effect = effect.__class__(temp_ball, effect.duration - effect.time_passed)
						copied_effect.real_owner = player

			# Create a timeout effect which is added to the ball.
			timeout_effect = timeout.Timeout(temp_ball, Multiball.duration)

		# Store a powerup of this type in entity owners powerup group, so we can display the powerups collected by a player.
		entity.owner.add_powerup(Multiball, timeout_effect)