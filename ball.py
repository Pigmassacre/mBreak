__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import paddle
from settings import *

class Ball(pygame.sprite.Sprite):

	def __init__(self, x, y, width, height, angle, speed, max_speed, image_path, owner):
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

		# Create the image attribute that is drawn to the surface.
		self.image = pygame.image.load(image_path)

		# Set the owner.
		self.owner = owner

		if DEBUG_MODE:
			print("Ball spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ") with angle " + str(self.angle) + " and speed " + str(self.speed))

	def update(self, ball_group, paddle_group):
		# Check collision with paddles.
		for paddle in paddle_group:
			if self.rect.colliderect(paddle.rect):
				if self.rect.bottom >= paddle.rect.top and self.rect.top < paddle.rect.top:
					# Top side of paddle collided with. Compare with edges:
					if paddle.rect.left - self.rect.left > paddle.rect.top - self.rect.top:
						# The ball collides more with the left side than top side.
						self.angle = math.pi - self.angle

						# Place ball to the left of the paddle.
						self.x = paddle.rect.left - self.rect.width - 1
						self.rect.x = self.x
					elif self.rect.right - paddle.rect.right > paddle.rect.top - self.rect.top:
						# The ball collides more with the right side than top side.
						self.angle = math.pi - self.angle

						# Place ball to the right of the paddle.
						self.x = paddle.rect.right + 1
						self.rect.x = self.x
					else:
						# The ball collides more with the top side than any other side.
						self.angle = -self.angle

						# Place ball on top of the paddle.
						self.y = paddle.rect.top - self.rect.height - 1
						self.rect.y = self.y
				elif self.rect.top <= paddle.rect.bottom and self.rect.bottom > paddle.rect.bottom:
					# Bottom side of paddle collided with. Compare with edges:
					if paddle.rect.left - self.rect.left > self.rect.bottom - paddle.rect.bottom:
						# The ball collides more with the left side than top side.
						self.angle = math.pi - self.angle

						# Place ball to the left of the paddle.
						self.x = paddle.rect.left - self.rect.width - 1
						self.rect.x = self.x
					elif self.rect.right - paddle.rect.right > self.rect.bottom - paddle.rect.bottom:
						# The ball collides more with the right side than top side.
						self.angle = math.pi - self.angle

						# Place ball to the right of the paddle.
						self.x = paddle.rect.right + 1
						self.rect.x = self.x
					else:
						# The ball collides more with the bottom side than any other side.
						self.angle = -self.angle

						# Place ball beneath the paddle.
						self.y = paddle.rect.bottom + 1
						self.rect.y = self.y
				elif self.rect.right >= paddle.rect.left and self.rect.left < paddle.rect.left:
					# Left side of paddle collided with.
					self.angle = math.pi - self.angle

					# Place ball to the left of the paddle.
					self.x = paddle.rect.left - self.rect.width - 1
					self.rect.x = self.x
				elif self.rect.left <= paddle.rect.right and self.rect.right > paddle.rect.right:
					# Right side of paddle collided with.
					self.angle = math.pi - self.angle

					# Place ball to the right of the paddle.
					self.x = paddle.rect.right + 1
					self.rect.x = self.x
				
		# Check collision with other balls.
		ball_group.remove(self)
		ball_collide_list = pygame.sprite.spritecollide(self, ball_group, False)
		for ball in ball_collide_list:
			if self.rect.bottom >= ball.rect.top and self.rect.top < ball.rect.top:
				# Top side of ball collided with. Compare with edges:
				if ball.rect.left - self.rect.left > ball.rect.top - self.rect.top:
					# The ball collides more with the left side than top side.
					# Place ball to the left of the ball.
					self.x = ball.rect.left - self.rect.width - 1
					self.rect.x = self.x
				elif self.rect.right - ball.rect.right > ball.rect.top - self.rect.top:
					# The ball collides more with the right side than top side.
					# Place ball to the right of the ball.
					self.x = ball.rect.right + 1
					self.rect.x = self.x
				else:
					# Place ball on top of the ball.
					self.y = ball.rect.top - self.rect.height - 1
					self.rect.y = self.y
			elif self.rect.top <= ball.rect.bottom and self.rect.bottom > ball.rect.bottom:
				# Bottom side of ball collided with.
				if ball.rect.left - self.rect.left > self.rect.bottom - ball.rect.bottom:
					# The ball collides more with the left side than top side.
					# Place ball to the left of the ball.
					self.x = ball.rect.left - self.rect.width - 1
					self.rect.x = self.x
				elif self.rect.right - ball.rect.right > self.rect.bottom - ball.rect.bottom:
					# The ball collides more with the right side than top side.
					# Place ball to the right of the ball.
					self.x = ball.rect.right + 1
					self.rect.x = self.x
				else:
					# The ball collides more with the bottom side than any other side.
					# Place ball beneath the ball.
					self.y = ball.rect.bottom + 1
					self.rect.y = self.y
			elif self.rect.right >= ball.rect.left and self.rect.left < ball.rect.left:
				# Left side of ball collided with.
				# Place ball to the left of the ball.
				self.x = ball.rect.left - self.rect.width - 1
				self.rect.x = self.x
			elif self.rect.left <= ball.rect.right and self.rect.right > ball.rect.right:
				# Right side of ball collided with.
				# Place ball to the right of the ball.
				self.x = ball.rect.right + 1
				self.rect.x = self.x

			# Handle self.
			delta_x = self.rect.centerx - ball.rect.centerx
			delta_y = self.rect.centery - ball.rect.centery
			self.angle = math.atan2(delta_y, delta_x)

			# Handle other ball.
			delta_x = ball.rect.centerx - self.rect.centerx
			delta_y = ball.rect.centery - self.rect.centery
			ball.angle = math.atan2(delta_y, delta_x)
		ball_group.add(self)

		# Check collision with x-edges.
		if self.rect.x < 0:
			self.angle = math.pi - self.angle

			# Constrain ball to screen size.
			self.x = 0
			self.rect.x = self.x
		elif self.rect.x + self.rect.width > SCREEN_WIDTH:
			self.angle = math.pi - self.angle

			# Constrain ball to screen size.
			self.x = SCREEN_WIDTH - self.rect.width			
			self.rect.x = self.x

		# Check collision with y-edges.
		if self.rect.y < 0:
			self.angle = -self.angle

			# Constrain ball to screen size.
			self.y = 0
			self.rect.y = self.y
		elif self.rect.y + self.rect.height > SCREEN_HEIGHT:
			self.angle = -self.angle

			# Constrain ball to screen size.
			self.y = SCREEN_HEIGHT - self.rect.height
			self.rect.y = self.y
			
		# Finally, move the ball with speed in consideration.
		self.x = self.x + (math.cos(self.angle) * self.speed)
		self.y = self.y + (math.sin(self.angle) * self.speed)
		self.rect.x = self.x
		self.rect.y = self.y

		#if DEBUG_MODE:
		#	print("New pos @ (" + str(self.x) + ", " + str(self.y) + ")")
