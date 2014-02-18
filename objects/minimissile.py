__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.camera as camera
import objects.effects.stun as stun
import objects.effects.explosion as explosion
import objects.dummy as dummy
import objects.missile as missile
import objects.powerups.powerup as powerup
import objects.shadow as shadow
import objects.particle as particle
import objects.ball as ball
import objects.groups as groups
import settings.settings as settings

"""

This is the MiniMissile effect. When picked up by a ball, it applies the "Charged" effect to that ball only.

"""

def convert():
	# We put this here so the game-class can call this method to "preload" the image used for this powerup.
	# I could probably put this in the constructor of the powerup, but I worry about performance so I make sure to only do it once.
	MiniMissile.image.convert_alpha()

class MiniMissile(missile.Missile):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/attack/minimissile.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	particle_spawn_rate = 25
	particle_spawn_amount = 5

	speed = 0.07 * settings.GAME_FPS * settings.GAME_SCALE
	acceleration = 0.035 * settings.GAME_FPS * settings.GAME_SCALE

	# These particles are spawned when the MiniMissile hits its target.
	hit_particle_min_amount = 12
	hit_particle_max_amount = 18
	hit_particle_min_speed = 1 * settings.GAME_FPS * settings.GAME_SCALE
	hit_particle_max_speed = 2.5 * settings.GAME_FPS * settings.GAME_SCALE

	# The amount of damage the MiniMissile deals to a hit block.
	damage = 2.5

	paddle_stun_duration = 100

	paddle_shake_strength = 0.33
	paddle_shake_duration = 350
	block_shake_strength = 0.66
	block_shake_duration = 350

	# These variables affect how the MiniMissile homes to its target.
	angle_correction = 0.0005 * settings.GAME_FPS
	angle_correction_rate = 0.1 * settings.GAME_FPS
	max_speed = 3 * settings.GAME_FPS * settings.GAME_SCALE

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y, angle, owner, target):
		super(MiniMissile, self).__init__(x, y, angle, owner, target)