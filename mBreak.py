__author__ = "Olof Karlsson"
__version__ = "0.2"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *
import other.useful as useful
import settings.settings as settings
import settings.graphics as graphics

# Import any needed game screens here.
import screens.splash as splash

def main():
	""" The following parts are the ones that run first when booting up the game. """

	# Initiates the PyGame module.
	pygame.init()

	# Instantiates a PyGame Clock.
	main_clock = pygame.time.Clock()

	# Load the settings.
	settings.load()
	graphics.load()

	# Setup the window surface to be used.
	window_surface = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), DOUBLEBUF | HWSURFACE)
	
	# Set the allowed events so we don't have to check for events that we don't listen to anyway.
	pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

	# Set the window caption.
	pygame.display.set_caption(settings.WINDOW_CAPTION)

	# Start the intro menu.
	splash.Splash(window_surface, main_clock)

# Start the game!
main()
