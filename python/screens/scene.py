__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import random
import other.debug as debug
import gui.transition as transition
import gui.traversal as traversal
import settings.settings as settings
import settings.graphics as graphics
import objects.groups as groups

"""

This is the base class of all screens / scenes in the game. It's very simple, it simply handles a few specific events and provides some
"common ground". Implementing classes have to take care of starting the gameloop themselves.

"""

class Scene:

	# We use this list of music to randomly choose what track to play. It's empty here, but subclasses can add to it.
	music_list = []

	def __init__(self, window_surface, main_clock):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# We use one single transition object to handle all transitions. If we want, we can ofcourse add more transition objects
		# to subclasses of this class, but hey.
		self.transition = transition.Transition()

		# We also store a list of all menus, for use with the traversal code.
		self.menu_list = []	

		# We also set pygame to send an event every time a song ends, so that scenes can know and then restart the music.
		pygame.mixer.music.set_endevent(settings.MUSIC_EVENT)

	def play_music(self):
		if len(self.__class__.music_list) > 0:
			choice = random.choice(self.__class__.music_list)
			pygame.mixer.music.load(choice)
		pygame.mixer.music.play()

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
				elif (event.type == settings.MUSIC_EVENT):
					self.play_music()

				# Subclasses implementing this class should handle their events in self.event(event).
				self.event(event)

				# We try to traverse the menus, if there is any.
				traversal.traverse_menus(event, self.menu_list)

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