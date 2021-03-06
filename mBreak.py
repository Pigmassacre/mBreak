__author__ = "Olof Karlsson"
__version__ = "0.2"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *
import objects.camera as camera
import settings.settings as settings
import objects.gameclock as gameclock
import settings.graphics as graphics

# We start the splash screen after everything is setup, so we import it here.
import screens.splash as splash

"""

This is the module to run when you want to start the game. It takes care of loading the settings, creating a clock object,
creating a window_surface and other such stuff.

When everything is setup, it starts the splash screen.

"""

def main():
	# Initiates the PyGame module.
	pygame.init()

	# Instantiates a PyGame Clock.
	main_clock = gameclock.GameClock()

	# Load the settings.
	settings.load()
	graphics.load()

	# Display modes, these are by standard double buffering (for performance reasons) and hardware acceleration (works if fullscreen is enabled).
	if graphics.FULLSCREEN:
		display_modes = DOUBLEBUF | HWSURFACE | FULLSCREEN | SCALED
	else:
		display_modes = DOUBLEBUF | HWSURFACE | SCALED

	# Setup the window surface to be used.
	window_surface = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), display_modes)

	# Initialize the camera.
	camera.create_camera(0, 0, settings.LEVEL_WIDTH, settings.LEVEL_HEIGHT)

	# Initialize the joystick module.
	pygame.joystick.init()

	# Initialize the available joysticks.
	for joystick in ([pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]):
		joystick.init()
	
	# Set the allowed events so we don't have to check for events that we don't listen to anyway.
	pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, JOYAXISMOTION, JOYBUTTONDOWN, JOYBUTTONUP])

	# Set the window caption.
	pygame.display.set_caption(settings.WINDOW_CAPTION)

	# Start the splash screen.
	splash.Splash(window_surface, main_clock)

# Start the game!
main()
