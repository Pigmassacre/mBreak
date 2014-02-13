__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import other.useful as useful
import gui.textitem as textitem
import gui.menu as menu
import gui.transition as transition
import gui.traversal as traversal
import settings.settings as settings
import screens.scene as scene
import screens

class Toast(scene.Scene):

	# Default color is red, since the toast is supposed to be a "warning" message.
	text_color = pygame.Color(255, 0, 0)
	text_color_odd = pygame.Color(255, 20, 20)

	def __init__(self, window_surface, main_clock, message):
		# Call the superconstructor.
		scene.Scene.__init__(self, window_surface, main_clock)

		# Tint the window surface and set it as the background surface.
		self.background_surface = self.window_surface.copy()
		useful.tint_surface(self.background_surface)

		distance_from_screen_edge = 6 * settings.GAME_SCALE
		max_width_of_text_line = (settings.SCREEN_WIDTH - (distance_from_screen_edge * 2))
		wrapped_message = useful.wrap_multi_line(message, pygame.font.Font(textitem.TextItem.font_path, textitem.TextItem.font_size), max_width_of_text_line)

		# We load a TextItem to display the message.
		self.message = []
		odd = True
		for line in wrapped_message:
			if odd:
				color = Toast.text_color
			else:
				color = Toast.text_color_odd
			message = textitem.TextItem(line, color)
			message.x = (settings.SCREEN_WIDTH - message.get_width()) / 2.0
			self.message.append(message)
			odd = not odd

		for message in self.message:
			message.y = (settings.SCREEN_HEIGHT - len(self.message) * message.get_height()) / 2.0 + self.message.index(message) * message.get_height()

		# Create, store and position the toast menu.
		self.toast_menu = self.setup_toast_menu()
		self.toast_menu.x = settings.SCREEN_WIDTH / 2
		self.toast_menu.y = self.message[len(self.message) - 1].y + self.message[0].get_height() + self.toast_menu.get_height()
		self.toast_menu.cleanup()
		self.toast_menu.items[0].selected = True

		# Setup the menu transitions.
		self.transitions = transition.Transition(self.main_clock)
		self.transitions.setup_single_item_transition(self.toast_menu.items[0], True, True, False, True)

		# And finally, start the gameloop!
		self.gameloop()

	def setup_toast_menu(self):
		# Creates and adds the items to the toast menu.
		toast_menu = menu.Menu()
		toast_menu.add(textitem.TextItem("Ok"), self.resume)
		return toast_menu

	def resume(self, item):
		# Finished the gameloop, allowing the class that started this toastmenu to resume.
		self.done = True

	def event(self, event):
		if (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == JOYBUTTONDOWN and event.button in settings.JOY_BUTTON_START):
			# If the escape key is pressed, we resume the game.
			self.resume(None)
		else:
			# Traversal handles key movement in menus!
			traversal.traverse_menus(event, [self.toast_menu])

	def update(self):
		# Update the transitions.
		self.transitions.update()

		# Update the toast menu.
		self.toast_menu.update(self.main_clock)

	def draw(self):
		# Begin every frame by blitting the background surface.
		self.window_surface.blit(self.background_surface, (0, 0))

		# Draw the toast message.
		for message in self.message:
			message.draw(self.window_surface)

		# Draw the toast menu.
		self.toast_menu.draw(self.window_surface)
