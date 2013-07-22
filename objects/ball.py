__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import other.useful as useful
import objects.paddle as paddle
import objects.particle as particle
import objects.trace as trace
import objects.shadow as shadow
import objects.groups as groups
from settings.settings import *

def convert():
	Ball.image.convert()

class Ball(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/ball/ball.png")

	pygame.mixer.init(44100, -16, 2, 512)
	sound_effect = pygame.mixer.Sound("res/sounds/ball_hit_wall.wav")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * GAME_SCALE
	height = image.get_height() * GAME_SCALE
	max_speed = 3 * GAME_SCALE
	spin_speed_strength = 0.05
	spin_angle_strength = 0.05
	trace_spawn_rate = 32

	# Scale image to game_scale.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y, angle, speed, damage, owner):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, Ball.width, Ball.height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# Set the angle variable.
		self.angle = angle

		# Set maximum speed of the ball.
		self.max_speed = Ball.max_speed

		# Set the speed variable.
		if speed <= self.max_speed:
			self.speed = speed
		else:
			self.speed = self.max_speed
		
		# Store the damage value, this is the damage the ball does to a block when it collides with it.
		self.damage = damage
		
		# Store the owner.
		self.owner = owner

		# Create the image attribute that is drawn to the surface.
		self.image = Ball.image.copy()

		# Colorize the image. We save a reference to the parents color in our own variable, so  that 
		# classes and modules that want to use our color do not have to call us.owner.color
		self.color = self.owner.color
		useful.colorize_image(self.image, self.color)

		# Load the sound effect.
		# self.sound_effect = Ball.sound_effect.
		self.collided = False

		# Setup the trace time keeping variable.
		self.trace_spawn_time = 0
		
		# Create a shadow.
		self.shadow = shadow.Shadow(self)

		# Store the ball in the owners ball_group and the main ball_group.
		self.owner.ball_group.add(self)
		groups.Groups.ball_group.add(self)

	def calculate_spin(self, paddle):
		# TODO: Look over this, it feels wrong.
		# I think it should be something like: If ball is in pi and 2pi degrees angle and velocity
		# is positive, increase speed for a short while and increase angle. Vice versa.
		if self.angle <= (math.pi / 2):
			self.angle = self.angle - (paddle.velocity_y * Ball.spin_angle_strength)
		elif self.angle <= math.pi:
			self.angle = self.angle + (paddle.velocity_y * Ball.spin_angle_strength)
		elif self.angle <= (3 * math.pi) / 2:
			self.angle = self.angle + (paddle.velocity_y * Ball.spin_angle_strength)
		elif self.angle <= (2 * math.pi):
			self.angle = self.angle - (paddle.velocity_y * Ball.spin_angle_strength)
		#self.speed = self.speed + (self.speed * Ball.spin_speed_strength)

	def place_left_of(self, other):
		self.x = other.rect.left - self.rect.width - 1
		self.rect.x = self.x

	def place_right_of(self, other):
		self.x = other.rect.right + 1
		self.rect.x = self.x

	def place_over(self, other):
		self.y = other.rect.top - self.rect.height - 1
		self.rect.y = self.y

	def place_below(self, other):
		self.y = other.rect.bottom + 1
		self.rect.y = self.y

	def hit_left_side_of_paddle(self, paddle):
		# Calculate spin, and then reverse angle.
		self.calculate_spin(paddle)
		if self.angle < (math.pi / 2) or self.angle > ((3 * math.pi) / 2):
			self.angle = math.pi - self.angle

		# Place ball to the left of the paddle.
		self.place_left_of(paddle)

	def hit_right_side_of_paddle(self, paddle):
		# Calculate spin, and then reverse angle.
		self.calculate_spin(paddle)
		if self.angle > (math.pi / 2) and self.angle < ((3 * math.pi) / 2):
			self.angle = math.pi - self.angle

		# Place ball to the right of the paddle.
		self.place_right_of(paddle)

	def hit_left_side_of_block(self, block):
		# Reverse angle.
		if self.angle < (math.pi / 2) or self.angle > ((3 * math.pi) / 2):
			self.angle = math.pi - self.angle

		# Place ball to the left of the block.
		self.place_left_of(block)

	def hit_right_side_of_block(self, block):
		# Reverse angle.
		if self.angle > (math.pi / 2) and self.angle < ((3 * math.pi) / 2):
			self.angle = math.pi - self.angle

		# Place ball to the right of the block.
		self.place_right_of(block)

	def spawn_particle(self):
		for i in range(0, 2):
			angle = self.angle + random.uniform(-0.20, 0.20)
			retardation = self.speed / 24.0
			alpha_step = 5
			particle.Particle(self.x, self.y, self.rect.width / 4, self.rect.height / 4, angle, self.speed, retardation, self.color, alpha_step)

	def check_collision_paddles(self):
		paddle_collide_list = pygame.sprite.spritecollide(self, groups.Groups.paddle_group, False)
		for paddle in paddle_collide_list:
			self.spawn_particle()
			self.collided = True
			if self.rect.bottom >= paddle.rect.top and self.rect.top < paddle.rect.top:
				# Top side of paddle collided with. Compare with edges:
				if paddle.rect.left - self.rect.left > paddle.rect.top - self.rect.top:
					# The ball collides more with the left side than top side.
					self.hit_left_side_of_paddle(paddle)
				elif self.rect.right - paddle.rect.right > paddle.rect.top - self.rect.top:
					# The ball collides more with the right side than top side.
					self.hit_right_side_of_paddle(paddle)
				else:
					# The ball collides more with the top side than any other side.
					if self.angle < math.pi:
						self.angle = -self.angle

					# Place ball on top of the paddle.
					self.place_over(paddle)
			elif self.rect.top <= paddle.rect.bottom and self.rect.bottom > paddle.rect.bottom:
				# Bottom side of paddle collided with. Compare with edges:
				if paddle.rect.left - self.rect.left > self.rect.bottom - paddle.rect.bottom:
					# The ball collides more with the left side than top side.
					self.hit_left_side_of_paddle(paddle)
				elif self.rect.right - paddle.rect.right > self.rect.bottom - paddle.rect.bottom:
					# The ball collides more with the right side than top side.
					self.hit_right_side_of_paddle(paddle)
				else:
					# The ball collides more with the bottom side than any other side.
					if self.angle > math.pi:
						self.angle = -self.angle

					# Place ball beneath the paddle.
					self.place_below(paddle)
			elif self.rect.right >= paddle.rect.left and self.rect.left < paddle.rect.left:
				# Left side of paddle collided with.
				self.hit_left_side_of_paddle(paddle)
			elif self.rect.left <= paddle.rect.right and self.rect.right > paddle.rect.right:
				# Right side of paddle collided with.
				self.hit_right_side_of_paddle(paddle)

	def check_collision_balls(self):
		groups.Groups.ball_group.remove(self)
		ball_collide_list = pygame.sprite.spritecollide(self, groups.Groups.ball_group, False)
		for ball in ball_collide_list:
			self.spawn_particle()
			if self.rect.bottom >= ball.rect.top and self.rect.top < ball.rect.top:
				# Top side of ball collided with. Compare with edges:
				if ball.rect.left - self.rect.left > ball.rect.top - self.rect.top:
					# The ball collides more with the left side than top side.
					# Place ball to the left of the ball.
					self.place_left_of(ball)
				elif self.rect.right - ball.rect.right > ball.rect.top - self.rect.top:
					# The ball collides more with the right side than top side.
					# Place ball to the right of the ball.
					self.place_right_of(ball)
				else:
					# Place ball on top of the ball.
					self.place_over(ball)
			elif self.rect.top <= ball.rect.bottom and self.rect.bottom > ball.rect.bottom:
				# Bottom side of ball collided with.
				if ball.rect.left - self.rect.left > self.rect.bottom - ball.rect.bottom:
					# The ball collides more with the left side than top side.
					# Place ball to the left of the ball.
					self.place_left_of(ball)
				elif self.rect.right - ball.rect.right > self.rect.bottom - ball.rect.bottom:
					# The ball collides more with the right side than top side.
					# Place ball to the right of the ball.
					self.place_right_of(ball)
				else:
					# The ball collides more with the bottom side than any other side.
					# Place ball beneath the ball.
					self.place_below(ball)
			elif self.rect.right >= ball.rect.left and self.rect.left < ball.rect.left:
				# Left side of ball collided with.
				# Place ball to the left of the ball.
				self.place_left_of(ball)
			elif self.rect.left <= ball.rect.right and self.rect.right > ball.rect.right:
				# Right side of ball collided with.
				# Place ball to the right of the ball.
				self.place_right_of(ball)

			# Handle self.
			delta_x = self.rect.centerx - ball.rect.centerx
			delta_y = self.rect.centery - ball.rect.centery
			self.angle = math.atan2(delta_y, delta_x)

			# Handle other ball.
			delta_x = ball.rect.centerx - self.rect.centerx
			delta_y = ball.rect.centery - self.rect.centery
			ball.angle = math.atan2(delta_y, delta_x)

			self.collided = True
		groups.Groups.ball_group.add(self)

	def check_collision_blocks(self):
		# TODO: Work out the last collision bugs with blocks. Possibly check how many units we are colliding with, and
		# 		use that to work out which of the possible cases to handle?
		#
		#		For example: (block = #, ball = o)
		#		
		#		#o	##	#o 	o#	# 	 #	o
		#		##	o#	 #	#	o#	#o 	##
		blocks_collided_with = pygame.sprite.spritecollide(self, groups.Groups.block_group, False)
		block_information = {}
		for block in blocks_collided_with:
			if self.rect.bottom >= block.rect.top and self.rect.top < block.rect.top:
				# Top side of block collided with. Compare with edges:
				if block.rect.left - self.rect.left > block.rect.top - self.rect.top:
					# The ball collides more with the left side than top side.
					self.hit_left_side_of_block(block)
					block_information[block] = "left"
				elif self.rect.right - block.rect.right > block.rect.top - self.rect.top:
					# The ball collides more with the right side than top side.
					self.hit_right_side_of_block(block)
					block_information[block] = "right"
				else:
					# The ball collides more with the top side than any other side.
					if self.angle < math.pi:
						self.angle = -self.angle
					block_information[block] = "top"

					# Place ball on top of the block.
					self.place_over(block)
			elif self.rect.top <= block.rect.bottom and self.rect.bottom > block.rect.bottom:
				# Bottom side of block collided with.
				if block.rect.left - self.rect.left > self.rect.bottom - block.rect.bottom:
					# The ball collides more with the left side than top side.
					self.hit_left_side_of_block(block)
					block_information[block] = "left"
				elif self.rect.right - block.rect.right > self.rect.bottom - block.rect.bottom:
					# The ball collides more with the right side than top side.
					self.hit_right_side_of_block(block)
					block_information[block] = "right"
				else:
					# The ball collides more with the bottom side than any other side.
					if self.angle > math.pi:
						self.angle = -self.angle
					block_information[block] = "bottom"

					# Place ball beneath the block.
					self.place_below(block)
			elif self.rect.right >= block.rect.left and self.rect.left < block.rect.left:
				# Left side of block collided with.
				self.hit_left_side_of_block(block)
				block_information[block] = "left"
			elif self.rect.left <= block.rect.right and self.rect.right > block.rect.right:
				# Right side of block collided with.
				self.hit_right_side_of_block(block)
				block_information[block] = "right"

		print("dict contains: " + str(block_information))

		# Deal damage to the hit blocks.
		#block.on_hit(self.damage)

		# Spawn particles and confirm that we've collided with an object.
		#self.collided = True

	def check_collision_powerups(self):
		powerup_collide_list = pygame.sprite.spritecollide(self, groups.Groups.powerup_group, False)
		for powerup in powerup_collide_list:
			powerup.hit(self)

	def update(self, main_clock):
		self.collided = False

		# Check collision with paddles.
		self.check_collision_paddles()
				
		# Check collision with other balls.
		self.check_collision_balls()

		# Check collision with blocks.
		self.check_collision_blocks()

		# Check collision with powerups.
		self.check_collision_powerups()

		# Constrain angle to angle != pi/2 and angle != 3pi/2
		if self.angle == (math.pi / 2)  or self.angle == ((3 * math.pi) / 2):
			self.angle = self.angle + random.randrange(-1, 2, 2) * 0.25

		# Constrain angle to 0 < angle < 2pi
		if self.angle > (2 * math.pi):
			self.angle = self.angle - (2 * math.pi)
		elif self.angle < 0:
			self.angle = (2 * math.pi) + self.angle
			
		# Move the ball with speed in consideration.
		self.x = self.x + (math.cos(self.angle) * self.speed)
		self.y = self.y + (math.sin(self.angle) * self.speed)
		self.rect.x = self.x
		self.rect.y = self.y

		# Check collision with x-edges.
		if self.rect.x < LEVEL_X:
			self.spawn_particle()
			self.collided = True
			# Reverse angle on x-axis.
			self.angle = math.pi - self.angle

			# Constrain ball to screen size.
			self.x = LEVEL_X
			self.rect.x = self.x
		elif self.rect.x + self.rect.width > LEVEL_MAX_X:
			self.spawn_particle()
			self.collided = True
			# Reverse angle on x-axis.
			self.angle = math.pi - self.angle

			# Constrain ball to screen size.
			self.x = LEVEL_MAX_X - self.rect.width			
			self.rect.x = self.x

		# Check collision with y-edges.
		if self.rect.y < LEVEL_Y:
			self.spawn_particle()
			self.collided = True
			# Reverse angle on y-axis.
			self.angle = -self.angle

			# Constrain ball to screen size.
			self.y = LEVEL_Y
			self.rect.y = self.y
		elif self.rect.y + self.rect.height > LEVEL_MAX_Y:
			self.spawn_particle()
			self.collided = True
			# Reverse angle on y-axis.
			self.angle = -self.angle

			# Constrain ball to screen size.
			self.y = LEVEL_MAX_Y - self.rect.height
			self.rect.y = self.y

		# If it's time, spawn a trace.
		self.trace_spawn_time = self.trace_spawn_time + main_clock.get_time()
		if self.trace_spawn_time >= Ball.trace_spawn_rate:
			trace.Trace(self)
			self.trace_spawn_time = 0

		# If we have collided with anything, play the sound effect.
		if self.collided:
			Ball.sound_effect.play()