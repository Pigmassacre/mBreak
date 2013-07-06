__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import paddle
import trail
import random
import particle
import useful
from settings import *

class Ball(pygame.sprite.Sprite):

	def __init__(self, x, y, width, height, angle, speed, max_speed, damage, image_path, color, owner):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# Set the angle variable.
		self.angle = angle

		# Set maximum speed of the ball.
		self.max_speed = max_speed

		# Set the speed variable.
		if speed <= self.max_speed:
			self.speed = speed
		else:
			self.speed = self.max_speed

		# Set the damage value, this is the damage the ball does to a block when it collides with it.
		self.damage = damage

		# Create the image attribute that is drawn to the surface.
		self.image = pygame.image.load(image_path)

		# Set the color value, the image is colorized to this value and it is used to colorize the particles spawned by this ball.
		self.color = color

		# Colorize the image.
		useful.colorize_image(self.image, self.color)

		# Set the owner.
		self.owner = owner

		# Store the ball in the owners ball_group.
		self.owner.add_ball(self)

		if DEBUG_MODE:
			print("Ball spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ") with angle " + str(self.angle) + " and speed " + str(self.speed))

	def calculate_spin(self, paddle):
		if self.angle < (math.pi / 2):
			# If angle is between 0 and 90 degrees.
			self.angle = self.angle - (paddle.velocity_y * 0.05)
		elif self.angle > ((3 * math.pi) / 2) and self.angle < (2 * math.pi):
			# If angle is between 270 and 359 degrees.
			self.angle = self.angle + (paddle.velocity_y * 0.05)

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

	def spawn_particle(self, particle_group):
		for i in range(0, 2):
			angle = math.pi + self.angle + random.uniform(-0.20, 0.20)
			retardation = self.speed / 24
			color = self.image.get_at((0, 0))
			particle_group.add(particle.Particle(self.x, self.y, self.rect.width / 4, self.rect.height / 4, angle, self.speed, retardation, color))

	def check_collision_paddles(self, paddle_group, particle_group):
		paddle_collide_list = pygame.sprite.spritecollide(self, paddle_group, False)
		for paddle in paddle_collide_list:
			self.spawn_particle(particle_group)
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

	def check_collision_balls(self, ball_group, particle_group):
		ball_group.remove(self)
		ball_collide_list = pygame.sprite.spritecollide(self, ball_group, False)
		for ball in ball_collide_list:
			self.spawn_particle(particle_group)
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
		ball_group.add(self)

	def check_collision_blocks(self, block_group, particle_group):
		block_collide_list = pygame.sprite.spritecollide(self, block_group, False)
		for block in block_collide_list:
			# Deal damage to the hit block.
			block.damage(self.damage)

			self.spawn_particle(particle_group)
			if self.rect.bottom >= block.rect.top and self.rect.top < block.rect.top:
				# Top side of block collided with. Compare with edges:
				if block.rect.left - self.rect.left > block.rect.top - self.rect.top:
					# The ball collides more with the left side than top side.
					self.hit_left_side_of_block(block)
				elif self.rect.right - block.rect.right > block.rect.top - self.rect.top:
					# The ball collides more with the right side than top side.
					self.hit_right_side_of_block(block)
				else:
					# The ball collides more with the top side than any other side.
					if self.angle < math.pi:
						self.angle = -self.angle

					# Place ball on top of the block.
					self.place_over(block)
			elif self.rect.top <= block.rect.bottom and self.rect.bottom > block.rect.bottom:
				# Bottom side of block collided with.
				if block.rect.left - self.rect.left > self.rect.bottom - block.rect.bottom:
					# The ball collides more with the left side than top side.
					self.hit_left_side_of_block(block)
				elif self.rect.right - block.rect.right > self.rect.bottom - block.rect.bottom:
					# The ball collides more with the right side than top side.
					self.hit_right_side_of_block(block)
				else:
					# The ball collides more with the bottom side than any other side.
					if self.angle > math.pi:
						self.angle = -self.angle

					# Place ball beneath the block.
					self.place_below(block)
			elif self.rect.right >= block.rect.left and self.rect.left < block.rect.left:
				# Left side of block collided with.
				self.hit_left_side_of_block(block)
			elif self.rect.left <= block.rect.right and self.rect.right > block.rect.right:
				# Right side of block collided with.
				self.hit_right_side_of_block(block)

	def update(self, ball_group, paddle_group, block_group, particle_group):
		# Check collision with paddles.
		self.check_collision_paddles(paddle_group, particle_group)
				
		# Check collision with other balls.
		self.check_collision_balls(ball_group, particle_group)

		# Check collision with blocks.
		self.check_collision_blocks(block_group, particle_group)

		""" Should I constrain angle only when it hits paddle / wall, or keep it like it is? """

		# Constrain angle to angle != pi and angle != 0
		if self.angle == 0  or self.angle == (2 * math.pi) or self.angle == math.pi:
			self.angle = self.angle + random.randrange(-1, 2, 2) * 0.15
			print("Angle was 0 or pi or 2pi, corrected to " + str(self.angle))

		# Constrain angle to angle != pi/2 and angle != 3pi/2
		if self.angle == (math.pi / 2)  or self.angle == ((3 * math.pi) / 2):
			self.angle = self.angle + random.randrange(-1, 2, 2) * 0.15
			print("Angle was pi/2 or 3pi/2, corrected to " + str(self.angle))

		# Constrain angle to 0 < angle < 2pi
		if self.angle > (2 * math.pi):
			self.angle = self.angle - (2 * math.pi)
		elif self.angle < 0:
			self.angle = (2 * math.pi) + self.angle

			
		# Finally, move the ball with speed in consideration.
		self.x = self.x + (math.cos(self.angle) * self.speed)
		self.y = self.y + (math.sin(self.angle) * self.speed)
		self.rect.x = self.x
		self.rect.y = self.y

		# Check collision with x-edges.
		if self.rect.x < 0:
			self.spawn_particle(particle_group)
			# Reverse angle on x-axis.
			self.angle = math.pi - self.angle

			# Constrain ball to screen size.
			self.x = 0
			self.rect.x = self.x
		elif self.rect.x + self.rect.width > SCREEN_WIDTH:
			self.spawn_particle(particle_group)
			# Reverse angle on x-axis.
			self.angle = math.pi - self.angle

			# Constrain ball to screen size.
			self.x = SCREEN_WIDTH - self.rect.width			
			self.rect.x = self.x

		# Check collision with y-edges.
		if self.rect.y < 0:
			self.spawn_particle(particle_group)
			# Reverse angle on y-axis.
			self.angle = -self.angle

			# Constrain ball to screen size.
			self.y = 0
			self.rect.y = self.y
		elif self.rect.y + self.rect.height > SCREEN_HEIGHT:
			self.spawn_particle(particle_group)
			# Reverse angle on y-axis.
			self.angle = -self.angle

			# Constrain ball to screen size.
			self.y = SCREEN_HEIGHT - self.rect.height
			self.rect.y = self.y
