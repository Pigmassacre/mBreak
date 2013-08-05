__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
from libs import pyganim
import math
import other.debug as debug
import other.useful as useful
import gui.textitem as texitem
import gui.logo as logo
from settings.settings import *

# Import any needed game screens here.
import screens.intromenu as intromenu

class Splash:

	splash = pygame.image.load("res/splash/splash_color.png")
	splash = pygame.transform.scale(splash, (SCREEN_HEIGHT, SCREEN_HEIGHT))
	splash_top_half = splash.subsurface(pygame.Rect((0, 0), (splash.get_width(), splash.get_height() / 2)))
	splash_bottom_half = splash.subsurface(pygame.Rect((0, (splash.get_height()) / 2), (splash.get_width(), splash.get_height() / 2)))

	splash_time = 1750
	top_half_speed = 30
	bottom_half_speed = -30

	background_color = pygame.Color(0, 0, 0)

	def __init__(self, window_surface, main_clock, debug_font):
		self.window_surface = window_surface
		self.main_clock = main_clock
		self.debug_font = debug_font

		self.x = (SCREEN_WIDTH - Splash.splash.get_width()) / 2
		self.y = (SCREEN_HEIGHT - Splash.splash.get_height()) / 2

		self.top_half_x = -Splash.splash_top_half.get_width()
		self.top_half_y = 0
		self.bottom_half_x = SCREEN_WIDTH
		self.bottom_half_y = (SCREEN_HEIGHT / 2)

		self.top_go_right = True
		self.bottom_go_left = True

		self.top_done = False
		self.bottom_done = False

		# Keeps track of how much time has passed.
		self.time_passed = 0

		self.gameloop()

	def gameloop(self):
		self.done = False

		while not self.done:
			# Every frame begins by filling the whole screen with the background color.
			self.window_surface.fill(Splash.background_color)
			
			for event in pygame.event.get():
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == KEYDOWN and event.key == K_RETURN):
					# If ENTER is pressed, proceed to the next screen, and end this loop.
					self.done = True

			if self.time_passed >= Splash.splash_time:
				self.done = True

			if self.top_go_right:
				self.top_half_x += Splash.top_half_speed
			else:
				self.top_half_x -= Splash.top_half_speed

			if self.top_half_x > (2 * SCREEN_WIDTH) - Splash.splash_top_half.get_width():
				self.top_go_right = False
			elif self.top_half_x <= (SCREEN_WIDTH - Splash.splash_top_half.get_width()) / 2 and not self.top_go_right:
				self.top_half_x = (SCREEN_WIDTH - Splash.splash_top_half.get_width()) / 2
				self.top_done = True

			if self.bottom_go_left:
				self.bottom_half_x += Splash.bottom_half_speed
			else:
				self.bottom_half_x -= Splash.bottom_half_speed

			if self.bottom_half_x < -SCREEN_WIDTH:
				self.bottom_go_left = False
			elif self.bottom_half_x >= (SCREEN_WIDTH - Splash.splash_bottom_half.get_width()) / 2 and not self.bottom_go_left:
				self.bottom_half_x = (SCREEN_WIDTH - Splash.splash_bottom_half.get_width()) / 2
				self.bottom_done = True

			if self.top_done and self.bottom_done:
				self.time_passed += self.main_clock.get_time()
				self.window_surface.blit(Splash.splash, (self.x, self.y))
			else:
				self.window_surface.blit(Splash.splash_top_half, (self.top_half_x, self.top_half_y))
				self.window_surface.blit(Splash.splash_bottom_half, (self.bottom_half_x, self.bottom_half_y))

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(MAX_FPS)

		intromenu.IntroMenu(self.window_surface, self.main_clock, self.debug_font)