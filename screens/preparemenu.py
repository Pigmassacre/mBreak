__author__ = "Olof Karlsson"
__version__ = "0.1"
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
from settings.settings import *
import settings.graphics as graphics

# Import any needed game screens here.
import screens.game as game
import screens

class PrepareMenu:

	def __init__(self, window_surface, main_clock):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# The next screen to be started when the gameloop ends.
		self.next_screen = game.Game

		# Setup all the menues.
		self.prepare_menu_one = self.setup_prepare_menu(self.color_one)
		self.prepare_menu_one.x = (SCREEN_WIDTH - self.prepare_menu_one.get_width()) / 2
		self.prepare_menu_one.y = (SCREEN_HEIGHT - self.prepare_menu_one.get_height()) / 4
		self.prepare_menu_two = self.setup_prepare_menu(self.color_two)
		self.prepare_menu_two.x = (SCREEN_WIDTH - self.prepare_menu_two.get_width()) / 2
		self.prepare_menu_two.y = 3 * ((SCREEN_HEIGHT - self.prepare_menu_two.get_height()) / 4)

		# Setup the menu transitions.
		self.prepare_menu_one_transition = transition.Transition()
		self.prepare_menu_one_transition.setup_grid_menu_transition(self.prepare_menu_one)
		self.prepare_menu_two_transition = transition.Transition()
		self.prepare_menu_two_transition.setup_grid_menu_transition(self.prepare_menu_two)

		# Setup and play music.
		self.setup_music()

		self.gameloop()

	def start(self, item):
		pygame.mixer.music.stop()
		self.done = True

	def setup_prepare_menu(self, function):
		prepare_menu = self.setup_grid_menu()
		self.setup_color_items(prepare_menu, function)
		prepare_menu.cleanup()
		return prepare_menu

	def setup_color_items(self, grid_menu, function):
		grid_menu.add(coloritem.ColorItem(pygame.Color(255, 0, 0, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(0, 255, 0, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(0, 0, 255, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(255, 255, 0, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(255, 0, 255, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(0, 255, 255, 255)), function)

	def color_one(self, item):
		print(str(item) + " with color " + str(item.color) + " clicked!")

	def color_two(self, item):
		print(str(item) + " with color " + str(item.color) + " clicked!")

	def setup_menu(self):
		x = SCREEN_WIDTH / 2
		y = SCREEN_HEIGHT / 2

		main_menu = menu.Menu(x, y)

		return main_menu

	def setup_grid_menu(self):
		x = SCREEN_WIDTH / 2
		y = SCREEN_HEIGHT / 2

		grid_menu = gridmenu.GridMenu(x, y)

		return grid_menu

	def setup_button(self, text):
		font_color = (255, 255, 255)
		alpha_value = 255

		text = textitem.TextItem(text, font_color, alpha_value)

		return text

	def setup_color_item(self, color):
		return coloritem.ColorItem()

	def setup_music(self):
		if not pygame.mixer.music.get_busy():
			pygame.mixer.music.load(TITLE_MUSIC)
			pygame.mixer.music.play()

	def start_game(self, item):
		pygame.mixer.music.stop()
		self.done = True

	def back(self, item):
		self.active_menu.pop()
		self.menu_transition.setup_menu_transition(self.active_menu[-1])

	def quit(self, item):
		self.done = True
		self.next_screen = None

	def gameloop(self):
		self.done = False

		while not self.done:
			# Every frame begins by filling the whole screen with the background color.
			self.window_surface.fill(BACKGROUND_COLOR)
			
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
					self.start()

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
		self.prepare_menu_one_transition.handle_menu_transition(self.prepare_menu_one)
		self.prepare_menu_two_transition.handle_menu_transition(self.prepare_menu_two)
		self.prepare_menu_one.update()
		self.prepare_menu_two.update()
		self.prepare_menu_one.draw(self.window_surface)
		self.prepare_menu_two.draw(self.window_surface)

	def on_exit(self):
		if self.next_screen == None:
			pygame.quit()
			sys.exit()
		else:
			self.next_screen(self.window_surface, self.main_clock)