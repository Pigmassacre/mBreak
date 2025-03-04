# nuitka-project: --msvc=latest
# nuitka-project: --mode=standalone
# nuitka-project: --include-module=pygame.display
# nuitka-project: --include-module=pygame.event
# nuitka-project: --include-module=pygame.joystick
# nuitka-project: --include-module=pygame.sprite
# nuitka-project: --include-module=pygame.font
# nuitka-project: --include-module=pygame.image
# nuitka-project: --include-module=pygame.mixer
# nuitka-project: --include-module=pygame.transform
# nuitka-project: --include-module=pygame.surface
# nuitka-project: --include-module=pygame.draw
# nuitka-project: --include-module=pygame.math
# nuitka-project: --include-module=pygame.time
# nuitka-project: --include-module=pygame.locals
# nuitka-project: --include-package-data=pygame
# nuitka-project: --include-data-files={MAIN_DIRECTORY}/settings.txt=settings.txt
# nuitka-project: --include-data-files=C:/Users/Olof/AppData/Local/Programs/Python/Python313/Lib/site-packages/pygame/libjpeg-62.dll=libjpeg-62.dll
# nuitka-project: --include-data-files=C:/Users/Olof/AppData/Local/Programs/Python/Python313/Lib/site-packages/pygame/libogg-0.dll=libogg-0.dll
# nuitka-project: --include-data-files=C:/Users/Olof/AppData/Local/Programs/Python/Python313/Lib/site-packages/pygame/libopus-0.dll=libopus-0.dll
# nuitka-project: --include-data-files=C:/Users/Olof/AppData/Local/Programs/Python/Python313/Lib/site-packages/pygame/libopusfile-0.dll=libopusfile-0.dll
# nuitka-project: --include-data-files=C:/Users/Olof/AppData/Local/Programs/Python/Python313/Lib/site-packages/pygame/libpng16-16.dll=libpng16-16.dll
# nuitka-project: --include-data-files=C:/Users/Olof/AppData/Local/Programs/Python/Python313/Lib/site-packages/pygame/libtiff-5.dll=libtiff-5.dll
# nuitka-project: --include-data-files=C:/Users/Olof/AppData/Local/Programs/Python/Python313/Lib/site-packages/pygame/libwavpack-1.dll=libwavpack-1.dll
# nuitka-project: --include-data-files=C:/Users/Olof/AppData/Local/Programs/Python/Python313/Lib/site-packages/pygame/libwebp-7.dll=libwebp-7.dll
# nuitka-project: --include-data-files=C:/Users/Olof/AppData/Local/Programs/Python/Python313/Lib/site-packages/pygame/libwebpdemux-2.dll=libwebpdemux-2.dll
# nuitka-project: --include-data-files=C:/Users/Olof/AppData/Local/Programs/Python/Python313/Lib/site-packages/pygame/libxmp.dll=libxmp.dll
# nuitka-project: --include-data-dir=res=res
# nuitka-project: --include-data-dir=fonts=fonts
# nuitka-project: --output-dir=build 

__author__ = "Olof Karlsson"
__version__ = "0.2"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *
import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
		display_modes = DOUBLEBUF | FULLSCREEN | SCALED
	else:
		display_modes = DOUBLEBUF | SCALED

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
