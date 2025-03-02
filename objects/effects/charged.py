__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import objects.camera as camera
import objects.groups as groups
import objects.effects.effect as effect
import objects.blocks.block as block
import objects.particle as particle
import settings.settings as settings

"""
This is the "Charged" effect. When a ball carrying this effect hits an enemy block, 
it creates a chain lightning attack that jumps between blocks, dealing decreasing damage with each jump.
The effect is then destroyed.
"""

class Charged(effect.Effect):

	# Initialize the mixer (so we can load a sound) and load the sound effect.
	pygame.mixer.init(44100, -16, 2, 2048)
	sound_effect = pygame.mixer.Sound("res/sounds/thunder.ogg")

	# Chain lightning settings
	search_radius = 40  # Larger radius to find blocks
	chain_jumps = 6  # Number of times the lightning will jump
	base_damage = 20  # Initial damage
	damage_decay = 0.9  # Each jump deals 90% of previous damage
	particle_spawn_rate = 450
	particle_spawn_amount = 5
	duration = 10000
	chain_delay = 125  # Delay between chain jumps in milliseconds

	def __init__(self, parent, duration = None):
		# We check if a duration has been given.
		if not duration == None:
			# We start by calling the superconstructor with the given duration value.
			effect.Effect.__init__(self, parent, duration)
		else:
			# We start by calling the superconstructor with the standard duration value.
			effect.Effect.__init__(self, parent, Charged.duration)

		# When this reaches particle_spawn_rate, a particle is spawned.
		self.particle_spawn_time = 0
		
		# Store chain lightning path for drawing
		self.lightning_path = []
		self.lightning_fade = 1.0
		self.lightning_fade_speed = 2.0  # Fade out over 0.5 seconds
		
		# Chain lightning state
		self.chaining = False
		self.chain_time = 0
		self.current_block = None
		self.current_damage = 0
		self.hit_blocks = []
		self.jumps_remaining = 0

	def find_next_target(self, current_block, hit_blocks):
		"""Find the next block to chain to within search radius."""
		available_blocks = []
		current_pos = pygame.math.Vector2(current_block.rect.center)
		
		for block in current_block.owner.block_group:
			if block not in hit_blocks:
				block_pos = pygame.math.Vector2(block.rect.center)
				distance = current_pos.distance_to(block_pos)
				if distance <= Charged.search_radius:
					# Weight score by distance - prefer blocks that are further away
					# Square the distance ratio to make far blocks even more attractive
					distance_ratio = (distance / Charged.search_radius) ** 2
					score = distance_ratio * random.uniform(0.8, 1.2)  # Add some randomness
					available_blocks.append((block, score))
		
		if available_blocks:
			# Sort by score (highest first) and select from top 3
			available_blocks.sort(key=lambda x: x[1], reverse=True)
			selection_pool = available_blocks[:min(3, len(available_blocks))]
			return random.choice(selection_pool)[0]
		return None

	def start_chain_lightning(self, start_block):
		"""Initialize the chain lightning sequence."""
		self.current_block = start_block
		self.current_damage = Charged.base_damage
		self.hit_blocks = [start_block]
		# Store damage values for visual effects
		self.lightning_path = [(start_block.rect.centerx, start_block.rect.centery, self.current_damage)]
		self.jumps_remaining = Charged.chain_jumps
		self.chaining = True
		self.chain_time = 0
		
		# Deal initial damage
		start_block.on_hit(self.current_damage)
		self.spawn_particles(start_block)
		
		# If the initial block was destroyed, we'll let the update handle the cleanup
		if not start_block in start_block.owner.block_group:
			self.chaining = False
			self.lightning_fade = 1.0

	def chain_to_next(self):
		"""Execute one chain jump to the next block."""
		next_block = self.find_next_target(self.current_block, self.hit_blocks)
		if next_block is None:
			self.chaining = False
			return
			
		# Calculate new damage
		self.current_damage *= Charged.damage_decay
		
		# Deal damage and add effects
		next_block.on_hit(self.current_damage)
		self.spawn_particles(next_block)
		self.hit_blocks.append(next_block)
		
		# Add to lightning path for drawing, including damage value
		self.lightning_path.append((next_block.rect.centerx, next_block.rect.centery, self.current_damage))
		
		# If this block was destroyed or we're out of jumps, stop chaining
		if not next_block in next_block.owner.block_group or self.jumps_remaining <= 1:
			self.chaining = False
		else:
			self.current_block = next_block
			self.jumps_remaining -= 1
			self.chain_time = 0

	def on_hit_block(self, hit_block):
		if self.parent.owner == self.real_owner:
			# If the hit block isn't one of the parents owners blocks...
			if hit_block.owner != self.parent.owner:
				# Play the sound effect.
				sound = Charged.sound_effect.play()
				if not sound is None:
					sound.set_volume(settings.SOUND_VOLUME)

				# Shake the camera
				camera.CAMERA.shake(250, 0.5)

				# Start chain lightning
				self.start_chain_lightning(hit_block)

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		if self.parent.owner == self.real_owner:
			# Handle chain lightning sequence
			if self.chaining:
				self.chain_time += main_clock.get_time()
				if self.chain_time >= Charged.chain_delay:
					self.chain_to_next()
			# Start fade when chaining is complete
			elif self.lightning_path:
				self.lightning_fade -= self.lightning_fade_speed * main_clock.delta_time
				if self.lightning_fade <= 0:
					self.destroy()

			# Spawn ambient particles
			self.particle_spawn_time += main_clock.get_time()
			if self.particle_spawn_time >= Charged.particle_spawn_rate:
				self.particle_spawn_time = 0
				self.spawn_particles(self)

	def draw(self, surface):
		# Draw the lightning effect if it exists
		if self.lightning_path and len(self.lightning_path) > 1 and self.lightning_fade > 0:
			for i in range(len(self.lightning_path) - 1):
				start_pos = self.lightning_path[i]
				end_pos = self.lightning_path[i + 1]
				
				# Calculate the distance between points
				dx = end_pos[0] - start_pos[0]
				dy = end_pos[1] - start_pos[1]
				distance = math.sqrt(dx * dx + dy * dy)
				
				# Calculate line width based on damage
				# Scale from 1 to 3 pixels based on damage ratio to base damage
				damage = end_pos[2]  # Damage value stored with the point
				width_scale = max(0.3, damage / Charged.base_damage)
				line_width = max(1, int(3 * width_scale))
				
				# Add 2-3 intermediate points for a more natural lightning look
				points = [start_pos]
				num_points = random.randint(2, 3)
				for j in range(num_points):
					# Calculate position along the line
					t = (j + 1) / (num_points + 1)
					mid_x = start_pos[0] + dx * t
					mid_y = start_pos[1] + dy * t
					
					# Add smaller, distance-based offset
					offset = min(10, distance / 10)  # Slightly reduced offset
					mid_x += random.uniform(-offset, offset)
					mid_y += random.uniform(-offset, offset)
					points.append((mid_x, mid_y))
				points.append(end_pos)
				
				# Draw lightning segments with fade
				# Base alpha on both the fade timer and position in the chain
				chain_pos_fade = 1.0 - (i / (len(self.lightning_path) - 1)) * 0.3  # Earlier segments stay brighter longer
				alpha = int(255 * self.lightning_fade * chain_pos_fade)
				color = (255, 255, min(255, int(100 + 155 * width_scale)), alpha)
				
				for j in range(len(points) - 1):
					p1 = points[j]
					p2 = points[j + 1]
					if isinstance(p1, tuple) and len(p1) > 2:  # Strip damage value if present
						p1 = (p1[0], p1[1])
					if isinstance(p2, tuple) and len(p2) > 2:
						p2 = (p2[0], p2[1])
					pygame.draw.line(surface, color,
								(p1[0] - camera.CAMERA.x, p1[1] - camera.CAMERA.y),
								(p2[0] - camera.CAMERA.x, p2[1] - camera.CAMERA.y), line_width)

	def spawn_particles(self, entity):
		# Spawns particles with electric colors
		for _ in range(0, random.randrange(2, Charged.particle_spawn_amount)):
			angle = random.uniform(0, 2 * math.pi)
			speed = random.uniform(0.9 * settings.GAME_FPS, 1.4 * settings.GAME_FPS)
			retardation = speed / 46.0
			# Electric blue/white colors
			random_value = random.randint(200, 255)
			color = pygame.Color(random_value, random_value, 255)
			random_size = random.randint(self.rect.width // 4, self.rect.width // 3)
			particle.Particle(entity.rect.centerx, entity.rect.centery, 
							random_size, random_size, angle, speed, retardation, 
							color, 20 * settings.GAME_FPS)