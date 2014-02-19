__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *
import other.useful as useful
import gui.textitem as textitem
import gui.listmenu as listmenu
import objects.groups as groups
import settings.settings as settings
import settings.graphics as graphics
import screens.scene as scene
import screens.confirmationmenu as confirmationmenu
import screens.optionsmenu as optionsmenu
import screens

"""

This is the class that handles the pause menu. The pause menu is only available during gameplay (not in the menus), but technically
it can be created from anywhere. Unless an option is chosen the pause menu runs indefinitely.

The available options are "Resume" and "Quit". If Quit is chosen, a confirmation menu is shown to confirm the quit request.

"""

class PauseMenu(scene.Scene):

	tint_color = pygame.Color(255, 255, 255, 128)

	def __init__(self, window_surface, main_clock):
		# Call the superconstructor.
		scene.Scene.__init__(self, window_surface, main_clock)

		# Tint the window surface and set it as the background surface.
		self.background_surface = self.window_surface.copy()
		useful.tint_surface(self.background_surface)

		# The next screen to be started when the gameloop ends.
		self.next_screen = None

		# Create, store and position the pause menu.
		self.setup_pause_menu()

		# Setup the menu transition.
		self.setup_transition()

		# And finally, start the gameloop!
		self.gameloop()

	def setup_pause_menu(self):
		# Creates and adds the items to the pause menu.
		self.pause_menu = listmenu.ListMenu()
		self.pause_menu.add(textitem.TextItem("Resume"), self.resume)
		self.pause_menu.add(textitem.TextItem("Options"), self.options)
		self.pause_menu.add(textitem.TextItem("Quit"), self.maybe_quit)
		self.pause_menu.x = settings.SCREEN_WIDTH / 2
		self.pause_menu.y = (settings.SCREEN_HEIGHT - self.pause_menu.get_height()) / 2.0
		self.pause_menu.cleanup()
		self.pause_menu.items[0].selected = True
		self.menu_list.append(self.pause_menu)

	def resume(self, item):
		# Finished the gameloop, allowing the class that started this pausemenu to resume.
		self.done = True

	def options(self, item):
		# Setup the transition so that if we return to the pause menu the items will transition.
		self.setup_transition()

		optionsmenu.OptionsMenu(self.window_surface, self.main_clock)

	def maybe_quit(self, item):
		# Setup the transition so that if we return to the pause menu the items will transition.
		self.setup_transition()

		# Blit the background surface over the window surface, so that the confirmation menu display over clean background surface.
		self.window_surface.blit(self.background_surface, (0, 0))
		confirmationmenu.ConfirmationMenu(self.window_surface, self.main_clock, self.quit, item)

	def quit(self, item):
		# We quit to the main menu, so we stop the music and set the next screen to the main menu.
		pygame.mixer.music.stop()
		self.done = True
		self.next_screen = screens.mainmenu.MainMenu

	def setup_transition(self):
		self.transition.setup_single_item_transition(self.pause_menu.items[0], True, True, True, False)
		for item in self.pause_menu.items[1:len(self.pause_menu.items) - 1]:
			# For every item other than the first and last item, we set these transition.
			self.transition.setup_single_item_transition(item, True, True, False, False)
		self.transition.setup_single_item_transition(self.pause_menu.items[-1], True, True, False, True)

	def event(self, event):
		if (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == JOYBUTTONDOWN and event.button in settings.JOY_BUTTON_START):
			# If the escape key is pressed, we resume the game.
			self.resume(None)

	def update(self):
		# Update the transition.
		self.transition.update(self.main_clock)

		# Update the pause menu.
		self.pause_menu.update(self.main_clock)

	def draw(self):
		# Begin every frame by blitting the background surface.
		self.window_surface.blit(self.background_surface, (0, 0))

		# Draw the pause menu.
		self.pause_menu.draw(self.window_surface)

	def on_exit(self):
		if not self.next_screen is None:
			# Gameloop is over, and since we're going to return to the main menu so we clear all the groups of their contents.
			groups.empty_all()
			self.next_screen(self.window_surface, self.main_clock)

		# Else, we do nothing. This resume to the gameloop where this pause menu was created.