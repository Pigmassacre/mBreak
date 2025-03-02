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
        
		# New AI variables for smoother movement
		self.target_y = None
		self.last_decision_time = 0
		self.decision_cooldown = 0.1  # Seconds between major decision recalculations
		self.movement_buffer = 5  # Pixels of buffer to prevent oscillation
		self.current_prediction = None
		self.prediction_confidence = 0
		self.last_direction_change = 0
		self.direction_change_cooldown = 0.15  # Seconds between direction changes

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

		if hasattr(self, 'image'):
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
		if hasattr(self, 'shadow'):
			self.shadow.kill()

		# Then, create a (new) shadow.
		self.shadow = shadow.Shadow(self)

	def add_size(self, added_width, added_height):
		self.set_size(self.actual_width + added_width, self.actual_height + added_height)

	def on_hit(self, entity):
		# If hit by an enemy ball, we increase our owners energy.
		if entity.owner != self.owner:
			if self.owner.energy + self.owner.energy_increase_on_hit < self.owner.max_energy:
				self.owner.energy += self.owner.energy_increase_on_hit
			else:
				self.owner.energy = self.owner.max_energy
		else:
			if self.owner.energy + self.owner.energy_increase_on_hit < self.owner.max_energy:
				self.owner.energy += self.owner.energy_increase_on_hit / 2.0
			else:
				self.owner.energy = self.owner.max_energy

		# Create a new on hit effect.
		self.effect_group.add(flash.Flash(self, copy.copy(Paddle.hit_effect_start_color), copy.copy(Paddle.hit_effect_final_color), Paddle.hit_effect_tick_amount))

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
		distance_y = math.fabs((self.rect.y + self.rect.height / 2.0) - predicted_y)
		total_distance = math.sqrt(math.pow(distance_x, 2) + math.pow(distance_y, 2))
		
		# Adjust distance based on item properties
		adjusted_distance = self.adjust_distance_by_priority(item, total_distance)
		
		# Adjust by confidence and time to reach
		adjusted_distance = adjusted_distance / confidence
		
		# If this item is closer than our current focused item, focus on it
		if adjusted_distance < self.min_distance:
			self.min_distance = adjusted_distance
			self.focused_item = item
			self.predicted_y = predicted_y
			self.current_prediction = prediction_data
			self.prediction_confidence = confidence

	def predict_trajectory(self, item):
		"""
		Predicts where the item will be when it reaches the paddle's x position.
		Returns (x, y) coordinates or None if item won't reach paddle.
		"""
		# Determine if we're the left or right paddle
		paddle_side_left = self.x < settings.SCREEN_WIDTH / 2
		
		# Check if item is moving toward this paddle
		if paddle_side_left:
			# Left paddle: item must be moving left (angle between π/2 and 3π/2)
			if not (item.angle >= math.pi / 2.0 and item.angle <= 3 * math.pi / 2.0):
				return None
			# Item must be to the right of paddle
			if item.x < self.x + self.width:
				return None
		else:
			# Right paddle: item must be moving right (angle between -π/2 and π/2 or between 3π/2 and 5π/2)
			if not ((item.angle <= math.pi / 2.0 and item.angle >= -math.pi / 2.0) or 
					(item.angle >= 3 * math.pi / 2.0 and item.angle <= 2 * math.pi + math.pi / 2.0)):
				return None
			# Item must be to the left of paddle
			if item.x > self.x:
				return None
				
		# Calculate time to reach paddle's x position
		speed_x = item.speed * math.cos(item.angle)
		
		# If speed_x is too small, item is moving almost vertically
		if abs(speed_x) < 0.1:
			return None
			
		# Calculate time to reach paddle
		if paddle_side_left:
			time_to_reach = (self.x + self.width - item.x) / speed_x
		else:
			time_to_reach = (self.x - item.x - item.rect.width) / speed_x
			
		# If time is negative, item is moving away from paddle
		if time_to_reach <= 0:
			return None
			
		# Calculate y position when item reaches paddle
		speed_y = item.speed * math.sin(item.angle)
		predicted_y = item.y + speed_y * time_to_reach
		
		# Check if item will hit top or bottom wall before reaching paddle
		# and calculate bounce if needed
		level_height = settings.LEVEL_MAX_Y - settings.LEVEL_Y
		bounces = 0
		max_bounces = 5  # Limit calculation to prevent infinite loops
		
		while bounces < max_bounces:
			if predicted_y < settings.LEVEL_Y:
				# Bounce off top wall
				overflow = settings.LEVEL_Y - predicted_y
				predicted_y = settings.LEVEL_Y + overflow
				bounces += 1
			elif predicted_y + item.rect.height > settings.LEVEL_MAX_Y:
				# Bounce off bottom wall
				overflow = (predicted_y + item.rect.height) - settings.LEVEL_MAX_Y
				predicted_y = settings.LEVEL_MAX_Y - item.rect.height - overflow
				bounces += 1
			else:
				# No more bounces needed
				break
		
		# Calculate confidence in prediction based on time and bounces
		confidence = 1.0 - (time_to_reach / 120.0) - (bounces * 0.15)
		confidence = max(0.1, min(1.0, confidence))
		
		return (self.x if paddle_side_left else self.x, predicted_y + item.rect.height / 2.0, confidence, time_to_reach)
		
	def adjust_distance_by_priority(self, item, distance):
		"""
		Adjusts the calculated distance based on item priority and properties.
		Returns the adjusted distance value.
		"""
		adjusted_distance = distance
		
		# Prioritize based on item type
		if hasattr(item, "owner"):
			# Prioritize enemy items over own items
			if item.owner == self.owner:
				adjusted_distance *= 2.0
			else:
				adjusted_distance *= 0.5
				
		# Prioritize based on speed
		if hasattr(item, "effect_group"):
			for effect in item.effect_group:
				if effect.__class__ == speed.Speed:
					adjusted_distance *= 0.5  # Higher priority for faster items
					
		# Prioritize based on distance from paddle
		if hasattr(item, "x"):
			x_distance = math.fabs(self.rect.x - item.x)
			if x_distance < 200:  # Close items get higher priority
				adjusted_distance *= 0.8
				
		return adjusted_distance
		
	def strategic_positioning(self):
		"""
		Determines the best strategic position when no immediate threats are present.
		"""
		# Default to center position
		target_y = settings.LEVEL_Y + (settings.LEVEL_MAX_Y - settings.LEVEL_Y) / 2.0 - self.rect.height / 2.0
		
		# If there are balls in play, try to position based on their general position
		ball_count = 0
		ball_y_sum = 0
		
		for ball in groups.Groups.ball_group:
			ball_count += 1
			ball_y_sum += ball.y + ball.rect.height / 2.0
			
		if ball_count > 0:
			# Position slightly toward the average ball position
			avg_ball_y = ball_y_sum / ball_count
			target_y = target_y * 0.7 + avg_ball_y * 0.3
			
		return target_y
		
	def decide_energy_usage(self):
		"""
		Makes intelligent decisions about when to use energy attacks.
		Returns True if should attack, False otherwise.
		"""
		# Base chance on energy level
		if self.owner.energy < 20:
			return False
			
		base_chance = self.owner.energy / 200.0  # 0.1 at 20 energy, 0.5 at full energy
		
		# Increase chance if enemy paddle is far from balls
		enemy_vulnerable = False
		for player in groups.Groups.player_group:
			if player != self.owner:
				for paddle in player.paddle_group:
					for ball in groups.Groups.ball_group:
						if math.fabs(paddle.rect.y + paddle.rect.height/2 - (ball.y + ball.rect.height/2)) > paddle.rect.height:
							enemy_vulnerable = True
							break
		
		if enemy_vulnerable:
			base_chance *= 2.0
			
		# Increase chance if we're losing
		if hasattr(self.owner, "lives") and hasattr(self.owner, "score"):
			for player in groups.Groups.player_group:
				if player != self.owner:
					if (hasattr(player, "lives") and player.lives > self.owner.lives) or \
					   (hasattr(player, "score") and player.score > self.owner.score):
						base_chance *= 1.5
						break
		
		# Cap the chance at 0.8 (80%)
		base_chance = min(base_chance, 0.8)
		
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
				# First check projectiles
				for projectile in groups.Groups.projectile_group:
					self.decide_which_item(projectile)
						
				# Then check balls
				for ball in groups.Groups.ball_group:
					self.decide_which_item(ball)
					
				# If we found a focused item, update target position
				if self.focused_item is not None:
					# Different behavior based on AI difficulty
					if self.owner.ai_difficulty >= 3:
						# Expert AI: Good positioning with minimal error
						self.target_y = self.predicted_y - self.rect.height / 2.0
						
						# Add small random offset for realism, but only when changing targets
						if self.focused_item != old_focused_item:
							self.target_y += random.uniform(-self.rect.height * 0.05, self.rect.height * 0.05)
					
					elif self.owner.ai_difficulty == 2:
						# Medium AI: Good positioning with moderate error
						self.target_y = self.predicted_y - self.rect.height / 2.0
						
						# Add moderate random offset, but only when changing targets
						if self.focused_item != old_focused_item:
							self.target_y += random.uniform(-self.rect.height * 0.15, self.rect.height * 0.15)
					
					else:
						# Easy AI: Basic positioning with significant error
						self.target_y = self.predicted_y - self.rect.height / 2.0
						
						# Add large random offset, but only when changing targets
						if self.focused_item != old_focused_item or random.random() < 0.1:
							self.target_y += random.uniform(-self.rect.height * 0.4, self.rect.height * 0.4)
				else:
					# No immediate threats, use strategic positioning
					self.target_y = self.strategic_positioning()
			
			# If we have a target position, move toward it
			if self.target_y is not None:
				# Calculate the center of the paddle
				paddle_center_y = self.y + self.rect.height / 2.0
				
				# Calculate distance to target
				distance_to_target = self.target_y - paddle_center_y
				
				# Only move if we're outside the buffer zone to prevent oscillation
				if abs(distance_to_target) > self.movement_buffer:
					# Check if we need to change direction
					changing_direction = (distance_to_target > 0 and self.velocity_y < 0) or (distance_to_target < 0 and self.velocity_y > 0)
					
					# Only allow direction changes after cooldown to prevent jerky movement
					if changing_direction:
						if current_time - self.last_direction_change < self.direction_change_cooldown:
							# Don't change direction yet, just slow down
							if self.velocity_y > 0:
								self.key_up_pressed = True
							else:
								self.key_down_pressed = True
						else:
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
						if random.random() < 0.15:
							self.key_up_pressed = False
							self.key_down_pressed = False
					elif self.owner.ai_difficulty == 2:
						# Medium AI occasionally hesitates
						if random.random() < 0.05:
							self.key_up_pressed = False
							self.key_down_pressed = False
				else:
					# We're close enough to the target, stop moving
					# This prevents oscillation around the target
					pass
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

	def unleash_charge(self):
		pass