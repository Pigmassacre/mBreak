__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.camera as camera
import objects.powerups.powerup as powerup
import objects.shadow as shadow
import objects.particle as particle
import objects.ball as ball
import objects.groups as groups
import settings.settings as settings

"""

This is the Firework effect. When it is destroyed, it spawns particles in every direction! Woo, pretty!

"""

class Firework(pygame.sprite.Sprite):

	# Initialize the mixer (so we can load a sound) and load the sound effects.
	pygame.mixer.init(44100, -16, 2, 2048)
	sound_effects = []
	sound_effects.append(pygame.mixer.Sound("res/sounds/explosion1.ogg"))
	sound_effects.append(pygame.mixer.Sound("res/sounds/explosion2.ogg"))
	sound_effects.append(pygame.mixer.Sound("res/sounds/explosion3.ogg"))
	sound_effects.append(pygame.mixer.Sound("res/sounds/explosion4.ogg"))

	width = 2 * settings.GAME_SCALE
	height = 2 * settings.GAME_SCALE
	color = pygame.Color(255, 255, 255)

	speed = 0.05 * settings.GAME_FPS * settings.GAME_SCALE
	max_speed = 5 * settings.GAME_FPS * settings.GAME_SCALE
	acceleration = 0.25 * settings.GAME_FPS * settings.GAME_SCALE

	def __init__(self, x, y, angle, duration):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, Firework.width, Firework.height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# We store the given angle of the Firework.
		self.angle = angle

		# We store the given speed of the Firework.
		self.speed = Firework.speed

		# We store the time passed, in order to know when to explode.
		self.time_passed = 0
		self.duration = duration

		# Store the given acceleration.
		self.acceleration = Firework.acceleration

		# Add self to the projectile group.
		groups.Groups.projectile_group.add(self)

	def destroy(self):
		self.kill()

		for _ in range(64):
			width = random.uniform(1 * settings.GAME_SCALE, 2.5 * settings.GAME_SCALE)
			angle = random.uniform(0, 2 * math.pi)
			speed = random.uniform(1.0 * settings.GAME_FPS * settings.GAME_SCALE, 2.25 * settings.GAME_FPS * settings.GAME_SCALE)
			retardation = 0.1 * settings.GAME_FPS
			color = pygame.Color(255, 0, 0)
			color.hsla = (random.uniform(0, 360), color.hsla[1], color.hsla[2], color.hsla[3])
			a_particle = particle.Particle(self.x + self.rect.width / 2.0, self.y + self.rect.height / 2.0, width, width, angle, speed, retardation, color, 2 * settings.GAME_FPS)
			a_particle.kill_outside_level = False
			a_particle.kill_when_speed_reaches_zero = False
			a_particle.gravity = 0.05 * settings.GAME_SCALE

		# Play a random sound from the sound_effects list.
		sound = Firework.sound_effects[random.randrange(0, len(Firework.sound_effects))].play()
		if not sound is None:
			sound.set_volume(settings.SOUND_VOLUME)

	def update(self, main_clock):
		self.time_passed += main_clock.get_time()
		if self.time_passed >= self.duration:
			# When the duration runs out, we destroy ourselves.
			self.destroy()

		# Update the speed according to the acceleration.
		self.speed += self.acceleration * main_clock.time_scale

		# Make sure speed doesn't go over max speed.
		if self.speed > self.max_speed:
			self.speed = self.max_speed

		# Move the firework with speed in consideration.
		self.x = self.x + (math.cos(self.angle) * self.speed * main_clock.delta_time)
		self.y = self.y + (math.sin(self.angle) * self.speed * main_clock.delta_time)
		self.rect.x = self.x
		self.rect.y = self.y

	def draw(self, surface):
		surface.fill(self.color, (self.rect.x - camera.CAMERA.x, self.rect.y - camera.CAMERA.y, self.rect.width, self.rect.height))