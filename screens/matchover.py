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

# Import any needed game screens here.
import screens
import screens.confirmationmenu as confirmationmenu

class MatchOver:

	tint_color = pygame.Color(255, 255, 255, 128)

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

		self.gameloop()

	def setup_menus(self):
		item_side_padding = textitem.TextItem.font_size

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

		# Register all menus with each other.
		for a_menu in self.all_menus:
			a_menu.register_other_menus(self.all_menus)

	def setup_transitions(self):
		self.transitions = transition.Transition()
		self.transitions.setup_single_item_transition(self.rounds_left_text, True, True, True, False)
		self.transitions.setup_single_item_transition(self.rounds_left_number_text, True, True, False, True)
		self.transitions.setup_single_item_transition(self.player_one_score_text, True, False, False, False)
		self.transitions.setup_single_item_transition(self.player_one_text, True, False, True, False)
		self.transitions.setup_single_item_transition(self.player_two_score_text, False, True, False, False)
		self.transitions.setup_single_item_transition(self.player_two_text, False, True, True, False)
		self.transitions.setup_transition(self.quit_menu, True, False, False, True)
		self.transitions.setup_transition(self.next_match_menu, False, True, False, True)

	def setup_music(self):
		pygame.mixer.music.load(settings.AFTER_GAME_MUSIC)
		pygame.mixer.music.play(-1)

	def maybe_quit(self, item):
		confirmationmenu.ConfirmationMenu(self.window_surface, self.main_clock, self.quit, item)

	def quit(self, item):
		self.next_screen = screens.mainmenu.MainMenu
		self.done = True
		pygame.mixer.music.stop()

	def next_match(self, item):
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
					# If the escape key is pressed, we do the same thing as the quit button.
					self.maybe_quit(None)
				else:
					traversal.traverse_menus(event, self.all_menus)

			# Update and draw all items.
			self.update_and_draw()

			if settings.DEBUG_MODE:
				# Display various debug information.
				debug.Debug.display(self.window_surface, self.main_clock)

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(settings.MAX_FPS)

		# The gameloop is over, so we either start the next screen or quit the game.
		self.on_exit()

	def update_and_draw(self):
		# Handle the transitions and blit all items.
		self.transitions.update()

		# We update the menus first, so if the confirmationmenu is shown the screen is empty.
		self.quit_menu.update()
		self.next_match_menu.update()

		# If the mouse cursor is above one menu, it unselect other menus.
		if self.quit_menu.is_mouse_over_item(self.quit_menu.items[0], pygame.mouse.get_pos()):
			self.next_match_menu.items[0].selected = False
		elif self.next_match_menu.is_mouse_over_item(self.next_match_menu.items[0], pygame.mouse.get_pos()):
			self.quit_menu.items[0].selected = False

		self.quit_menu.draw(self.window_surface)
		self.next_match_menu.draw(self.window_surface)

		self.rounds_left_text.draw(self.window_surface)
		self.rounds_left_number_text.draw(self.window_surface)

		self.player_one_text.draw(self.window_surface)
		self.player_one_score_text.draw(self.window_surface)

		self.player_two_text.draw(self.window_surface)
		self.player_two_score_text.draw(self.window_surface)

	def on_exit(self):
		if self.next_screen == None:
			pygame.quit()
			sys.exit()
		elif self.next_screen == screens.game.Game:
			# Next match is selected, so start game.
			self.next_screen(self.window_surface, self.main_clock, self.player_one, self.player_two, self.number_of_rounds, self.score, self.number_of_rounds_done)
		else:
			# Quit is selected, so return to the main menu.
			groups.empty_all()
			self.next_screen(self.window_surface, self.main_clock)