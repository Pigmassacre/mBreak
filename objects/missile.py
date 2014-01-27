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
	particle_spawn_rate = 25
	particle_spawn_amount = 5
	particle_width = height / 6
	particle_height = height / 6

	# These particles are spawned when the missile hits its target.
	hit_particle_min_amount = 12
	hit_particle_max_amount = 18
	hit_particle_min_speed = 2 * settings.GAME_SCALE
	hit_particle_max_speed = 3 * settings.GAME_SCALE

	# The amount of damage the missile deals to a hit block.
	damage = 10

	# These variables affect how the missile homes to its target.
	angle_correction = 0.01
	angle_correction_rate = 0.005
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

		# Store the original, unrotated version of the image.
		self.original_image = self.image.copy()

		# Store the angle to rotate the image separately.
		self.image_angle = self.angle

		# Rotate it to the given angle.
		self.rotate_image(self.image_angle * (180 / math.pi))

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

		# Add self to the projectile group.
		groups.Groups.projectile_group.add(self)

		# If we want, we can connect powerups to this effect that is killed when this missile is killed. Primarily used to 
		# connect the powerups that are displayed on the player.
		self.displayed_powerups = []

	def rotate_image(self, angle):
		old_center = self.rect.center
		self.image = pygame.transform.rotate(self.original_image, angle)
		self.rect = self.image.get_rect()
		self.rect.center = old_center

	def destroy(self):
		self.kill()
		self.shadow.kill()

		# Destroy all powerups that are connected to this missile.
		for powerup in self.displayed_powerups:
			powerup.destroy(False)

	def on_hit_block(self, block):
		# Destroy ourselves.
		self.destroy()

		# Tell the block that we've hit it.
		block.on_hit(Missile.damage)

		# Spawn some particles.
		self.spawn_destroy_particles()

	def spawn_destroy_particles(self):
		# Spawn a random amount of particles.
		for _ in range(0, random.randrange(Missile.hit_particle_min_amount, Missile.hit_particle_max_amount)):
			angle = self.angle + math.pi
			angle += random.uniform(math.pi - (math.pi / 16), math.pi + (math.pi / 16))
			speed = random.uniform(Missile.hit_particle_min_speed, Missile.hit_particle_max_speed)
			retardation = speed / 24.0
			color = pygame.Color(random.randint(200, 255), random.randint(0, 255), 0)
			particle.Particle(self.x + self.rect.width / 2, self.y + self.rect.height / 2, Missile.particle_width, Missile.particle_height, angle, speed, retardation, color, 5)

	def update(self, main_clock):
		# Check if we have collided with the target block.
		blocks_collide_list = pygame.sprite.spritecollide(self, self.target.owner.block_group, False)
		for block in blocks_collide_list:
			if block == self.target:
				self.on_hit_block(block)

		# If the target is already destroyed, choose a new target.
		if self.target.health <= 0 or self.target == None:
			# Create a list of all available blocks to target.
			block_list = []
			for player in groups.Groups.player_group:
				if player != self.owner:
					block_list = player.block_group.sprites()

			# If the list is not empty, set a random block as the target.
			if block_list:
				self.target = random.choice(block_list)
			else:
				# If the list is empty, simply destroy ourselves.
				self.destroy()
				self.spawn_destroy_particles()

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

		# Map relative angle to -pi <= angle <= +pi.
		if relative_angle_to_target > math.pi:
			relative_angle_to_target -= math.pi * 2
		elif relative_angle_to_target < -math.pi:
			relative_angle_to_target += math.pi * 2

		# Correct our own angle so it's closer to the target.
		self.angle += relative_angle_to_target * self.angle_correction

		# Update the speed according to the acceleration.
		self.speed += self.acceleration

		# Make sure speed doesn't go over max speed.
		if self.speed > self.max_speed:
			self.speed = self.max_speed

		# Move the missile with speed in consideration.
		self.x = self.x + (math.cos(self.angle) * self.speed)
		self.y = self.y + (math.sin(self.angle) * self.speed)
		self.rect.x = self.x
		self.rect.y = self.y

		# Convert the angle to degrees.
		if self.angle < 0:
			self.image_angle = self.angle * (180 / math.pi) + 360
		else:
			self.image_angle = self.angle * (180 / math.pi)
		self.image_angle += 90

		# Rotate the image to the angle, in degrees.
		self.rotate_image(-self.image_angle)

		# Improve the angle correction.
		self.angle_correction += self.angle_correction_rate

		# If it's time, spawn particles.
		self.particle_spawn_time += main_clock.get_time()
		if self.particle_spawn_time >= Missile.particle_spawn_rate:
			# Reset the particle spawn time.
			self.particle_spawn_time = 0

			# Spawn a random amount of particles.
			for _ in range(0, random.randrange(1, Missile.particle_spawn_amount)):
				angle = self.angle + random.uniform(math.pi - (math.pi / 24), math.pi + (math.pi / 24))
				speed = random.uniform(0.65 * settings.GAME_SCALE, 1.1 * settings.GAME_SCALE)
				retardation = speed / 24.0
				color = pygame.Color(random.randint(200, 255), random.randint(0, 255), 0)
				particle.Particle(self.x + self.rect.width / 2, self.y + self.rect.height / 2, Missile.particle_width, Missile.particle_height, angle, speed, retardation, color, 5)