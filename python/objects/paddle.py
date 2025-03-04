__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import copy
import math
import other.useful as useful
import objects.camera as camera
import objects.shadow as shadow
import objects.effects.flash as flash
import objects.effects.speed as speed
import objects.groups as groups
import settings.settings as settings

"""

This is the Paddle class. Paddles take care of their own movement (with the keys they should listen to provided by the player class).
Since paddles can move within the game area, they detect and handle their own collision with the edges of the game area.

"""

def convert():
	Paddle.top_image.convert()
	Paddle.middle_image.convert()
	Paddle.bottom_image.convert()

class Paddle(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	#image = pygame.image.load("res/paddle/paddle.png")
	top_image = pygame.image.load("res/paddle/paddle_top.png")
	middle_image = pygame.image.load("res/paddle/paddle_middle.png")
	bottom_image = pygame.image.load("res/paddle/paddle_bottom.png")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = middle_image.get_width()
	height = 22
	acceleration = 1.0 * settings.GAME_FPS
	retardation = 2.5 * settings.GAME_FPS
	max_speed = 2.5 * settings.GAME_FPS

	max_height = 33
	min_height = 11

	max_width = width
	min_width = width

	# On hit effect values.
	hit_effect_start_color = pygame.Color(255, 255, 255, 160)
	hit_effect_final_color = pygame.Color(255, 255, 255, 0)
	hit_effect_tick_amount = 22 * settings.GAME_FPS

	# Used for hit effect on the paddle.
	stabilize_speed = 0.1 * settings.GAME_FPS
	max_nudge_distance = 2.5

	# Scale the images.
	top_image = pygame.transform.scale(top_image, (top_image.get_width(), top_image.get_height()))
	middle_image = pygame.transform.scale(middle_image, (middle_image.get_width(), middle_image.get_height()))
	bottom_image = pygame.transform.scale(bottom_image, (bottom_image.get_width(), bottom_image.get_height()))

	def __init__(self, x, y, owner):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)
		
		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, Paddle.width, Paddle.height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# We store the max and min height of the paddle, for easy access by other classes.
		self.max_height = Paddle.max_height
		self.min_height = Paddle.min_height

		# We store the actual height that can go beyond max or min height.
		self.actual_width = self.rect.width
		self.actual_height = self.rect.height

		# This is the actual desired x position of the paddle. Used for visual effects.
		self.center_x = self.x

		# The velocity at which the Paddle will be moved when it is updated.
		self.velocity_y = 0

		# These values affect the velocity of the paddle.
		self.acceleration = Paddle.acceleration
		self.retardation = Paddle.retardation
		self.max_speed = Paddle.max_speed

		# The owner is the player that owns the paddle.
		self.owner = owner

		# Store the paddle in the owners paddle_group.
		self.owner.paddle_group.add(self)

		# Store the whether or not keys are held down for this paddle.
		self.key_up_pressed = False
		self.key_down_pressed = False

		# AI variables.
		self.focused_item = None
		self.old_focused_item = None
		self.chosen_distance_from_center = 0
		self.min_x_distance = 99999
		self.min_y_distance = 99999
		self.min_distance = 99999
		self.missed_balls = 0  # Counter for missed balls
		self.direction_change_cooldown = 0.1  # Minimum time between direction changes
		self.last_direction_change = 0
        
		# New AI variables for smoother movement
		self.target_y = None
		self.last_decision_time = 0
		self.decision_cooldown = 0.08  # Slightly faster recalculation for better accuracy
		self.movement_buffer = 3  # Smaller buffer for more precise positioning
		self.current_prediction = None
		self.prediction_confidence = 0

		# Set the size of the paddle. This takes care of storing the image attribute and coloring it.
		self.set_size(Paddle.width, Paddle.height)

		# Add self to to owners paddle_group and main paddle_group.
		self.owner.paddle_group.add(self)
		groups.Groups.paddle_group.add(self)

		# Create an effect group to handle effects on this paddle.
		self.effect_group = pygame.sprite.Group()

	def set_size(self, new_width, new_height):
		# Set the actual width and height to the new width and height.
		self.actual_width = new_width
		self.actual_height = new_height

		# Temporarily store the old width and height, used for positioning the paddle later.
		old_width = self.rect.width
		old_height = self.rect.height

		# Change the rect width.
		if self.actual_width > self.max_width:
			self.rect.width = self.max_width
		elif self.actual_width < self.min_width:
			self.rect.width = self.min_width
		else:
			self.rect.width = self.actual_width

		# Change the rect height.
		if self.actual_height > self.max_height:
			self.rect.height = self.max_height
		elif self.actual_height < self.min_height:
			self.rect.height = self.min_height
		else:
			self.rect.height = self.actual_height

		# Make sure the position of the paddle isn't changed.
		self.x += (old_width - self.rect.width) / 2.0
		self.y += (old_height - self.rect.height) / 2.0

		if hasattr(self, 'image') and self.image is not None:
			# Resize the current image.
			self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
		else:
			# Create the image attribute that is drawn to the surface.
			self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.locals.SRCALPHA)
		
		# Blit the top part.
		self.image.blit(Paddle.top_image, (0, 0))

		# Blit the middle parts.
		for i in range(Paddle.top_image.get_height(), self.rect.height - Paddle.bottom_image.get_height()):
			self.image.blit(Paddle.middle_image, (0, i))

		# Blit the bottom part.
		self.image.blit(Paddle.bottom_image, (0, self.rect.height - Paddle.bottom_image.get_height()))

		useful.colorize_image(self.image, copy.copy(self.owner.color), False, False)

		# If the shadow already exists, kill it first.
		if hasattr(self, 'shadow') and self.shadow is not None:
			self.shadow.kill()

		# Then, create a (new) shadow.
		self.shadow = shadow.Shadow(self)

	def add_size(self, added_width, added_height):
		self.set_size(self.actual_width + added_width, self.actual_height + added_height)

	def on_hit(self, entity):
		# If hit by an enemy ball, we increase our owners energy.
		# Energy gain grows with consecutive paddle hits if hit by a ball
		energy_multiplier = 1.0
		if hasattr(entity, 'paddle_hit_counter'):  # Check if entity is a ball
			energy_multiplier = min(3.0, 1.0 + (entity.paddle_hit_counter * 0.5))  # Cap at 3x
		energy_gain = self.owner.energy_increase_on_hit * energy_multiplier

		if entity.owner != self.owner:
			if self.owner.energy + energy_gain < self.owner.max_energy:
				self.owner.energy += energy_gain
			else:
				self.owner.energy = self.owner.max_energy
		else:
			if self.owner.energy + energy_gain/2.0 < self.owner.max_energy:
				self.owner.energy += energy_gain/2.0
			else:
				self.owner.energy = self.owner.max_energy

		# Create a new on hit effect.
		self.effect_group.add(flash.Flash(self, copy.copy(Paddle.hit_effect_start_color), copy.copy(Paddle.hit_effect_final_color), Paddle.hit_effect_tick_amount))
		
		# Record successful hit for AI learning
		self.last_hit_time = pygame.time.get_ticks() / 1000.0
		self.missed_balls = max(0, self.missed_balls - 1)  # Reduce missed ball count on successful hit

	def debug_draw(self, surface):
		if self.focused_item != None and settings.DEBUG_MODE:
			color = copy.copy(self.owner.color)
			color.a = 128
			surface.fill(color, pygame.Rect(self.focused_item.rect.x - 1 - camera.CAMERA.x, self.focused_item.y - 1 - camera.CAMERA.y, self.focused_item.width + 2, self.focused_item.height + 2))

	def decide_which_item(self, item):
		# Calculate predicted position based on trajectory
		prediction_data = self.predict_trajectory(item)
		
		if prediction_data is None:
			return
			
		predicted_x, predicted_y, confidence, time_to_reach = prediction_data
			
		# Calculate distance to predicted position
		distance_x = math.fabs(self.rect.x - predicted_x)
		# Use the center of the paddle for distance calculation
		paddle_center_y = self.rect.y + self.rect.height / 2.0
		distance_y = math.fabs(paddle_center_y - predicted_y)
		total_distance = math.sqrt(math.pow(distance_x, 2) + math.pow(distance_y, 2))
		
		# Adjust distance based on item properties
		adjusted_distance = self.adjust_distance_by_priority(item, total_distance)
		
		# Adjust by confidence and time to reach
		adjusted_distance = adjusted_distance / confidence
		
		# Give higher priority to slow balls that are close to prevent missing them
		if hasattr(item, "speed") and item.speed is not None and item.speed < 5 and distance_x < 100:
			adjusted_distance *= 0.3  # Much higher priority for slow, close balls
		
		# If this item is closer than our current focused item, focus on it
		if adjusted_distance < self.min_distance:
			self.min_distance = adjusted_distance
			self.focused_item = item
			self.predicted_y = predicted_y
			self.current_prediction = prediction_data
			self.prediction_confidence = confidence
			
			# If this is our ball and we're a higher difficulty AI, try to aim it at opponent blocks
			if self.owner.ai_difficulty >= 2 and hasattr(item, "owner") and item.owner is not None and item.owner == self.owner:
				# Check if we're close enough to the ball to aim it
				paddle_side_left = self.x < settings.SCREEN_WIDTH / 2
				ball_x = item.x + item.rect.width / 2.0
				
				# Only try to aim if the ball is approaching our paddle
				if (paddle_side_left and ball_x > self.x) or (not paddle_side_left and ball_x < self.x + self.rect.width):
					# Calculate distance to ball
					ball_distance = math.fabs(ball_x - (self.x + self.rect.width/2.0))
					
					# Only try to aim if the ball is close enough
					if ball_distance < 150:
						aim_position = self.calculate_aim_position()
						if aim_position is not None:
							# Adjust the predicted position based on aiming
							# For expert AI, prioritize aiming more
							if self.owner.ai_difficulty >= 3:
								self.predicted_y = (self.predicted_y * 0.2 + aim_position * 0.8)
							else:
								self.predicted_y = (self.predicted_y * 0.5 + aim_position * 0.5)

	def predict_trajectory(self, item):
		"""
		Predicts where the item will be when it reaches the paddle's x position.
		Returns (predicted_x, predicted_y, confidence, time_to_reach) or None if item won't reach paddle.
		"""
		# Determine if we're the left or right paddle
		paddle_side_left = self.x < settings.SCREEN_WIDTH / 2
		
		# Check if ball is behind paddle and moving away
		ball_behind = False
		if paddle_side_left:
			if item.x < self.x + self.rect.width:
				ball_behind = True
				# For left paddle: check if ball is moving right (angle between -π/2 and π/2)
				angle = item.angle
				if angle > math.pi:
					angle -= 2 * math.pi  # Normalize angle to [-π, π] range
				if angle > -math.pi/2 and angle < math.pi/2:
					# Ball is behind and moving away - move opposite to ball's vertical direction
					speed_y = item.speed * math.sin(item.angle)
					target_y = item.y + item.rect.height/2.0
					if speed_y > 0:
						# Ball moving down, move up
						target_y = settings.LEVEL_Y + self.rect.height
					else:
						# Ball moving up, move down
						target_y = settings.LEVEL_MAX_Y - self.rect.height
					return (self.x, target_y, 0.95, 1)
		else:
			if item.x > self.x - item.rect.width:
				ball_behind = True
				# For right paddle: check if ball is moving left (angle between π/2 and 3π/2)
				if item.angle > math.pi/2 and item.angle < 3*math.pi/2:
					# Ball is behind and moving away - move opposite to ball's vertical direction
					speed_y = item.speed * math.sin(item.angle)
					target_y = item.y + item.rect.height/2.0
					if speed_y > 0:
						# Ball moving down, move up
						target_y = settings.LEVEL_Y + self.rect.height
					else:
						# Ball moving up, move down
						target_y = settings.LEVEL_MAX_Y - self.rect.height
					return (self.x + self.rect.width, target_y, 0.95, 1)
		
		# If ball is behind but not moving away, ignore it
		if ball_behind:
			return None
			
		# Check if item is moving toward this paddle
		if paddle_side_left:
			# Left paddle: item must be moving left (angle between π/2 and 3π/2)
			if not (item.angle >= math.pi / 2.0 and item.angle <= 3 * math.pi / 2.0):
				return None
		else:
			# Right paddle: item must be moving right (angle between -π/2 and π/2)
			# Fix: Properly handle angle range for right paddle
			angle = item.angle
			if angle > math.pi:
				angle -= 2 * math.pi  # Normalize angle to [-π, π] range
			if not (angle >= -math.pi / 2.0 and angle <= math.pi / 2.0):
				return None
				
		# Calculate time to reach paddle
		speed_x = item.speed * math.cos(item.angle)
		
		# If speed_x is too small, item is moving almost vertically
		if abs(speed_x) < 0.1:
			# Check if the ball is very close to the paddle
			if (paddle_side_left and item.x > self.x - 50 and item.x < self.x + 50) or \
			   (not paddle_side_left and item.x < self.x + self.rect.width + 50 and item.x > self.x - 50):
				# For very close balls, just use current y position with high confidence
				return (self.x if paddle_side_left else self.x + self.rect.width, item.y + item.rect.height / 2.0, 0.95, 1)
			return None
			
		# Calculate time to reach paddle
		if paddle_side_left:
			time_to_reach = (self.x + self.width - item.x) / speed_x
		else:
			time_to_reach = (self.x - item.x - item.rect.width) / speed_x
			
		# If time is negative, item is moving away from paddle
		if time_to_reach <= 0:
			# Special case: if ball is very close and behind paddle, still track it
			if (paddle_side_left and item.x < self.x + 100) or \
			   (not paddle_side_left and item.x > self.x - 100):
				return (self.x if paddle_side_left else self.x + self.rect.width, item.y + item.rect.height / 2.0, 0.9, 1)
			return None
			
		# Calculate y position when item reaches paddle
		speed_y = item.speed * math.sin(item.angle)
		predicted_y = item.y + speed_y * time_to_reach
		
		# Check if item will hit top or bottom wall before reaching paddle
		# and calculate bounce if needed
		level_height = settings.LEVEL_MAX_Y - settings.LEVEL_Y
		bounces = 0
		max_bounces = 5  # Limit calculation to prevent infinite loops
		
		# More accurate bounce calculation
		remaining_time = time_to_reach
		current_y = item.y
		current_speed_y = speed_y
		
		while remaining_time > 0 and bounces < max_bounces:
			# Calculate time to hit top or bottom wall
			time_to_top = float('inf') if current_speed_y >= 0 else (settings.LEVEL_Y - current_y) / current_speed_y
			time_to_bottom = float('inf') if current_speed_y <= 0 else ((settings.LEVEL_MAX_Y - item.rect.height) - current_y) / current_speed_y
			
			# Find the earliest collision
			time_to_collision = min(time_to_top, time_to_bottom)
			
			# If no collision before reaching paddle, calculate final position
			if time_to_collision >= remaining_time or time_to_collision <= 0:
				current_y += current_speed_y * remaining_time
				break
				
			# Move to collision point
			current_y += current_speed_y * time_to_collision
			remaining_time -= time_to_collision
			
			# Bounce (reverse y velocity)
			current_speed_y = -current_speed_y
			bounces += 1
		
		predicted_y = current_y
		
		# Calculate confidence in prediction based on time and bounces
		confidence = 1.0 - (time_to_reach / 120.0) - (bounces * 0.15)
		
		# Increase confidence for balls that are close
		if time_to_reach < 30:
			confidence += 0.3
		
		# Increase confidence for slow balls that are close
		if time_to_reach < 20 and item.speed < 5:
			confidence += 0.4
			
		# Increase confidence for balls that are moving directly toward paddle
		direct_angle = math.pi if paddle_side_left else 0
		angle_diff = min(abs(item.angle - direct_angle), abs(abs(item.angle - direct_angle) - 2 * math.pi))
		if angle_diff < math.pi / 4:  # Within 45 degrees of direct path
			confidence += 0.2
		
		confidence = max(0.1, min(1.0, confidence))
		
		# Return the predicted position - this is the center of the item
		# Fix: Return correct x position for right paddle
		return (self.x if paddle_side_left else self.x + self.rect.width, predicted_y + item.rect.height / 2.0, confidence, time_to_reach)
		
	def adjust_distance_by_priority(self, item, distance):
		"""
		Adjusts the calculated distance based on item priority and properties.
		Returns the adjusted distance value.
		"""
		adjusted_distance = distance
		
		# Prioritize balls over projectiles
		if hasattr(item, "__class__") and item.__class__ is not None and item.__class__.__name__ == "Ball":
			adjusted_distance *= 0.5  # Even higher priority for balls (was 0.6)
		
		# Prioritize based on item type
		if hasattr(item, "owner") and item.owner is not None:
			# Prioritize enemy items over own items
			if item.owner == self.owner:
				adjusted_distance *= 1.5  # Less extreme priority difference (was 2.0)
			else:
				adjusted_distance *= 0.5
				
		# Prioritize based on speed
		if hasattr(item, "speed") and item.speed is not None:
			# Give higher priority to slow balls as they're easier to aim
			if item.speed < 5:
				adjusted_distance *= 0.6  # Higher priority for slow balls
			elif hasattr(item, "effect_group") and item.effect_group is not None:
				for effect in item.effect_group:
					if effect.__class__ == speed.Speed:
						adjusted_distance *= 0.5  # Higher priority for faster items
					
		# Prioritize based on distance from paddle
		if hasattr(item, "x") and item.x is not None:
			x_distance = math.fabs(self.rect.x - item.x)
			if x_distance < 100:  # Very close items get highest priority
				adjusted_distance *= 0.4
			elif x_distance < 200:  # Close items get higher priority
				adjusted_distance *= 0.6
			elif x_distance < 300:
				adjusted_distance *= 0.8
				
		# If we've been missing balls, prioritize easier ones
		if self.missed_balls > 2 and hasattr(item, "speed") and item.speed is not None:
			if item.speed < 5:  # Slower balls are easier to hit
				adjusted_distance *= 0.5  # Higher priority (was 0.7)
				
		return adjusted_distance
		
	def strategic_positioning(self):
		"""
		Determines the best strategic position when no immediate threats are present.
		"""
		# Check if we have an active laser
		active_laser = False
		laser_height = 0
		laser_power = 1.0
		for effect in groups.Groups.effect_group:
			if effect.__class__.__name__ == "Laserbeam" and effect.owner == self.owner:
				active_laser = True
				laser_height = effect.rect.height
				laser_power = effect.power_level
				break
				
		if active_laser:
			# Get current paddle position as starting point
			current_y = self.rect.y + self.rect.height / 2.0
			paddle_side_left = self.x < settings.SCREEN_WIDTH / 2.0
			
			# Find all enemy blocks and their positions
			enemy_blocks = []
			for block in groups.Groups.block_group:
				if block.owner != self.owner:
					enemy_blocks.append(block)
			
			if not enemy_blocks:
				return current_y
				
			# Group blocks by vertical position to find clusters
			block_clusters = []
			current_cluster = []
			sorted_blocks = sorted(enemy_blocks, key=lambda b: b.rect.y)
			
			for block in sorted_blocks:
				if not current_cluster:
					current_cluster.append(block)
				else:
					# If block is within laser height of cluster, add to cluster
					cluster_center = sum(b.rect.y + b.rect.height/2.0 for b in current_cluster) / len(current_cluster)
					block_center = block.rect.y + block.rect.height/2.0
					if abs(block_center - cluster_center) <= laser_height:
						current_cluster.append(block)
					else:
						block_clusters.append(current_cluster)
						current_cluster = [block]
			
			if current_cluster:
				block_clusters.append(current_cluster)
				
			# Score each cluster
			best_score = -1
			best_position = current_y
			
			for cluster in block_clusters:
				# Calculate cluster center
				cluster_center = sum(b.rect.y + b.rect.height/2.0 for b in cluster) / len(cluster)
				
				# Calculate score based on several factors
				score = 0
				
				# Base score from number of blocks that would be hit
				blocks_hit = len(cluster)
				score += blocks_hit * 10
				
				# Bonus for weak/damaged blocks
				for block in cluster:
					if hasattr(block, "health"):
						# More points for lower health blocks
						health_factor = 1.0 - (block.health / 100.0)
						if block.__class__.__name__ == "WeakBlock":
							score += 5 * (1.0 + health_factor)
						elif block.__class__.__name__ == "NormalBlock":
							score += 3 * (1.0 + health_factor)
						else:  # StrongBlock
							score += 2 * (1.0 + health_factor)
				
				# Bonus if cluster is on same side of screen as paddle
				cluster_x = sum(b.rect.x for b in cluster) / len(cluster)
				if (paddle_side_left and cluster_x > self.rect.x) or \
				   (not paddle_side_left and cluster_x < self.rect.x):
					score *= 1.2
				
				# Small penalty for distance from current position
				distance_penalty = abs(cluster_center - current_y) / (settings.LEVEL_MAX_Y - settings.LEVEL_Y)
				score *= (1.0 - distance_penalty * 0.3)  # Reduced penalty to allow more movement
				
				# Bonus for powerful laser (can hit more blocks reliably)
				score *= math.sqrt(laser_power)
				
				if score > best_score:
					best_score = score
					best_position = cluster_center
			
			# If we found a good position, move toward it
			# But maintain some inertia to prevent constant jumping
			return (best_position * 0.7 + current_y * 0.3)
		
		# If no laser is active or no good position found, use normal strategic positioning
		# Default to center position
		target_y = settings.LEVEL_Y + (settings.LEVEL_MAX_Y - settings.LEVEL_Y) / 2.0
		
		# If there are balls in play, try to position based on their general position
		ball_count = 0
		ball_y_sum = 0
		closest_ball_y = None
		closest_ball_distance = float('inf')
		paddle_side_left = self.x < settings.SCREEN_WIDTH / 2
		
		for ball in groups.Groups.ball_group:
			ball_count += 1
			ball_center_y = ball.y + ball.rect.height / 2.0
			ball_y_sum += ball_center_y
			
			# Track the closest ball's position
			ball_x = ball.x + ball.rect.width / 2.0
			distance = abs(ball_x - (self.x + self.rect.width/2.0))
			if distance < closest_ball_distance:
				closest_ball_distance = distance
				closest_ball_y = ball_center_y
			
		if ball_count > 0:
			# Use weighted average of ball positions, with more weight on closest ball
			avg_ball_y = ball_y_sum / ball_count
			if closest_ball_y is not None:
				# Weight the closest ball more heavily
				target_y = (avg_ball_y * 0.3 + closest_ball_y * 0.4 + target_y * 0.3)
			else:
				target_y = (avg_ball_y * 0.3 + target_y * 0.7)
			
		# Try to aim at opponent blocks if we have a high enough AI difficulty
		if self.owner.ai_difficulty >= 2 and ball_count > 0:
			aim_position = self.calculate_aim_position()
			if aim_position is not None:
				# For higher difficulties, prioritize aiming more but stay closer to center
				if self.owner.ai_difficulty >= 3:
					# Reduce the influence of aim_position to prevent extreme positioning
					target_y = (target_y * 0.5 + aim_position * 0.5)
				else:
					target_y = (target_y * 0.6 + aim_position * 0.4)
			
		# Add a slight bias toward the center when no immediate threats
		screen_center_y = settings.LEVEL_Y + (settings.LEVEL_MAX_Y - settings.LEVEL_Y) / 2.0
		target_y = (target_y * 0.7 + screen_center_y * 0.3)
		
		# Ensure we stay within screen bounds
		min_y = settings.LEVEL_Y + self.rect.height / 2.0
		max_y = settings.LEVEL_MAX_Y - self.rect.height / 2.0
		target_y = max(min_y, min(max_y, target_y))
		
		return target_y

	def calculate_aim_position(self):
		"""
		Calculates the optimal paddle position to aim at opponent blocks.
		Returns the y-position where the paddle should be positioned to aim at blocks.
		"""
		# Determine if we're the left or right paddle
		paddle_side_left = self.x < settings.SCREEN_WIDTH / 2
		
		# Find opponent blocks
		opponent_blocks = []
		for block in groups.Groups.block_group:
			if block.owner != self.owner:
				opponent_blocks.append(block)
				
		if not opponent_blocks:
			return None
			
		# Find the most vulnerable blocks (prioritize weak blocks first, then normal, then strong)
		weak_blocks = [b for b in opponent_blocks if b.__class__.__name__ == "WeakBlock"]
		normal_blocks = [b for b in opponent_blocks if b.__class__.__name__ == "NormalBlock"]
		strong_blocks = [b for b in opponent_blocks if b.__class__.__name__ == "StrongBlock"]
		
		# Prioritize blocks with lower health
		target_blocks = []
		if weak_blocks:
			target_blocks = sorted(weak_blocks, key=lambda b: b.health)
		elif normal_blocks:
			target_blocks = sorted(normal_blocks, key=lambda b: b.health)
		elif strong_blocks:
			target_blocks = sorted(strong_blocks, key=lambda b: b.health)
			
		if not target_blocks:
			return None
		
		# Find a ball that we can use to aim
		available_balls = []
		for ball in groups.Groups.ball_group:
			# For left paddle, use balls owned by us
			# For right paddle, use balls owned by opponent
			if (paddle_side_left and ball.owner == self.owner) or (not paddle_side_left and ball.owner != self.owner):
				available_balls.append(ball)
				
		if not available_balls:
			# If no suitable ball found, aim based on block position
			target_block = target_blocks[0]
			return target_block.y + target_block.rect.height / 2.0
			
		# Try to find the best block to aim at
		best_target = None
		best_score = float('-inf')
		best_paddle_position = None
		
		# Try each of the top 3 most vulnerable blocks (or fewer if there aren't that many)
		for target_block in target_blocks[:min(3, len(target_blocks))]:
			# Try to calculate trajectory to this block
			for ball in available_balls:
				trajectory_data = self.calculate_trajectory_to_block(ball, target_block, paddle_side_left)
				if trajectory_data:
					paddle_position, score = trajectory_data
					
					# If this is the best score so far, remember this target
					if score > best_score:
						best_score = score
						best_target = target_block
						best_paddle_position = paddle_position
		
		# If we found a good target, return the paddle position to aim at it
		if best_paddle_position is not None:
			return best_paddle_position
			
		# Fallback to simpler aiming logic if we couldn't calculate a good trajectory
		target_block = target_blocks[0]  # Start with the most vulnerable block
		
		# Calculate the desired angle to hit the target block
		if paddle_side_left:
			# Left paddle aims right
			desired_angle = 0  # Straight right
		else:
			# Right paddle aims left
			desired_angle = math.pi  # Straight left
			
		# Calculate the normalized distance needed to achieve this angle
		# From hit_left_side_of_paddle: self.angle = math.pi - normalized_distance * max_angle_offset
		# From hit_right_side_of_paddle: self.angle = normalized_distance * max_angle_offset
		max_angle_offset = (math.pi / 2 - 0.32)  # Using Ball.least_allowed_vertical_angle
		
		# Adjust for vertical position of the target block
		block_center_y = target_block.y + target_block.rect.height / 2.0
		screen_center_y = settings.LEVEL_Y + (settings.LEVEL_MAX_Y - settings.LEVEL_Y) / 2.0
		
		# Calculate normalized_distance based on block position
		# If block is above center, we want to hit lower on paddle (higher normalized_distance)
		# If block is below center, we want to hit higher on paddle (lower normalized_distance)
		if block_center_y < screen_center_y:
			# Block is above center, we need to aim upward
			normalized_distance = 0.7  # Hit lower part of paddle to aim upward
		elif block_center_y > screen_center_y:
			# Block is below center, we need to aim downward
			normalized_distance = 0.3  # Hit upper part of paddle to aim downward
		else:
			# Block is at center, aim straight
			normalized_distance = 0.5
			
		# Calculate the paddle position that would result in this normalized_distance
		# For any available ball
		if available_balls:
			ball = available_balls[0]
			ball_height = ball.rect.height
			
			# Calculate max_distance
			paddle_center = self.rect.height / 2.0
			max_distance = paddle_center + ball_height
			
			# Calculate where the ball should hit relative to paddle center
			hit_position_from_center = normalized_distance * max_distance - (paddle_center / 2.0)
			
			# Calculate the paddle center position that would achieve this
			ball_center_y = ball.y + ball.rect.height / 2.0
			target_paddle_center = ball_center_y - hit_position_from_center
			
			# Ensure the paddle stays within the screen bounds
			min_paddle_center = settings.LEVEL_Y + self.rect.height / 2.0
			max_paddle_center = settings.LEVEL_MAX_Y - self.rect.height / 2.0
			target_paddle_center = max(min_paddle_center, min(max_paddle_center, target_paddle_center))
			
			return target_paddle_center
				
		# If no suitable ball found, aim based on block position
		return block_center_y
		
	def calculate_trajectory_to_block(self, ball, target_block, paddle_side_left):
		"""
		Calculates the trajectory needed to hit a specific block.
		Returns (paddle_position, score) or None if no valid trajectory.
		Score indicates how good the trajectory is (higher is better).
		"""
		# Calculate the target point (center of the block)
		target_x = target_block.x + target_block.rect.width / 2.0
		target_y = target_block.y + target_block.rect.height / 2.0
		
		# Calculate the angle needed to hit the target
		ball_x = ball.x + ball.rect.width / 2.0
		ball_y = ball.y + ball.rect.height / 2.0
		
		# Calculate the angle from ball to target
		dx = target_x - ball_x
		dy = target_y - ball_y
		
		# Skip if the ball is not on the correct side of the paddle
		if paddle_side_left and ball_x < self.x:
			return None
		if not paddle_side_left and ball_x > self.x + self.rect.width:
			return None
			
		# Calculate the desired angle
		desired_angle = math.atan2(dy, dx)
		if desired_angle < 0:
			desired_angle += 2 * math.pi
			
		# Check if this angle is achievable with the paddle
		# Use the same minimum angle as in the ball's ensure_minimum_angle method
		min_angle = math.pi / 10  # ~18 degrees
		max_angle_offset = (math.pi / 2 - min_angle)
		
		# Calculate the normalized distance needed to achieve this angle
		if paddle_side_left:
			# For left paddle: angle = math.pi - normalized_distance * max_angle_offset
			# We want angle = desired_angle
			# So: math.pi - normalized_distance * max_angle_offset = desired_angle
			# normalized_distance = (math.pi - desired_angle) / max_angle_offset
			normalized_distance = (math.pi - desired_angle) / max_angle_offset
		else:
			# For right paddle: angle = normalized_distance * max_angle_offset
			# We want angle = desired_angle
			# So: normalized_distance * max_angle_offset = desired_angle
			# normalized_distance = desired_angle / max_angle_offset
			normalized_distance = desired_angle / max_angle_offset
			
		# Check if the normalized distance is within valid range [0,1]
		if normalized_distance < 0 or normalized_distance > 1:
			# This angle is not achievable with the paddle
			return None
			
		# Calculate the paddle position that would result in this normalized_distance
		ball_height = ball.rect.height
		
		# Calculate max_distance
		# This is the distance from paddle center to the top of the paddle plus ball height
		paddle_center = self.rect.height / 2.0
		max_distance = paddle_center + ball_height
		
		# Calculate where the ball should hit relative to paddle center
		hit_position_from_center = normalized_distance * max_distance - (paddle_center / 2.0)
		
		# Calculate the paddle center position that would achieve this
		ball_center_y = ball.y + ball.rect.height / 2.0
		target_paddle_center = ball_center_y - hit_position_from_center
		
		# Ensure the paddle stays within the screen bounds
		min_paddle_center = settings.LEVEL_Y + self.rect.height / 2.0
		max_paddle_center = settings.LEVEL_MAX_Y - self.rect.height / 2.0
		
		# If the required position is outside the screen bounds, this trajectory is not possible
		if target_paddle_center < min_paddle_center or target_paddle_center > max_paddle_center:
			return None
			
		# Calculate a score for this trajectory
		# Higher score for:
		# - Lower health blocks
		# - Blocks that are easier to hit (more central)
		# - Trajectories that don't require extreme paddle positions
		
		# Base score on block health (lower health = higher score)
		score = 100 - target_block.health
		
		# Bonus for weak blocks
		if target_block.__class__.__name__ == "WeakBlock":
			score += 50
		elif target_block.__class__.__name__ == "NormalBlock":
			score += 25
			
		# Penalty for extreme paddle positions (prefer more central positions)
		screen_center_y = settings.LEVEL_Y + (settings.LEVEL_MAX_Y - settings.LEVEL_Y) / 2.0
		position_penalty = abs(target_paddle_center - screen_center_y) / (settings.LEVEL_MAX_Y - settings.LEVEL_Y)
		score -= position_penalty * 30
		
		# Penalty for extreme angles (prefer more direct shots)
		angle_penalty = abs(normalized_distance - 0.5) * 20
		score -= angle_penalty
		
		return (target_paddle_center, score)

	def decide_energy_usage(self):
		"""
		Makes intelligent decisions about when to use energy attacks.
		Returns True if should attack, False otherwise.
		"""
		# Base chance on energy level - increased minimum energy requirement
		if self.owner.energy < 40:  # Increased from 20 to 40
			return False
			
		# Count enemy blocks and blocks in potential laser path
		enemy_block_count = 0
		blocks_in_path = 0
		max_blocks_in_path = 0
		paddle_center_y = self.rect.y + self.rect.height / 2.0
		laser_height = 40  # Approximate laser height at base power
		
		# Adjust laser height based on energy level
		if self.owner.energy >= 100:
			laser_height = 200  # 5x power
		elif self.owner.energy >= 80:
			laser_height = 160  # 4x power
		elif self.owner.energy >= 60:
			laser_height = 120  # 3x power
		elif self.owner.energy >= 40:
			laser_height = 80   # 2x power
		
		# Check blocks in potential laser path and count total enemy blocks
		for block in groups.Groups.block_group:
			if block.owner != self.owner:
				enemy_block_count += 1
				block_center_y = block.rect.y + block.rect.height / 2.0
				if abs(block_center_y - paddle_center_y) <= laser_height:
					# Block is within vertical range of laser
					if (self.x < settings.SCREEN_WIDTH / 2.0 and block.rect.x > self.rect.x) or \
					   (self.x > settings.SCREEN_WIDTH / 2.0 and block.rect.x < self.rect.x):
						blocks_in_path += 1
				max_blocks_in_path += 1
		
		# Adjust base chance based on enemy block count - more conservative scaling
		if enemy_block_count <= 3:
			# Very aggressive when enemy has few blocks - use energy whenever possible
			base_chance = (self.owner.energy - 40) / 100.0  # Scales from 0.0 at 40 energy to 0.6 at full energy
			# Even more aggressive if we can hit multiple of the remaining blocks
			if blocks_in_path > 0 and blocks_in_path >= enemy_block_count * 0.5:
				base_chance *= 1.5  # Reduced multiplier from 2.0
		elif enemy_block_count <= 6:
			# Moderately aggressive
			base_chance = (self.owner.energy - 40) / 200.0  # Scales from 0.0 at 40 energy to 0.3 at full energy
		else:
			# Very conservative when enemy has many blocks - gather more energy
			base_chance = (self.owner.energy - 40) / 300.0  # Scales from 0.0 at 40 energy to 0.2 at full energy
			# Save up energy unless we can hit multiple blocks
			if blocks_in_path <= 1:
				base_chance *= 0.3  # More aggressive reduction from 0.5
		
		# Significant boost if we can hit multiple blocks - adjusted scaling
		if blocks_in_path > 0:
			# Scale multiplier based on how many enemy blocks remain
			if enemy_block_count <= 3:
				# High multiplier when few blocks remain
				base_chance *= (1.0 + (blocks_in_path / max(1, enemy_block_count)) * 2.0)  # Reduced from 3.0
			elif enemy_block_count <= 6:
				# Moderate multiplier for moderate block count
				base_chance *= (1.0 + (blocks_in_path / max(1, enemy_block_count)) * 1.5)  # Reduced from 2.5
			else:
				# Lower multiplier for many blocks
				base_chance *= (1.0 + (blocks_in_path / max(1, enemy_block_count)) * 1.0)  # Reduced from 2.0
		
		# Check if enemy paddle is vulnerable (far from balls)
		enemy_vulnerable = False
		for player in groups.Groups.player_group:
			if player != self.owner:
				for paddle in player.paddle_group:
					for ball in groups.Groups.ball_group:
						if math.fabs(paddle.rect.y + paddle.rect.height/2 - (ball.y + ball.rect.height/2)) > paddle.rect.height:
							enemy_vulnerable = True
							break
		
		if enemy_vulnerable:
			# Scale vulnerability bonus based on remaining blocks - reduced bonuses
			if enemy_block_count <= 3:
				base_chance *= 1.5  # Reduced from 2.0
			elif enemy_block_count <= 6:
				base_chance *= 1.25  # Reduced from 1.5
			else:
				base_chance *= 1.1  # Reduced from 1.25
			
		# Increase chance if we're losing - reduced bonuses
		if hasattr(self.owner, "lives") and self.owner.lives is not None and hasattr(self.owner, "score") and self.owner.score is not None:
			for player in groups.Groups.player_group:
				if player != self.owner:
					if (hasattr(player, "lives") and player.lives > self.owner.lives) or \
					   (hasattr(player, "score") and player.score > self.owner.score):
						# Scale losing bonus based on remaining blocks
						if enemy_block_count <= 3:
							base_chance *= 1.3  # Reduced from 1.5
						else:
							base_chance *= 1.15  # Reduced from 1.25
						break
		
		# Higher chance to use laser if we have more energy (exponential scaling) - more conservative
		# Scale energy factor based on enemy block count
		if enemy_block_count <= 3:
			# More aggressive energy usage when few blocks remain
			energy_factor = math.pow(self.owner.energy / 100.0, 1.5)  # Increased exponent from 1.2
		elif enemy_block_count <= 6:
			energy_factor = math.pow(self.owner.energy / 100.0, 1.8)  # Increased exponent from 1.5
		else:
			# Save energy when many blocks remain
			energy_factor = math.pow(self.owner.energy / 100.0, 2.2)  # Increased exponent from 1.8
		
		base_chance *= (1.0 + energy_factor)
		
		# Adjust max chance based on enemy block count - more conservative
		if enemy_block_count <= 3:
			max_chance = 0.9  # Reduced from 1.0
		elif enemy_block_count <= 6:
			max_chance = 0.8  # Reduced from 0.95
		else:
			max_chance = 0.7  # Reduced from 0.9
			
		base_chance = min(base_chance, max_chance)
		
		return random.random() <= base_chance

	def update(self, main_clock):
		# AI implementation
		if self.owner.ai_difficulty > 0:
			self.key_up_pressed = False
			self.key_down_pressed = False

			if self.x < settings.SCREEN_WIDTH / 2:
				paddle_side_left = True
			else:
				paddle_side_left = False

			# Only recalculate decisions periodically to reduce jerky movement
			current_time = pygame.time.get_ticks() / 1000.0
			should_recalculate = (current_time - self.last_decision_time) >= self.decision_cooldown
			
			# Always recalculate if we don't have a target yet
			if self.target_y is None:
				should_recalculate = True
				
			# Recalculate more frequently if we've been missing balls
			if self.missed_balls > 0:
				should_recalculate = should_recalculate or (current_time - self.last_decision_time) >= (self.decision_cooldown * 0.5)
				
			# Decide whether to use energy attack (less frequently than movement decisions)
			if should_recalculate and random.random() < 0.2:  # Only check 20% of decision times
				if self.decide_energy_usage():
					self.owner.attack()

			if should_recalculate:
				self.last_decision_time = current_time
				
				# Reset the targeting variables
				old_focused_item = self.focused_item
				old_prediction = self.current_prediction
				
				self.focused_item = None
				self.min_distance = 99999
				self.predicted_y = None
				self.current_prediction = None
				self.prediction_confidence = 0

				# Find the most important item to focus on
				# First check balls (prioritize balls over projectiles)
				for ball in groups.Groups.ball_group:
					self.decide_which_item(ball)
						
				# Then check projectiles
				for projectile in groups.Groups.projectile_group:
					self.decide_which_item(projectile)
					
				# If we found a focused item, update target position
				if self.focused_item is not None:
					# Check if this is our ball and it's approaching our paddle
					is_our_ball = hasattr(self.focused_item, "owner") and self.focused_item.owner is not None and self.focused_item.owner == self.owner
					ball_approaching = False
					
					if hasattr(self.focused_item, "x") and self.focused_item.x is not None:
						ball_x = self.focused_item.x + self.focused_item.rect.width / 2.0
						ball_distance = math.fabs(ball_x - (self.x + self.rect.width/2.0))
						
						# Consider balls behind the paddle if they're close
						if (paddle_side_left and ball_x < self.x + self.rect.width + 100) or \
						   (not paddle_side_left and ball_x > self.x - 100):
							ball_approaching = True
					
					# If this is our ball and it's approaching, try to aim it at opponent blocks
					if is_our_ball and ball_approaching and self.owner.ai_difficulty >= 2:
						aim_position = self.calculate_aim_position()
						if aim_position is not None:
							# For higher difficulties, prioritize aiming more
							if self.owner.ai_difficulty >= 3:
								self.target_y = (self.predicted_y * 0.6 + aim_position * 0.4)
							else:
								self.target_y = (self.predicted_y * 0.7 + aim_position * 0.3)
					else:
						# Different behavior based on AI difficulty
						if self.owner.ai_difficulty >= 3:
							# Expert AI: Good positioning with minimal error
							self.target_y = self.predicted_y
							
							# Add very small random offset for realism, but only when changing targets
							if self.focused_item != old_focused_item:
								offset_amount = self.rect.height * 0.03
								self.target_y += random.uniform(-offset_amount, offset_amount)
						
						elif self.owner.ai_difficulty == 2:
							# Medium AI: Good positioning with small error
							self.target_y = self.predicted_y
							
							# Add small random offset, but only when changing targets
							if self.focused_item != old_focused_item:
								offset_amount = self.rect.height * 0.08
								self.target_y += random.uniform(-offset_amount, offset_amount)
						
						else:
							# Easy AI: Basic positioning with moderate error
							self.target_y = self.predicted_y
							
							# Add moderate random offset, but only when changing targets
							if self.focused_item != old_focused_item:
								offset_amount = self.rect.height * 0.2
								self.target_y += random.uniform(-offset_amount, offset_amount)
				else:
					# No immediate threats, use strategic positioning
					self.target_y = self.strategic_positioning()
					
					# Add a slight bias toward the center when no immediate threats
					screen_center_y = settings.LEVEL_Y + (settings.LEVEL_MAX_Y - settings.LEVEL_Y) / 2.0
					self.target_y = (self.target_y * 0.7 + screen_center_y * 0.3)

			# If we have a target position, move toward it
			if self.target_y is not None:
				# Calculate the center of the paddle
				paddle_center_y = self.y + self.rect.height / 2.0
				
				# Calculate distance to target
				distance_to_target = self.target_y - paddle_center_y
				
				# Adjust buffer based on difficulty and missed balls
				effective_buffer = self.movement_buffer
				if self.owner.ai_difficulty >= 3:
					effective_buffer = max(1, self.movement_buffer - self.missed_balls)
				elif self.owner.ai_difficulty == 2:
					effective_buffer = max(2, self.movement_buffer - (self.missed_balls // 2))
				
				# Only move if we're outside the buffer zone
				if abs(distance_to_target) > effective_buffer:
					# Check if we need to change direction
					changing_direction = (distance_to_target > 0 and self.velocity_y < 0) or (distance_to_target < 0 and self.velocity_y > 0)
					
					# Only allow direction changes after cooldown
					if changing_direction:
						# Adjust cooldown based on missed balls
						effective_cooldown = self.direction_change_cooldown
						if self.missed_balls > 0:
							effective_cooldown *= 0.5
							
						if current_time - self.last_direction_change >= effective_cooldown:
							# Change direction and record the time
							self.last_direction_change = current_time
							if distance_to_target > 0:
								self.key_down_pressed = True
							else:
								self.key_up_pressed = True
					else:
						# Continue in same direction
						if distance_to_target > 0:
							self.key_down_pressed = True
						else:
							self.key_up_pressed = True
					
					# Adjust movement based on AI difficulty
					if self.owner.ai_difficulty < 2:
						# Easy AI occasionally hesitates
						hesitation_chance = 0.1
						if random.random() < hesitation_chance:
							self.key_up_pressed = False
							self.key_down_pressed = False
					elif self.owner.ai_difficulty == 2:
						# Medium AI rarely hesitates
						hesitation_chance = 0.03
						if random.random() < hesitation_chance:
							self.key_up_pressed = False
							self.key_down_pressed = False
			
			# Check if we might have missed a ball
			for ball in groups.Groups.ball_group:
				self.check_if_missed_ball(ball, paddle_side_left)
		else:
			# If no AI, we just check for key presses.
			self.key_up_pressed = pygame.key.get_pressed()[self.owner.key_up]
			self.key_down_pressed = pygame.key.get_pressed()[self.owner.key_down]

		# Check for key_up or key_down events. If key_up is pressed, the paddle will move up and vice versa for key_down.
		# However, we only move the paddle if max_speed is above zero, since if it is zero the paddle cannot move anyway.
		if self.max_speed > 0:
			if self.key_up_pressed:
					self.velocity_y -= self.acceleration
					if self.velocity_y < -self.max_speed:
						self.velocity_y = -self.max_speed
			elif self.key_down_pressed:
					self.velocity_y += self.acceleration
					if self.velocity_y > self.max_speed:
						self.velocity_y = self.max_speed
			elif self.velocity_y > 0:
				self.velocity_y -= self.retardation
				if self.velocity_y < 0:
					self.velocity_y = 0
			elif self.velocity_y < 0:
				self.velocity_y += self.retardation
				if self.velocity_y > 0:
					self.velocity_y = 0
		else:
			# If max_speed is zero, we still want to reduce our velocity.
			if self.velocity_y > 0:
				self.velocity_y -= self.retardation
				if self.velocity_y < 0:
					self.velocity_y = 0
			elif self.velocity_y < 0:
				self.velocity_y += self.retardation
				if self.velocity_y > 0:
					self.velocity_y = 0

		# Move the paddle according to its velocity.
		self.y += self.velocity_y * main_clock.delta_time
		self.rect.y = self.y

		# Move paddle to it's center x.
		if self.x > self.center_x:
			if self.x > self.center_x + Paddle.max_nudge_distance:
				self.x = self.center_x + Paddle.max_nudge_distance

			if self.x - Paddle.stabilize_speed * main_clock.delta_time < self.center_x:
				self.x = self.center_x
			else:
				self.x -= Paddle.stabilize_speed * main_clock.delta_time
		else:
			if self.x < self.center_x - Paddle.max_nudge_distance:
				self.x = self.center_x - Paddle.max_nudge_distance

			if self.x + Paddle.stabilize_speed * main_clock.delta_time > self.center_x:
				self.x = self.center_x
			else:
				self.x += Paddle.stabilize_speed * main_clock.delta_time
		self.rect.x = self.x

		# Check collision with y-edges.
		if self.rect.y < settings.LEVEL_Y:
			# Constrain paddle to screen size.
			self.y = settings.LEVEL_Y
			self.rect.y = self.y
		elif self.rect.y + self.rect.height > settings.LEVEL_MAX_Y:
			# Constrain paddle to screen size.
			self.y = settings.LEVEL_MAX_Y - self.rect.height
			self.rect.y = self.y

		# Move any effects on the paddle.
		for effect in self.effect_group:
			effect.rect.x = self.rect.x
			effect.rect.y = self.rect.y

	def check_if_missed_ball(self, ball, paddle_side_left):
		"""
		Checks if we just missed a ball and updates the missed_balls counter.
		"""
		# If ball just passed our paddle
		if (paddle_side_left and ball.x < self.x and ball.rect.right > self.x - 20) or \
		   (not paddle_side_left and ball.x > self.x + self.rect.width and ball.rect.left < self.x + self.rect.width + 20):
			# Compare the center of the ball to the center of the paddle
			paddle_center_y = self.y + self.rect.height / 2.0
			ball_center_y = ball.y + ball.rect.height / 2.0
			
			if abs(ball_center_y - paddle_center_y) < self.rect.height * 1.5:
				# We probably missed it
				self.missed_balls += 1
				# Force recalculation next frame
				self.last_decision_time = 0
				return True
		return False

	def unleash_charge(self):
		pass