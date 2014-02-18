__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.camera as camera
import objects.effects.stun as stun
import objects.effects.explosion as explosion
import objects.dummy as dummy
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

	# Initialize the mixer (so we can load a sound) and load the sound effects.
	pygame.mixer.init(44100, -16, 2, 2048)
	sound_effects = []
	sound_effects.append(pygame.mixer.Sound("res/sounds/explosion1.ogg"))
	sound_effects.append(pygame.mixer.Sound("res/sounds/explosion2.ogg"))
	sound_effects.append(pygame.mixer.Sound("res/sounds/explosion3.ogg"))
	sound_effects.append(pygame.mixer.Sound("res/sounds/explosion4.ogg"))

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/powerup/missile.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	particle_spawn_rate = 25
	particle_spawn_amount = 5

	speed = 0.05 * settings.GAME_FPS * settings.GAME_SCALE
	acceleration = 0.025 * settings.GAME_FPS * settings.GAME_SCALE

	# These particles are spawned when the missile hits its target.
	hit_particle_min_amount = 12
	hit_particle_max_amount = 18
	hit_particle_min_speed = 1 * settings.GAME_FPS * settings.GAME_SCALE
	hit_particle_max_speed = 2.5 * settings.GAME_FPS * settings.GAME_SCALE

	# The amount of damage the missile deals to a hit block.
	damage = 20

	paddle_stun_duration = 600

	paddle_shake_strength = 0.33
	paddle_shake_duration = 350
	block_shake_strength = 0.66
	block_shake_duration = 350

	# These variables affect how the missile homes to its target.
	angle_correction = 0.0005 * settings.GAME_FPS
	angle_correction_rate = 0.1 * settings.GAME_FPS
	max_speed = 3 * settings.GAME_FPS * settings.GAME_SCALE

	# Scale image to settings.GAME_SCALE.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y, angle, owner, target):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, self.__class__.width, self.__class__.height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# We store the given angle of the Missile.
		self.angle = angle

		# We store the given speed of the Missile.
		self.speed = self.__class__.speed

		# Store the given acceleration.
		self.acceleration = self.__class__.acceleration

		# If this is set to anything higher than 0, this missile will not "fire" until this reaches 0.
		self.delay = 0

		# Store the owner.
		self.owner = owner

		# Store the target.
		self.target = target

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0

		# Load the image file.
		self.image = self.__class__.image.copy()

		# Store the original, unrotated version of the image.
		self.original_image = self.image.copy()

		# Store the angle to rotate the image separately.
		self.image_angle = self.angle

		# Create a shadow.
		self.shadow = shadow.Shadow(self)

		# Rotate it to the given angle.
		self.rotate_image(self.image_angle * (180 / math.pi))

		# Add self to the projectile group.
		groups.Groups.projectile_group.add(self)

		# If we want, we can connect powerups to this effect that is killed when this missile is killed. Primarily used to 
		# connect the powerups that are displayed on the player.
		self.displayed_powerups = []

	def rotate_image(self, angle):
		# Rotate image.
		old_center = self.rect.center
		self.image = pygame.transform.rotate(self.original_image, angle)
		self.rect = self.image.get_rect()
		self.rect.center = old_center

		# Rotate shadow.
		old_center = self.shadow.rect.center
		self.shadow.image = pygame.transform.rotate(self.shadow.original_image, angle)
		self.shadow.rect = self.shadow.image.get_rect()
		self.shadow.rect.center = old_center

	def destroy(self):
		self.kill()
		self.shadow.kill()

		# Destroy all powerups that are connected to this missile.
		for powerup in self.displayed_powerups:
			powerup.destroy(False)

		# Play a random sound from the sound_effects list.
		sound = self.__class__.sound_effects[random.randrange(0, len(self.__class__.sound_effects))].play()
		if not sound is None:
			sound.set_volume(settings.SOUND_VOLUME)

	def on_hit_block(self, block):
		# Destroy ourselves.
		self.destroy()

		# Tell the block that we've hit it.
		block.on_hit(self.__class__.damage)

		# Shake the camera slightly.
		camera.CAMERA.shake(self.__class__.block_shake_duration, self.__class__.block_shake_strength)

		# Spawn some particles.
		self.spawn_destroy_particles()

		# Create a dummy and attach an explosion effect to it.
		a_dummy = dummy.Dummy(1000, block.rect.centerx - explosion.Explosion.frame_width / 2.0,
									block.rect.centery - explosion.Explosion.frame_height / 2.0, 
									explosion.Explosion.frame_width, explosion.Explosion.frame_height)
		a_dummy.effect_group.add(explosion.Explosion(a_dummy))

	def on_hit_paddle(self, paddle):
		# Destroy ourselves.
		self.destroy()

		# Tell the paddle that it has been hit.
		paddle.on_hit(self)

		# Apply a stun effect to the hit paddle.
		stun.Stun(paddle, self.__class__.paddle_stun_duration)

		# Shake the camera slightly.
		camera.CAMERA.shake(self.__class__.paddle_shake_duration, self.__class__.paddle_shake_strength)

		# Spawn some particles.
		self.spawn_destroy_particles()

		# Create a dummy and attach an explosion effect to it.
		a_dummy = dummy.Dummy(1000, self.rect.centerx - explosion.Explosion.frame_width / 2.0,
									self.rect.centery - explosion.Explosion.frame_height / 2.0, 
									explosion.Explosion.frame_width, explosion.Explosion.frame_height)
		a_dummy.effect_group.add(explosion.Explosion(a_dummy))

	def spawn_destroy_particles(self):
		# Spawn a random amount of particles.
		for _ in range(0, random.randrange(self.__class__.hit_particle_min_amount, self.__class__.hit_particle_max_amount)):
			width = random.uniform(self.__class__.width / 4.5, self.__class__.width / 3.25)
			angle = self.angle + math.pi
			angle += random.uniform(math.pi - (math.pi / 16.0), math.pi + (math.pi / 16.0))
			speed = min(max(self.speed, self.__class__.hit_particle_min_speed), self.__class__.hit_particle_max_speed) * random.uniform(0.75, 1.25)
			retardation = speed / 21.0
			color = pygame.Color(random.randint(200, 255), random.randint(0, 255), 0)
			particle.Particle(self.x + self.rect.width / 2, self.y + self.rect.height / 2, width, width, angle, speed, retardation, color, 5)

	def update(self, main_clock):
		# Check if we have collided with the target block.
		blocks_collide_list = pygame.sprite.spritecollide(self, self.target.owner.block_group, False)
		for block in blocks_collide_list:
			if block == self.target:
				self.on_hit_block(block)

		# Check if we have collided with any paddle.
		paddle_collide_list = pygame.sprite.spritecollide(self, self.target.owner.paddle_group, False)
		for paddle in paddle_collide_list:
			self.on_hit_paddle(paddle)

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
				# Create a dummy and attach an explosion effect to it.
				a_dummy = dummy.Dummy(1000, self.rect.centerx - explosion.Explosion.frame_width / 2.0,
											self.rect.centery - explosion.Explosion.frame_height / 2.0, 
											explosion.Explosion.frame_width, explosion.Explosion.frame_height)
				a_dummy.effect_group.add(explosion.Explosion(a_dummy))

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
		self.angle += relative_angle_to_target * self.angle_correction * main_clock.delta_time

		# Update the speed according to the acceleration.
		self.speed += self.acceleration * main_clock.time_scale

		# Make sure speed doesn't go over max speed.
		if self.speed > self.max_speed:
			self.speed = self.max_speed

		# Move the missile with speed in consideration.
		self.x = self.x + (math.cos(self.angle) * self.speed * main_clock.delta_time)
		self.y = self.y + (math.sin(self.angle) * self.speed * main_clock.delta_time)
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
		self.angle_correction += self.angle_correction_rate * main_clock.delta_time

		# If it's time, spawn particles.
		self.particle_spawn_time += main_clock.get_time()
		if self.particle_spawn_time >= self.__class__.particle_spawn_rate:
			# Reset the particle spawn time.
			self.particle_spawn_time = 0

			# Spawn a random amount of particles.
			for _ in range(0, random.randrange(1, self.__class__.particle_spawn_amount)):
				width = random.uniform(self.__class__.width / 5.0, self.__class__.width / 4.0)
				angle = self.angle + random.uniform(math.pi - (math.pi / 24.0), math.pi + (math.pi / 24.0))
				speed = random.uniform(0.65 * settings.GAME_FPS * settings.GAME_SCALE, 1.1 * settings.GAME_FPS * settings.GAME_SCALE)
				retardation = speed / 24.0
				color = pygame.Color(random.randint(200, 255), random.randint(0, 255), 0)
				particle.Particle(self.x + self.rect.width / 2, self.y + self.rect.height / 2, width, width, angle, speed, retardation, color, 5)

	def draw(self, surface):
		surface.blit(self.image, (self.rect.x - camera.CAMERA.x, self.rect.y - camera.CAMERA.y))