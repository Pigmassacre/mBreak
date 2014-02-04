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
import screens.confirmationmenu as confirmationmenu

"""

This is the screen that is displayed after a match is over, but there are still matches left to play.
The screen gives the players the ability to either start the next match, or quit to the main menu.
If the players chose the quit option, they have to confirm their choice via the confirmation menu.

They can also view their score so far, see the number of rounds they have left, and last but not least:
listen to the sweet, sweet after-game music! :) (MUSIC NOT MADE BY ME!)

"""

class MatchOver:

	def __init__(self, window_surface, main_clock, player_one, player_two, number_of_rounds, score, number_of_rounds_done):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# Tint the window surface and set it as the background surface.
		self.background_surface = window_surface.copy()
		useful.tint_surface(self.background_surface)

		# The next screen to be started when the gameloop ends.
		self.next_screen = screens.game.Game

		# Keep track of the players and the score for displaying.
		self.player_one = player_one
		self.player_two = player_two
		self.score = score

		# Keep track of the number of rounds and the number of rounds already done. We send this to Game if next match is clicked.
		self.number_of_rounds = number_of_rounds
		self.number_of_rounds_done = number_of_rounds_done

		# Configure the GUI.
		self.setup_menus()

		# Setup the menu transitions.
		self.setup_transitions()

		# Setup and play music.
		self.setup_music()

		# And finally, start the gameloop!
		self.gameloop()

	def setup_menus(self):
		# This is the distance from the screen edges to the GUI elements
		item_side_padding = textitem.TextItem.font_size

		# We setup and position all the needed textitems and menus.
		self.rounds_left_text = textitem.TextItem("Rounds Left", pygame.Color(255, 255, 255))
		self.rounds_left_text.x = (settings.SCREEN_WIDTH - self.rounds_left_text.get_width()) / 2
		self.rounds_left_text.y = item_side_padding

		self.rounds_left_number_text = textitem.TextItem(str(self.number_of_rounds - self.number_of_rounds_done), pygame.Color(255, 255, 255))
		self.rounds_left_number_text.x = (settings.SCREEN_WIDTH - self.rounds_left_number_text.get_width()) / 2
		self.rounds_left_number_text.y = self.rounds_left_text.y + (2 * self.rounds_left_number_text.get_height())

		self.player_one_score_text = textitem.TextItem(str(self.score[self.player_one]), pygame.Color(255, 255, 255))
		self.player_one_score_text.set_size(27 * settings.GAME_SCALE)
		self.player_one_score_text.x = (settings.SCREEN_WIDTH - self.player_one_score_text.get_width()) / 4
		self.player_one_score_text.y = (settings.SCREEN_HEIGHT - self.player_one_score_text.get_height()) / 2

		self.player_one_text = textitem.TextItem(self.player_one.name, pygame.Color(255, 255, 255))
		self.player_one_text.x = self.player_one_score_text.x + ((self.player_one_score_text.get_width() - self.player_one_text.get_width()) / 2)
		self.player_one_text.y = self.player_one_score_text.y - (2 * self.player_one_text.get_height())

		self.player_two_score_text = textitem.TextItem(str(self.score[self.player_two]), pygame.Color(255, 255, 255))
		self.player_two_score_text.set_size(27 * settings.GAME_SCALE)
		self.player_two_score_text.x = 3 * ((settings.SCREEN_WIDTH - self.player_two_score_text.get_width()) / 4)
		self.player_two_score_text.y = (settings.SCREEN_HEIGHT - self.player_two_score_text.get_height()) / 2

		self.player_two_text = textitem.TextItem(self.player_two.name, pygame.Color(255, 255, 255))
		self.player_two_text.x = self.player_two_score_text.x + ((self.player_two_score_text.get_width() - self.player_two_text.get_width()) / 2)
		self.player_two_text.y = self.player_two_score_text.y - (2 * self.player_two_text.get_height())

		# A list of all menus, so we can easily register all menus to all menus (so they know to unselect items in other menus and stuff like that).
		self.all_menus = []

		quit_button = textitem.TextItem("Quit")
		self.quit_menu = menu.Menu(item_side_padding + (quit_button.get_width() / 2), settings.SCREEN_HEIGHT - item_side_padding - quit_button.get_height())
		self.quit_menu.add(quit_button, self.maybe_quit)
		self.quit_menu.items[0].selected = True
		self.all_menus.append(self.quit_menu)
		
		next_match_button = textitem.TextItem("Next Round")
		self.next_match_menu = menu.Menu(settings.SCREEN_WIDTH - item_side_padding - (next_match_button.get_width() / 2), settings.SCREEN_HEIGHT - item_side_padding - next_match_button.get_height())
		self.next_match_menu.add(next_match_button, self.next_match)
		self.all_menus.append(self.next_match_menu)

		# Register all menus with each other. This is for gui.traversals sake, so it knows that there are more than one menu to traverse upon.
		for a_menu in self.all_menus:
			a_menu.register_other_menus(self.all_menus)

	def setup_transitions(self):
		# Sets up the different transitions of all the items.
		self.transitions = transition.Transition(self.main_clock)
		self.transitions.setup_single_item_transition(self.rounds_left_text, True, True, True, False)
		self.transitions.setup_single_item_transition(self.rounds_left_number_text, True, True, False, True)
		self.transitions.setup_single_item_transition(self.player_one_score_text, True, False, False, False)
		self.transitions.setup_single_item_transition(self.player_one_text, True, False, True, False)
		self.transitions.setup_single_item_transition(self.player_two_score_text, False, True, False, False)
		self.transitions.setup_single_item_transition(self.player_two_text, False, True, True, False)
		self.transitions.setup_transition(self.quit_menu, True, False, False, True)
		self.transitions.setup_transition(self.next_match_menu, False, True, False, True)

	def setup_music(self):
		# Loads the after-game music and plays it, looping forever.
		pygame.mixer.music.load(settings.AFTER_GAME_MUSIC)
		pygame.mixer.music.play(-1)

	def maybe_quit(self, item):
		# We ask the players if they REALLY want to quit, since they're in between matches.
		confirmationmenu.ConfirmationMenu(self.window_surface, self.main_clock, self.quit, item)

	def quit(self, item):
		# This is called if the players confirm the quit option.
		self.next_screen = screens.mainmenu.MainMenu
		self.done = True
		pygame.mixer.music.stop()

	def next_match(self, item):
		# Stop the music and start a new instance of Game!
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
					# If the escape key is pressed, we do the same thing as the quit button.
					self.maybe_quit(None)
				else:
					# The traversal module handles key movement between menus.
					traversal.traverse_menus(event, self.all_menus)

			# Update and draw all items.
			self.update_and_draw()

			if settings.DEBUG_MODE:
				# Display various debug information.
				debug.Debug.display(self.window_surface, self.main_clock)

			pygame.display.update()
			
		# The gameloop is over, so we either start the next screen or quit the game.
		self.on_exit()

	def update_and_draw(self):
		# Handle the transitions and blit all items.
		self.transitions.update()

		# We update the menus first, so if the confirmationmenu is shown the screen is empty of items and menus (other than the confirmation menu, ofc).
		self.quit_menu.update()
		self.next_match_menu.update()

		self.quit_menu.draw(self.window_surface)
		self.next_match_menu.draw(self.window_surface)

		# Draw all the other textitems.
		self.rounds_left_text.draw(self.window_surface)
		self.rounds_left_number_text.draw(self.window_surface)

		self.player_one_text.draw(self.window_surface)
		self.player_one_score_text.draw(self.window_surface)

		self.player_two_text.draw(self.window_surface)
		self.player_two_score_text.draw(self.window_surface)

	def on_exit(self):
		if self.next_screen == None:
			# If no screen is chosen, we simply quit.s
			pygame.quit()
			sys.exit()
		elif self.next_screen == screens.game.Game:
			# Next match is selected, so we start Game.
			self.next_screen(self.window_surface, self.main_clock, self.player_one, self.player_two, self.number_of_rounds, self.score, self.number_of_rounds_done)
		else:
			# Quit is selected, so we return to the main menu.
			groups.empty_all()
			self.next_screen(self.window_surface, self.main_clock)