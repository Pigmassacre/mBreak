__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import copy
import math
import random
import objects.effects.flash as flash
import objects.groups as groups
import settings.settings as settings

"""

This is the base class of all powerups. It handles stuff like position and destroying the powerup safely, for example.
It also handles the sound effects that are played when the powerup is destroyed (picked up by a ball).

"""

class Powerup(pygame.sprite.Sprite):

	# Initialize the mixer (so we can load a sound) and load the sound effects.
	pygame.mixer.init(44100, -16, 2, 2048)
	sound_effects = []
	sound_effects.append(pygame.mixer.Sound("res/sounds/powerup1.ogg"))
	sound_effects.append(pygame.mixer.Sound("res/sounds/powerup2.ogg"))
	sound_effects.append(pygame.mixer.Sound("res/sounds/powerup3.ogg"))
	sound_effects.append(pygame.mixer.Sound("res/sounds/powerup4.ogg"))

	# The standard width of all powerup image files. Each individual powerup can ofcourse be bigger/smaller, but this is the standard size.
	width = 8 * settings.GAME_SCALE
	height = 8 * settings.GAME_SCALE

	# On hit effect values.
	spawn_effect_start_color = pygame.Color(255, 255, 255, 255)
	spawn_effect_final_color = pygame.Color(255, 255, 255, 0)
	spawn_effect_tick_amount = 18

	def __init__(self, x, y, width, height, bob = True):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y
		self.center_y = self.y

		# Keep track of whether or not this powerup should bob.
		self.bob = bob
		self.start_time = pygame.time.get_ticks()

		# Store self in the main powerup_group.
		groups.Groups.powerup_group.add(self)

		# We also create an effect_group ourselves, in case anyone wants to add any sort of effect to us.
		self.effect_group = pygame.sprite.Group()

		# We create a flash effect as a sort of spawn effect.
		self.effect_group.add(flash.Flash(self, copy.copy(Powerup.spawn_effect_start_color), copy.copy(Powerup.spawn_effect_final_color), Powerup.spawn_effect_tick_amount))

		if settings.DEBUG_MODE:
			print("Powerup spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ")")

	def hit(self, entity):
		# When hit, we destroy ourselves.
		self.destroy()

	def destroy(self, play_sound = True):
		self.kill()

		# Destroy all effects attached to this powerup.
		for effect in self.effect_group:
			effect.destroy()

		# Play a random sound from the sound_effects list.
		if play_sound:
			Powerup.sound_effects[random.randrange(0, len(Powerup.sound_effects))].play()

	def update(self, main_clock):
		# Update the position according to the bob effect.
		if self.bob:
			self.y = self.center_y + math.sin(self.start_time + pygame.time.get_ticks() * 0.0075) * 1.5

		# Update the rects position.
		self.rect.x = self.x
		self.rect.y = self.y