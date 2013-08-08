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
from settings.settings import *
import settings.graphics as graphics

# Import any needed game screens here.
import screens.game as game
import screens

class PauseMenu:

	def __init__(self, window_surface, main_clock, background_surface):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock
		self.background_surface = background_surface

		# Configure the GUI.
		self.prepare_menu_one = self.setup_prepare_menu(self.color_one)
		self.prepare_menu_one.x = (SCREEN_WIDTH - self.prepare_menu_one.get_width()) / 4
		self.prepare_menu_one.y = (SCREEN_HEIGHT - self.prepare_menu_one.get_height()) / 2

		# Setup the menu transitions.
		self.prepare_menu_one_transition = transition.Transition()
		self.prepare_menu_one_transition.setup_transition(self.prepare_menu_one, True, False, False, True)

		self.gameloop()

	def setup_pause_menu(self, function):
		pause_menu = self.setup_menu()
		self.setup_color_items(pause_menu, function)
		return pause_menu

	def setup_menu(self):
		x = SCREEN_WIDTH / 2
		y = SCREEN_HEIGHT / 2

		main_menu = menu.Menu(x, y)

		return main_menu

	def resume(self, item):
		self.done = True

	def quit(self, item):
		self.done = True
		self.next_screen = mainmenu.MainMenu

	def gameloop(self):
		self.done = False

		while not self.done:
			# Begin every frame by blitting the background surface.
			self.window_surface.blit(self.background_surface (0, 0))
			
			for event in pygame.event.get():
				if event.type == QUIT:
					# If the window is closed, the game is shut down.
					sys.exit()
					pygame.quit()
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					# If the escape key is pressed, we go back to the main menu.
					self.next_screen = screens.mainmenu.MainMenu
					self.done = True
				elif event.type == KEYDOWN and event.key == K_RETURN:
					# If ENTER is pressed, proceed to the next screen, and end this loop.
					for item in self.active_menu[-1].items:
						if item.selected:
							self.active_menu[-1].functions[item](item)
							break
				elif event.type == KEYDOWN and event.key == K_UP:
					for item in self.active_menu[-1].items:
						if item.selected:
							if self.active_menu[-1].items.index(item) - 1 >= 0:
								self.active_menu[-1].items[self.active_menu[-1].items.index(item) - 1].selected = True
								item.selected = False
								break
				elif event.type == KEYDOWN and event.key == K_DOWN:
					for item in self.active_menu[-1].items:
						if item.selected:
							if self.active_menu[-1].items.index(item) + 1 <= len(self.active_menu[-1].items) - 1:
								self.active_menu[-1].items[self.active_menu[-1].items.index(item) + 1].selected = True
								item.selected = False
								break

			self.show_player_text()

			self.show_menu()

			self.show_toasts()

			if DEBUG_MODE:
				# Display various debug information.
				debug.Debug.display(self.window_surface, self.main_clock)

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(MAX_FPS)

		# The gameloop is over, so we either start the next screen or quit the game.
		self.on_exit()

	def show_player_text(self):
		self.player_one_text.draw(self.window_surface)
		self.player_two_text.draw(self.window_surface)

	def show_menu(self):
		self.prepare_menu_one_transition.handle_menu_transition(self.prepare_menu_one)
		self.prepare_menu_one.update()
		self.prepare_menu_one.draw(self.window_surface)

		self.player_one_text_transition.handle_item_transition(self.player_one_text)
		self.player_one_text.draw(self.window_surface)

		self.prepare_menu_two_transition.handle_menu_transition(self.prepare_menu_two)
		self.prepare_menu_two.update()
		self.prepare_menu_two.draw(self.window_surface)

		self.player_two_text_transition.handle_item_transition(self.player_two_text)
		self.player_two_text.draw(self.window_surface)
		
		self.back_menu_transition.handle_menu_transition(self.back_menu)
		self.back_menu.update()
		
		self.start_menu_transition.handle_menu_transition(self.start_menu)
		self.start_menu.update()

		# If the mouse cursor is above one menu, it unselect other menus.
		if self.back_menu.is_mouse_over_item(self.back_menu.items[0], pygame.mouse.get_pos()):
			self.start_menu.items[0].selected = False
		elif self.start_menu.is_mouse_over_item(self.start_menu.items[0], pygame.mouse.get_pos()):
			self.back_menu.items[0].selected = False

		self.back_menu.draw(self.window_surface)
		self.start_menu.draw(self.window_surface)

	def show_toasts(self):
		self.not_all_colors_chosen_toast.update_and_draw(self.window_surface)

	def on_exit(self):
		if self.next_screen == None:
			pygame.quit()
			sys.exit()
		elif self.next_screen == game.Game:
			self.next_screen(self.window_surface, self.main_clock, self.player_one_color, self.player_two_color)
		else:
			self.next_screen(self.window_surface, self.main_clock)