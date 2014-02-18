__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.groups as groups
import settings.settings as settings

"""

Laserbeam.

"""

class Laserbeam(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/attack/laser.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, owner):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		self.owner = owner

		self.attack_paddle = None
		for player in groups.Groups.player_group:
			if player == self.owner:
				for paddle in player.paddle_group:
					self.attack_paddle = paddle

		width = settings.LEVEL_WIDTH
		height = self.__class__.height
		self.rect = pygame.Rect(settings.LEVEL_X, settings.LEVEL_Y, width, height)					
		self.figure_out_rect_size()

		# Create the image attribute that is drawn over the parent surface.
		self.image = pygame.surface.Surface((self.rect.width, self.rect.height), pygame.locals.SRCALPHA)

		# Store the image that we use to create the final image.
		self.laser_image = self.__class__.image.copy()

		# Create the final image.
		self.create_final_image()

		# Add self to the projectile group.
		groups.Groups.effect_group.add(self)

	def figure_out_rect_size(self):
		if self.attack_paddle.x < settings.SCREEN_WIDTH / 2.0:
			self.rect.x = self.attack_paddle.rect.x + self.attack_paddle.rect.width
			self.rect.y = self.attack_paddle.rect.y + ((self.attack_paddle.rect.height - self.rect.height) / 2.0)

			# Check collision against blocks.
			least_x = self.rect.x + self.rect.width
			for block in groups.Groups.block_group:
				if block.owner != self.owner:
					if self.rect.colliderect(block.rect):
						if block.rect.x < least_x:
							least_x = block.rect.x

			for paddle in groups.Groups.paddle_group:
				if paddle.owner != self.owner:
					if self.rect.colliderect(paddle.rect):
						if paddle.rect.x < least_x:
							least_x = paddle.rect.x

			self.rect.width = least_x - self.rect.x
			if self.rect.x + self.rect.width > settings.LEVEL_MAX_X:
				self.rect.width = settings.LEVEL_MAX_X - self.rect.x
		else:
			self.rect.x = settings.LEVEL_X
			self.rect.y = self.attack_paddle.rect.y + ((self.attack_paddle.rect.height - self.rect.height) / 2.0)

			# Check collision against blocks.
			max_x = self.rect.x
			for block in groups.Groups.block_group:
				if block.owner != self.owner:
					if self.rect.colliderect(block.rect):
						if block.rect.x + block.rect.width > max_x:
							max_x = block.rect.x + block.rect.width

			for paddle in groups.Groups.paddle_group:
				if paddle.owner != self.owner:
					if self.rect.colliderect(paddle.rect):
						if paddle.rect.x + paddle.rect.width > max_x:
							max_x = paddle.rect.x + paddle.rect.width

			self.rect.width = self.attack_paddle.x - max_x
			self.rect.x = max_x

	def create_final_image(self):
		self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
		for x in range(0, int(math.ceil(self.rect.width / float(self.laser_image.get_width())))):
			for y in range(0, int(math.ceil(self.rect.height / float(self.laser_image.get_height())))):
				self.image.blit(self.laser_image, (self.laser_image.get_width() * x, self.laser_image.get_height() * y))

	def destroy(self):
		self.kill()

	def update(self, main_clock):
		old_width = self.rect.width

		self.rect.width += 1 * settings.GAME_SCALE
		if self.attack_paddle.x > settings.SCREEN_WIDTH / 2.0:
			self.rect.x -= 1 * settings.GAME_SCALE

		for block in groups.Groups.block_group:
			if block.owner != self.owner:
				if self.rect.colliderect(block.rect):
					block.on_hit(60 * main_clock.delta_time)

		self.rect.width -= 1 * settings.GAME_SCALE
		if self.attack_paddle.x > settings.SCREEN_WIDTH / 2.0:
			self.rect.x += 1 * settings.GAME_SCALE
		self.rect.width = settings.LEVEL_WIDTH

		self.figure_out_rect_size()

		if self.rect.width != old_width:
			self.create_final_image()

	def draw(self, surface):
		surface.blit(self.image, self.rect)