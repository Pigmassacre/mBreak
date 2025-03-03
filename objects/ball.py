__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import copy
import math
import random
import other.useful as useful
import objects.paddle as paddle
import objects.particle as particle
import objects.trace as trace
import objects.shadow as shadow
import objects.effects.flash as flash
import objects.effects.stun as stun
import objects.dummy as dummy
import objects.groups as groups
import settings.settings as settings
import settings.graphics as graphics
import objects.trajectory as trajectory
from settings.sounds import BALL_SOUND, play_sound

"""

This is the Ball class. Each ball created in the game uses this class. Balls take care of their own collision handling.
Balls have a position in the game world, a rect used to handle drawing the ball and calculating the collisions, an image
that is used when drawing the ball, an angle at which they are traveling and the speed they are traveling at. (The have more
attributes than that, as you can see below).

When a ball collides with either a block, another ball or a paddle (or the edges of the game area) they each ball is responsible
for their own collision handling. I would argue the collision handling is very rigid, as I've played a few hundred games and haven't
seen any odd side effects.

Anyway, the code is commented pretty thoroughly, so read on if you're interested!

"""

def convert():
	# Same here as with powerups, arguably this could be put in the constructor (as it's safe to call this method more than once)
	# but I worry about performance (pygame uses SDL (not SDL 2.0) which uses the CPU for everything, so it's pretty performance heavy).
	Ball.image.convert()

