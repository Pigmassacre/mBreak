__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
import math
from pygame.locals import *
import other.debug as debug
import gui.textitem as textitem
import gui.menu as menu
import gui.gridmenu as gridmenu
import gui.imageitem as imageitem
import gui.transition as transition
import gui.traversal as traversal
import settings.settings as settings
import settings.graphics as graphics

# Import any needed game screens here.
import screens

class AboutMenu:

	def __init__(self, window_surface, main_clock, came_from_options = False):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# We also store wether or not we've come from the options menu in the main menu or not.
		self.came_from_options = came_from_options

		# The next screen to be started when the gameloop ends.
		self.next_screen = screens.mainmenu.MainMenu

		# The back button, displayed in the middle-bottom of the screen.
		back_button = textitem.TextItem("Back")
		self.back_menu = menu.Menu()
		self.back_menu.x = settings.SCREEN_WIDTH / 2
		self.back_menu.y = settings.SCREEN_HEIGHT - (2 * back_button.get_height())
		self.back_menu.add(back_button, self.back)
		self.back_menu.items[0].selected = True

		font_size = 6 * settings.GAME_SCALE

		self.pyganim_credits = textitem.TextItem("Pyganim is used for animating the mBreak logo")
		self.pyganim_credits.set_size(font_size)
		self.pyganim_credits.x = (settings.SCREEN_WIDTH - self.pyganim_credits.get_width()) / 2
		self.pyganim_credits.y = 9 * settings.GAME_SCALE

		self.pyganim_credits_source_code = textitem.TextItem("Pyganim source code is not included in this game")
		self.pyganim_credits_source_code.set_size(font_size)
		self.pyganim_credits_source_code.x = (settings.SCREEN_WIDTH - self.pyganim_credits_source_code.get_width()) / 2
		self.pyganim_credits_source_code.y = self.pyganim_credits.y + self.pyganim_credits_source_code.get_height()

		self.pyganim_credits_author = textitem.TextItem("Pyganim is made by Al Sweigart", pygame.Color(255, 255, 255))
		self.pyganim_credits_author.set_size(font_size)
		self.pyganim_credits_author.x = (settings.SCREEN_WIDTH - self.pyganim_credits_author.get_width()) / 2
		self.pyganim_credits_author.y = self.pyganim_credits_source_code.y + self.pyganim_credits_author.get_height()

		self.music_credits_title = textitem.TextItem("Title screen music is sexxxy bit 3 dot xm")
		self.music_credits_title.set_size(font_size)
		self.music_credits_title.x = (settings.SCREEN_WIDTH - self.music_credits_title.get_width()) / 2
		self.music_credits_title.y = self.pyganim_credits_author.y + (2 * self.music_credits_title.get_height())

		self.music_credits_after_game = textitem.TextItem("Postgame music is october chip dot xm")
		self.music_credits_after_game.set_size(font_size)
		self.music_credits_after_game.x = (settings.SCREEN_WIDTH - self.music_credits_after_game.get_width()) / 2
		self.music_credits_after_game.y = self.music_credits_title.y + self.music_credits_after_game.get_height()

		self.music_credits_title_author = textitem.TextItem("Both made by Drozerix", pygame.Color(255, 255, 255))
		self.music_credits_title_author.set_size(font_size)
		self.music_credits_title_author.x = (settings.SCREEN_WIDTH - self.music_credits_title_author.get_width()) / 2
		self.music_credits_title_author.y = self.music_credits_after_game.y + self.music_credits_title_author.get_height()

		self.music_credits_game = textitem.TextItem("Game music is stardstm dot mod")
		self.music_credits_game.set_size(font_size)
		self.music_credits_game.x = (settings.SCREEN_WIDTH - self.music_credits_game.get_width()) / 2
		self.music_credits_game.y = self.music_credits_title_author.y + (2 * self.music_credits_game.get_height())

		self.music_credits_game_author = textitem.TextItem("Made by Jester", pygame.Color(255, 255, 255))
		self.music_credits_game_author.set_size(font_size)
		self.music_credits_game_author.x = (settings.SCREEN_WIDTH - self.music_credits_game_author.get_width()) / 2
		self.music_credits_game_author.y = self.music_credits_game.y + self.music_credits_game_author.get_height()

		self.sound_effect_credits = textitem.TextItem("Sound effects mostly made using bfxr")
		self.sound_effect_credits.set_size(font_size)
		self.sound_effect_credits.x = (settings.SCREEN_WIDTH - self.sound_effect_credits.get_width()) / 2
		self.sound_effect_credits.y = self.music_credits_game_author.y + (2 * self.sound_effect_credits.get_height())

		self.sound_effect_credits_author = textitem.TextItem("Bfxr is made by increpare", pygame.Color(255, 255, 255))
		self.sound_effect_credits_author.set_size(font_size)
		self.sound_effect_credits_author.x = (settings.SCREEN_WIDTH - self.sound_effect_credits_author.get_width()) / 2
		self.sound_effect_credits_author.y = self.sound_effect_credits.y + self.sound_effect_credits_author.get_height()

		self.more_info_and_licenses = textitem.TextItem("More info and licenses are in the readme", pygame.Color(200, 20, 200))
		self.more_info_and_licenses.set_size(font_size)
		self.more_info_and_licenses.x = (settings.SCREEN_WIDTH - self.more_info_and_licenses.get_width()) / 2
		self.more_info_and_licenses.y = self.sound_effect_credits_author.y + (2 * self.more_info_and_licenses.get_height())

		self.made_by_author = textitem.TextItem("Olof Karlsson AKA Pigmassacre", pygame.Color(200, 0, 0))
		self.made_by_author.set_size(font_size)
		self.made_by_author.x = (settings.SCREEN_WIDTH - self.made_by_author.get_width()) / 2
		self.made_by_author.y = self.back_menu.y - (2 * self.made_by_author.get_height())

		self.made_by_info = textitem.TextItem("Everything else made by me", pygame.Color(255, 255, 255))
		self.made_by_info.set_size(font_size)
		self.made_by_info.x = (settings.SCREEN_WIDTH - self.made_by_info.get_width()) / 2
		self.made_by_info.y = self.made_by_author.y - self.made_by_info.get_height()

		self.images_current_scale = 1 * settings.GAME_SCALE

		self.image_left = pygame.image.load("res/splash/splash_bloody_left.png")
		self.image_left = pygame.transform.scale(self.image_left, (self.image_left.get_width() * self.images_current_scale, self.image_left.get_height() * self.images_current_scale))

		self.image_right = pygame.image.load("res/splash/splash_bloody_right.png")
		self.image_right = pygame.transform.scale(self.image_right, (self.image_right.get_width() * self.images_current_scale, self.image_right.get_height() * self.images_current_scale))

		# We setup all menu transitions.
		self.transitions = transition.Transition()
		self.transitions.speed = 20 * settings.GAME_SCALE
		self.transitions.setup_transition(self.back_menu, True, True, False, False)
		self.transitions.setup_single_item_transition(self.pyganim_credits, True, True, False, False)
		self.transitions.setup_single_item_transition(self.pyganim_credits_source_code, True, True, False, False)
		self.transitions.setup_single_item_transition(self.pyganim_credits_author, True, True, False, False)
		self.transitions.setup_single_item_transition(self.music_credits_title, True, True, False, False)
		self.transitions.setup_single_item_transition(self.music_credits_after_game, True, True, False, False)
		self.transitions.setup_single_item_transition(self.music_credits_title_author, True, True, False, False)
		self.transitions.setup_single_item_transition(self.music_credits_game, True, True, False, False)
		self.transitions.setup_single_item_transition(self.music_credits_game_author, True, True, False, False)
		self.transitions.setup_single_item_transition(self.sound_effect_credits, True, True, False, False)
		self.transitions.setup_single_item_transition(self.sound_effect_credits_author, True, True, False, False)
		self.transitions.setup_single_item_transition(self.more_info_and_licenses, True, True, False, False)
		self.transitions.setup_single_item_transition(self.made_by_author, True, True, False, False)
		self.transitions.setup_single_item_transition(self.made_by_info, True, True, False, False)

		# We setup and play music.
		self.setup_music()

		# And finally, we start the gameloop!
		self.gameloop()

	def setup_music(self):
		if not pygame.mixer.music.get_busy():
			# We only care about loading and playing the music if it isn't already playing.
			pygame.mixer.music.load(settings.TITLE_MUSIC)
			pygame.mixer.music.play(-1)

	def back(self, item):
		# Simply moves back to the main menu.
		self.next_screen = screens.mainmenu.MainMenu
		self.done = True

	def gameloop(self):
		self.done = False
		while not self.done:
			# Every frame begins by filling the whole screen with the background color.
			self.window_surface.fill(settings.BACKGROUND_COLOR)
			
			# We then check for any events.
			for event in pygame.event.get():
				if event.type == QUIT:
					# If the window is closed, the game is shut down.
					sys.exit()
					pygame.quit()
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					# If the escape key is pressed, we go back to the main menu.
					self.back(None)
				else:
					traversal.traverse_menus(event, [self.back_menu])

			# We update and draw the menus.
			self.show_menu()

			if settings.DEBUG_MODE:
				# Display various debug information.
				debug.Debug.display(self.window_surface, self.main_clock)

			# We have to update the display if we want anything we just did to actually display.
			pygame.display.update()
			
			# Finally, we constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(settings.MAX_FPS)

		# The gameloop is over, so we either start the next screen or quit the game.
		self.on_exit()

	def show_menu(self):
		# Handle all transitions.
		self.transitions.update()

		self.window_surface.blit(self.image_left, (self.made_by_author.x - self.image_left.get_width() - self.made_by_author.get_height(), self.made_by_author.y - (self.image_left.get_height() / 2)))
		self.window_surface.blit(self.image_right, (self.made_by_author.x + self.made_by_author.get_width() + self.made_by_author.get_height(), self.made_by_author.y - (self.image_left.get_height() / 2)))

		self.pyganim_credits.draw(self.window_surface)
		self.pyganim_credits_author.draw(self.window_surface)
		self.pyganim_credits_source_code.draw(self.window_surface)

		self.music_credits_title.draw(self.window_surface)
		self.music_credits_after_game.draw(self.window_surface)
		self.music_credits_title_author.draw(self.window_surface)

		self.music_credits_game.draw(self.window_surface)
		self.music_credits_game_author.draw(self.window_surface)

		self.sound_effect_credits.draw(self.window_surface)
		self.sound_effect_credits_author.draw(self.window_surface)

		self.more_info_and_licenses.draw(self.window_surface)

		self.made_by_info.draw(self.window_surface)
		self.made_by_author.draw(self.window_surface)

		self.back_menu.update()
		self.back_menu.draw(self.window_surface)

	def on_exit(self):
		if self.next_screen == None:
			# If next_screen haven't been set, we just quit.
			pygame.quit()
			sys.exit()
		elif self.next_screen == screens.mainmenu.MainMenu:
			# Start the mainmenu but make sure that we retain the menu history we had when we entered the help menu.
			self.next_screen(self.window_surface, self.main_clock, None, self.came_from_options, self.__class__)
		else:
			# For any other screen we just call it using the normal variables.
			self.next_screen(self.window_surface, self.main_clock)
