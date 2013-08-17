__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import random
import objects.groups as groups
import settings.settings as settings

class Powerup(pygame.sprite.Sprite):

	# Initialize the mixer (so we can load a sound) and load the sound effects.
	pygame.mixer.init(44100, -16, 2, 2048)
	sound_effects = []
	sound_effects.append(pygame.mixer.Sound("res/sounds/powerup1.ogg"))
	sound_effects.append(pygame.mixer.Sound("res/sounds/powerup2.ogg"))
	sound_effects.append(pygame.mixer.Sound("res/sounds/powerup3.ogg"))
	sound_effects.append(pygame.mixer.Sound("res/sounds/powerup4.ogg"))

	width = 8 * settings.GAME_SCALE
	height = 8 * settings.GAME_SCALE

	def __init__(self, x, y, width, height):
		# We start by calling the superconstructor.
		pygame.sprite.Sprite.__init__(self)

		# Create the rect used for collision detection, position etc.
		self.rect = pygame.rect.Rect(x, y, width, height)

		# Keep track of x and y as floats, for preciseness sake (rect keeps track of x,y as ints)
		self.x = x
		self.y = y

		# Store self in the main powerup_group.
		groups.Groups.powerup_group.add(self)

		# We also create an effect_group ourselves, in case anyone wants to add any sort of effect to us.
		self.effect_group = pygame.sprite.Group()

		if settings.DEBUG_MODE:
			print("Powerup spawned @ (" + str(self.rect.x) + ", " + str(self.rect.y) + ")")

	def hit(self, entity):
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
		# Update the rects position.
		self.rect.x = self.x
		self.rect.y = self.y