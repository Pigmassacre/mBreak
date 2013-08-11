__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import other.useful as useful
import objects.shadow as shadow
import objects.groups as groups
import objects.particle as particle
import gui.textitem as textitem
import settings.settings as settings

class Block(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/block/block.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	particle_spawn_amount = 4
	particle_size = 0.75 * settings.GAME_SCALE

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, owner, x, y, width, height, health):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# The owner is the player that owns the block.
		self.owner = owner

		# Set the health. This is the amount of damage the block can take before it breaks.
		self.health = health

		# Create the image attribute that is drawn to the surface.
		self.image = Block.image.copy()

		# Colorize the block.
		self.color = self.owner.color
		useful.colorize_image(self.image, self.color)

		# Create a shadow.
		self.shadow = shadow.Shadow(self)
		
		# Add self to owners block_group and main block_group.
		self.owner.block_group.add(self)
		groups.Groups.block_group.add(self)

	def on_hit(self, damage):
		self.spawn_particles()

		self.health = self.health - damage
		if self.health <= 0:
			self.kill()
			self.shadow.kill()

	def spawn_particles(self):
		for _ in range(0, Block.particle_spawn_amount):
			angle = random.uniform(0, math.pi)
			speed = 5
			retardation = 0.25
			alpha_step = 5
			particle.Particle(self.x, self.y, Block.particle_size, Block.particle_size, angle, speed, retardation, self.color, alpha_step)