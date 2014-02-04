__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import objects.groups as groups
import settings.settings as settings

"""

This is the base class of all effects in the game. It takes care of alot of things, like updating the position of the effect
and destroying the effect when the duration runs out. It also provides a few overridable methods.

"""

class GameClock():

	default_game_speed = 1

	def __init__(self):
		# We start by creating a default pygame clock.
		self.clock = pygame.time.Clock()

		# We store the game speed.
		self.game_speed = GameClock.default_game_speed

	def tick(self, framerate = 0):
		return self.clock.tick(framerate)

	def tick_busy_loop(self, framerate = 0):
		return self.clock.tick_busy_loop(framerate)

	def get_time(self):
		# Returns the time passed between two ticks, modified by game_speed.
		actual_time = self.clock.get_time()
		return actual_time * self.game_speed

	def get_rawtime(self):
		# Returns the time passed between two ticks, modified by game_speed.
		actual_time = self.clock.get_rawtime()
		return actual_time * self.game_speed

	def get_fps(self):
		return self.clock.get_fps()	