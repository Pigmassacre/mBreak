__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *
import other.debug as debug
import gui.textitem as textitem
import gui.listmenu as listmenu
import settings.settings as settings
import settings.graphics as graphics
import screens.scene as scene

"""

This screen presents the user with a confirmation menu. The user can select between Yes or No.
If Yes is selected, a given function will be called with a given function_argument.
If No is selected, this screen does nothing, so the user is returned to the screen that created
the confirmation menu.

The window_surface given is copied and saved as a background_surface, so it looks like the menu
is displayed on top of the screen that created the confirmation menu.

"""

class ConfirmationMenu(scene.Scene):

	def __init__(self, window_surface, main_clock, function_to_call, function_argument):
		# Call the superconstructor.
		scene.Scene.__init__(self, window_surface, main_clock)

		# This is the function that will be called if the dialog is accepted.
		self.function_to_call = function_to_call

		# The argument we will use to call the function_to_call.
		self.function_argument = function_argument

		# If this is true when the gameloop ends, function_to_call will be called.
		self.accepted = False

		# Tint the window surface and set it as the background surface.
		self.background_surface = self.window_surface.copy()

		# The next screen to be started when the gameloop ends.
		self.next_screen = None

		# Configure the GUI.
		self.setup_menu()

		# Setup the menu transition.
		self.setup_transition()

		self.gameloop()

	def setup_menu(self):
		# Setup the textitem.
		self.confirmation_text = textitem.TextItem("Are you sure?", pygame.Color(255, 255, 255))
		self.confirmation_text.x = (settings.SCREEN_WIDTH - self.confirmation_text.get_width()) / 2

		# Setup the menu.
		self.confirmation_menu = listmenu.ListMenu()
		self.confirmation_menu.add(textitem.TextItem("Yes"), self.accept)
		self.confirmation_menu.add(textitem.TextItem("No"), self.refuse)
		self.confirmation_menu.x = settings.SCREEN_WIDTH / 2

		# Set the default action to be to refuse.
		self.confirmation_menu.items[1].selected = True
		self.menu_list.append(self.confirmation_menu)

		self.confirmation_text.y = (settings.SCREEN_HEIGHT - ((2 * self.confirmation_text.get_height()) + self.confirmation_menu.get_height())) / 2.0
		self.confirmation_menu.y = self.confirmation_text.y + (2 * self.confirmation_text.get_height())
		self.confirmation_menu.cleanup()

	def setup_transition(self):
		self.transition.setup_single_item_transition(self.confirmation_text, True, True, True, False)
		self.transition.setup_single_item_transition(self.confirmation_menu.items[0], True, True, False, False)
		self.transition.setup_single_item_transition(self.confirmation_menu.items[1], True, True, False, True)

	def accept(self, item):
		# Ends the gameloop and sets accepted to True.
		self.done = True
		self.accepted = True

	def refuse(self, item):
		# Ends the gameloop but sets accepted to False.
		self.done = True
		self.accepted = False

	def event(self, event):
		if (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == JOYBUTTONDOWN and event.button in settings.JOY_BUTTON_BACK):
			# If the escape key is pressed, we call refuse.
			self.refuse(None)

	def update(self):
		# Handle all transition.
		self.transition.update(self.main_clock)

		# Update the confirmation menu.
		self.confirmation_menu.update(self.main_clock)

	def draw(self):
		# Begin every frame by blitting the background surface.
		self.window_surface.blit(self.background_surface, (0, 0))		

		# Draw the confirmation text.
		self.confirmation_text.draw(self.window_surface)

		# Draw the confirmation menu.
		self.confirmation_menu.draw(self.window_surface)

	def on_exit(self):
		# We're done, so we call the function_to_call if we should, otherwise we do nothing.
		if self.accepted:
			self.function_to_call(self.function_argument)