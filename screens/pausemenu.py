__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
from libs import pyganim
import math
import random
import other.debug as debug
import other.useful as useful
import gui.textitem as textitem
import gui.logo as logo
import gui.menu as menu
import gui.gridmenu as gridmenu
import gui.coloritem as coloritem
import gui.transition as transition
import gui.toast as toast
import objects.groups as groups
from settings.settings import *
import settings.graphics as graphics

# Import any needed game screens here.
import screens

class PauseMenu:

	def __init__(self, window_surface, main_clock):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock
		self.background_surface = window_surface.copy()

		# The next screen to be started when the gameloop ends.
		self.next_screen = None

		# Configure the GUI.
		self.pause_menu = self.setup_pause_menu()
		self.pause_menu.x = SCREEN_WIDTH / 2
		self.pause_menu.y = (SCREEN_HEIGHT - self.pause_menu.get_height()) / 2
		self.pause_menu.cleanup()
		self.pause_menu.items[0].selected = True

		# Setup the menu transitions.
		self.pause_menu_back_transition = transition.Transition()
		self.pause_menu_back_transition.setup_single_item_transition(self.pause_menu.items[0], True, True, True, False)

		self.pause_menu_quit_transition = transition.Transition()
		self.pause_menu_quit_transition.setup_single_item_transition(self.pause_menu.items[1], True, True, False, True)

		self.gameloop()

	def setup_pause_menu(self):
		pause_menu = menu.Menu()
		pause_menu.add(textitem.TextItem("Resume"), self.resume)
		pause_menu.add(textitem.TextItem("Quit"), self.quit)
		return pause_menu

	def resume(self, item):
		self.done = True

	def quit(self, item):
		self.done = True
		self.next_screen = screens.mainmenu.MainMenu

	def gameloop(self):
		self.done = False

		while not self.done:
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
				elif event.type == KEYDOWN and event.key == K_RETURN:
					# If ENTER is pressed, proceed to the next screen, and end this loop.
					for item in self.pause_menu.items:
						if item.selected:
							self.pause_menu.functions[item](item)
							break
				elif event.type == KEYDOWN and event.key == K_UP:
					for item in self.pause_menu.items:
						if item.selected:
							if self.pause_menu.items.index(item) - 1 >= 0:
								self.pause_menu.items[self.pause_menu.items.index(item) - 1].selected = True
								item.selected = False
								break
				elif event.type == KEYDOWN and event.key == K_DOWN:
					for item in self.pause_menu.items:
						if item.selected:
							if self.pause_menu.items.index(item) + 1 <= len(self.pause_menu.items) - 1:
								self.pause_menu.items[self.pause_menu.items.index(item) + 1].selected = True
								item.selected = False
								break

			self.show_menu()

			if DEBUG_MODE:
				# Display various debug information.
				debug.Debug.display(self.window_surface, self.main_clock)

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(MAX_FPS)

		# The gameloop is over, so we either start the next screen or quit the game.
		self.on_exit()

	def show_menu(self):
		self.pause_menu_back_transition.handle_item_transition(self.pause_menu.items[0])
		self.pause_menu_quit_transition.handle_item_transition(self.pause_menu.items[1])
		self.pause_menu.update()
		self.pause_menu.draw(self.window_surface)

	def on_exit(self):
		if not self.next_screen == None:
			# Gameloop is over, so we clear all the groups of their contents.
			groups.empty()
			self.next_screen(self.window_surface, self.main_clock)