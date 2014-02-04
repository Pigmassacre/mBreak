__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import other.debug as debug
import other.useful as useful
import gui.textitem as textitem
import gui.menu as menu
import gui.transition as transition
import gui.traversal as traversal
import objects.groups as groups
import settings.settings as settings
import settings.graphics as graphics
import screens
import screens.confirmationmenu as confirmationmenu

"""

This is the class that handles the pause menu. The pause menu is only available during gameplay (not in the menus), but technically
it can be created from anywhere. Unless an option is chosen the pause menu runs indefinitely.

The available options are "Resume" and "Quit". If Quit is chosen, a confirmation menu is shown to confirm the quit request.

"""

class PauseMenu:

	tint_color = pygame.Color(255, 255, 255, 128)

	def __init__(self, window_surface, main_clock):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# Tint the window surface and set it as the background surface.
		self.background_surface = window_surface.copy()
		useful.tint_surface(self.background_surface)

		# The next screen to be started when the gameloop ends.
		self.next_screen = None

		# Create, store and position the pause menu.
		self.pause_menu = self.setup_pause_menu()
		self.pause_menu.x = settings.SCREEN_WIDTH / 2
		self.pause_menu.y = (settings.SCREEN_HEIGHT - self.pause_menu.get_height()) / 2
		self.pause_menu.cleanup()
		self.pause_menu.items[0].selected = True

		# Setup the menu transitions.
		self.transitions = transition.Transition(self.main_clock)
		self.transitions.setup_single_item_transition(self.pause_menu.items[0], True, True, True, False)
		self.transitions.setup_single_item_transition(self.pause_menu.items[1], True, True, False, True)

		# And finally, start the gameloop!
		self.gameloop()

	def setup_pause_menu(self):
		# Creates and adds the items to the pause menu.
		pause_menu = menu.Menu()
		pause_menu.add(textitem.TextItem("Resume"), self.resume)
		pause_menu.add(textitem.TextItem("Quit"), self.maybe_quit)
		return pause_menu

	def resume(self, item):
		# Finished the gameloop, allowing the class that started this pausemenu to resume.
		self.done = True

	def maybe_quit(self, item):
		# Setup the transitions so that if we return to the pause menu the items will transition.
		self.transitions.setup_single_item_transition(self.pause_menu.items[0], True, True, True, False)
		self.transitions.setup_single_item_transition(self.pause_menu.items[1], True, True, False, True)
		confirmationmenu.ConfirmationMenu(self.window_surface, self.main_clock, self.quit, item)

	def quit(self, item):
		# We quit to the main menu, so we stop the music and set the next screen to the main menu.
		pygame.mixer.music.stop()
		self.done = True
		self.next_screen = screens.mainmenu.MainMenu

	def gameloop(self):
		self.done = False
		while not self.done:
			# Constrain the game to a set maximum amount of FPS, and update the delta time value.
			self.main_clock.tick(graphics.MAX_FPS)

			# Begin every frame by blitting the background surface.
			self.window_surface.blit(self.background_surface, (0, 0))
			
			for event in pygame.event.get():
				if event.type == QUIT:
					# If the window is closed, the game is shut down.
					sys.exit()
					pygame.quit()
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					# If the escape key is pressed, we resume the game.
					self.resume(None)
				else:
					# Traversal handles key movement in menus!
					traversal.traverse_menus(event, [self.pause_menu])

			# Update and show the menu.
			self.show_menu()

			if settings.DEBUG_MODE:
				# Display various debug information.
				debug.Debug.display(self.window_surface, self.main_clock)

			pygame.display.update()

		# The gameloop is over, so we either start the next screen or quit the game.
		self.on_exit()

	def show_menu(self):
		# Update the transitions.
		self.transitions.update()

		# Update and show the menu.
		self.pause_menu.update()
		self.pause_menu.draw(self.window_surface)

	def on_exit(self):
		if not self.next_screen == None:
			# Gameloop is over, and since we're going to return to the main menu so we clear all the groups of their contents.
			groups.empty_all()
			self.next_screen(self.window_surface, self.main_clock)

		# Else, we do nothing. This resume to the gameloop where this pause menu was created.