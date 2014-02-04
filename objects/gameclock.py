__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame

class GameClock():

	default_time_scale = 1

	def __init__(self):
		# We start by creating a default pygame clock.
		self.clock = pygame.time.Clock()

		# We store the game speed.
		self.time_scale = GameClock.default_time_scale

		# We also store the default time scale, for easy access.
		self.default_time_scale = GameClock.default_time_scale

		# We store the delta time in seconds. Updated whenever .tick() is called.
		self.delta_time = 0

	def tick(self, framerate = 0):
		delta_time_ms = self.clock.tick(framerate) * self.time_scale
		self.delta_time = (delta_time_ms / 1000.0)
		return delta_time_ms

	def tick_busy_loop(self, framerate = 0):
		return self.clock.tick_busy_loop(framerate)

	def get_time(self):
		# Returns the time passed between two ticks, modified by time_scale.
		return self.clock.get_time() * self.time_scale

	def get_rawtime(self):
		# Returns the time passed between two ticks, modified by time_scale.
		return self.clock.get_rawtime() * self.time_scale

	def get_fps(self):
		return self.clock.get_fps()	