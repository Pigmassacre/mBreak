__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.groups as groups
import objects.ball as ball
import objects.powerups.powerup as powerup
import objects.missile as missile
import settings.settings as settings

"""

This is the player class. mBreak is currently designed with two players in mind, but it wouldn't take too much work
 to allow more players than that (not sure about how fun that would be though.. :P).

Each player handles updating their own paddles, by sending the key_up and key_down variables to the update method of
each of the paddle that the player owns. Currently both players only have one paddle, but it's trivial to add
more than one.

"""

class Player(pygame.sprite.Sprite):

	def __init__(self, x, y, name, key_up, key_down, key_unleash_energy, joy_unleash_energy, gamepad_id, color, ai_difficulty = 1):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Store the x and y position. This is used to display the list of powerups the player currently has.
		self.x = x
		self.y = y

		# The name is dislayed at the end of each match/game.
		self.name = name

		# These are the keys that any paddles connected to this player will respond to.
		self.key_up = key_up
		self.key_down = key_down
		self.key_unleash_energy = key_unleash_energy
		self.joy_unleash_energy = joy_unleash_energy
		self.unleash_energy_pressed = False

		# This value can be "spent" to create powerup effects. The higher the energy value, the more / more powerful effects will be created.
		self.energy = 0
		self.max_energy = 100
		self.energy_increase_on_hit = 10
		self.missiles_to_spawn = 0
		self.missile_spawn_time = 200
		self.time_passed = 0

		# Store the number of the gamepad that controls this player.
		self.gamepad_id = gamepad_id
		self.joystick = None
		if not self.gamepad_id is None:
			self.joystick = pygame.joystick.Joystick(self.gamepad_id)
			self.joystick.init()

		# Store the difficulty of the AI. A higher number equals a smarter/more cheaty AI. A difficulty of 0 means no AI.
		self.ai_difficulty = ai_difficulty

		# Create and store the paddle.
		self.paddle_group = pygame.sprite.Group()

		# Create a group to store balls in.
		self.ball_group = pygame.sprite.Group()

		# Create a group to store blocks in.
		self.block_group = pygame.sprite.Group()

		# Create a group to store effects in.
		self.effect_group = pygame.sprite.Group()

		# Store the player in the main player_group.
		groups.Groups.player_group.add(self)

		# Create a OrdereredUpdates group used to store and display the powerups (in order) currently on this player.
		self.powerup_group = pygame.sprite.OrderedUpdates()

		# This is used to determine if an item has been added or removed from the group.
		self.last_powerup_group_size = len(self.powerup_group)

		# The offset between each powerup.
		self.powerup_offset = 2 * settings.GAME_SCALE

		# Store the selected color, used to colorize objects that belong to the player.
		self.color = color

	def empty_groups(self):
		# Empty all the groups.
		self.paddle_group.empty()
		self.ball_group.empty()
		self.block_group.empty()
		self.powerup_group.empty()
		self.effect_group.empty()
		
	def add_powerup(self, classname, effect):
		# Determine what position to place the powerup at.
		if self.x <= settings.SCREEN_WIDTH / 2:
			# If position is on the left half of the screen, place the powerup after the item with the highest x value in the powerup group.
			max_x = self.x
			for a_powerup in self.powerup_group:
				if a_powerup.x + a_powerup.width > max_x:
					max_x = a_powerup.x + a_powerup.width + self.powerup_offset
			x = max_x
			y = self.y
		else:
			# If position is on the right half of the screen, place the powerup before the item with the lowest x value in the powerup group.
			min_x = self.x
			for a_powerup in self.powerup_group:
				if a_powerup.x - self.powerup_offset - powerup.Powerup.width < min_x:
					min_x = a_powerup.x - self.powerup_offset - powerup.Powerup.width
			x = min_x
			y = self.y

		# Stores a powerup in our powerup group, and connects it to the effect so the powerup can be killed when the effect is killed.
		temp_powerup = classname(x, y)
		temp_powerup.is_display = True
		effect.displayed_powerups.append(temp_powerup)
		self.powerup_group.add(temp_powerup)

		# Change the last_powerup_group_size to match the current size of the group.
		self.last_powerup_group_size = len(self.powerup_group)

	def spawn_missile(self):
		# Create a list of available blocks to target.
		block_list = []
		for player in groups.Groups.player_group:
			if player != self:
				block_list = player.block_group.sprites()

		for paddle in self.paddle_group:
			# Create a missile that homes in on a random block in the block list.
			the_missile = missile.Missile(paddle.x + (paddle.width / 2) - (missile.Missile.width / 2), paddle.y + (paddle.height / 2) - (missile.Missile.height / 2), random.uniform(0, 2*math.pi), self, random.choice(block_list))
			the_missile.acceleration *= random.uniform(1.5, 3)

	def unleash_energy(self):
		print(str(self.name) + "'s energy level: " + str(self.energy))
		if self.energy >= 20:
			print("unleash_energy")
			# Set how many missiles to spawn.
			self.missiles_to_spawn += self.energy / 20

			self.spawn_missile()
			self.missiles_to_spawn -= 1

			# Reduce our energy to 0.
			self.energy = 0

	def update(self, main_clock):
		# Check if we're to spawn a missile.
		if self.missiles_to_spawn > 0:
			self.time_passed += main_clock.get_time()
			if self.time_passed >= self.missile_spawn_time:
				self.spawn_missile()

				self.missiles_to_spawn -= 1
				self.time_passed = 0

		# We check if any object has been removed from the powerup group.
		if len(self.powerup_group) < self.last_powerup_group_size:
			# We use this to position the powerups.
			previous_powerup = None

			# If an object has been removed, we update the position of all items in the list.
			for a_powerup in self.powerup_group:
				# Determine how to place the powerups.
				if previous_powerup == None:
					# If the previous powerup is none, we can just place the powerup at our position.
					a_powerup.x = self.x
				else:
					# Otherwise, we place the powerup next to the previous powerup.
					if self.x <= settings.SCREEN_WIDTH / 2:
						# To the left of the previous powerup.
						a_powerup.x = previous_powerup.x + previous_powerup.width + self.powerup_offset
					else:
						# To the right of the previous powerup.
						a_powerup.x = previous_powerup.x - a_powerup.width - self.powerup_offset
					
				# Set this powerup as the previous one.
				previous_powerup = a_powerup

			# Finally, change the last_powerup_group_size to match the current size.
			self.last_powerup_group_size = len(self.powerup_group)		

	def handle_events(self, event):
		# Work on this later...
		pass