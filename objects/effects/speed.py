__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import objects.groups as groups
import objects.effects.effect as effect
import settings.settings as settings

"""

This is the speed effect. It will call the update method of whatever entity it has set as parent. Since all "game objects"
in the game has pygame.sprite.Sprite as it's base class, we can be sure that the update method always exists on whatever object
we have set as parent. Well, if we make sure to only apply the speed effect to game objects, that is...

"""

class Speed(effect.Effect):

	def __init__(self, parent, duration):
		# We start by calling the superconstructor.
		effect.Effect.__init__(self, parent, duration)

	def update(self, main_clock):
		# We make sure to call the supermethod.
		effect.Effect.update(self, main_clock)

		# To simulate double speed and make sure that all collisions are handled, we simply call the parents update method.
		self.parent.update(main_clock)
