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

	def __init__(self, window_surface, main_clock, debug_font):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock
		self.debug_font = debug_font

		self.background_surface = self.window_surface.copy()

		self.time_passed = 0
		self.time_to_countdown = 1500
		self.countdown_ready_time = 1000
		#self.countdown_ready_transition_time = 250
		self.countdown_go_time = 600
		#self.countdown_go_transition_time = 250
		self.countdown_ready = textitem.TextItem("Ready", (255, 255, 255))
		self.countdown_ready.x = (SCREEN_WIDTH - self.countdown_ready.get_width()) / 2
		self.countdown_ready.y = (SCREEN_HEIGHT - self.countdown_ready.get_height()) / 2
		self.countdown_go = textitem.TextItem("GO", (255, 255, 255))
		self.countdown_go.x = (SCREEN_WIDTH - self.countdown_go.get_width()) / 2
		self.countdown_go.y = (SCREEN_HEIGHT - self.countdown_go.get_height()) / 2

		self.gameloop()

	def gameloop(self):
		self.done = False
		while not self.done:
			# Every frame begins by filling the whole screen with the background color.
			self.window_surface.blit(self.background_surface, (0, 0))

			self.time_passed += self.main_clock.get_time()
			if self.time_passed < self.time_to_countdown:
				print("soon countdown")
			elif self.time_passed < self.time_to_countdown + self.countdown_ready_time:
				print("displaying ready")
				self.countdown_ready.draw(self.window_surface)
			elif self.time_passed < self.time_to_countdown + self.countdown_ready_time + self.countdown_go_time:
				print("displaying go")
				self.countdown_go.draw(self.window_surface)
			else:
				print("game has started")
				self.done = True

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(MAX_FPS)