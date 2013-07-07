__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
from libs import pyganim
import useful
import textitem
import logo
import debug
import math
from settings import *

# Import any needed game screens here.
import intromenu

def main(window_surface, game_surface, main_clock, debug_font):
	# Setup the splash image.
	splash_image_path = "res/splash/splash_color.png"
	splash = pygame.image.load(splash_image_path)

	splash = pygame.transform.scale(splash, (splash.get_width() * 2, splash.get_height() * 2))

	splash_x = (BASE_WIDTH - splash.get_width()) / 2
	splash_y = (BASE_HEIGHT - splash.get_height()) / 2

	splash_time = 1750

	scaled_splash = pygame.transform.scale(splash, (BASE_HEIGHT, BASE_HEIGHT))
	
	top_half = pygame.Rect((0, 0), (scaled_splash.get_width(), scaled_splash.get_height() / 2))
	bottom_half = pygame.Rect((0, (scaled_splash.get_height()) / 2), (scaled_splash.get_width(), scaled_splash.get_height() / 2))

	splash_top_half = scaled_splash.subsurface(top_half)
	splash_bottom_half = scaled_splash.subsurface(bottom_half)

	top_half_speed = 30
	bottom_half_speed = -30

	top_half_x = -splash_top_half.get_width()
	top_half_y = 0
	bottom_half_x = BASE_WIDTH
	bottom_half_y = (BASE_HEIGHT / 2)

	top_go_right = True
	bottom_go_left = True

	top_done = False
	bottom_done = False

	# Keeps track of how much time has passed.
	time_passed = 0


	background_color = (0, 0, 0)

	while True:
		# Every frame begins by filling the whole screen with the background color.
		window_surface.fill(background_color)
		game_surface.fill(background_color)
		
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == KEYDOWN and event.key == K_RETURN):
				# If ENTER is pressed, proceed to the next screen, and end this loop.
				intromenu.main(window_surface, game_surface, main_clock, debug_font)

		if time_passed >= splash_time:
			intromenu.main(window_surface, game_surface, main_clock, debug_font)

		if top_go_right:
			top_half_x += top_half_speed
		else:
			top_half_x -= top_half_speed

		if top_half_x > (2 * BASE_WIDTH) - splash_top_half.get_width():
			top_go_right = False
		elif top_half_x <= (BASE_WIDTH - splash_top_half.get_width()) / 2 and not top_go_right:
			top_half_x = (BASE_WIDTH - splash_top_half.get_width()) / 2
			top_done = True

		if bottom_go_left:
			bottom_half_x += bottom_half_speed
		else:
			bottom_half_x -= bottom_half_speed

		if bottom_half_x < -BASE_WIDTH:
			bottom_go_left = False
		elif bottom_half_x >= (BASE_WIDTH - splash_bottom_half.get_width()) / 2 and not bottom_go_left:
			bottom_half_x = (BASE_WIDTH - splash_bottom_half.get_width()) / 2
			bottom_done = True

		if top_done and bottom_done:
			time_passed += main_clock.get_time()
			game_surface.blit(splash, (splash_x, splash_y))
		else:
			game_surface.blit(splash_top_half, (top_half_x, top_half_y))
			game_surface.blit(splash_bottom_half, (bottom_half_x, bottom_half_y))

		#window_surface.blit(game_surface, ((SCREEN_WIDTH - BASE_WIDTH) / 2, (SCREEN_HEIGHT - BASE_HEIGHT) / 2))
		temp_surface = pygame.transform.scale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
		window_surface.blit(temp_surface, (0, 0))

		pygame.display.update()
		
		# Finally, constrain the game to a set maximum amount of FPS.
		main_clock.tick(MAX_FPS)