class Ball(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	image = pygame.image.load("res/ball/ball.png")

	# Initialize the sound effect.
	sound_effect = BALL_SOUND

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width()
	height = image.get_height()
	speed = 1.5 * settings.GAME_FPS
	max_speed = 5 * settings.GAME_FPS
	speed_step = 0.75 * settings.GAME_FPS
	paddle_nudge_distance = 1.34
	least_allowed_vertical_angle = 0.32 # Exists to prevent the balls from getting stuck bouncing up and down in the middle of the gamefield.
	trace_spawn_rate = 0.53 * settings.GAME_FPS
	particle_spawn_amount = 3

	# Damage stuff.
	damage = 10
	damage_percentage_dealt_to_own_blocks = 0.25

	# Smash stuff.
	smash_speed = 0.2 * settings.GAME_FPS
	smash_damage_factor = 1
	smash_max_stack = 12
	smash_effect_size_increase = 1
	smash_effect_start_color = pygame.Color(255, 255, 255, 255)
	smash_effect_final_color = pygame.Color(255, 255, 255, 0)
	smash_effect_tick_amount = 10 * settings.GAME_FPS

	# On hit effect values.
	hit_effect_start_color = pygame.Color(255, 255, 255, 150)
	hit_effect_final_color = pygame.Color(255, 255, 255, 0)
	hit_effect_tick_amount = 8 * settings.GAME_FPS

	# Scale image to match the game scale.
	image = pygame.transform.scale(image, (width, height))

	def __init__(self, x, y, angle, owner):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Store the owner.
		self.owner = owner

		# Store the x and y position.
		self.x = x
		self.y = y

		# Store the angle.
		self.angle = angle

		# Store the speed.
		self.speed = Ball.speed
		self.base_speed = Ball.speed
		self.tick_speed = 0

		# Track consecutive paddle hits for energy growth
		self.paddle_hit_counter = 0

		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, Ball.width, Ball.height)

		# Keep track of the balls position in the previous frame, used for collision handling.
		self.previous = pygame.rect.Rect(self.x, self.y, Ball.width, Ball.height)

		# Set maximum speed of the ball.
		self.max_speed = Ball.max_speed

		# Set the speed variable.
		self.speed = Ball.speed
		self.tick_speed = self.speed
		
		# Store the current level of smash stack.
		self.smash_stack = 0

		# Create one image attribute per player.
		self.player_images = {}
		for player in groups.Groups.player_group:
			player_image = Ball.image.copy()
			
			# Colorize the image to the color of the player.
			useful.colorize_image(player_image, player.color)
			
			# Finally, add this image to the list of player images.
			self.player_images[player] = player_image

		# Create the image attribute that is drawn to the surface.
		self.image = self.player_images[self.owner]

		# We save a reference to the parents color in our own variable, so that classes and modules
		# that want to use our color do not have to call us.owner.color.
		self.color = self.owner.color

		# If collided is True, the ball sound is played.
		self.collided = False

		# Setup the trace time keeping variable.
		self.trace_spawn_time = 0
		
		# Create a shadow.
		self.shadow = shadow.Shadow(self)

		# Store the ball in the owners ball_group and the main ball_group.
		self.owner.ball_group.add(self)
		groups.Groups.ball_group.add(self)

		# Create an effect group to handle effects on this ball.
		self.effect_group = pygame.sprite.Group()

		# Add gravity properties (initially no gravity)
		self.gravity_direction = 0
		self.gravity_strength = 0

		# Create a trajectory visualization
		self.trajectory = trajectory.Trajectory(self)

	def destroy(self):
		# This should be called when the ball is to be destroyed. It will take care of killing itself and anything affecting it completely.
		self.kill()
		self.shadow.kill()
		for effect in self.effect_group:
			effect.destroy()
		self.trajectory.destroy()

	def on_hit(self):
		# Create a new dummy and add a on hit effect to that dummy.
		effect_dummy = dummy.Dummy(1000, self.rect.x, self.rect.y, self.rect.width, self.rect.height)
		effect_dummy.add_flash(copy.copy(Ball.hit_effect_start_color), copy.copy(Ball.hit_effect_final_color), Ball.hit_effect_tick_amount)

	def change_owner(self, new_owner):
		if new_owner != self.owner:
			self.owner = new_owner
			self.image = self.player_images[self.owner]
			self.color = self.owner.color

	def update(self, main_clock):
		# We assume we haven't collided with anything yet.
		self.collided = False

		# Store the amount of speed we've handled this turn.
		speed_handled = 0

		# While we still have speed to handle...
		while speed_handled < self.speed:
			# Calculate how much speed we should handle this step.
			if speed_handled + self.tick_speed > self.speed:
				# If adding tick_speed would put us over the total amount of speed, we just add the difference.
				self.tick_speed = self.speed - speed_handled
			
			# Move the ball with speed in consideration.
			self.x = self.x + (math.cos(self.angle) * self.tick_speed * main_clock.delta_time)
			self.y = self.y + (math.sin(self.angle) * self.tick_speed * main_clock.delta_time)
			self.rect.x = self.x
			self.rect.y = self.y

			# Check for collision with paddles.
			self.check_collision_paddles()

			# Check for collision with other balls.
			self.check_collision_balls()

			# Check for collision with blocks.
			self.check_collision_blocks()

			# Check for collision with powerups.
			self.check_collision_powerups()

			# Check if we've hit any walls.
			if self.rect.x < settings.LEVEL_X:
				# We hit the left wall.
				self.hit_wall()

				# Reverse angle on x-axis.
				if self.angle > 0:
					self.angle = math.pi - self.angle
				else:
					self.angle = -math.pi - self.angle

				# Constrain ball to screen size.
				self.x = settings.LEVEL_X
				self.rect.x = self.x
			elif self.rect.x + self.rect.width > settings.LEVEL_MAX_X:
				# We hit the right wall.
				self.hit_wall()

				# Reverse angle on x-axis.
				if self.angle > 0:
					self.angle = math.pi - self.angle
				else:
					self.angle = -math.pi - self.angle

				# Constrain ball to screen size.
				self.x = settings.LEVEL_MAX_X - self.rect.width
				self.rect.x = self.x
			elif self.rect.y < settings.LEVEL_Y:
				# We hit the top wall.
				self.hit_wall()

				# Reverse angle on y-axis.
				self.angle = -self.angle

				# Constrain ball to screen size.
				self.y = settings.LEVEL_Y
				self.rect.y = self.y
			elif self.rect.y + self.rect.height > settings.LEVEL_MAX_Y:
				# We hit the bottom wall.
				self.hit_wall()

				# Reverse angle on y-axis.
				self.angle = -self.angle

				# Constrain ball to screen size.
				self.y = settings.LEVEL_MAX_Y - self.rect.height
				self.rect.y = self.y

			# If we have collided with anything, play the sound effect.
			if self.collided:
				play_sound(Ball.sound_effect)

			# Increase the amount of speed that we've handled this turn.
			speed_handled += self.tick_speed

		# We check if it's time to spawn a trace.
		self.trace_spawn_time += main_clock.get_time()
		if self.trace_spawn_time >= Ball.trace_spawn_rate:
			# It's time, so we spawn a trace (if the graphics options allows it).
			if graphics.TRACES:
				trace.Trace(self)
				self.trace_spawn_time = 0

	def hit_wall(self):
		# Spawn some particles.
		self.spawn_particles()

		# Tell ourselves that we have been hit.
		self.on_hit()

		# Tell all the effects that we've just hit a wall.
		for effect in self.effect_group:
			effect.on_hit_wall()

		# Obviously we have collided with something, so we set collided to True.
		self.collided = True

	def calculate_smash(self, paddle):
		# Add smash speed to ourselves.
		self.speed += Ball.smash_speed
		
		# Also update the base speed
		self.base_speed += Ball.smash_speed

		# Increase our smash stack.
		self.smash_stack += 1

	def place_left_of(self, other):
		self.x = other.rect.left - self.rect.width - 1
		self.rect.x = self.x

	def place_right_of(self, other):
		self.x = other.rect.right + 1
		self.rect.x = self.x

	def place_over(self, other):
		self.y = other.rect.top - self.rect.height - 1
		self.rect.y = self.y

	def place_below(self, other):
		self.y = other.rect.bottom + 1
		self.rect.y = self.y

	def spawn_particles(self):
		# Spawn a slightly random amount of particles.
		for _ in range(0, Ball.particle_spawn_amount):
			width = random.uniform(self.rect.width / 4.0, self.rect.width / 3.0)
			angle = self.angle + random.uniform(-0.20, 0.20)
			max_speed = min(self.speed, self.max_speed / 2.0)
			speed = random.uniform(max_speed - max_speed / 7.0, max_speed + max_speed / 7.0)
			retardation = self.speed / 24.0
			alpha_step = 5 * settings.GAME_FPS
			particle.Particle(self.x + self.rect.width / 2, self.y + self.rect.height / 2, width, width, angle, speed, retardation, self.color, alpha_step)

	def check_collision_paddles(self):
		# This method is used to check if we've collided with any paddles. If a collision is detected, we
		# also handle it here.
		paddle_collide_list = pygame.sprite.spritecollide(self, groups.Groups.paddle_group, False)
		for paddle in paddle_collide_list:
			self.hit_paddle(paddle)
			if self.rect.bottom >= paddle.rect.top and self.rect.top < paddle.rect.top:
				# Top side of paddle collided with. Compare with edges:
				if paddle.rect.left - self.rect.left > paddle.rect.top - self.rect.top:
					# The ball collides more with the left side than top side.
					self.hit_left_side_of_paddle(paddle)
				elif self.rect.right - paddle.rect.right > paddle.rect.top - self.rect.top:
					# The ball collides more with the right side than top side.
					self.hit_right_side_of_paddle(paddle)
				else:
					# The ball collides more with the top side than any other side.
					if self.angle < math.pi:
						# So we reverse the angle.
						self.angle = -self.angle

					# Place ball on top of the paddle.
					self.place_over(paddle)
			elif self.rect.top <= paddle.rect.bottom and self.rect.bottom > paddle.rect.bottom:
				# Bottom side of paddle collided with. Compare with edges:
				if paddle.rect.left - self.rect.left > self.rect.bottom - paddle.rect.bottom:
					# The ball collides more with the left side than top side.
					self.hit_left_side_of_paddle(paddle)
				elif self.rect.right - paddle.rect.right > self.rect.bottom - paddle.rect.bottom:
					# The ball collides more with the right side than top side.
					self.hit_right_side_of_paddle(paddle)
				else:
					# The ball collides more with the bottom side than any other side.
					if self.angle > math.pi:
						# So we reverse the angle.
						self.angle = -self.angle

					# Place ball beneath the paddle.
					self.place_below(paddle)
			elif self.rect.right >= paddle.rect.left and self.rect.left < paddle.rect.left:
				# Left side of paddle collided with.
				self.hit_left_side_of_paddle(paddle)
			elif self.rect.left <= paddle.rect.right and self.rect.right > paddle.rect.right:
				# Right side of paddle collided with.
				self.hit_right_side_of_paddle(paddle)

	def remove_smash_effects(self):
		# Remove all stun effects.
		for effect in self.effect_group:
			if effect.__class__ == stun.Stun:
				effect.destroy()

		# Remove smash speed.
		self.speed = Ball.speed
		
		# Also reset the base speed
		self.base_speed = Ball.speed

		# Then reset our smash stack.
		self.smash_stack = 0

	def hit_paddle(self, paddle):
		# Spawn a few particles.
		self.spawn_particles()

		# Calculate the spin.
		self.calculate_smash(paddle)

		# Tell ourselves that we have been hit.
		self.on_hit()

		# Increment paddle hit counter
		self.paddle_hit_counter += 1

		# Tell the paddle that it has been hit.
		paddle.on_hit(self)

		# Tell all the effects that we've just hit a paddle.
		for effect in self.effect_group:
			effect.on_hit_paddle(paddle)

		# Attach a new flash effect to the ball.
		self.effect_group.add(flash.Flash(self, copy.copy(Ball.smash_effect_start_color), copy.copy(Ball.smash_effect_final_color), Ball.smash_effect_tick_amount))

		# Change the owner of the ball to the owner of the paddle.
		self.change_owner(paddle.owner)

		# We hit a paddle, so...
		self.collided = True

	def hit_left_side_of_paddle(self, paddle):
		# Calculate the new angle of the ball.
		paddle_center = paddle.y + paddle.rect.height / 2.0
		distance_from_paddle_center = (self.y + self.height / 2.0) - paddle_center
		max_distance = (paddle.y + paddle.rect.height + self.height) - paddle_center
		normalized_distance = (distance_from_paddle_center / max_distance)
		max_angle_offset = (math.pi / 2 - Ball.least_allowed_vertical_angle)
		self.angle = math.pi - normalized_distance * max_angle_offset

		# Place ball to the left of the paddle.
		self.place_left_of(paddle)

		# Nudge paddle a tiny bit.
		paddle.x += Ball.paddle_nudge_distance

	def hit_right_side_of_paddle(self, paddle):
		# Calculate the new angle of the ball.
		paddle_center = paddle.y + paddle.rect.height / 2
		distance_from_paddle_center = (self.y + self.height / 2) - paddle_center
		max_distance = (paddle.y + paddle.rect.height + self.height) - paddle_center
		normalized_distance = (distance_from_paddle_center / max_distance)
		max_angle_offset = (math.pi / 2 - Ball.least_allowed_vertical_angle)
		self.angle = normalized_distance * max_angle_offset

		# Place ball to the right of the paddle.
		self.place_right_of(paddle)

		# Nudge paddle a tiny bit.
		paddle.x -= Ball.paddle_nudge_distance

	def check_collision_balls(self):
		# This method is used to check for collision with other balls. If a collision is detected, it is also
		# handled here.
		groups.Groups.ball_group.remove(self) # We don't want to check for collisions against ourselves!
		ball_collide_list = pygame.sprite.spritecollide(self, groups.Groups.ball_group, False)
		for ball in ball_collide_list:
			self.hit_ball(ball)
			if self.rect.bottom >= ball.rect.top and self.rect.top < ball.rect.top:
				# Top side of ball collided with. Compare with edges:
				if ball.rect.left - self.rect.left > ball.rect.top - self.rect.top:
					# The ball collides more with the left side than top side.
					# Place ball to the left of the ball.
					self.place_left_of(ball)
				elif self.rect.right - ball.rect.right > ball.rect.top - self.rect.top:
					# The ball collides more with the right side than top side.
					# Place ball to the right of the ball.
					self.place_right_of(ball)
				else:
					# Place ball on top of the ball.
					self.place_over(ball)
			elif self.rect.top <= ball.rect.bottom and self.rect.bottom > ball.rect.bottom:
				# Bottom side of ball collided with.
				if ball.rect.left - self.rect.left > self.rect.bottom - ball.rect.bottom:
					# The ball collides more with the left side than top side.
					# Place ball to the left of the ball.
					self.place_left_of(ball)
				elif self.rect.right - ball.rect.right > self.rect.bottom - ball.rect.bottom:
					# The ball collides more with the right side than top side.
					# Place ball to the right of the ball.
					self.place_right_of(ball)
				else:
					# The ball collides more with the bottom side than any other side.
					# Place ball beneath the ball.
					self.place_below(ball)
			elif self.rect.right >= ball.rect.left and self.rect.left < ball.rect.left:
				# Left side of ball collided with.
				# Place ball to the left of the ball.
				self.place_left_of(ball)
			elif self.rect.left <= ball.rect.right and self.rect.right > ball.rect.right:
				# Right side of ball collided with.
				# Place ball to the right of the ball.
				self.place_right_of(ball)

			# Handle self.
			delta_x = self.rect.centerx - ball.rect.centerx
			delta_y = self.rect.centery - ball.rect.centery
			self.angle = math.atan2(delta_y, delta_x)

			# Handle other ball.
			delta_x = ball.rect.centerx - self.rect.centerx
			delta_y = ball.rect.centery - self.rect.centery
			ball.angle = math.atan2(delta_y, delta_x)
		groups.Groups.ball_group.add(self)

	def hit_ball(self, ball):
		# Spawn some particles.
		self.spawn_particles()

		# Tell self that we've been hit.
		self.on_hit()

		# Tell the other ball that it has been hit.
		ball.on_hit()

		# Tell all the effects that we've just hit another ball.
		for effect in self.effect_group:
			effect.on_hit_ball(ball)

		# We just collided with another ball, so!
		self.collided = True

	def check_collision_blocks(self):
		# This check for collision with blocks (and handles them if they are detected).
		blocks_collided_with = pygame.sprite.spritecollide(self, groups.Groups.block_group, False)
		
		if not blocks_collided_with:
			return  # No collisions, nothing to do
		
		# Calculate current velocity components
		velocity_x = math.cos(self.angle) * self.speed
		velocity_y = math.sin(self.angle) * self.speed
		
		# Store original position and velocity for potential rollback
		original_x, original_y = self.x, self.y
		original_velocity_x, original_velocity_y = velocity_x, velocity_y
		
		# Determine the closest collision point and normal
		closest_block = None
		closest_distance = float('inf')
		collision_normal_x, collision_normal_y = 0, 0
		collision_side = None
		
		for block in blocks_collided_with:
			# Calculate center points
			ball_center_x = self.rect.x + self.rect.width / 2
			ball_center_y = self.rect.y + self.rect.height / 2
			block_center_x = block.rect.x + block.rect.width / 2
			block_center_y = block.rect.y + block.rect.height / 2
			
			# Calculate vector from ball center to block center
			delta_x = ball_center_x - block_center_x
			delta_y = ball_center_y - block_center_y
			
			# Calculate distance between centers
			distance = math.sqrt(delta_x**2 + delta_y**2)
			
			# Find the closest block
			if distance < closest_distance:
				closest_distance = distance
				closest_block = block
				
				# Calculate collision normal (normalized vector from block to ball)
				if distance > 0:  # Avoid division by zero
					collision_normal_x = delta_x / distance
					collision_normal_y = delta_y / distance
				
				# Determine which side of the block was hit
				# Calculate the absolute projections onto each axis
				proj_x = abs(delta_x)
				proj_y = abs(delta_y)
				
				# Calculate the overlap thresholds
				overlap_x = (self.rect.width + block.rect.width) / 2
				overlap_y = (self.rect.height + block.rect.height) / 2
				
				# Determine the collision side based on the smallest overlap
				if proj_x / overlap_x > proj_y / overlap_y:
					# Horizontal collision (left or right)
					collision_side = "left" if delta_x < 0 else "right"
				else:
					# Vertical collision (top or bottom)
					collision_side = "top" if delta_y < 0 else "bottom"
		
		# If we found a collision, handle it
		if closest_block:
			# Hit the block (apply damage, effects, etc.)
			self.hit_block(closest_block)
			
			# Handle the collision based on the side
			if collision_side == "top":
				self.place_over(closest_block)
				# Only reverse y velocity if moving downward
				if velocity_y > 0:
					velocity_y = -velocity_y
			elif collision_side == "bottom":
				self.place_below(closest_block)
				# Only reverse y velocity if moving upward
				if velocity_y < 0:
					velocity_y = -velocity_y
			elif collision_side == "left":
				self.place_left_of(closest_block)
				# Only reverse x velocity if moving rightward
				if velocity_x > 0:
					velocity_x = -velocity_x
			elif collision_side == "right":
				self.place_right_of(closest_block)
				# Only reverse x velocity if moving leftward
				if velocity_x < 0:
					velocity_x = -velocity_x
			
			# Calculate new angle from velocity components
			self.angle = math.atan2(velocity_y, velocity_x)
			
			# Add a small random variation to prevent getting stuck in patterns
			self.angle += random.uniform(-0.05, 0.05)
			
			# Ensure minimum angles to prevent getting stuck
			self.ensure_minimum_angle()
			
			# Handle secondary collisions
			for block in blocks_collided_with:
				if block != closest_block:
					self.hit_block(block)
		
		# Check if we're still colliding after resolution
		if pygame.sprite.spritecollide(self, groups.Groups.block_group, False):
			# We're still colliding, try a more aggressive approach
			# Move away from all blocks
			for block in blocks_collided_with:
				# Calculate direction away from block
				delta_x = self.rect.centerx - block.rect.centerx
				delta_y = self.rect.centery - block.rect.centery
				
				# Normalize direction
				distance = max(0.1, math.sqrt(delta_x**2 + delta_y**2))
				delta_x /= distance
				delta_y /= distance
				
				# Move away from block
				self.x += delta_x * 2
				self.y += delta_y * 2
				self.rect.x = self.x
				self.rect.y = self.y
			
			# Randomize angle more aggressively
			self.angle = random.uniform(0, 2 * math.pi)
			self.ensure_minimum_angle()

	def ensure_minimum_angle(self):
		"""Ensures the ball's angle isn't too horizontal or vertical to prevent getting stuck."""
		# Normalize angle to 0-2π range
		normalized_angle = self.angle % (2 * math.pi)
		
		# Minimum angles (in radians)
		min_vertical_angle = math.pi / 10  # ~18 degrees from horizontal
		min_horizontal_angle = math.pi / 10  # ~18 degrees from vertical
		
		# Check if angle is too close to horizontal
		if abs(math.sin(normalized_angle)) < math.sin(min_vertical_angle):
			# Adjust angle to maintain direction but increase vertical component
			if normalized_angle < math.pi:
				self.angle = min_vertical_angle if normalized_angle < math.pi/2 else math.pi - min_vertical_angle
			else:
				self.angle = -min_vertical_angle if normalized_angle < 3*math.pi/2 else 2*math.pi - min_vertical_angle
		
		# Check if angle is too close to vertical
		elif abs(math.cos(normalized_angle)) < math.cos(min_horizontal_angle):
			# Adjust angle to maintain direction but increase horizontal component
			if normalized_angle < math.pi/2 or normalized_angle > 3*math.pi/2:
				self.angle = min_horizontal_angle if normalized_angle < math.pi/2 else 2*math.pi - min_horizontal_angle
			else:
				self.angle = math.pi - min_horizontal_angle if normalized_angle < math.pi else math.pi + min_horizontal_angle

	def hit_block(self, block):
		# We've hit a block, so we do a bunch of things. First, spawn a few particles.
		self.spawn_particles()

		# Tell ourselves that we have been hit.
		self.on_hit()

		# Reset paddle hit counter since we hit a block
		self.paddle_hit_counter = 0

		# Damage is increased the higher the speed is over the standard speed.
		damage_dealt = Ball.damage * (self.speed / Ball.speed) * Ball.smash_damage_factor

		# If the block owner and the ball owner is the same, we deal a reduced amount of damage (for balance purposes).
		if block.owner == self.owner:
			block.on_hit(damage_dealt * Ball.damage_percentage_dealt_to_own_blocks)
		else:
			block.on_hit(damage_dealt)

		# Tell all the effects that we've just hit a block.
		for effect in self.effect_group:
			effect.on_hit_block(block)

		# Remove all smash effects.
		self.remove_smash_effects()

		# We just collided with a block, so we set collided to True.
		self.collided = True

	def hit_top_side_of_block(self, block):
		# Reverse angle.
		if self.angle < math.pi:
			self.hit_block(block)
			self.angle = -self.angle
			# Add small random variation
			self.angle += random.uniform(-0.05, 0.05)

		# Place ball on top of the block.
		self.place_over(block)
		
		# Ensure we're not stuck in a horizontal pattern
		self.ensure_minimum_angle()

	def hit_left_side_of_block(self, block):
		# Reverse angle.
		if self.angle < (math.pi / 2) or self.angle > ((3 * math.pi) / 2):
			self.hit_block(block)
			self.angle = math.pi - self.angle
			# Add small random variation
			self.angle += random.uniform(-0.05, 0.05)

		# Place ball to the left of the block.
		self.place_left_of(block)
		
		# Ensure we're not stuck in a vertical pattern
		self.ensure_minimum_angle()

	def hit_right_side_of_block(self, block):
		# Reverse angle.
		if self.angle > (math.pi / 2) and self.angle < ((3 * math.pi) / 2):
			self.hit_block(block)
			self.angle = math.pi - self.angle
			# Add small random variation
			self.angle += random.uniform(-0.05, 0.05)

		# Place ball to the right of the block.
		self.place_right_of(block)
		
		# Ensure we're not stuck in a vertical pattern
		self.ensure_minimum_angle()

	def hit_bottom_side_of_block(self, block):
		# Reverse angle.
		if self.angle > math.pi:
			self.hit_block(block)
			self.angle = -self.angle
			# Add small random variation
			self.angle += random.uniform(-0.05, 0.05)

		# Place ball below the block.
		self.place_below(block)
		
		# Ensure we're not stuck in a horizontal pattern
		self.ensure_minimum_angle()

	def check_collision_powerups(self):
		# Here we check if we've collided with any powerups. If we have, we simply tell that powerup that we just
		# hit it. We don't need to do anything else, each powerup handles the rest.
		powerup_collide_list = pygame.sprite.spritecollide(self, groups.Groups.powerup_group, False)
		for powerup in powerup_collide_list:
			powerup.hit(self)

	def update_speed_from_effects(self):
		"""
		Updates the ball's speed based on active speed effects.
		This ensures that when multiple speed effects are applied or removed,
		the ball's speed is calculated correctly.
		"""
		# Find all active speed effects
		active_speed_effects = [effect for effect in self.effect_group if effect.__class__.__name__ == "Speed" and effect.parent.owner == effect.real_owner]
		
		if active_speed_effects:
			# If there are active speed effects, apply the highest multiplier
			highest_multiplier = max(effect.speed_multiplier for effect in active_speed_effects)
			self.speed = self.base_speed * highest_multiplier
		else:
			# If no active speed effects, restore to base speed
			self.speed = self.base_speed
