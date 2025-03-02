__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import copy
import objects.shadow as shadow
import objects.groups as groups
import objects.particle as particle
import objects.effects.flash as flash
import settings.settings as settings
from settings.sounds import EXPLOSION_SOUND, play_sound

"""

This is the base class of all blocks in the game. A block has health, and when that health reaches zero the block is destroyed.

"""

class Block(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/block/block.png")
	half_health_image = pygame.image.load("res/block/block.png")

	# Initialize the sound effect.
	sound_effect = EXPLOSION_SOUND

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width()
	height = image.get_height()
	particle_spawn_amount = 4
	particle_size = 0.75
	half_health_blend_color = pygame.Color(128, 128, 128)

	# Death particle values
	death_particle_spawn_amount = 15
	death_particle_size = 1.2
	death_particle_min_speed = 0.5 * settings.GAME_FPS
	death_particle_max_speed = 0.9 * settings.GAME_FPS
	death_particle_alpha_step = 3 * settings.GAME_FPS

	# On hit effect values.
	hit_effect_start_color = pygame.Color(255, 255, 255, 255)
	hit_effect_final_color = pygame.Color(255, 255, 255, 0)
	hit_effect_tick_amount = 15 * settings.GAME_FPS

	# Scale image.
	image = pygame.transform.scale(image, (width, height))
	half_health_image = pygame.transform.scale(image, (width, height))

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

		# We also store the health as the maximum amount of health the block has.
		self.max_health = health
		
		# Add self to owners block_group and main block_group.
		self.owner.block_group.add(self)
		groups.Groups.block_group.add(self)

		# Create an effect group to handle effects on this block.
		self.effect_group = pygame.sprite.Group()

	def hurt(self, damage):
		# Reduce the health.
		self.health = self.health - damage

		# Change the image to the half health image if health is under half.
		if self.health <= self.max_health / 2:
			self.image = self.half_health_image

	def on_hit(self, damage):
		# Damage self.
		self.hurt(damage)

		# Create a new on hit effect.
		self.effect_group.add(flash.Flash(self, copy.copy(Block.hit_effect_start_color), copy.copy(Block.hit_effect_final_color), Block.hit_effect_tick_amount))

		# Spawn some particles.
		for _ in range(0, Block.particle_spawn_amount):
			angle = random.uniform(0, 2 * math.pi)
			speed = 5 * settings.GAME_FPS
			retardation = speed / 24.0  # Calculate retardation based on speed like death particles
			alpha_step = 5 * settings.GAME_FPS
			particle.Particle(self.x + self.rect.width / 2, self.y + self.rect.height / 2, Block.particle_size, Block.particle_size, angle, speed, retardation, self.color, alpha_step)

	def destroy(self):
		# Takes care of killing self and shadow.
		self.kill()
		self.shadow.kill()

	def spawn_death_particles(self):
		# Spawn particles in all directions when the block is destroyed
		for i in range(0, Block.death_particle_spawn_amount):
			# Calculate angle to spread particles in a circle
			angle = (i / Block.death_particle_spawn_amount) * 2 * math.pi
			
			# Random speed between min and max
			speed = random.uniform(Block.death_particle_min_speed, Block.death_particle_max_speed)
			retardation = speed / 24.0
			
			# Randomly choose between block color and a brighter variant
			if random.random() > 0.3:  # 70% chance of bright particle
				# Create a brighter version of the block's color
				r = min(255, self.color.r + random.randint(50, 100))
				g = min(255, self.color.g + random.randint(50, 100))
				b = min(255, self.color.b + random.randint(50, 100))
				particle_color = pygame.Color(r, g, b)
			else:
				particle_color = self.color
			
			# Create particle with random variations
			width = random.uniform(Block.death_particle_size * 0.7, Block.death_particle_size * 1.3)
			particle.Particle(
				self.x + self.rect.width / 2, 
				self.y + self.rect.height / 2,
				width,  # Random size variation
				width,
				angle + random.uniform(-0.3, 0.3),  # More angle variation
				speed,
				retardation,
				particle_color,
				Block.death_particle_alpha_step
			)

	def update(self):
		# Kill the block if health is reduced to zero.
		if self.health <= 0:
			# Spawn death particles before destroying
			self.spawn_death_particles()
			
			self.destroy()
			for effect in self.effect_group:
				effect.destroy()

			# Play a sound effect.
			play_sound(Block.sound_effect)
