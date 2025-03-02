__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import objects.groups as groups
import objects.effects.effect as effect
import settings.settings as settings

"""

This is the speed effect. It modifies the speed of the ball by a percentage multiplier.
When the effect expires, it restores the ball's original speed.

"""

class Speed(effect.Effect):

	# Default speed multiplier (1.0 means no change, 2.0 means double speed)
	default_speed_multiplier = 2.0

	def __init__(self, parent, duration, speed_multiplier=None):
		# We start by calling the superconstructor.
		effect.Effect.__init__(self, parent, duration)
		
		# Store the speed multiplier, use default if none provided
		self.speed_multiplier = speed_multiplier if speed_multiplier is not None else Speed.default_speed_multiplier
		
		# Apply the speed multiplier using the ball's method
		if hasattr(parent, 'update_speed_from_effects'):
			parent.update_speed_from_effects()
		else:
			# Fallback for entities that don't have the method
			parent.speed = parent.base_speed * self.speed_multiplier
		
		# Initialize the mixer (so we can load a sound) and load the sound effect.
		pygame.mixer.init(44100, -16, 2, 2048)
		self.sound_effect = pygame.mixer.Sound("res/sounds/powerup1.ogg")
		
		# Play the sound effect
		sound = self.sound_effect.play()
		if sound is not None:
			sound.set_volume(settings.SOUND_VOLUME)

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		# Only apply speed effect if the ball is owned by the player who picked up the powerup
		if self.parent.owner == self.real_owner:
			# Update speed using the ball's method
			if hasattr(self.parent, 'update_speed_from_effects'):
				self.parent.update_speed_from_effects()

	def on_kill(self):
		# Update speed using the ball's method
		if hasattr(self.parent, 'update_speed_from_effects'):
			self.parent.update_speed_from_effects()
		else:
			# Fallback for entities that don't have the method
			self.parent.speed = self.parent.base_speed
		
	def on_hit_paddle(self, paddle):
		# When the ball hits a paddle, it changes ownership
		# We need to update the speed immediately based on ownership
		if paddle.owner == self.real_owner:
			# The ball is now owned by the player who picked up the powerup
			# Update speed using the ball's method
			if hasattr(self.parent, 'update_speed_from_effects'):
				self.parent.update_speed_from_effects()
		else:
			# The ball is now owned by the opponent
			# Update speed using the ball's method
			if hasattr(self.parent, 'update_speed_from_effects'):
				self.parent.update_speed_from_effects()
			else:
				# Fallback for entities that don't have the method
				self.parent.speed = self.parent.base_speed
