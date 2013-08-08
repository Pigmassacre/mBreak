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

class PrepareMenu:

	def __init__(self, window_surface, main_clock):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# The next screen to be started when the gameloop ends.
		self.next_screen = game.Game
		self.player_one_color = None
		self.player_two_color = None

		# Configure the GUI.
		self.prepare_menu_one = self.setup_prepare_menu(self.color_one)
		self.prepare_menu_one.x = (SCREEN_WIDTH - self.prepare_menu_one.get_width()) / 4
		self.prepare_menu_one.y = (SCREEN_HEIGHT - self.prepare_menu_one.get_height()) / 2

		self.player_one_text = self.setup_textitem("Player One")
		self.player_one_text.x = self.prepare_menu_one.x + ((self.prepare_menu_one.get_width() - self.player_one_text.get_width()) / 2)
		self.player_one_text.y = self.prepare_menu_one.y - (self.player_one_text.get_height() * 2)
		
		self.prepare_menu_two = self.setup_prepare_menu(self.color_two)
		self.prepare_menu_two.x = 3 * ((SCREEN_WIDTH - self.prepare_menu_two.get_width()) / 4)
		self.prepare_menu_two.y = (SCREEN_HEIGHT - self.prepare_menu_two.get_height()) / 2

		self.player_two_text = self.setup_textitem("Player Two")
		self.player_two_text.x = self.prepare_menu_two.x + ((self.prepare_menu_two.get_width() - self.player_two_text.get_width()) / 2)
		self.player_two_text.y = self.prepare_menu_two.y - (self.player_two_text.get_height() * 2)

		back_button = self.setup_textitem("Back")
		self.back_menu = menu.Menu(SCREEN_WIDTH / 5, SCREEN_HEIGHT - (2 * back_button.get_height()))
		self.back_menu.add(back_button, self.back)
		self.back_menu.items[0].selected = True
		
		start_button = self.setup_textitem("Start")
		self.start_menu = menu.Menu(SCREEN_WIDTH - (SCREEN_WIDTH / 5), SCREEN_HEIGHT - (2 * start_button.get_height()))
		self.start_menu.add(start_button, self.start)

		# Setup the menu transitions.
		self.prepare_menu_one_transition = transition.Transition()
		self.prepare_menu_one_transition.setup_transition(self.prepare_menu_one, True, False, False, True)

		self.player_one_text_transition = transition.Transition()
		self.player_one_text_transition.setup_single_item_transition(self.player_one_text, True, False, False, False)

		self.prepare_menu_two_transition = transition.Transition()
		self.prepare_menu_two_transition.setup_transition(self.prepare_menu_two, False, True, False, True)

		self.player_two_text_transition = transition.Transition()
		self.player_two_text_transition.setup_single_item_transition(self.player_two_text, False, True, False, False)

		self.back_menu_transition = transition.Transition()
		self.back_menu_transition.setup_transition(self.back_menu, True, False, False, True)

		self.start_menu_transition = transition.Transition()
		self.start_menu_transition.setup_transition(self.start_menu, False, True, False, True)

		# This toast is displayed when the start button is pressed if not all players have chosen their colors.
		self.not_all_colors_chosen_toast = toast.Toast("Both players need to pick a color", 1000, self.main_clock)
		self.not_all_colors_chosen_toast.x = (SCREEN_WIDTH - self.not_all_colors_chosen_toast.get_width()) / 2
		self.not_all_colors_chosen_toast.y = self.prepare_menu_two.y + self.prepare_menu_two.get_height() +  (2 * self.not_all_colors_chosen_toast.get_height())

		# Setup and play music.
		self.setup_music()

		self.gameloop()

	def setup_prepare_menu(self, function):
		prepare_menu = self.setup_grid_menu()
		self.setup_color_items(prepare_menu, function)
		return prepare_menu

	def setup_color_items(self, grid_menu, function):
		grid_menu.add(coloritem.ColorItem(pygame.Color(255, 0, 0, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(0, 255, 0, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(0, 0, 255, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(255, 255, 0, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(255, 0, 255, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(0, 255, 255, 255)), function)

	def color_one(self, item):
		self.player_one_color = self.toggle_color(item, self.prepare_menu_one, self.prepare_menu_two)
		print("color: " + str(self.player_one_color))

	def color_two(self, item):
		self.player_two_color = self.toggle_color(item, self.prepare_menu_two, self.prepare_menu_one)
		print("color: " + str(self.player_two_color))

	def toggle_color(self, item, primary_menu, secondary_menu):
		chosen_item = None
		for menu_item in primary_menu.items:
			if menu_item.chosen:
				chosen_item = menu_item
				break

		if chosen_item == None:
			if not item.unavailable:
				item.chosen = not item.chosen
				secondary_menu.items[primary_menu.items.index(item)].unavailable = not secondary_menu.items[primary_menu.items.index(item)].unavailable
				return item.color
		elif chosen_item == item:
			item.chosen = not item.chosen
			secondary_menu.items[primary_menu.items.index(item)].unavailable = not secondary_menu.items[primary_menu.items.index(item)].unavailable
			return None
		elif not chosen_item == item:
			return chosen_item.color

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

	def setup_textitem(self, text):
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

	def start(self, item):
		if not self.player_one_color == None and not self.player_two_color == None:
			pygame.mixer.music.stop()
			self.done = True
		else:
			self.not_all_colors_chosen_toast.start()

	def back(self, item):
		self.next_screen = screens.mainmenu.MainMenu
		self.done = True

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
					if self.back_menu.items[0].selected:
						self.back_menu.functions[self.back_menu.items[0]](self.back_menu.items[0])
					elif self.start_menu.items[0].selected:
						self.start_menu.functions[self.start_menu.items[0]](self.start_menu.items[0])
				elif event.type == KEYDOWN and event.key == K_LEFT:
					if self.start_menu.items[0].selected:
						self.start_menu.items[0].selected = False
						self.back_menu.items[0].selected = True
				elif event.type == KEYDOWN and event.key == K_RIGHT:
					if self.back_menu.items[0].selected:
						self.back_menu.items[0].selected = False
						self.start_menu.items[0].selected = True

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