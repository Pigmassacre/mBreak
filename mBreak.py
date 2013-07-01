__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import useful
from settings import *
import intromenu

'''

TODO List

* Find out how to best handle switching between game states/scenes.
* Add main menu.
* Implement Ball and Paddle classes.

'''

def main():
	""" The following parts are the ones that should run first when booting up the game. """

	# Initiates the PyGame module.
	pygame.init()

	# Instantiates a PyGame Clock.
	main_clock = pygame.time.Clock()

	# Setup the window surface to be used.
	window_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

	# Set the window caption.
	pygame.display.set_caption(WINDOW_CAPTION)

	""" The parts below should probably go to a introscreen class/method/module? """

	intromenu.main(window_surface, main_clock)

# Start the game!
main()