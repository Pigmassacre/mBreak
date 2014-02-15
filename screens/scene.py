__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import other.debug as debug
import settings.settings as settings
import settings.graphics as graphics
import objects.groups as groups

"""

This is the base class of all screens / scenes in the game. It's very simple, it simply handles a few specific events and provides some
"common ground". Implementing classes have to take care of starting the gameloop themselves.

"""

class Scene:

	def __init__(self, window_surface, main_clock):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

	def gameloop(self):
		self.done = False
		while not self.done:
			# Constrain the game to a set maximum amount of FPS, and update the delta time value.
			self.main_clock.tick(graphics.MAX_FPS)

			# Check for any events.
			for event in pygame.event.get():
				if event.type == QUIT:
					# If the window is closed, the game is shut down.
					sys.exit()
					pygame.quit()

				# Subclasses implementing this class should handle their events in self.event(event).
				self.event(event)

			# Call the update method. Implement the handling of all game logic in this method.
			self.update()

			# Call the draw method. Implement all drawing/blitting etc. in this method.
			self.draw()

			# Display various debug information, if debug mode is enabled.
			if settings.DEBUG_MODE and not self.done:
				debug.Debug.display(self.window_surface, self.main_clock)

			# Finally, update the display.
			pygame.display.update()

		# The gameloop is over, so call the exit method.
		self.on_exit()

	def event(self, event):
		# Handle events in this method.
		pass

	def update(self):
		# Handle update logic in this method.
		pass

	def draw(self):
		# Handle all drawing in this method.
		pass

	def on_exit(self):
		# Handle what to do when the gameloop ends in this method.
		pass