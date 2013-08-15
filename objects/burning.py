__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import objects.groups as groups
import objects.effect as effect
import objects.particle as particle
import settings.settings as settings

class Burning(effect.Effect):

	damage_per_second = 1.0
	particle_spawn_rate = 100
	particle_spawn_amount = 3

	def __init__(self, parent, duration = 10000):
		# We start by calling the superconstructor.
		effect.Effect.__init__(self, parent, duration)

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0

	def on_hit_block(self, hit_block):
		# Spread the effect to any hit blocks.
		Burning(hit_block)

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		# If the parent has health, deal damage to it.
		if hasattr(self.parent, "health"):
			self.parent.health -= Burning.damage_per_second / main_clock.get_time()

		# If it's time, spawn particles.
		self.particle_spawn_time += main_clock.get_time()
		if self.particle_spawn_time >= Burning.particle_spawn_rate:
			# Reset the particle spawn time.
			self.particle_spawn_time = 0

			# Spawn a random amount of particles.
			for _ in range(0, random.randrange(1, Burning.particle_spawn_amount)):
				angle = random.uniform(0, 2 * math.pi)
				speed = random.uniform(0.75 * settings.GAME_SCALE, 0.9 * settings.GAME_SCALE)
				retardation = speed / 24.0
				color = pygame.Color(random.randint(200, 255), random.randint(0, 255), 0)
				particle.Particle(self.parent.x + self.parent.rect.width / 2, self.parent.y + self.parent.rect.height / 2, self.parent.rect.width / 4, self.parent.rect.width / 4, angle, speed, retardation, color, 5)
