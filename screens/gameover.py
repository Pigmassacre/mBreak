__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import copy
from pygame.locals import *
import other.useful as useful
import objects.groups as groups
import objects.firework as firework
import gui.textitem as textitem
import gui.listmenu as listmenu
import settings.settings as settings
import settings.graphics as graphics
import screens.scene as scene
import screens

"""

This is the screen that is displayed after amount of rounds that should be played have been played.
It allows the players to either return to the main menu or go for a rematch.

"""

class GameOver(scene.Scene):

	tint_color = pygame.Color(255, 255, 255, 128)

	def __init__(self, window_surface, main_clock, player_one, player_two, number_of_rounds, score, winner):
		# Call the superconstructor.
		scene.Scene.__init__(self, window_surface, main_clock)

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

		# Store the winner
		self.winner = winner

		# Configure the GUI.
		item_side_padding = textitem.TextItem.font_size

		# This sets up the winner text, coloring it and everything.
		self.setup_winner_text()

		quit_button = textitem.TextItem("Quit")
		self.quit_menu = listmenu.ListMenu(item_side_padding + (quit_button.get_width() / 2), settings.SCREEN_HEIGHT - item_side_padding - quit_button.get_height())
		self.quit_menu.add(quit_button, self.quit)
		self.quit_menu.items[0].selected = True
		self.menu_list.append(self.quit_menu)
		
		rematch_button = textitem.TextItem("Rematch")
		self.rematch_menu = listmenu.ListMenu(settings.SCREEN_WIDTH - item_side_padding - (rematch_button.get_width() / 2), settings.SCREEN_HEIGHT - item_side_padding - rematch_button.get_height())
		self.rematch_menu.add(rematch_button, self.rematch)
		self.menu_list.append(self.rematch_menu)

		# Register all menus with each other.
		for a_menu in self.menu_list:
			a_menu.register_other_menus(self.menu_list)

		# Setup the menu transition.
		for letter_item in self.winning_player_text:
			self.transition.setup_single_item_transition(letter_item, True, True, True, True)
		self.transition.setup_transition(self.quit_menu, True, False, False, True)
		self.transition.setup_transition(self.rematch_menu, False, True, False, True)

		self.firework_spawn_time = 300
		self.time_passed = 0

		# Setup and play music.
		self.setup_music()

		self.gameloop()

	def setup_winner_text(self):
		# Determine if there is a clear winner, or if there is a draw.
		if not self.winner is None:
			winning_string = self.winner.name + " wins!"
		else:
			winning_string = "Draw"

		# Create a list of textitems for all the letters in the winning_string.
		self.winning_player_text = textitem.generate_list_from_string(winning_string)

		length_of_winning_player_text = sum(letter_item.get_width() for letter_item in self.winning_player_text)

		last_offset = 0
		for letter_item in self.winning_player_text:
			letter_item.x = ((settings.SCREEN_WIDTH - length_of_winning_player_text) / 2.0) + last_offset
			letter_item.y = (settings.SCREEN_HEIGHT - letter_item.get_height()) / 2.0
			last_offset += letter_item.get_width()

			color = copy.copy(self.winner.color)
			h = color.hsla[0] + ((360 / (len(self.winning_player_text) * 2)) * self.winning_player_text.index(letter_item))
			h %= 360
			color.hsla = (h, color.hsla[1], color.hsla[2], color.hsla[3])
			letter_item.set_color(color)

		self.passed_time = 0

	def setup_music(self):
		# Set the music list.
		self.__class__.music_list = settings.AFTER_GAME_MUSIC
		self.play_music()

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

	def event(self, event):
		if (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == JOYBUTTONDOWN and event.button in settings.JOY_BUTTON_BACK):
			# If the escape key is pressed, we go back to the main menu.
			self.quit(None)
			
	def update(self):
		# Update all transition.
		self.transition.update(self.main_clock)

		self.time_passed += self.main_clock.get_time()
		if self.time_passed >= self.firework_spawn_time:
			x = random.uniform(settings.SCREEN_WIDTH / 10.0, settings.SCREEN_WIDTH - settings.SCREEN_WIDTH / 10.0)
			y = settings.SCREEN_HEIGHT
			angle = 3 * math.pi / 2.0
			duration = random.uniform((settings.SCREEN_HEIGHT / 4.0) * firework.Firework.speed / 4.0, (settings.SCREEN_HEIGHT - (settings.SCREEN_HEIGHT / 2.0)) * firework.Firework.speed / 4.0)
			firework.Firework(x, y, angle, duration)
			self.time_passed = 0

		# Update the fireworks.
		for projectile in groups.Groups.projectile_group:
			projectile.update(self.main_clock)

		for particle in groups.Groups.particle_group:
			particle.update(self.main_clock)

		# Update the winning player text.
		self.passed_time += self.main_clock.get_time()
		for letter_item in self.winning_player_text:
			bob_height_differentiator = self.winning_player_text.index(letter_item) * 64

			scale = 0.0075

			sin = 4 * settings.GAME_SCALE
			sin *= math.pow(math.sin((self.passed_time + bob_height_differentiator) * (scale / 32.0)), 3)
			sin *= math.sin((self.passed_time + bob_height_differentiator) * (scale / 8.0))
			sin *= math.sin((self.passed_time + bob_height_differentiator) * scale)

			letter_item_standard_y = (settings.SCREEN_HEIGHT - letter_item.get_height()) / 2.0
			letter_item.y = letter_item_standard_y + sin * 2.0 * settings.GAME_SCALE
			"""
			cos = 4 * settings.GAME_SCALE
			cos *= math.pow(math.cos((self.passed_time + bob_height_differentiator) * (scale / 32.0)), 3)
			cos *= math.cos((self.passed_time + bob_height_differentiator) * (scale / 8.0))
			cos *= math.cos((self.passed_time + bob_height_differentiator) * scale)

			length_of_winning_player_text = sum(letter_item.get_width() for letter_item in self.winning_player_text)
			offset = 0
			for x in range(0, self.winning_player_text.index(letter_item)):
				offset += self.winning_player_text[x].get_width()
			letter_item_standard_x = ((settings.SCREEN_WIDTH - length_of_winning_player_text) / 2.0) + offset
			letter_item.x = letter_item_standard_x + cos * 2.0 * settings.GAME_SCALE"""

			h = letter_item.font_color.hsla[0]
			h += self.main_clock.get_time() * 0.2			
			h %= 360
			new_color = copy.copy(letter_item.font_color)
			new_color.hsla = (h, letter_item.font_color.hsla[1], letter_item.font_color.hsla[2], letter_item.font_color.hsla[3])
			letter_item.set_color(new_color)

		# Update the menus.
		self.quit_menu.update(self.main_clock)
		self.rematch_menu.update(self.main_clock)
		
	def draw(self):
		# Every frame begins by blitting the background surface.
		self.window_surface.blit(self.background_surface, (0, 0))

		# Draw the fireworks.
		for projectile in groups.Groups.projectile_group:
			projectile.draw(self.window_surface)

		for particle in groups.Groups.particle_group:
			particle.draw(self.window_surface)

		# Draw the winning players name.
		for letter_item in self.winning_player_text:
			letter_item.draw(self.window_surface)

		# Draw the menus.
		self.quit_menu.draw(self.window_surface)
		self.rematch_menu.draw(self.window_surface)

	def on_exit(self):
		if self.next_screen is screens.game.Game:
			groups.empty_after_round()
			# If a rematch was selected, we reset the score and start a new instance of Game.
			self.score[self.player_one] = 0
			self.score[self.player_two] = 0
			self.next_screen(self.window_surface, self.main_clock, self.player_one, self.player_two, self.number_of_rounds, self.score)
		elif not self.next_screen is None:
			# If quit was selected, we empty all the groups and return to the main menu.
			groups.empty_all()
			self.next_screen(self.window_surface, self.main_clock)

		# Else, we simply let this scene end.