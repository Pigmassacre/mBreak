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
	splash_image_path = "res/splash/splash_bloodied.png"
	splash = pygame.image.load(splash_image_path)
	splash = pygame.transform.scale(splash, (splash.get_width() * 2, splash.get_height() * 2))

	splash_x = (BASE_WIDTH - splash.get_width()) / 2
	splash_y = (BASE_HEIGHT - splash.get_height()) / 2
		
	# Keeps track of how much time has passed.
	time_passed = 0

	while True:
		# Every frame begins by filling the whole screen with the background color.
		window_surface.fill(BACKGROUND_COLOR)
		game_surface.fill(BACKGROUND_COLOR)
		
		for event in pygame.event.get():
			#if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				# If the ESCAPE key is pressed or the window is closed, the game is shut down.
			#	pygame.quit()
			#	sys.exit()
			if event.type == KEYDOWN and event.key == K_RETURN:
				# If ENTER is pressed, proceed to the next screen, and end this loop.
				intromenu.main(window_surface, game_surface, main_clock, debug_font)

		# Increment the time passed.
		time_passed += main_clock.get_time()

		# When time is over, go to next screen.
		if time_passed >= SPLASH_TIME:
			intromenu.main(window_surface, game_surface, main_clock, debug_font)

		game_surface.blit(splash, (splash_x, splash_y))

		temp_surface = pygame.transform.scale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
		window_surface.blit(temp_surface, (0, 0))

		pygame.display.update()
		
		# Finally, constrain the game to a set maximum amount of FPS.
		main_clock.tick(MAX_FPS)