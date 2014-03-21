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

	# Initialize the mixer (so we can load a sound) and load the sound effect.
	pygame.mixer.init(44100, -16, 2, 2048)
	sound_effect = pygame.mixer.Sound("res/sounds/ball.ogg")

	# Standard values. These will be used unless any other values are specified per instance of this class.
	width = image.get_width() * settings.GAME_SCALE
	height = image.get_height() * settings.GAME_SCALE
	speed = 1.5 * settings.GAME_FPS * settings.GAME_SCALE
	max_speed = 5 * settings.GAME_FPS * settings.GAME_SCALE
	speed_step = 0.75 * settings.GAME_FPS * settings.GAME_SCALE
	paddle_nudge_distance = 1.34 * settings.GAME_SCALE
	least_allowed_vertical_angle = 0.32 # Exists to prevent the balls from getting stuck bouncing up and down in the middle of the gamefield.
	trace_spawn_rate = 0.53 * settings.GAME_FPS
	particle_spawn_amount = 3

	# Damage stuff.
	damage = 10
	damage_percentage_dealt_to_own_blocks = 0.25

	# Smash stuff.
	smash_speed = 0.2 * settings.GAME_FPS * settings.GAME_SCALE
	smash_damage_factor = 1
	smash_max_stack = 12
	smash_effect_size_increase = 1 * settings.GAME_SCALE
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

		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, Ball.width, Ball.height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# Keep track of the balls position in the previous frame, used for collision handling.
		self.previous = pygame.rect.Rect(self.x, self.y, Ball.width, Ball.height)

		# Set the angle variable.
		self.angle = angle

		# Set maximum speed of the ball.
		self.max_speed = Ball.max_speed

		# Set the speed variable.
		self.speed = Ball.speed
		self.tick_speed = self.speed

		# Store the current level of smash stack.
		self.smash_stack = 0
		
		# Store the owner.
		self.owner = owner

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

	def destroy(self):
		# This should be called when the ball is to be destroyed. It will take care of killing itself and anything affecting it completely.
		self.kill()
		self.shadow.kill()
		for effect in self.effect_group:
			effect.destroy()

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

		speed_handled = 0
		while speed_handled < self.speed:
			# Setup the speed values to use for this iteration.
			if self.speed - speed_handled >= Ball.speed_step:
				self.tick_speed = Ball.speed_step
			else:
				self.tick_speed = self.speed - speed_handled

			# Check collision with paddles.
			self.check_collision_paddles()
					
			# Check collision with other balls.
			self.check_collision_balls()

			# Check collision with blocks.
			self.check_collision_blocks()

			# Check collision with powerups.
			self.check_collision_powerups()

			# Here we check if the angle of the ball is in the restricted areas. We do this to make sure that the balls don't get stuck
			# bouncing up and down in the middle of the gamefield, since that makes for a very boring game.
			if self.angle > (math.pi / 2) - Ball.least_allowed_vertical_angle and self.angle < (math.pi / 2) + Ball.least_allowed_vertical_angle:
				if self.angle > (math.pi / 2):
					self.angle = (math.pi / 2) + Ball.least_allowed_vertical_angle
				elif self.angle < (math.pi / 2):
					self.angle = (math.pi / 2) - Ball.least_allowed_vertical_angle
				else:
					# If the angle is EXACTLY pi/2, we just randomly decide what angle to "nudge" the ball to.
					self.angle += random.randrange(-1, 2, 2) * Ball.least_allowed_vertical_angle
			elif self.angle > ((3 * math.pi) / 2) - Ball.least_allowed_vertical_angle and self.angle < ((3 * math.pi) / 2) + Ball.least_allowed_vertical_angle:			
				if self.angle > ((3 * math.pi) / 2):
					self.angle = ((3 * math.pi) / 2) + Ball.least_allowed_vertical_angle
				elif self.angle < ((3 * math.pi) / 2):
					self.angle = ((3 * math.pi) / 2) - Ball.least_allowed_vertical_angle
				else:
					# If the angle is EXACTLY 3pi/2, we just randomly decide what angle to "nudge" the ball to.
					self.angle += random.randrange(-1, 2, 2) * Ball.least_allowed_vertical_angle

			# Constrain angle to 0 < angle < 2pi. Even though angles over 2pi or under 0 work fine when translating the angles to x and y positions, 
			# such angles mess with our ability to calculate other stuff. So we just make sure that the angle is between 0 and 2pi.
			if self.angle > (2 * math.pi):
				self.angle -= (2 * math.pi)
			elif self.angle < 0:
				self.angle += (2 * math.pi)

			# We make sure that speed isn't over max_speed.
			if self.speed > self.max_speed:
				self.speed = self.max_speed

			# Move the ball with speed in consideration.
			self.x = self.x + (math.cos(self.angle) * self.tick_speed * main_clock.delta_time)
			self.y = self.y + (math.sin(self.angle) * self.tick_speed * main_clock.delta_time)
			self.rect.x = self.x
			self.rect.y = self.y

			# Check collision with x-edges.
			if self.rect.x < settings.LEVEL_X:
				# We hit the left wall.
				self.hit_wall()

				# Reverse angle on x-axis.
				self.angle = math.pi - self.angle

				# Constrain ball to screen size.
				self.x = settings.LEVEL_X
				self.rect.x = self.x
			elif self.rect.x + self.rect.width > settings.LEVEL_MAX_X:
				# We hit the right wall.
				self.hit_wall()

				# Reverse angle on x-axis.
				self.angle = math.pi - self.angle

				# Constrain ball to screen size.
				self.x = settings.LEVEL_MAX_X - self.rect.width			
				self.rect.x = self.x

			# Check collision with y-edges.
			if self.rect.y < settings.LEVEL_Y:
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
				sound = Ball.sound_effect.play()
				if not sound is None:
					sound.set_volume(settings.SOUND_VOLUME)

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

		# Then reset our smash stack.
		self.smash_stack = 0

	def hit_paddle(self, paddle):
		# Spawn a few particles.
		self.spawn_particles()

		# Calculate the spin.
		self.calculate_smash(paddle)

		# Tell ourselves that we have been hit.
		self.on_hit()

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
		# Since movement in this game is done step by step (we do not use raytracing) it's possible
		# for balls to collided with more blocks than they actually should've collided with.
		# This method meticulously goes through every possible combination of blocks collided with
		# and deals with each accordingly.
		blocks_collided_with = pygame.sprite.spritecollide(self, groups.Groups.block_group, False)

		# This dictionary is used to store a side with each block we collided with. This is so we can
		# handle each possible collision case later on.
		block_information = {}
		for block in blocks_collided_with:
			# Determine what side of the block we've collided with.
			if self.rect.bottom >= block.rect.top and self.rect.top < block.rect.top:
				# Top side of block collided with. Compare with edges:
				if block.rect.left - self.rect.left > block.rect.top - self.rect.top:
					# The ball collides more with the left side than top side.
					block_information[block] = "left"
				elif self.rect.right - block.rect.right > block.rect.top - self.rect.top:
					# The ball collides more with the right side than top side.
					block_information[block] = "right"
				else:
					# The ball collides more with the top side than any other side.
					block_information[block] = "top"
			elif self.rect.top <= block.rect.bottom and self.rect.bottom > block.rect.bottom:
				# Bottom side of block collided with.
				if block.rect.left - self.rect.left > self.rect.bottom - block.rect.bottom:
					# The ball collides more with the left side than top side.
					block_information[block] = "left"
				elif self.rect.right - block.rect.right > self.rect.bottom - block.rect.bottom:
					# The ball collides more with the right side than top side.
					block_information[block] = "right"
				else:
					# The ball collides more with the bottom side than any other side.
					block_information[block] = "bottom"
			elif self.rect.right >= block.rect.left and self.rect.left < block.rect.left:
				# Left side of block collided with.
				block_information[block] = "left"
			elif self.rect.left <= block.rect.right and self.rect.right > block.rect.right:
				# Right side of block collided with.
				block_information[block] = "right"

		if len(block_information) > 3:
			print("block_information len " + str(len(block_information)))

		# If we've only hit one block, we don't need to check so much. Just check which side we've collided with and act accordingly.
		if len(block_information) == 1:
			# Check what side we've hit that block and act accordingly.
			for block, side in block_information.iteritems():
				if side == "top":
					self.hit_top_side_of_block(block)
				elif side == "left":
					self.hit_left_side_of_block(block)
				elif side == "right":
					self.hit_right_side_of_block(block)
				elif side == "bottom":
					self.hit_bottom_side_of_block(block)
		# If we've hit two blocks, we need to check what combination of sides we've hit, to determine how to act.
		elif len(block_information) == 2:
			# Setup a few help lists to more easily determine how to act.
			block_list = []
			side_list = []
			for block, side in block_information.iteritems():
				block_list.append(block)
				side_list.append(side)

			# Are the two hit blocks side by side?
			if block_list[0].y == block_list[1].y:
				# Check if we've hit the top side of either block.
				if "top" in side_list:
					self.hit_top_side_of_block(block_list[0])
					self.hit_block(block_list[1])
				elif "bottom" in side_list:
					self.hit_bottom_side_of_block(block_list[0])
					self.hit_block(block_list[1])
			# Are the two blocks hit above/below each other?
			elif block_list[0].x == block_list[1].x:
				# Check what side we've hit, and act accordingly.
				if "left" in side_list:
					self.hit_left_side_of_block(block_list[0])
					self.hit_block(block_list[1])
				elif "right" in side_list:
					self.hit_right_side_of_block(block_list[0])
					self.hit_block(block_list[1])
			# Are the two blocks hit diagonal of each other?
			else:
				for block, side in block_information.iteritems():
					if side == "top":
						self.hit_top_side_of_block(block)
					elif side == "left":
						self.hit_left_side_of_block(block)
					elif side == "right":
						self.hit_right_side_of_block(block)
					elif side == "bottom":
						self.hit_bottom_side_of_block(block)
		# If we've hit three blocks, it's a little bit more complex. We have a lot of cases to handle.
		elif len(block_information) == 3:
			# Setup a few help lists to more easily determine how to act.
			block_list = []
			side_list = []
			for block, side in block_information.iteritems():
				block_list.append(block)
				side_list.append(side)

			# Here we're meticulously going through every possible combination and acting accordingly.
			# We also damage each block separately, since we cannot be sure what block we've "really"
			# hit until we've checked.
			if block_list[0].y == block_list[1].y:
				self.check_block_collisions(block_list[0], block_list[1], block_list[2], side_list[2])
			elif block_list[1].y == block_list[2].y:
				self.check_block_collisions(block_list[1], block_list[2], block_list[0], side_list[0])
			elif block_list[2].y == block_list[0].y:
				self.check_block_collisions(block_list[2], block_list[0], block_list[1], side_list[1])
		elif len(block_information) > 3:
			least_x_distance = 999999
			least_y_distance = 999999
			for block, side in block_information.iteritems():
				if abs(block.x - self.x) < least_x_distance:
					least_x_distance = block.x - self.x

				if abs(block.y - self.y) < least_y_distance:
					least_y_distance = block.y - self.y

			self.x += least_x_distance
			self.y += least_y_distance

	def check_block_collisions(self, block_one, block_two, block_three, block_three_side):
		# Given a different combination of block_one, two and three (and the side of block three) this figures out
		# what blocks we've actually hit.
		if block_three_side == "left":
			self.hit_left_side_of_block(block_three)
		else:
			self.hit_right_side_of_block(block_three)

		if block_three.y > block_one.y:
			if block_one.x > block_two.x:
				self.hit_bottom_side_of_block(block_one)
			else:
				self.hit_bottom_side_of_block(block_two)
		else:
			if block_one.x > block_two.x:
				self.hit_top_side_of_block(block_one)
			else:
				self.hit_top_side_of_block(block_two)

	def hit_block(self, block):
		# We've hit a block, so we do a bunch of things. First, spawn a few particles.
		self.spawn_particles()

		# Tell ourselves that we have been hit.
		self.on_hit()

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

		# Place ball on top of the block.
		self.place_over(block)

	def hit_left_side_of_block(self, block):
		# Reverse angle.
		if self.angle < (math.pi / 2) or self.angle > ((3 * math.pi) / 2):
			self.hit_block(block)
			self.angle = math.pi - self.angle

		# Place ball to the left of the block.
		self.place_left_of(block)

	def hit_right_side_of_block(self, block):
		# Reverse angle.
		if self.angle > (math.pi / 2) and self.angle < ((3 * math.pi) / 2):
			self.hit_block(block)
			self.angle = math.pi - self.angle

		# Place ball to the right of the block.
		self.place_right_of(block)

	def hit_bottom_side_of_block(self, block):
		# Reverse angle.
		if self.angle > math.pi:
			self.hit_block(block)
			self.angle = -self.angle

		# Place ball below the block.
		self.place_below(block)

	def check_collision_powerups(self):
		# Here we check if we've collided with any powerups. If we have, we simply tell that powerup that we just
		# hit it. We don't need to do anything else, each powerup handles the rest.
		powerup_collide_list = pygame.sprite.spritecollide(self, groups.Groups.powerup_group, False)
		for powerup in powerup_collide_list:
			powerup.hit(self)
