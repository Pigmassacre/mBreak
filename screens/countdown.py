__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import gui.textitem as textitem
import settings.settings as settings

"""

This class displays a countdown when the update_and_draw method is called, if the countdown isn't already over.

This is used at the beginning of each round.

"""

class Countdown:

	def __init__(self, main_clock, function_to_call):
		# We use the main clock to keep track of the time passed.
		self.main_clock = main_clock

		# This is the function that is called when the countdown is over.
		self.function_to_call = function_to_call

		# When time passed reaches time to countdown, the countdown ends.
		self.time_passed = 0
		self.time_to_countdown = 1500

		# This is the amount of time that ready is displayed.
		self.countdown_ready_time = 2000

		# This is the amount of time that go is displayed.
		self.countdown_go_time = 1250

		# Create, position and store the "Ready" textitem.
		self.countdown_ready = textitem.TextItem("Ready", (255, 255, 255))
		self.countdown_ready.x = -self.countdown_ready.get_width()
		self.countdown_ready.y = (settings.SCREEN_HEIGHT - self.countdown_ready.get_height()) / 2
		self.countdown_ready_desired_x = (settings.SCREEN_WIDTH / 2) - self.countdown_ready.get_width()
		self.countdown_ready_desired_y = (settings.SCREEN_HEIGHT - self.countdown_ready.get_height()) / 2
		self.countdown_ready_speed = 780 * settings.GAME_SCALE
		self.countdown_ready_slow_speed = 60 * settings.GAME_SCALE

		# Create, position and store the "GO" textitem.
		self.countdown_go = textitem.TextItem("GO", (255, 255, 255))
		self.countdown_go.set_size(18 * settings.GAME_SCALE)
		self.countdown_go.x = -self.countdown_go.get_width()
		self.countdown_go.y = (settings.SCREEN_HEIGHT - self.countdown_go.get_height()) / 2
		self.countdown_go_desired_x = (settings.SCREEN_WIDTH - self.countdown_go.get_width()) / 2
		self.countdown_go_desired_y = (settings.SCREEN_HEIGHT / 2) - self.countdown_go.get_height()
		self.countdown_go_speed = 780 * settings.GAME_SCALE
		self.countdown_go_slow_speed = 78 * settings.GAME_SCALE

		# This is the surface that is actually drawn when the draw method is called.
		self.active_surface = self.countdown_ready

		# When this is false, the update_and_draw method displays the countdown.
		self.done = False

	def update(self):
		if not self.done:
			# If we're not done yet, increment the time passed.
			self.time_passed += self.main_clock.get_time()
			if self.time_passed > self.time_to_countdown and self.time_passed < self.time_to_countdown + self.countdown_ready_time:
				# If it's time to display the ready text, position it and do so.
				if self.countdown_ready.x < self.countdown_ready_desired_x:
					if (self.countdown_ready.x + self.countdown_ready_speed * self.main_clock.delta_time) > self.countdown_ready_desired_x:
						self.countdown_ready.x = self.countdown_ready_desired_x
					else:
						self.countdown_ready.x += self.countdown_ready_speed * self.main_clock.delta_time
				elif self.countdown_ready.x >= (self.countdown_ready_desired_x + self.countdown_ready.get_width()):
						self.countdown_ready.x += self.countdown_ready_speed * self.main_clock.delta_time
				else:
					if (self.countdown_ready.x + self.countdown_ready_slow_speed * self.main_clock.delta_time) > (self.countdown_ready_desired_x + self.countdown_ready.get_width()):
						self.countdown_ready.x = self.countdown_ready_desired_x + self.countdown_ready.get_width()
					else:
						self.countdown_ready.x += self.countdown_ready_slow_speed * self.main_clock.delta_time
				self.active_surface = self.countdown_ready
			elif self.time_passed > self.time_to_countdown + self.countdown_ready_time and self.time_passed < self.time_to_countdown + self.countdown_ready_time + self.countdown_go_time:
				# If it's time to display the GO text, position it and do so.
				if self.countdown_go.x < self.countdown_go_desired_x:
					if (self.countdown_go.x + self.countdown_go_speed * self.main_clock.delta_time) > self.countdown_go_desired_x:
						self.countdown_go.x = self.countdown_go_desired_x
					else:
						self.countdown_go.x += self.countdown_go_speed * self.main_clock.delta_time
				elif self.countdown_go.x >= (self.countdown_go_desired_x + self.countdown_go.get_width()):
						self.countdown_go.x += self.countdown_go_speed * self.main_clock.delta_time
				else:
					if (self.countdown_go.x + self.countdown_go_slow_speed * self.main_clock.delta_time) > (self.countdown_go_desired_x + self.countdown_go.get_width()):
						self.countdown_go.x = self.countdown_go_desired_x + self.countdown_go.get_width()
					else:
						self.countdown_go.x += self.countdown_go_slow_speed * self.main_clock.delta_time
				self.active_surface = self.countdown_go
			elif self.time_passed > self.time_to_countdown + self.countdown_ready_time + self.countdown_go_time:
				# Okay, the countdown is over. Set done to True and call the given function.
				self.done = True
				self.function_to_call()

	def draw(self, surface):
		if not self.done:
			self.active_surface.draw(surface)