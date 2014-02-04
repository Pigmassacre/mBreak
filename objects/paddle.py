__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import copy
import math
import other.useful as useful
import objects.shadow as shadow
import objects.effects.flash as flash
import objects.effects.speed as speed
import objects.groups as groups
import settings.settings as settings

"""

This is the Paddle class. Paddles take care of their own movement (with the keys they should listen to provided by the player class).
Since paddles can move within the game area, they detect and handle their own collision with the edges of the game area.

"""

def convert():
	Paddle.top_image.convert()
	Paddle.middle_image.convert()
	Paddle.bottom_image.convert()

class Paddle(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	#image = pygame.image.load("res/paddle/paddle.png")
	top_image = pygame.image.load("res/paddle/paddle_top.png")
	middle_image = pygame.image.load("res/paddle/paddle_middle.png")
	bottom_image = pygame.image.load("res/paddle/paddle_bottom.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = middle_image.get_width() * settings.GAME_SCALE
	height = 18 * settings.GAME_SCALE
	acceleration = 0.5 * settings.GAME_SCALE
	retardation = 2 * settings.GAME_SCALE
	max_speed = 2 * settings.GAME_SCALE

	max_height = 32 * settings.GAME_SCALE
	min_height = 4 * settings.GAME_SCALE

	max_width = width
	min_width = width

	# On hit effect values.
	hit_effect_start_color = pygame.Color(255, 255, 255, 160)
	hit_effect_final_color = pygame.Color(255, 255, 255, 0)
	hit_effect_tick_amount = 22

	# Used for hit effect on the paddle.
	stabilize_speed = 0.45
	max_nudge_distance = 6

	# Scale the images to settings.GAME_SCALE.
	top_image = pygame.transform.scale(top_image, (top_image.get_width() * settings.GAME_SCALE, top_image.get_height() * settings.GAME_SCALE))
	middle_image = pygame.transform.scale(middle_image, (middle_image.get_width() * settings.GAME_SCALE, middle_image.get_height() * settings.GAME_SCALE))
	bottom_image = pygame.transform.scale(bottom_image, (bottom_image.get_width() * settings.GAME_SCALE, bottom_image.get_height() * settings.GAME_SCALE))

	def __init__(self, x, y, owner):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, Paddle.width, Paddle.height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# We store the max and min height of the paddle, for easy access by other classes.
		self.max_height = Paddle.max_height
		self.min_height = Paddle.min_height

		# We store the actual height that can go beyond max or min height.
		self.actual_width = self.rect.width
		self.actual_height = self.rect.height

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

		# AI variables.
		self.focused_ball = None
		self.old_focused_ball = None
		self.chosen_distance_from_center = 0
		self.min_x_distance = 99999
		self.min_y_distance = 99999
		self.min_distance = 99999

		# Set the size of the paddle. This takes care of storing the image attribute and coloring it.
		self.set_size(Paddle.width, Paddle.height)

		# Add self to to owners paddle_group and main paddle_group.
		self.owner.paddle_group.add(self)
		groups.Groups.paddle_group.add(self)

		# Create an effect group to handle effects on this paddle.
		self.effect_group = pygame.sprite.Group()

	def set_size(self, new_width, new_height):
		# Set the actual width and height to the new width and height.
		self.actual_width = new_width
		self.actual_height = new_height

		# Temporarily store the old width and height, used for positioning the paddle later.
		old_width = self.rect.width
		old_height = self.rect.height

		# Change the rect width.
		if self.actual_width > self.max_width:
			self.rect.width = self.max_width
		elif self.actual_width < self.min_width:
			self.rect.width = self.min_width
		else:
			self.rect.width = self.actual_width

		# Change the rect height.
		if self.actual_height > self.max_height:
			self.rect.height = self.max_height
		elif self.actual_height < self.min_height:
			self.rect.height = self.min_height
		else:
			self.rect.height = self.actual_height

		# Make sure the position of the paddle isn't changed.
		self.x += (old_width - self.rect.width) / 2.0
		self.y += (old_height - self.rect.height) / 2.0

		if hasattr(self, 'image'):
			# Resize the current image.
			self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
		else:
			# Create the image attribute that is drawn to the surface.
			self.image = pygame.Surface((self.rect.width, self.rect.height))
		
		# Blit the top part.
		self.image.blit(Paddle.top_image, (0, 0))

		# Blit the middle parts.
		for i in range(Paddle.top_image.get_height(), self.rect.height - Paddle.bottom_image.get_height()):
			self.image.blit(Paddle.middle_image, (0, i))

		# Blit the bottom part.
		self.image.blit(Paddle.bottom_image, (0, self.rect.height - Paddle.bottom_image.get_height()))

		useful.colorize_image(self.image, copy.copy(self.owner.color), False, False)

		# If the shadow already exists, kill it first.
		if hasattr(self, 'shadow'):
			self.shadow.kill()

		# Then, create a (new) shadow.
		self.shadow = shadow.Shadow(self)

	def add_size(self, added_width, added_height):
		self.set_size(self.actual_width + added_width, self.actual_height + added_height)

	def on_hit(self, other_object):
		# Create a new on hit effect.
		self.effect_group.add(flash.Flash(self, copy.copy(Paddle.hit_effect_start_color), copy.copy(Paddle.hit_effect_final_color), Paddle.hit_effect_tick_amount))

	def debug_draw(self, surface):
		if self.focused_ball != None and settings.DEBUG_MODE:
			color = copy.copy(self.owner.color)
			color.a = 128
			surface.fill(color, pygame.Rect(self.focused_ball.rect.x - 2, self.focused_ball.y - 2, self.focused_ball.width + 4, self.focused_ball.height + 4))

	def decide_which_ball(self, ball):
		if self.owner.ai_difficulty >= 2:
			# The higher the difficulty the smarter / cheatier the AI.
			if math.fabs(self.x - ball.x) < self.min_x_distance:
				self.min_x_distance = math.fabs(self.x - ball.x)
				self.focused_ball = ball
		else:
			# Standard difficulty, no cheat. Simply seek out the ball with the least distance to
			# the paddle, and move towards that ball.
			self.min_x_distance = math.fabs(self.x - ball.x)
			self.min_y_distance = math.fabs(self.y - ball.y)
			if math.sqrt(math.pow(self.min_x_distance, 2) + math.pow(self.min_y_distance, 2)) < self.min_distance:
				self.min_distance = math.sqrt(math.pow(self.min_x_distance, 2) + math.pow(self.min_y_distance, 2))

				# For each speed effect on the ball, we halve the distance to it (since each speed effect doubles it's speed)
				for effect in ball.effect_group:
					if effect.__class__ == speed.Speed:
						self.min_distance = self.min_distance / 2

				self.focused_ball = ball

	def update(self, key_up, key_down):
		# Very simple AI.
		if self.owner.ai:
			key_up_pressed = False
			key_down_pressed = False

			if self.x < settings.SCREEN_WIDTH / 2:
				paddle_side_left = True
			else:
				paddle_side_left = False

			# Reset the targeting variables.
			self.focused_ball = None
			self.min_x_distance = 99999
			self.min_y_distance = 99999
			self.min_distance = 99999

			# Loop over every ball in the game, and figure out which ball to focus on.
			for ball in groups.Groups.ball_group:
				if paddle_side_left:
					# If this is the left paddle, we only care about the balls that have an angle that points to
					# the paddle, and balls that are on the right side of the paddle.
					if ball.angle >= math.pi / 2 and ball.angle <= 3 * math.pi / 2 and ball.x >= self.x + (self.width / 3):
						self.decide_which_ball(ball)
				else:
					# If this is the right paddle, we only care about balls to the left of this paddle (and balls
					# that have an angle that points to the paddle).
					if ball.angle <= math.pi / 2 or ball.angle >= 3 * math.pi / 2 and ball.x < self.x + (self.width / 3):
						self.decide_which_ball(ball)

			if self.focused_ball != None:
				if self.focused_ball != self.old_focused_ball:
					self.chosen_distance_from_center = random.uniform((self.y + self.height / 2) - self.y + self.focused_ball.height, (self.y + self.height / 2) - (self.y + self.height) - self.focused_ball.height) / 2

				if self.owner.ai_difficulty >= 2:
					# If cheaty AI, teleport to ball.
					self.y = self.focused_ball.y + (self.focused_ball.height / 2) - (self.height / 2)
				else:
					# If normal AI, move to ball.
					if self.focused_ball.y + self.chosen_distance_from_center < self.y + self.height / 2:
						if self.focused_ball.y < self.y + self.height / 3:
							key_up_pressed = True
					elif self.focused_ball.y + self.chosen_distance_from_center > self.y + self.height / 2:
						if self.focused_ball.y > self.y + self.height - self.height / 3:
							key_down_pressed = True

			self.old_focused_ball = self.focused_ball
		else:
			# If no AI, we just check for key presses.
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