__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import copy
import math
import other.useful as useful
import objects.shadow as shadow
import objects.effects.flash as flash
import objects.groups as groups
import settings.settings as settings

"""

This is the Paddle class. Paddles take care of their own movement (with the keys they should listen to provided by the player class).
Since paddles can move within the game area, they detect and handle their own collision with the edges of the game area.

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

	# On hit effect values.
	hit_effect_start_color = pygame.Color(255, 255, 255, 160)
	hit_effect_final_color = pygame.Color(255, 255, 255, 0)
	hit_effect_tick_amount = 22

	# Used for hit effect on the paddle.
	stabilize_speed = 0.45
	max_nudge_distance = 6

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

		# This is the actual desired x position of the paddle. Used for visual effects.
		self.center_x = self.x

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

	def on_hit(self, other_object):
		# Create a new on hit effect.
		self.effect_group.add(flash.Flash(self, copy.copy(Paddle.hit_effect_start_color), copy.copy(Paddle.hit_effect_final_color), Paddle.hit_effect_tick_amount))

	def update(self, key_up, key_down):
		if self.owner.ai:
			key_up_pressed = False
			key_down_pressed = False

			# Simple, stupid AI. Lol.
			if self.x < settings.SCREEN_WIDTH / 2:
				paddle_side_left = True
			else:
				paddle_side_left = False

			focused_ball = None
			min_x_distance = 99999
			min_x_ball = None
			min_y_distance = 99999
			min_y_ball = None
			for ball in groups.Groups.ball_group:
				if focused_ball == None:
					focused_ball = ball

				if min_x_ball == None:
					min_x_ball = ball

				if min_y_ball == None:
					min_y_ball = ball

				if paddle_side_left:
					if ball.angle >= math.pi / 2 and ball.angle <= 3 * math.pi / 2:
						if ball.x - self.x < min_x_distance:
							min_x_distance = ball.x - self.x
							min_x_ball = ball

						if ball.y + (ball.height / 2) < self.y + (self.height / 2):
							if self.y - ball.y < min_y_distance:
								min_y_distance = self.y - ball.y
								min_y_ball = ball
						else:
							if ball.y - self.y < min_y_distance:
								min_y_distance = ball.y - self.y
								min_y_ball = ball

						if min_x_distance < min_y_distance:
							focused_ball = min_x_ball
						else:
							focused_ball = min_x_ball # Doesnt actually care about y distance yet, TODO

					if min_x_distance <= self.width:
						focused_ball = None
				else:
					if ball.angle <= math.pi / 2 or ball.angle >= 3 * math.pi / 2:
						if self.x - ball.x < min_x_distance:
							min_x_distance = self.x - ball.x
							min_x_ball = ball

						if ball.y + (ball.height / 2) < self.y + (self.height / 2):
							if self.y - ball.y < min_y_distance:
								min_y_distance = self.y - ball.y
								min_y_ball = ball
						else:
							if ball.y - self.y < min_y_distance:
								min_y_distance = ball.y - self.y
								min_y_ball = ball

						if min_x_distance < min_y_distance:
							focused_ball = min_x_ball
						else:
							focused_ball = min_x_ball # Doesnt actually care about y distance yet, TODO

					if min_x_distance <= -self.width:
						focused_ball = None

			if focused_ball != None:
				if focused_ball.y + (focused_ball.height / 2) < self.y:
					key_up_pressed = True
				elif focused_ball.y + (focused_ball.height / 2) > self.y + self.height:
					key_down_pressed = True
		else:
			key_up_pressed = pygame.key.get_pressed()[key_up]
			key_down_pressed = pygame.key.get_pressed()[key_down]

		# Check for key_up or key_down events. If key_up is pressed, the paddle will move up and vice versa for key_down.
		# However, we only move the paddle if max_speed is above zero, since if it is zero the paddle cannot move anyway.
		if self.max_speed > 0:
			if key_up_pressed:
					self.velocity_y = self.velocity_y - self.acceleration
					if self.velocity_y < -self.max_speed:
						self.velocity_y = -self.max_speed
			elif key_down_pressed:
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

		# Move paddle to it's center x.
		if self.x > self.center_x:
			if self.x > self.center_x + Paddle.max_nudge_distance:
				self.x = self.center_x + Paddle.max_nudge_distance

			if self.x - Paddle.stabilize_speed < self.center_x:
				self.x = self.center_x
			else:
				self.x -= Paddle.stabilize_speed
		else:
			if self.x < self.center_x - Paddle.max_nudge_distance:
				self.x = self.center_x - Paddle.max_nudge_distance

			if self.x + Paddle.stabilize_speed > self.center_x:
				self.x = self.center_x
			else:
				self.x += Paddle.stabilize_speed
		self.rect.x = self.x

		# Check collision with y-edges.
		if self.rect.y < settings.LEVEL_Y:
			# Constrain paddle to screen size.
			self.y = settings.LEVEL_Y
			self.rect.y = self.y
		elif self.rect.y + self.rect.height > settings.LEVEL_MAX_Y:
			# Constrain paddle to screen size.
			self.y = settings.LEVEL_MAX_Y - self.rect.height
			self.rect.y = self.y

		# Move any effects on the paddle.
		for effect in self.effect_group:
			effect.rect.x = self.rect.x
			effect.rect.y = self.rect.y