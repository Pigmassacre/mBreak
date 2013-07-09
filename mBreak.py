__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *
from settings import *
import useful

# Import any needed game screens here.
import splash

def main():
	""" The following parts are the ones that run first when booting up the game. """

	# Initiates the PyGame module.
	pygame.init()

	# Instantiates a PyGame Clock.
	main_clock = pygame.time.Clock()

	# Setup the window surface to be used.
	window_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	#game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), SRCALPHA)

	# Set the window caption.
	pygame.display.set_caption(WINDOW_CAPTION)

	# Setup the debug font, used for all debug messages.
	debug_font = pygame.font.Font(DEBUG_FONT, 9)

	# Start the intro menu.
	splash.main(window_surface, main_clock, debug_font)

# Start the game!
main()