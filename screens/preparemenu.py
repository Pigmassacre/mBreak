__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
from libs import pyganim
import math
import random
import other.debug as debug
import other.useful as useful
import objects.player as player
import gui.textitem as textitem
import gui.logo as logo
import gui.menu as menu
import gui.gridmenu as gridmenu
import gui.coloritem as coloritem
import gui.choiceitem as choiceitem
import gui.transition as transition
import gui.toast as toast
import settings.settings as settings
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
		distance_from_screen_edge = 9 * settings.GAME_SCALE

		self.number_of_rounds_menu = gridmenu.GridMenu()
		# We set the default number of rounds to 1.
		temp_item = choiceitem.ChoiceItem(1)
		self.rounds(temp_item)
		self.number_of_rounds_menu.add(temp_item, self.rounds)
		self.number_of_rounds_menu.add(choiceitem.ChoiceItem(3), self.rounds)
		self.number_of_rounds_menu.add(choiceitem.ChoiceItem(5), self.rounds)
		self.number_of_rounds_menu.x = (settings.SCREEN_WIDTH - self.number_of_rounds_menu.get_width()) / 2
		self.number_of_rounds_menu.y = distance_from_screen_edge * 3

		self.number_of_rounds_text = textitem.TextItem("Rounds", pygame.Color(255, 255, 255))
		self.number_of_rounds_text.x = (settings.SCREEN_WIDTH - self.number_of_rounds_text.get_width()) / 2
		self.number_of_rounds_text.y = self.number_of_rounds_menu.y - (self.number_of_rounds_text.get_height() * 2)

		self.color_menu_one = self.setup_color_menu(self.color_one)
		self.color_menu_one.x = (settings.SCREEN_WIDTH - self.color_menu_one.get_width()) / 4
		self.color_menu_one.y = settings.SCREEN_HEIGHT / 2

		self.player_one_text = textitem.TextItem("Player One", pygame.Color(255, 255, 255))
		self.player_one_text.x = self.color_menu_one.x + ((self.color_menu_one.get_width() - self.player_one_text.get_width()) / 2)
		self.player_one_text.y = self.color_menu_one.y - (self.player_one_text.get_height() * 2)
		
		self.color_menu_two = self.setup_color_menu(self.color_two)
		self.color_menu_two.x = 3 * ((settings.SCREEN_WIDTH - self.color_menu_two.get_width()) / 4)
		self.color_menu_two.y = settings.SCREEN_HEIGHT / 2

		self.player_two_text = textitem.TextItem("Player Two", pygame.Color(255, 255, 255))
		self.player_two_text.x = self.color_menu_two.x + ((self.color_menu_two.get_width() - self.player_two_text.get_width()) / 2)
		self.player_two_text.y = self.color_menu_two.y - (self.player_two_text.get_height() * 2)

		back_button = textitem.TextItem("Back")
		self.back_menu = menu.Menu()
		self.back_menu.x = distance_from_screen_edge + (back_button.get_width() / 2)
		self.back_menu.y = settings.SCREEN_HEIGHT - (2 * back_button.get_height())
		self.back_menu.add(back_button, self.back)
		self.back_menu.items[0].selected = True
		
		start_button = textitem.TextItem("Start")
		self.start_menu = menu.Menu()
		self.start_menu.x = settings.SCREEN_WIDTH - distance_from_screen_edge - (start_button.get_width() / 2)
		self.start_menu.y = settings.SCREEN_HEIGHT - (2 * start_button.get_height())
		self.start_menu.add(start_button, self.start)

		# Setup the menu transitions.
		self.number_of_rounds_menu_transition = transition.Transition()
		self.number_of_rounds_menu_transition.setup_transition(self.number_of_rounds_menu, True, True, False, False)

		self.number_of_rounds_text_transition = transition.Transition()
		self.number_of_rounds_text_transition.setup_single_item_transition(self.number_of_rounds_text, True, True, True, False)

		self.color_menu_one_transition = transition.Transition()
		self.color_menu_one_transition.setup_transition(self.color_menu_one, True, False, False, True)

		self.player_one_text_transition = transition.Transition()
		self.player_one_text_transition.setup_single_item_transition(self.player_one_text, True, False, True, False)

		self.color_menu_two_transition = transition.Transition()
		self.color_menu_two_transition.setup_transition(self.color_menu_two, False, True, False, True)

		self.player_two_text_transition = transition.Transition()
		self.player_two_text_transition.setup_single_item_transition(self.player_two_text, False, True, True, False)

		self.back_menu_transition = transition.Transition()
		self.back_menu_transition.setup_transition(self.back_menu, True, False, False, True)

		self.start_menu_transition = transition.Transition()
		self.start_menu_transition.setup_transition(self.start_menu, False, True, False, True)

		# This toast is displayed when the start button is pressed if not all players have chosen their colors.
		self.not_all_colors_chosen_toast = toast.Toast("Both players need to pick a color", 1700, self.main_clock)
		self.not_all_colors_chosen_toast.x = (settings.SCREEN_WIDTH - self.not_all_colors_chosen_toast.get_width()) / 2
		self.not_all_colors_chosen_toast.y = self.color_menu_two.y + self.color_menu_two.get_height() +  self.not_all_colors_chosen_toast.get_height()

		# Setup and play music.
		self.setup_music()

		self.gameloop()

	def setup_music(self):
		if not pygame.mixer.music.get_busy():
			pygame.mixer.music.load(settings.TITLE_MUSIC)
			pygame.mixer.music.play()

	def setup_color_menu(self, function):
		color_menu = gridmenu.GridMenu()
		self.setup_color_items(color_menu, function)
		return color_menu

	def setup_color_items(self, grid_menu, function):
		grid_menu.add(coloritem.ColorItem(pygame.Color(255, 0, 0, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(0, 255, 0, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(0, 0, 255, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(255, 255, 0, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(255, 0, 255, 255)), function)
		grid_menu.add(coloritem.ColorItem(pygame.Color(0, 255, 255, 255)), function)

	def color_one(self, item):
		self.player_one_color = self.toggle_color(item, self.color_menu_one, self.color_menu_two)

	def color_two(self, item):
		self.player_two_color = self.toggle_color(item, self.color_menu_two, self.color_menu_one)

	def toggle_color(self, item, primary_menu, secondary_menu):
		chosen_item = None
		for menu_item in primary_menu.items:
			if menu_item.chosen:
				chosen_item = menu_item
				break

		if chosen_item == None:
			if not item.unavailable:
				item.chosen = True
				secondary_menu.items[primary_menu.items.index(item)].unavailable = True
				return item.color
		elif chosen_item == item:
			item.chosen = False
			secondary_menu.items[primary_menu.items.index(item)].unavailable = False
			return None
		elif not chosen_item == item:
			if not item.unavailable:
				chosen_item.chosen = False
				secondary_menu.items[primary_menu.items.index(chosen_item)].unavailable = False
				item.chosen = True
				secondary_menu.items[primary_menu.items.index(item)].unavailable = True
				return item.color
			return chosen_item.color

	def rounds(self, item):
		self.number_of_rounds = self.choose_number_of_rounds(item, self.number_of_rounds_menu)

	def choose_number_of_rounds(self, item, grid_menu):
		chosen_item = None
		for menu_item in grid_menu.items:
			if menu_item.chosen:
				chosen_item = menu_item
				break

		if chosen_item == None:
			item.chosen = True
		elif not chosen_item == item:
			chosen_item.chosen = False
			item.chosen = True

		return item.value

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
			self.window_surface.fill(settings.BACKGROUND_COLOR)
			
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

			self.show_menu()

			self.show_toasts()

			if settings.DEBUG_MODE:
				# Display various debug information.
				debug.Debug.display(self.window_surface, self.main_clock)

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(settings.MAX_FPS)

		# The gameloop is over, so we either start the next screen or quit the game.
		self.on_exit()

	def show_menu(self):
		self.number_of_rounds_menu_transition.handle_menu_transition(self.number_of_rounds_menu)
		self.number_of_rounds_menu.update()
		self.number_of_rounds_menu.draw(self.window_surface)

		self.number_of_rounds_text_transition.handle_item_transition(self.number_of_rounds_text)
		self.number_of_rounds_text.draw(self.window_surface)

		self.color_menu_one_transition.handle_menu_transition(self.color_menu_one)
		self.color_menu_one.update()
		self.color_menu_one.draw(self.window_surface)

		self.player_one_text_transition.handle_item_transition(self.player_one_text)
		self.player_one_text.draw(self.window_surface)

		self.color_menu_two_transition.handle_menu_transition(self.color_menu_two)
		self.color_menu_two.update()
		self.color_menu_two.draw(self.window_surface)

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
			player_one = self.create_player_one(self.player_one_color)
			player_two = self.create_player_two(self.player_two_color)
			score = {}
			score[player_one] = 0
			score[player_two] = 0
			self.next_screen(self.window_surface, self.main_clock, player_one, player_two, self.number_of_rounds, score)
		else:
			self.next_screen(self.window_surface, self.main_clock)

	def create_player_one(self, color):
		name = settings.PLAYER_ONE_NAME
		key_up = settings.PLAYER_ONE_KEY_UP
		key_down = settings.PLAYER_ONE_KEY_DOWN
		return player.Player(name, key_up, key_down, color)

	def create_player_two(self, color):
		name = settings.PLAYER_TWO_NAME
		key_up = settings.PLAYER_TWO_KEY_UP
		key_down = settings.PLAYER_TWO_KEY_DOWN
		return player.Player(name, key_up, key_down, color)