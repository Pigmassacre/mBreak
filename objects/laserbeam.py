__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.groups as groups
import settings.settings as settings
import objects.camera as camera
import objects.particle as particle

"""

Laserbeam.

"""

class Laserbeam(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/attack/laser.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width()
	height = image.get_height()

	# Particle effect values
	particle_spawn_rate = 50  # How often to spawn particles (in milliseconds)
	particle_min_amount = 2
	particle_max_amount = 4
	particle_min_speed = 0.8 * settings.GAME_FPS
	particle_max_speed = 1.5 * settings.GAME_FPS
	particle_size_min = 1.5
	particle_size_max = 3.0
	particle_lifetime = 3 * settings.GAME_FPS

	# Scale image.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, owner, power_level=1.0, duration=1000):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		self.owner = owner
		# Store the power level which affects damage and height (clamp between 1.0 and 5.0)
		self.power_level = max(1.0, min(5.0, power_level))
		
		# Animation parameters
		self.creation_time = pygame.time.get_ticks()
		self.total_time_alive = 0
		self.fade_in_percentage = 0.15  # First 15% of lifetime is growing
		self.fade_out_percentage = 0.25  # Last 25% of lifetime is fading out
		self.current_height_multiplier = 0.0  # Start at 0 height
		self.duration = duration  # Store the duration locally
		
		# Particle spawn timing
		self.particle_spawn_time = 0
		
		# Debug output
		print(f"Creating laserbeam with power level: {self.power_level}, duration: {self.duration}ms")

		# Find the attack paddle
		self.attack_paddle = None
		for player in groups.Groups.player_group:
			if player == self.owner:
				for paddle in player.paddle_group:
					self.attack_paddle = paddle
					break
				break
				
		# If we couldn't find a paddle, we can't create a laserbeam
		if self.attack_paddle is None:
			print("Error: Could not find attack paddle for laserbeam")
			self.kill()
			return

		# Set initial dimensions
		width = settings.LEVEL_WIDTH
		# Start with a small height that will grow
		height = int(self.__class__.height)
		self.rect = pygame.Rect(settings.LEVEL_X, settings.LEVEL_Y, width, height)
		
		# Calculate the actual size and position
		self.figure_out_rect_size()
		
		# Check if we have valid dimensions
		if self.rect.width <= 0 or self.rect.height <= 0:
			print("Error: Invalid laserbeam dimensions")
			self.kill()
			return

		# Create the image attribute that is drawn over the parent surface.
		self.image = pygame.surface.Surface((self.rect.width, self.rect.height), pygame.locals.SRCALPHA)

		# Store the image that we use to create the final image.
		self.laser_image = self.__class__.image.copy()
		
		# Store the base height (without animation)
		self.base_height = int(self.__class__.height * max(1.0, self.power_level))

		# Create the final image.
		self.create_final_image()

		# Add self to the effect group.
		groups.Groups.effect_group.add(self)
		print(f"Laserbeam created with dimensions: {self.rect.width}x{self.rect.height}")

		# Add screen shake based on power level
		shake_duration = int(250 * self.power_level)  # 250ms to 1250ms
		shake_intensity = 0.5 * self.power_level  # 0.5 to 2.5
		camera.CAMERA.shake(shake_duration, shake_intensity)

	def figure_out_rect_size(self):
		# Make sure we have a valid attack paddle
		if self.attack_paddle is None:
			return
			
		# Store the current height - we want to preserve it when adjusting width
		current_height = self.rect.height
		
		# Calculate the center position of the paddle for vertical alignment
		paddle_center_y = self.attack_paddle.rect.y + (self.attack_paddle.rect.height / 2.0)
		
		if self.attack_paddle.x < settings.SCREEN_WIDTH / 2.0:
			# Left side player - beam goes right
			self.rect.x = self.attack_paddle.rect.x + self.attack_paddle.rect.width
			# Center the laser beam vertically based on its current animated height
			self.rect.y = paddle_center_y - (current_height / 2.0)

			# Check collision against blocks.
			least_x = settings.LEVEL_MAX_X  # Start with maximum possible value
			for block in groups.Groups.block_group:
				if block.owner != self.owner and block.rect.x > self.rect.x:
					if block.rect.y < self.rect.y + current_height and block.rect.y + block.rect.height > self.rect.y:
						if block.rect.x < least_x:
							least_x = block.rect.x

			for paddle in groups.Groups.paddle_group:
				if paddle.owner != self.owner and paddle.rect.x > self.rect.x:
					if paddle.rect.y < self.rect.y + current_height and paddle.rect.y + paddle.rect.height > self.rect.y:
						if paddle.rect.x < least_x:
							least_x = paddle.rect.x

			# If we didn't find any obstacles, use the level boundary
			if least_x == settings.LEVEL_MAX_X:
				self.rect.width = settings.LEVEL_MAX_X - self.rect.x
			else:
				self.rect.width = least_x - self.rect.x
				
			# Ensure we don't exceed level boundaries
			if self.rect.x + self.rect.width > settings.LEVEL_MAX_X:
				self.rect.width = settings.LEVEL_MAX_X - self.rect.x
		else:
			# Right side player - beam goes left
			# Start with the left edge of the level
			self.rect.x = settings.LEVEL_X
			# Center the laser beam vertically based on its current animated height
			self.rect.y = paddle_center_y - (current_height / 2.0)

			# Check collision against blocks.
			max_x = settings.LEVEL_X  # Start with minimum possible value
			for block in groups.Groups.block_group:
				if block.owner != self.owner and block.rect.x + block.rect.width < self.attack_paddle.rect.x:
					if block.rect.y < self.rect.y + current_height and block.rect.y + block.rect.height > self.rect.y:
						if block.rect.x + block.rect.width > max_x:
							max_x = block.rect.x + block.rect.width

			for paddle in groups.Groups.paddle_group:
				if paddle.owner != self.owner and paddle.rect.x + paddle.rect.width < self.attack_paddle.rect.x:
					if paddle.rect.y < self.rect.y + current_height and paddle.rect.y + paddle.rect.height > self.rect.y:
						if paddle.rect.x + paddle.rect.width > max_x:
							max_x = paddle.rect.x + paddle.rect.width

			# If we didn't find any obstacles, use the paddle position
			if max_x == settings.LEVEL_X:
				self.rect.width = self.attack_paddle.rect.x - settings.LEVEL_X
				self.rect.x = settings.LEVEL_X
			else:
				self.rect.width = self.attack_paddle.rect.x - max_x
				self.rect.x = max_x
				
		# Ensure the height is maintained
		self.rect.height = current_height

	def create_final_image(self):
		# Check if we have valid dimensions
		if self.rect.width <= 0 or self.rect.height <= 0:
			print("Error: Invalid dimensions for laserbeam image")
			return
			
		# Resize the image surface to match the current rect dimensions
		self.image = pygame.surface.Surface((self.rect.width, self.rect.height), pygame.locals.SRCALPHA)
		
		# Use the current animated height for scaling
		scaled_laser_height = self.rect.height
		scaled_laser_width = self.__class__.width
		
		# Create a scaled copy of the original class image
		if scaled_laser_height > 0:
			scaled_laser = pygame.transform.scale(self.__class__.image, (scaled_laser_width, scaled_laser_height))
			
			# Tile the scaled laser image across the surface
			for x in range(0, int(math.ceil(self.rect.width / float(scaled_laser_width)))):
				y_offset = 0
				while y_offset < self.rect.height:
					self.image.blit(scaled_laser, (scaled_laser_width * x, y_offset))
					y_offset += scaled_laser_height

	def destroy(self):
		self.kill()

	def update(self, main_clock):
		# Update total time alive
		self.total_time_alive += main_clock.get_time()
		
		# Calculate the height multiplier based on animation phase
		lifetime_ratio = self.total_time_alive / float(self.duration)
		
		# Fade in phase
		if lifetime_ratio < self.fade_in_percentage:
			# Map 0->fade_in_percentage to 0->1 using sine for smooth growth
			phase = lifetime_ratio / self.fade_in_percentage  # 0 to 1
			self.current_height_multiplier = math.sin(phase * math.pi / 2)  # Sine from 0 to 1
		# Stable phase
		elif lifetime_ratio < (1.0 - self.fade_out_percentage):
			self.current_height_multiplier = 1.0
		# Fade out phase
		else:
			# Map (1-fade_out)->1 to 1->0 using sine for smooth fade
			phase = (lifetime_ratio - (1.0 - self.fade_out_percentage)) / self.fade_out_percentage  # 0 to 1
			self.current_height_multiplier = math.cos(phase * math.pi / 2)  # Cosine from 1 to 0
			
		# If we've exceeded our duration, destroy the laserbeam
		if self.total_time_alive >= self.duration:
			self.destroy()
			return
		
		# Calculate the animated height
		animated_height = int(self.base_height * self.current_height_multiplier)
		if animated_height < 1:
			animated_height = 1  # Ensure at least 1 pixel height
			
		# Store the old dimensions to check if we need to recreate the image
		old_width = self.rect.width
		old_height = self.rect.height
		
		# Update the rect height with the animated height
		self.rect.height = animated_height

		# Make sure the attack paddle reference is still valid
		if self.attack_paddle is None or not self.attack_paddle.alive():
			for player in groups.Groups.player_group:
				if player == self.owner:
					for paddle in player.paddle_group:
						self.attack_paddle = paddle
			# If we still can't find a valid paddle, destroy this laserbeam
			if self.attack_paddle is None:
				self.destroy()
				return

		# Temporarily expand the width for collision detection
		self.rect.width += 1
		if self.attack_paddle.x > settings.SCREEN_WIDTH / 2.0:
			self.rect.x -= 1

		# Apply damage to blocks - scale damage by height multiplier for smooth damage ramp-up/down
		for block in groups.Groups.block_group:
			if block.owner != self.owner:
				if self.rect.colliderect(block.rect):
					# Scale damage based on power level and current height multiplier
					damage = 60 * main_clock.delta_time * self.power_level * self.current_height_multiplier
					block.on_hit(damage)

					# Spawn impact particles at collision points
					self.particle_spawn_time += main_clock.get_time()
					if self.particle_spawn_time >= self.__class__.particle_spawn_rate:
						self.particle_spawn_time = 0
						
						# Calculate impact point - use the edge of the laser beam
						if self.attack_paddle.x < settings.SCREEN_WIDTH / 2.0:
							impact_x = block.rect.left
						else:
							impact_x = block.rect.right
							
						# Calculate vertical position within intersection
						intersection_top = max(self.rect.y, block.rect.y)
						intersection_bottom = min(self.rect.y + self.rect.height, block.rect.y + block.rect.height)
						impact_y = (intersection_top + intersection_bottom) / 2

						# Spawn particles
						for _ in range(random.randint(self.__class__.particle_min_amount, self.__class__.particle_max_amount)):
							# Calculate particle angle based on laser direction
							base_angle = math.pi if self.attack_paddle.x < settings.SCREEN_WIDTH / 2.0 else 0
							angle = base_angle + random.uniform(-math.pi/4, math.pi/4)  # 45-degree cone
							
							# Random speed and size
							speed = random.uniform(self.__class__.particle_min_speed, self.__class__.particle_max_speed)
							size = random.uniform(self.__class__.particle_size_min, self.__class__.particle_size_max)
							
							# Create particle with laser-like color (bright white/blue)
							color = pygame.Color(
								random.randint(200, 255),  # High red for brightness
								random.randint(200, 255),  # High green for brightness
								255  # Full blue for laser effect
							)
							
							# Create the particle
							particle.Particle(
								impact_x, 
								impact_y,
								size, 
								size,
								angle,
								speed,
								speed / 24.0,  # Retardation
								color,
								self.__class__.particle_lifetime
							)

		# Check for paddle hits and create particles
		for paddle in groups.Groups.paddle_group:
			if paddle.owner != self.owner:
				if self.rect.colliderect(paddle.rect):
					# Spawn impact particles at collision points
					self.particle_spawn_time += main_clock.get_time()
					if self.particle_spawn_time >= self.__class__.particle_spawn_rate:
						self.particle_spawn_time = 0
						
						# Calculate impact point - use the edge of the laser beam
						if self.attack_paddle.x < settings.SCREEN_WIDTH / 2.0:
							impact_x = paddle.rect.left
						else:
							impact_x = paddle.rect.right
							
						# Calculate vertical position within intersection
						intersection_top = max(self.rect.y, paddle.rect.y)
						intersection_bottom = min(self.rect.y + self.rect.height, paddle.rect.y + paddle.rect.height)
						impact_y = (intersection_top + intersection_bottom) / 2

						# Spawn particles - use more particles for paddle hits
						for _ in range(random.randint(self.__class__.particle_min_amount + 1, self.__class__.particle_max_amount + 2)):
							# Calculate particle angle based on laser direction
							base_angle = math.pi if self.attack_paddle.x < settings.SCREEN_WIDTH / 2.0 else 0
							angle = base_angle + random.uniform(-math.pi/3, math.pi/3)  # 60-degree cone for more spread
							
							# Random speed and size - slightly faster for paddle hits
							speed = random.uniform(self.__class__.particle_min_speed * 1.2, self.__class__.particle_max_speed * 1.2)
							size = random.uniform(self.__class__.particle_size_min, self.__class__.particle_size_max)
							
							# Create particle with laser-like color (bright white/blue with more variation)
							color = pygame.Color(
								random.randint(180, 255),  # More variation in red
								random.randint(180, 255),  # More variation in green
								random.randint(230, 255)   # Slight variation in blue
							)
							
							# Create the particle
							particle.Particle(
								impact_x, 
								impact_y,
								size, 
								size,
								angle,
								speed,
								speed / 28.0,  # Less retardation for paddle hits
								color,
								self.__class__.particle_lifetime
							)

		# Restore original width
		self.rect.width -= 1
		if self.attack_paddle.x > settings.SCREEN_WIDTH / 2.0:
			self.rect.x += 1
		
		# Reset width to level width before recalculating
		self.rect.width = settings.LEVEL_WIDTH

		# Recalculate the rect size based on current game state
		self.figure_out_rect_size()
		
		# Restore the animated height after figure_out_rect_size (which might change it)
		self.rect.height = animated_height

		# If dimensions changed, recreate the image
		if self.rect.width != old_width or self.rect.height != old_height:
			self.create_final_image()

	def draw(self, surface):
		surface.blit(self.image, self.rect)