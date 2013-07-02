__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import paddle
from settings import *

class Ball(pygame.sprite.Sprite):

	def __init__(self, x, y, width, height, angle, speed, image_path):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# Set the angle variable.
		self.angle = angle

		# Set the speed variable.
		self.speed = speed

		# Create the image attribute that is drawn to the surface.
		self.image = pygame.image.load(image_path)

		if DEBUG_MODE:
			print("Ball spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ") with angle " + str(self.angle) + " and speed " + str(self.speed))

	def update(self, ball_group, paddle_group):
		# Check collision with paddles.
		for paddle in paddle_group:
			if self.rect.colliderect(paddle.rect):
				delta_x = self.rect.centerx - paddle.rect.centerx
				delta_y = self.rect.centery - paddle.rect.centery
				self.angle = math.atan2(delta_x, delta_y)
				"""
				# Nudge the ball.
				self.x = self.x + math.cos(self.angle)
				self.y = self.y + math.sin(self.angle)
				self.rect.x = self.x
				self.rect.y = self.y"""

		# Check collision with other balls.
		ball_group.remove(self)
		ball_collide_list = pygame.sprite.spritecollide(self, ball_group, False)
		for ball in ball_collide_list:
			# Handle self collision response.
			delta_x = self.rect.centerx - ball.rect.centerx
			delta_y = self.rect.centery - ball.rect.centery
			self.angle = math.atan2(delta_x, delta_y)
			"""
			# Nudge the ball.
			self.x = self.x + math.cos(self.angle)
			self.y = self.y + math.sin(self.angle)
			self.rect.x = self.x
			self.rect.y = self.y
			"""
			# Handle other ball collision response.
			delta_x = ball.rect.x - self.rect.x
			delta_y = ball.rect.y - self.rect.y
			ball.angle = math.atan2(delta_x, delta_y)
			"""
			# Nudge the other ball.
			ball.x = ball.x + math.cos(ball.angle)
			ball.y = ball.y + math.sin(ball.angle)
			ball.rect.x = ball.x
			ball.rect.y = ball.y"""

			if DEBUG_MODE:
				print("Collision @ (" + str(ball.rect.x) + ", " + str(ball.rect.y) + ")")
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
