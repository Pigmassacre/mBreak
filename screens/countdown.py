__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
from libs import pyganim
import math
import random
import other.debug as debug
import other.useful as useful
import gui.textitem as textitem
import gui.logo as logo
import gui.menu as menu
from settings.settings import *

class Countdown:

	def __init__(self, main_clock, function_to_call):
		# We use the main clock to keep track of the time passed.
		self.main_clock = main_clock
		# This is the function that is called when the countdown is over.
		self.function_to_call = function_to_call

		self.time_passed = 0
		self.time_to_countdown = 1500
		self.countdown_ready_time = 2000
		self.countdown_go_time = 1250
		self.countdown_ready = textitem.TextItem("Ready", (255, 255, 255))
		self.countdown_ready.x = -self.countdown_ready.get_width()
		self.countdown_ready.y = (SCREEN_HEIGHT - self.countdown_ready.get_height()) / 2
		self.countdown_ready_desired_x = (SCREEN_WIDTH / 2) - self.countdown_ready.get_width()
		self.countdown_ready_desired_y = (SCREEN_HEIGHT - self.countdown_ready.get_height()) / 2
		self.countdown_ready_speed = 50
		self.countdown_ready_slow_speed = 2
		self.countdown_go = textitem.TextItem("GO", (255, 255, 255))
		self.countdown_go.set_size(18 * GAME_SCALE)
		self.countdown_go.x = -self.countdown_go.get_width()
		self.countdown_go.y = (SCREEN_HEIGHT - self.countdown_go.get_height()) / 2
		self.countdown_go_desired_x = (SCREEN_WIDTH - self.countdown_go.get_width()) / 2
		self.countdown_go_desired_y = (SCREEN_HEIGHT / 2) - self.countdown_go.get_height()
		self.countdown_go_speed = 50
		self.countdown_go_slow_speed = 3

		self.done = False

	def update_and_draw(self, surface):
		if not self.done:
			self.time_passed += self.main_clock.get_time()
			if self.time_passed > self.time_to_countdown and self.time_passed < self.time_to_countdown + self.countdown_ready_time:
				if self.countdown_ready.x < self.countdown_ready_desired_x:
					if (self.countdown_ready.x + self.countdown_ready_speed) > self.countdown_ready_desired_x:
						self.countdown_ready.x = self.countdown_ready_desired_x
					else:
						self.countdown_ready.x += self.countdown_ready_speed
				elif self.countdown_ready.x >= (self.countdown_ready_desired_x + self.countdown_ready.get_width()):
						self.countdown_ready.x += self.countdown_ready_speed
				else:
					if (self.countdown_ready.x + self.countdown_ready_slow_speed) > (self.countdown_ready_desired_x + self.countdown_ready.get_width()):
						self.countdown_ready.x = self.countdown_ready_desired_x + self.countdown_ready.get_width()
					else:
						self.countdown_ready.x += self.countdown_ready_slow_speed
				self.countdown_ready.draw(surface)
			elif self.time_passed > self.time_to_countdown + self.countdown_ready_time and self.time_passed < self.time_to_countdown + self.countdown_ready_time + self.countdown_go_time:
				if self.countdown_go.x < self.countdown_go_desired_x:
					if (self.countdown_go.x + self.countdown_go_speed) > self.countdown_go_desired_x:
						self.countdown_go.x = self.countdown_go_desired_x
					else:
						self.countdown_go.x += self.countdown_go_speed
				elif self.countdown_go.x >= (self.countdown_go_desired_x + self.countdown_go.get_width()):
						self.countdown_go.x += self.countdown_go_speed
				else:
					if (self.countdown_go.x + self.countdown_go_slow_speed) > (self.countdown_go_desired_x + self.countdown_go.get_width()):
						self.countdown_go.x = self.countdown_go_desired_x + self.countdown_go.get_width()
					else:
						self.countdown_go.x += self.countdown_go_slow_speed
				self.countdown_go.draw(surface)
			elif self.time_passed > self.time_to_countdown + self.countdown_ready_time + self.countdown_go_time:
				self.function_to_call()
				self.done = True
