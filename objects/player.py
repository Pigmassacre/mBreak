__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *
import random
import math
import copy
import objects.camera as camera
import objects.groups as groups
import objects.ball as ball
import objects.powerups.powerup as powerup
import objects.attacks.missilestorm as missilestorm
import objects.attacks.laser as laser
import settings.settings as settings

"""

This is the player class. mBreak is currently designed with two players in mind, but it wouldn't take too much work
 to allow more players than that (not sure about how fun that would be though.. :P).

"""

class Player(pygame.sprite.Sprite):

	# Load the image file here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	energy_image_top_left = pygame.image.load("res/player/energy/energy_top_left_2.png")
	energy_image_middle_left = pygame.image.load("res/player/energy/energy_middle_4.png")
	energy_image_middle_right = pygame.image.load("res/player/energy/energy_middle_right_4.png")
	energy_image_bottom_left = pygame.image.load("res/player/energy/energy_bottom_left_2.png")

	energy_image_top_left_width = energy_image_top_left.get_width() * settings.GAME_SCALE
	energy_image_top_left_height = energy_image_top_left.get_height() * settings.GAME_SCALE
	energy_image_middle_left_width = energy_image_middle_left.get_width() * settings.GAME_SCALE
	energy_image_middle_left_height = energy_image_middle_left.get_height() * settings.GAME_SCALE
	energy_image_middle_right_width = energy_image_middle_right.get_width() * settings.GAME_SCALE
	energy_image_middle_right_height = energy_image_middle_right.get_height() * settings.GAME_SCALE
	energy_image_bottom_left_width = energy_image_bottom_left.get_width() * settings.GAME_SCALE
	energy_image_bottom_left_height = energy_image_bottom_left.get_height() * settings.GAME_SCALE

	# Scale image to settings.GAME_SCALE.
	energy_image_top_left = pygame.transform.scale(energy_image_top_left, (energy_image_top_left_width, energy_image_top_left_height))
	energy_image_middle_left = pygame.transform.scale(energy_image_middle_left, (energy_image_middle_left_width, energy_image_middle_left_height))
	energy_image_middle_right = pygame.transform.scale(energy_image_middle_right, (energy_image_middle_right_width, energy_image_middle_right_height))
	energy_image_bottom_left = pygame.transform.scale(energy_image_bottom_left, (energy_image_bottom_left_width, energy_image_bottom_left_height))

	def __init__(self, x, y, name, key_up, key_down, key_unleash_energy, joy_unleash_energy, gamepad_id, color, ai_difficulty = 1):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Store the x and y position. This is used to display the list of powerups the player currently has.
		self.x = x
		self.y = y

		# The name is dislayed at the end of each match/game.
		self.name = name

		# Store the selected color, used to colorize objects that belong to the player.
		self.color = color

		# These are the keys that any paddles connected to this player will respond to.
		self.key_up = key_up
		self.key_down = key_down
		self.key_unleash_energy = key_unleash_energy
		self.joy_unleash_energy = joy_unleash_energy
		self.unleash_energy_pressed = False

		# This value can be "spent" to create powerup effects. The higher the energy value, the more / more powerful effects will be created.
		self.energy = 0
		self.max_energy = 100
		self.energy_increase_on_hit = 2.5
		
		#self.energy_attack = missilestorm.MissileStorm(self)
		self.energy_attack = laser.Laser(self)

		# Store the number of the gamepad that controls this player.
		self.gamepad_id = gamepad_id
		self.joystick = None
		if not self.gamepad_id is None:
			self.joystick = pygame.joystick.Joystick(self.gamepad_id)
			self.joystick.init()

		# Store the difficulty of the AI. A higher number equals a smarter/more cheaty AI. A difficulty of 0 means no AI.
		self.ai_difficulty = ai_difficulty

		# Store the energy images.
		self.energy_image_top = Player.energy_image_top_left.copy()
		self.energy_image_bottom = Player.energy_image_bottom_left.copy()
		if self.x <= settings.SCREEN_WIDTH / 2:
			self.energy_image_middle = Player.energy_image_middle_left.copy()

			self.energy_top_x = settings.LEVEL_X - self.energy_image_top.get_width() - 4 * settings.GAME_SCALE
			self.energy_middle_x = settings.LEVEL_X - self.energy_image_middle.get_width() - 4 * settings.GAME_SCALE
			self.energy_bottom_x = settings.LEVEL_X - self.energy_image_bottom.get_width() - 4 * settings.GAME_SCALE

			self.energy_level_x = self.energy_middle_x + 1 * settings.GAME_SCALE
		else:
			self.energy_image_top = pygame.transform.flip(self.energy_image_top, True, False)
			self.energy_image_middle = Player.energy_image_middle_right.copy()
			self.energy_image_bottom = pygame.transform.flip(self.energy_image_bottom, True, False)

			self.energy_top_x = settings.LEVEL_MAX_X + 4 * settings.GAME_SCALE
			self.energy_middle_x = settings.LEVEL_MAX_X + 4 * settings.GAME_SCALE
			self.energy_bottom_x = settings.LEVEL_MAX_X + 4 * settings.GAME_SCALE

			self.energy_level_x = self.energy_middle_x
		self.energy_top_y = settings.LEVEL_Y
		self.energy_middle_y = self.energy_top_y + self.energy_image_top.get_height()
		self.energy_bottom_y = self.energy_middle_y + self.energy_image_middle.get_height()

		# This is the surface used to draw the actual energy level.
		self.energy_level_surface = pygame.surface.Surface((self.energy_image_middle.get_width() - 1 * settings.GAME_SCALE, self.energy_image_middle.get_height()), pygame.locals.SRCALPHA)
		self.energy_level_y = self.energy_middle_y

		# This is the energy rect, this changes according to the energy level of the player.
		energy_y = self.energy_level_surface.get_height() - (self.energy_level_surface.get_height() * (self.energy / float(self.max_energy)))
		self.energy_rect = pygame.rect.Rect(0, energy_y, self.energy_level_surface.get_width(), self.energy_level_surface.get_height() * (self.energy / float(self.max_energy)))

		# This is the color of the energy level.
		self.energy_color = copy.copy(self.color)
		self.energy_color.a = 180
		self.energy_color_r = self.energy_color.r
		self.energy_color_g = self.energy_color.g
		self.energy_color_b = self.energy_color.b

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

	def empty_groups(self):
		# Empty all the groups.
		self.paddle_group.empty()
		self.ball_group.empty()
		self.block_group.empty()
		self.powerup_group.empty()
		self.effect_group.empty()

		# Reset our energy.
		self.energy = 0
		self.energy_attack.reset()

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

	def attack(self):
		self.energy_attack.attack()

	def event(self, event):
		if self.ai_difficulty == 0:
			if ((event.type == KEYDOWN and event.key == self.key_unleash_energy) or 
				(event.type == JOYBUTTONDOWN and event.button == self.joy_unleash_energy)):
					self.attack()

	def update(self, main_clock):
		# Update the energy rect.
		self.energy_rect.height = self.energy_level_surface.get_height() * (self.energy / float(self.max_energy))
		self.energy_rect.y = self.energy_level_surface.get_height() - self.energy_rect.height

		# Update the color of the energy.
		new_r = int(self.energy_color_r + math.sin(pygame.time.get_ticks() * 0.005) * (50 * (self.energy / float(self.max_energy))))
		if new_r <= 255 and new_r >= 0:
			self.energy_color.r = new_r
		else:
			if new_r < 0:
				self.energy_color.r = 0
			else:
				self.energy_color.r = 255

		new_g = int(self.energy_color_g + math.sin(pygame.time.get_ticks() * 0.005) * (50 * (self.energy / float(self.max_energy))))
		if new_g <= 255 and new_g >= 0:
			self.energy_color.g = new_g
		else:
			if new_g < 0:
				self.energy_color.g = 0
			else:
				self.energy_color.g = 255

		new_b = int(self.energy_color_b + math.sin(pygame.time.get_ticks() * 0.005) * (50 * (self.energy / float(self.max_energy))))
		if new_b <= 255 and new_b >= 0:
			self.energy_color.b = new_b
		else:
			if new_b < 0:
				self.energy_color.b = 0
			else:
				self.energy_color.b = 255

		# Update our attack.
		self.energy_attack.update(main_clock)

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

	def draw(self, surface):
		# Draw the energy images.
		surface.blit(self.energy_image_top, (self.energy_top_x - camera.CAMERA.x, self.energy_top_y - camera.CAMERA.y))
		surface.blit(self.energy_image_middle, (self.energy_middle_x - camera.CAMERA.x, self.energy_middle_y - camera.CAMERA.y))

		temp_energy_surface = self.energy_level_surface.copy()
		temp_energy_surface.fill(self.energy_color, self.energy_rect)
		surface.blit(temp_energy_surface, (self.energy_level_x - camera.CAMERA.x, self.energy_level_y - camera.CAMERA.y))

		surface.blit(self.energy_image_bottom, (self.energy_bottom_x - camera.CAMERA.x, self.energy_bottom_y - camera.CAMERA.y))

	def handle_events(self, event):
		# Work on this later...
		pass