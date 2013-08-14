__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import objects.groups as groups
import objects.effect as effect
import objects.paddle as paddle
import objects.particle as particle
import settings.settings as settings

class Freezing(effect.Effect):

	acceleration_reduction = 2 * settings.GAME_SCALE
	paddle_freezing_duration = 2000
	particle_spawn_rate = 150
	particle_spawn_amount = 2

	def __init__(self, parent, duration = 10000):
		# We start by calling the superconstructor.
		effect.Effect.__init__(self, parent, duration)

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0

		# If the parent is a paddle, prevent movement.
		if self.parent.__class__ == paddle.Paddle:
			self.parent.acceleration -= Freezing.acceleration_reduction

	def on_hit_paddle(self, hit_paddle):
		# Spread the effect to any hit paddles. This effect does not last as long on paddles as it does on any other object.
		Freezing(hit_paddle, Freezing.paddle_freezing_duration)

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		# If it's time, spawn particles.
		self.particle_spawn_time += main_clock.get_time()
		if self.particle_spawn_time >= Freezing.particle_spawn_rate:
			# Reset the particle spawn time.
			self.particle_spawn_time = 0

			# Spawn a random amount of particles.
			for _ in range(0, random.randrange(0, Freezing.particle_spawn_amount)):
				angle = random.uniform(0, 2 * math.pi)
				speed = 0.8
				retardation = speed / 36.0
				color = pygame.Color(random.randint(0, 50), random.randint(0, 255), random.randint(220, 255))
				particle.Particle(self.parent.x + self.parent.rect.width / 2, self.parent.y + self.parent.rect.height / 2, self.parent.rect.width / 4, self.parent.rect.width / 4, angle, speed, retardation, color, 5)

	def on_kill(self):
		# We make sure to call the supermethod.
		effect.Effect.on_kill(self)

		# Restore the acceleration we removed from the parent.
		if self.parent.__class__ == paddle.Paddle:
			self.parent.acceleration += Freezing.acceleration_reduction