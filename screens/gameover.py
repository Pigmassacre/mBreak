__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
from libs import pyganim
import math
import random
import other.debug as debug
import other.useful as useful
import objects.groups as groups
import gui.textitem as textitem
import gui.logo as logo
import gui.menu as menu
import gui.gridmenu as gridmenu
import gui.coloritem as coloritem
import gui.transition as transition
import gui.toast as toast
import settings.settings as settings
import settings.graphics as graphics

# Import any needed game screens here.
#import screens.game as game
import screens

class GameOver:

	tint_color = pygame.Color(255, 255, 255, 128)

	def __init__(self, window_surface, main_clock, player_one, player_two, number_of_rounds, score):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# Tint the window surface and set it as the background surface.
		self.background_surface = window_surface.copy()
		useful.tint_surface(self.background_surface)

		# The next screen to be started when the gameloop ends.
		self.next_screen = screens.mainmenu.MainMenu

		# Keep track of the players and the score for displaying.
		self.player_one = player_one
		self.player_two = player_two
		self.score = score

		# Keep track of the number of rounds for rematch purposes.
		self.number_of_rounds = number_of_rounds

		# Figure out the winner from the score.
		if self.score[self.player_one] > self.score[self.player_two]:
			self.winner = self.player_one
			self.loser = self.player_two
		elif self.score[self.player_one] < self.score[self.player_two]:
			self.winner = self.player_two
			self.loser = self.player_one
		else:
			self.winner = None

		# Configure the GUI.
		item_side_padding = textitem.TextItem.font_size

		if not self.winner == None:
			winning_text = self.winner.name + " Wins"
		else:
			winning_text = "Draw"

		self.winning_player_text = textitem.TextItem(winning_text, pygame.Color(255, 255, 255))
		self.winning_player_text.x = (settings.SCREEN_WIDTH - self.winning_player_text.get_width()) / 2
		self.winning_player_text.y = (settings.SCREEN_HEIGHT - self.winning_player_text.get_height()) / 2

		quit_button = textitem.TextItem("Quit")
		self.quit_menu = menu.Menu(item_side_padding + (quit_button.get_width() / 2), settings.SCREEN_HEIGHT - item_side_padding - quit_button.get_height())
		self.quit_menu.add(quit_button, self.quit)
		self.quit_menu.items[0].selected = True
		
		rematch_button = textitem.TextItem("Rematch")
		self.rematch_menu = menu.Menu(settings.SCREEN_WIDTH - item_side_padding - (rematch_button.get_width() / 2), settings.SCREEN_HEIGHT - item_side_padding - rematch_button.get_height())
		self.rematch_menu.add(rematch_button, self.rematch)

		# Setup the menu transitions.
		self.winning_player_text_transition = transition.Transition()
		self.winning_player_text_transition.setup_single_item_transition(self.winning_player_text, True, True, True, False)

		self.quit_menu_transition = transition.Transition()
		self.quit_menu_transition.setup_transition(self.quit_menu, True, False, False, True)

		self.rematch_menu_transition = transition.Transition()
		self.rematch_menu_transition.setup_transition(self.rematch_menu, False, True, False, True)

		# Setup and play music.
		self.setup_music()

		self.gameloop()

	def setup_music(self):
		pygame.mixer.music.load(settings.TITLE_MUSIC)
		pygame.mixer.music.play()

	def quit(self, item):
		self.next_screen = screens.mainmenu.MainMenu
		self.done = True

	def rematch(self, item):
		pygame.mixer.music.stop()
		self.done = True
		self.next_screen = screens.game.Game

	def gameloop(self):
		self.done = False
		while not self.done:
			# Every frame begins by filling the whole screen with the background color.
			self.window_surface.blit(self.background_surface, (0, 0))

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
					if self.quit_menu.items[0].selected:
						self.quit_menu.functions[self.quit_menu.items[0]](self.quit_menu.items[0])
					elif self.rematch_menu.items[0].selected:
						self.rematch_menu.functions[self.rematch_menu.items[0]](self.rematch_menu.items[0])
				elif event.type == KEYDOWN and event.key == K_LEFT:
					if self.rematch_menu.items[0].selected:
						self.rematch_menu.items[0].selected = False
						self.quit_menu.items[0].selected = True
				elif event.type == KEYDOWN and event.key == K_RIGHT:
					if self.quit_menu.items[0].selected:
						self.quit_menu.items[0].selected = False
						self.rematch_menu.items[0].selected = True

			self.show_player_text()

			self.show_menu()

			if settings.DEBUG_MODE:
				# Display various debug information.
				debug.Debug.display(self.window_surface, self.main_clock)

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(settings.MAX_FPS)

		# The gameloop is over, so we either start the next screen or quit the game.
		self.on_exit()

	def show_player_text(self):
		self.winning_player_text.draw(self.window_surface)

	def show_menu(self):
		self.winning_player_text_transition.handle_item_transition(self.winning_player_text)
		self.winning_player_text.draw(self.window_surface)

		self.quit_menu_transition.handle_menu_transition(self.quit_menu)
		self.quit_menu.update()
		
		self.rematch_menu_transition.handle_menu_transition(self.rematch_menu)
		self.rematch_menu.update()

		# If the mouse cursor is above one menu, it unselect other menus.
		if self.quit_menu.is_mouse_over_item(self.quit_menu.items[0], pygame.mouse.get_pos()):
			self.rematch_menu.items[0].selected = False
		elif self.rematch_menu.is_mouse_over_item(self.rematch_menu.items[0], pygame.mouse.get_pos()):
			self.quit_menu.items[0].selected = False

		self.quit_menu.draw(self.window_surface)
		self.rematch_menu.draw(self.window_surface)

	def on_exit(self):
		if self.next_screen == None:
			pygame.quit()
			sys.exit()
		elif self.next_screen == screens.game.Game:
			self.score[self.player_one] = 0
			self.score[self.player_two] = 0
			self.next_screen(self.window_surface, self.main_clock, self.player_one, self.player_two, self.number_of_rounds, self.score)
		else:
			groups.empty_all()
			self.next_screen(self.window_surface, self.main_clock)