__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import other.useful as useful
from libs import pyganim
import objects.powerups.powerup as powerup
import objects.effects.timeout as timeout
import objects.effects.freezing as freezing
import objects.shadow as shadow
import objects.particle as particle
import objects.ball as ball
import objects.groups as groups
import settings.settings as settings

"""

This is the Frost powerup. When picked up by a ball, it applys the "freezing" effect to that ball and all the other balls of
that balls owner. 

"""

def convert():
	# We put this here so the game-class can call this method to "preload" the image used for this powerup.
	# I could probably put this in the constructor of the powerup, but I worry about performance so I make sure to only do it once.
	Frost.image_sheet.convert_alpha()
	#Frost.image_02.convert_alpha()
	#Frost.image_03.convert_alpha()

class Frost(powerup.Powerup):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image_sheet = pygame.image.load("res/powerup/frost.png")
	#image_02 = pygame.image.load("res/powerup/frost_02.png")
	#image_03 = pygame.image.load("res/powerup/frost_03.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image_sheet.get_width() * settings.GAME_SCALE
	height = image_sheet.get_height() * settings.GAME_SCALE
	frame_width = width
	frame_height = width
	particle_spawn_rate = 600
	particle_spawn_amount = 2

	# Scale image to settings.GAME_SCALE.
	image_sheet = pygame.transform.scale(image_sheet, (width, height))
	#image_02 = pygame.transform.scale(image_02, (width, height))
	#image_03 = pygame.transform.scale(image_03, (width, height))

	def __init__(self, x, y):
		# We start by calling the superconstructor.
		powerup.Powerup.__init__(self, x, y, Frost.width, Frost.height)

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0

		# Load the image file.
		# Generate the animation frames.
		self.frames = useful.create_frames_from_sheet(Frost.image_sheet, Frost.frame_width, Frost.frame_height)
		#self.image_01 = Frost.image_01.copy()
		#self.image_02 = Frost.image_02.copy()
		#self.image_03 = Frost.image_03.copy()
		self.image = self.frames[1]

		# This affects how far the powerup must be from it's center y to change frames.
		self.center_y_grace = 0.2 * settings.GAME_SCALE

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

	def create_effect(self, entity):
		return freezing.Freezing(entity)

	def hit(self, entity):
		# Call the supermethod, it takes care of killing the powerup and printing debug message(s).
		powerup.Powerup.hit(self, entity)
		self.shadow.kill()
		
		# Create a speed effect to be added to the ball.
		created_effect = self.create_effect(entity)

		# Add this effect to the owner of the ball.
		entity.owner.effect_group.add(created_effect)

		# Store a powerup of this type in entity owners powerup group, so we can display the powerups collected by a player.
		entity.owner.add_powerup(self.__class__, created_effect)

	def update(self, main_clock):
		# We make sure to call the supermethod.
		powerup.Powerup.update(self, main_clock)

		# Update the current image.
		if self.y < self.center_y - self.center_y_grace:
			self.image = self.frames[0]
		elif self.y > self.center_y + self.center_y_grace:
			self.image = self.frames[2]
		else:
			self.image = self.frames[1]

		# If it's time, spawn particles.
		self.particle_spawn_time += main_clock.get_time()
		if self.particle_spawn_time >= Frost.particle_spawn_rate:
			# Reset the particle spawn time.
			self.particle_spawn_time = 0

			# Spawn a random amount of particles.
			for _ in range(0, random.randrange(0, Frost.particle_spawn_amount)):
				angle = random.uniform(0, 2 * math.pi)
				speed = random.uniform(0.2 * settings.GAME_FPS * settings.GAME_SCALE, 0.35 * settings.GAME_FPS * settings.GAME_SCALE)
				retardation = speed / 76.0
				color = pygame.Color(random.randint(0, 50), random.randint(125, 255), random.randint(220, 255))
				particle.Particle(self.x + self.rect.width / 2, self.y + self.rect.height / 2, self.rect.width / 4, self.rect.width / 4, angle, speed, retardation, color, 1 * settings.GAME_FPS)