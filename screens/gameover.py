__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import other.debug as debug
import other.useful as useful
import objects.groups as groups
import gui.textitem as textitem
import gui.menu as menu
import gui.transition as transition
import gui.traversal as traversal
import settings.settings as settings
import settings.graphics as graphics
import screens

"""

This is the screen that is displayed after amount of rounds that should be played have been played.
It allows the players to either return to the main menu or go for a rematch.

"""

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

		# Determine if there is a clear winner, or if there is a draw.
		if not self.winner == None:
			winning_text = self.winner.name + " Wins"
		else:
			winning_text = "Draw"

		self.winning_player_text = textitem.TextItem(winning_text, pygame.Color(255, 255, 255))
		self.winning_player_text.x = (settings.SCREEN_WIDTH - self.winning_player_text.get_width()) / 2
		self.winning_player_text.y = (settings.SCREEN_HEIGHT - self.winning_player_text.get_height()) / 2

		# A list of all menus, so we can easily register all menus to all menus (so they know to unselect items in other menus and stuff like that).
		self.all_menus = []

		quit_button = textitem.TextItem("Quit")
		self.quit_menu = menu.Menu(item_side_padding + (quit_button.get_width() / 2), settings.SCREEN_HEIGHT - item_side_padding - quit_button.get_height())
		self.quit_menu.add(quit_button, self.quit)
		self.quit_menu.items[0].selected = True
		self.all_menus.append(self.quit_menu)
		
		rematch_button = textitem.TextItem("Rematch")
		self.rematch_menu = menu.Menu(settings.SCREEN_WIDTH - item_side_padding - (rematch_button.get_width() / 2), settings.SCREEN_HEIGHT - item_side_padding - rematch_button.get_height())
		self.rematch_menu.add(rematch_button, self.rematch)
		self.all_menus.append(self.rematch_menu)

		# Register all menus with each other.
		for a_menu in self.all_menus:
			a_menu.register_other_menus(self.all_menus)

		# Setup the menu transitions.
		self.transitions = transition.Transition(self.main_clock)
		self.transitions.setup_single_item_transition(self.winning_player_text, True, True, True, False)
		self.transitions.setup_transition(self.quit_menu, True, False, False, True)
		self.transitions.setup_transition(self.rematch_menu, False, True, False, True)

		# Setup and play music.
		self.setup_music()

		self.gameloop()

	def setup_music(self):
		pygame.mixer.music.load(settings.AFTER_GAME_MUSIC)
		pygame.mixer.music.play()

	def quit(self, item):
		# When the quit button is activated, we want to return to the main menu.
		self.next_screen = screens.mainmenu.MainMenu
		self.done = True
		pygame.mixer.music.stop()

	def rematch(self, item):
		# When the rematch button is actived, we want to start a new instance of Game.
		pygame.mixer.music.stop()
		self.done = True
		self.next_screen = screens.game.Game

	def gameloop(self):
		self.done = False
		while not self.done:
			# Constrain the game to a set maximum amount of FPS, and update the delta time value.
			self.main_clock.tick(graphics.MAX_FPS)

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
				else:
					traversal.traverse_menus(event, self.all_menus)

			self.show_player_text()

			self.show_menu()

			if settings.DEBUG_MODE:
				# Display various debug information.
				debug.Debug.display(self.window_surface, self.main_clock)

			pygame.display.update()

		# The gameloop is over, so we either start the next screen or quit the game.
		self.on_exit()

	def show_player_text(self):
		self.winning_player_text.draw(self.window_surface)

	def show_menu(self):
		# Update all transitions.
		self.transitions.update()

		# Draw the winning players name.
		self.winning_player_text.draw(self.window_surface)

		# Update the menus.
		self.quit_menu.update()
		self.rematch_menu.update()

		# If the mouse cursor is above one menu, it unselect other menus.
		if self.quit_menu.is_mouse_over_item(self.quit_menu.items[0], pygame.mouse.get_pos()):
			self.rematch_menu.items[0].selected = False
		elif self.rematch_menu.is_mouse_over_item(self.rematch_menu.items[0], pygame.mouse.get_pos()):
			self.quit_menu.items[0].selected = False

		# Draw the menus.
		self.quit_menu.draw(self.window_surface)
		self.rematch_menu.draw(self.window_surface)

	def on_exit(self):
		if self.next_screen == None:
			# If no next_screen is specified, we quit.
			pygame.quit()
			sys.exit()
		elif self.next_screen == screens.game.Game:
			# If a rematch was selected, we reset the score and start a new instance of Game.
			self.score[self.player_one] = 0
			self.score[self.player_two] = 0
			self.next_screen(self.window_surface, self.main_clock, self.player_one, self.player_two, self.number_of_rounds, self.score)
		else:
			# If quit was selected, we empty all the groups and return to the main menu.
			groups.empty_all()
			self.next_screen(self.window_surface, self.main_clock)