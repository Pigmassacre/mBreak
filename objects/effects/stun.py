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

A simple stun effect. Paddles effected by this effect have their speed reduced to zero for the duration of the effect.

"""

class Stun(effect.Effect):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/effect/stun.png")

	# Initialize the mixer (so we can load a sound) and load the sound effect.
	pygame.mixer.init(44100, -16, 2, 2048)
	sound_effect = pygame.mixer.Sound("res/sounds/freezing.ogg")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	max_speed_reduction = 100 * settings.GAME_SCALE
	particle_spawn_rate = 120
	particle_spawn_amount = 5

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, parent, paddle_stun_duration, on_kill_function = None, duration = 6000):
		# We start by calling the superconstructor with the given duration value.
		# If parent is a paddle, set the duration to the paddle stun duration.
		if parent.__class__ == paddle.Paddle:
			effect.Effect.__init__(self, parent, paddle_stun_duration)
		else:
			effect.Effect.__init__(self, parent, duration)

		# We store the given stun duration for paddles.
		self.paddle_stun_duration = paddle_stun_duration

		# Store the given on kill function.
		self.on_kill_function = on_kill_function

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0

		# If the parent is a paddle, prevent movement and show an effect on top of the paddle.
		if self.parent.__class__ == paddle.Paddle:
			self.parent.max_speed -= Stun.max_speed_reduction

			# Create the image attribute that is drawn to the surface.
			self.image = Stun.image.copy()

			# Set the rects width and height to the standard values.
			self.rect.width = Stun.width
			self.rect.height = Stun.height

	def on_hit_paddle(self, hit_paddle):
		# Spread the effect to any hit paddles not owned by the parents owner. This effect does not last as long on paddles as it does on any other object.
		if not self.parent.owner == hit_paddle.owner:
			Stun(hit_paddle, self.paddle_stun_duration)
			Stun.sound_effect.play()
			self.destroy()

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		# If it's time, spawn particles.
		self.particle_spawn_time += main_clock.get_time()
		if self.particle_spawn_time >= Stun.particle_spawn_rate:
			# Reset the particle spawn time.
			self.particle_spawn_time = 0

			# Spawn a random amount of particles.
			for _ in range(0, random.randrange(0, Stun.particle_spawn_amount)):
				angle = random.uniform(0, 2 * math.pi)
				speed = random.uniform(0.6 * settings.GAME_SCALE, 0.35 * settings.GAME_SCALE)
				retardation = speed / 25.0
				color_value = random.randint(100, 250)
				color = pygame.Color(color_value, color_value, color_value)
				particle.Particle(self.parent.x + self.parent.rect.width / 3, self.parent.y + self.parent.rect.height / 3, self.parent.rect.width / 3, self.parent.rect.width / 3, angle, speed, retardation, color, 1)

	def on_kill(self):
		# Restore the max speed we removed from the parent.
		if self.parent.__class__ == paddle.Paddle:
			self.parent.max_speed += Stun.max_speed_reduction

		# Run the given on kill function.
		if self.on_kill_function != None:
			self.on_kill_function()