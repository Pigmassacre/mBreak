__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import objects.groups as groups
import objects.effects.effect as effect
import objects.paddle as paddle
import objects.particle as particle
import settings.settings as settings

"""

This is the Freezing effect. Balls that have this effect will spread it to enemy paddles, and paddles that have this effect
will be frozen, having their max_speed lowered for a short duration.

"""

class Freezing(effect.Effect):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/effect/freezing.png")

	# Initialize the mixer (so we can load a sound) and load the sound effect.
	pygame.mixer.init(44100, -16, 2, 2048)
	sound_effect = pygame.mixer.Sound("res/sounds/freezing.ogg")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	max_speed_reduction = 0.41 * settings.GAME_SCALE
	paddle_freezing_duration = 1100
	particle_spawn_rate = 600
	particle_spawn_amount = 2
	duration = 10000

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, parent, duration = None):
		# We check if a duration has been given.
		if not duration == None:
			# We start by calling the superconstructor with the given duration value.
			effect.Effect.__init__(self, parent, duration)
		else:
			# We start by calling the superconstructor with the standard duration value.
			effect.Effect.__init__(self, parent, Freezing.duration)

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0

		# If the parent is a paddle, prevent movement and show an effect on top of the paddle.
		if self.parent.__class__ == paddle.Paddle:
			self.parent.max_speed -= Freezing.max_speed_reduction

			# Create the image attribute that is drawn to the surface.
			self.image = Freezing.image.copy()

			# Set the rects width and height to the standard values.
			self.rect.width = Freezing.width
			self.rect.height = Freezing.height

	def on_hit_paddle(self, hit_paddle):
		# Spread the effect to any hit paddles not owned by the parents owner. This effect does not last as long on paddles as it does on any other object.
		if not self.parent.owner == hit_paddle.owner:
			Freezing(hit_paddle, Freezing.paddle_freezing_duration)
			Freezing.sound_effect.play()

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
				speed = random.uniform(0.2 * settings.GAME_SCALE, 0.35 * settings.GAME_SCALE)
				retardation = speed / 76.0
				color = pygame.Color(random.randint(0, 50), random.randint(125, 255), random.randint(220, 255))
				particle.Particle(self.parent.x + self.parent.rect.width / 2, self.parent.y + self.parent.rect.height / 2, self.parent.rect.width / 2, self.parent.rect.width / 2, angle, speed, retardation, color, 1)

	def on_kill(self):
		# Restore the acceleration we removed from the parent.
		if self.parent.__class__ == paddle.Paddle:
			self.parent.max_speed += Freezing.max_speed_reduction