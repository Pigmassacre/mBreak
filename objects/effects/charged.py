__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import objects.groups as groups
import objects.effects.effect as effect
import objects.blocks.block as block
import objects.particle as particle
import settings.settings as settings

"""

This is the "Charged" effect. When a ball carrying this effect hits an enemy block, that block and blocks around it take some extra damage.
The effect is then destroyed.

"""

class Charged(effect.Effect):

	# Initialize the mixer (so we can load a sound) and load the sound effect.
	pygame.mixer.init(44100, -16, 2, 2048)
	sound_effect = pygame.mixer.Sound("res/sounds/thunder.ogg")

	damage_width = 16 * settings.GAME_SCALE
	damage_height = 16 * settings.GAME_SCALE
	damage = 5
	max_speed_reduction = 0.41 * settings.GAME_FPS * settings.GAME_SCALE
	particle_spawn_rate = 450
	particle_spawn_amount = 5

	def __init__(self, parent, duration = 10000):
		# We start by calling the superconstructor with the given duration value.
		effect.Effect.__init__(self, parent, duration)

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0

		self.damage_rect = pygame.rect.Rect(self.rect.x + ((self.rect.width - self.damage_width) / 2), self.rect.y + ((self.rect.height - self.damage_height) / 2), self.damage_width, self.damage_height)

	def on_hit_block(self, hit_block):
		if self.parent.owner == self.real_owner:
			# If the hit block isn't one of the parents owners blocks...
			if hit_block.owner != self.parent.owner:
				# This makes it so that we only play the sound effect once.
				already_played_sound = False

				# We spawn a few extra particles for extra effect!
				self.spawn_particles(hit_block)

				# Lets see if there are any additional blocks to damage.
				for block in hit_block.owner.block_group:
					# We check to see if any of their rects collide with damage_rect.
					if self.damage_rect.colliderect(block.rect):
						# It does, so we damage that block and spawn some particles.
						block.on_hit(Charged.damage)
						self.spawn_particles(block)
						# Play the sound effect if we should.
						if not already_played_sound:
							Charged.sound_effect.play()
							already_played_sound = True

				# Finally, we destroy the effect, since we just want it to be able to discharge once.
				self.destroy()

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		# Position the damage rect.
		self.damage_rect.x = self.rect.x + ((self.rect.width - self.damage_width) / 2)
		self.damage_rect.y = self.rect.y + ((self.rect.height - self.damage_height) / 2)

		if self.parent.owner == self.real_owner:
			# If it's time, spawn particles.
			self.particle_spawn_time += main_clock.get_time()
			if self.particle_spawn_time >= Charged.particle_spawn_rate:
				# Reset the particle spawn time.
				self.particle_spawn_time = 0

				# Spawn a random amount of particles.
				self.spawn_particles(self)
			
	def spawn_particles(self, entity):
		# Spawns a few particles with random color, angle, speed and so on.
		for _ in range(0, random.randrange(2, Charged.particle_spawn_amount)):
			angle = random.uniform(0, 2 * math.pi)
			speed = random.uniform(0.9 * settings.GAME_FPS * settings.GAME_SCALE, 1.4 * settings.GAME_FPS * settings.GAME_SCALE)
			retardation = speed / 46.0
			random_value = random.randint(225, 255)
			color = pygame.Color(random_value, random_value, random.randint(0, 100))
			random_size = random.randint(self.rect.width / 4, self.rect.width / 3)
			particle.Particle(self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2, random_size, random_size, angle, speed, retardation, color, 20 * settings.GAME_FPS)
