__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.powerups.powerup as powerup
import objects.shadow as shadow
import objects.particle as particle
import objects.ball as ball
import objects.groups as groups
import settings.settings as settings

"""

This is the Missile effect. When picked up by a ball, it applies the "Charged" effect to that ball only.

"""

def convert():
	# We put this here so the game-class can call this method to "preload" the image used for this powerup.
	# I could probably put this in the constructor of the powerup, but I worry about performance so I make sure to only do it once.
	Missile.image.convert_alpha()

class Missile(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/missile.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	particle_spawn_rate = 65
	particle_spawn_amount = 4

	# The amount of damage the missile deals to a hit block.
	damage = 10

	# These variables affect how the missile homes to its target.
	angle_correction = 0.1
	max_speed = 2 * settings.GAME_SCALE

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y, angle, speed, acceleration, owner, target):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, Missile.width, Missile.height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# We store the given angle of the Missile.
		self.angle = angle

		# We store the given speed of the Missile.
		self.speed = speed

		# Store the given acceleration.
		self.acceleration = acceleration

		# Store the owner.
		self.owner = owner

		# Store the target.
		self.target = target

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0

		# Load the image file.
		self.image = Missile.image.copy()

		# Rotate it to the given angle.
		old_center = self.rect.center
		self.image = pygame.transform.rotate(self.image, self.angle * (180 / math.pi))
		self.rect = self.image.get_rect()
		self.rect.center = old_center
		print("AT START ANGLE IS " + str(self.angle))

		# Store the original, unrotated version of the image.
		self.original_image = self.image.copy()

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

		# Add self to the projectile group.
		groups.Groups.projectile_group.add(self)

		# If we want, we can connect powerups to this effect that is killed when this missile is killed. Primarily used to 
		# connect the powerups that are displayed on the player.
		self.displayed_powerups = []

	def destroy(self):
		self.kill()
		self.shadow.kill()

		# Destroy all powerups that are connected to this missile.
		for powerup in self.displayed_powerups:
			powerup.destroy(False)

	def update(self, main_clock):
		# Check if we have collided with the target block.
		blocks_collide_list = pygame.sprite.spritecollide(self, self.target.owner.block_group, False)
		for block in blocks_collide_list:
			if block == self.target:
				self.destroy()
				self.target.on_hit(Missile.damage)

		# Keep angle between pi and -pi.
		if self.angle > math.pi:
			self.angle -= math.pi * 2
		elif self.angle < -math.pi:
			self.angle += math.pi * 2

		# Figure out the angle to the target
		delta_x = self.target.rect.centerx - self.rect.centerx
		delta_y = self.target.rect.centery - self.rect.centery
		angle_to_target = math.atan2(delta_y, delta_x)

		# Calculate the relative angle to target.
		relative_angle_to_target = angle_to_target - self.angle

		# Correct our own angle so it's closer to the target.
		if relative_angle_to_target > math.pi:
			relative_angle_to_target -= math.pi * 2
		elif relative_angle_to_target < -math.pi:
			relative_angle_to_target += math.pi * 2

		self.angle += relative_angle_to_target * self.angle_correction
		print("now angle is " + str(self.angle))
		# Update the speed according to the acceleration.
		self.speed += self.acceleration

		# Move the missile with speed in consideration.
		self.x = self.x + (math.cos(self.angle) * self.speed)
		self.y = self.y + (math.sin(self.angle) * self.speed)
		self.rect.x = self.x
		self.rect.y = self.y
		
		# Rotate the image to the angle.
		old_center = self.rect.center
		self.image = pygame.transform.rotate(self.original_image, (self.angle + math.pi) * (180 / math.pi)) # WTF DOES NOT WORK OMG
		self.rect = self.image.get_rect()
		self.rect.center = old_center

		# If it's time, spawn particles.
		self.particle_spawn_time += main_clock.get_time()
		if self.particle_spawn_time >= Missile.particle_spawn_rate:
			# Reset the particle spawn time.
			self.particle_spawn_time = 0

			# Spawn a random amount of particles.
			for _ in range(0, random.randrange(1, Missile.particle_spawn_amount)):
				angle = self.angle + random.uniform(math.pi - (math.pi / 32), math.pi + (math.pi / 32))
				speed = random.uniform(0.75 * settings.GAME_SCALE, 0.9 * settings.GAME_SCALE)
				retardation = speed / 24.0
				color = pygame.Color(random.randint(200, 255), random.randint(0, 255), 0)
				particle.Particle(self.x + self.rect.width / 2, self.y + self.rect.height / 2, self.rect.height / 6, self.rect.height / 6, angle, speed, retardation, color, 5)