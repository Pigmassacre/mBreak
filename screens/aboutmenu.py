__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
import math
import random
from pygame.locals import *
import other.debug as debug
import gui.textitem as textitem
import gui.listmenu as listmenu
import gui.gridmenu as gridmenu
import gui.imageitem as imageitem
#import gui.transition as transition
import gui.traversal as traversal
import settings.settings as settings
import settings.graphics as graphics
import screens.scene as scene
import screens

"""

An about menu, where credits are shown. Can be reached from the main menu.

The only actions the user can take from here is to return to the main menu, which is done either with the ESCAPE key
or the back button.

NOTE!!!!

For some reason, if you keep entering and leaving this menu (and the helpmenu) lots of times in a row, the game will crash
with an "IOError: unable to read font filename". I haven't been able to fix this bug, and from what I understand it must
have something to do with creating way too many font objects, and the garbage collector has no chance to keep up with
destroying all objects. Or something. I really don't know, but luckily getting to this crash bug is a kind of inane process.

I don't think anyone should ever go in and out of a menu repeatedly... But if they do, well, then I don't know what to do. :(

"""

class AboutMenu(scene.Scene):

	def __init__(self, window_surface, main_clock):
		# Call the superconstructor.
		scene.Scene.__init__(self, window_surface, main_clock)

		# The next screen to be started when the gameloop ends.
		self.next_screen = None

		# The back button, displayed in the middle-bottom of the screen.
		back_button = textitem.TextItem("Back")
		self.back_menu = listmenu.ListMenu()
		self.back_menu.x = settings.SCREEN_WIDTH / 2
		self.back_menu.y = settings.SCREEN_HEIGHT - (2 * back_button.get_height())
		self.back_menu.add(back_button, self.back)
		self.back_menu.items[0].selected = True
		self.menu_list.append(self.back_menu)

		# We choose a smaller font size here for all the credits.
		font_size = 6 * settings.GAME_SCALE

		# Create and setup all the textitems.
		self.pyganim_credits = textitem.TextItem("Pyganim is used to help animate items in the game")
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

		self.music_credits_title = textitem.TextItem("Title screen music is sexxxy bit 3.xm")
		self.music_credits_title.set_size(font_size)
		self.music_credits_title.x = (settings.SCREEN_WIDTH - self.music_credits_title.get_width()) / 2
		self.music_credits_title.y = self.pyganim_credits_author.y + (2 * self.music_credits_title.get_height())

		self.music_credits_after_game = textitem.TextItem("Postgame music is october chip.xm")
		self.music_credits_after_game.set_size(font_size)
		self.music_credits_after_game.x = (settings.SCREEN_WIDTH - self.music_credits_after_game.get_width()) / 2
		self.music_credits_after_game.y = self.music_credits_title.y + self.music_credits_after_game.get_height()

		self.music_credits_title_author = textitem.TextItem("Both made by Drozerix", pygame.Color(255, 255, 255))
		self.music_credits_title_author.set_size(font_size)
		self.music_credits_title_author.x = (settings.SCREEN_WIDTH - self.music_credits_title_author.get_width()) / 2
		self.music_credits_title_author.y = self.music_credits_after_game.y + self.music_credits_title_author.get_height()

		self.music_credits_game = textitem.TextItem("Game music is stardstm.mod")
		self.music_credits_game.set_size(font_size)
		self.music_credits_game.x = (settings.SCREEN_WIDTH - self.music_credits_game.get_width()) / 2
		self.music_credits_game.y = self.music_credits_title_author.y + (2 * self.music_credits_game.get_height())

		self.music_credits_game_author = textitem.TextItem("Made by Jester", pygame.Color(255, 255, 255))
		self.music_credits_game_author.set_size(font_size)
		self.music_credits_game_author.x = (settings.SCREEN_WIDTH - self.music_credits_game_author.get_width()) / 2
		self.music_credits_game_author.y = self.music_credits_game.y + self.music_credits_game_author.get_height()

		self.sound_effect_credits = textitem.TextItem("Most sound effects made using bfxr")
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

		# The scale of the left and right looking pigs at the bottom of the screen.
		self.images_current_scale = 1 * settings.GAME_SCALE

		self.image_left = pygame.image.load("res/splash/splash_bloody_left.png")
		self.image_left = pygame.transform.scale(self.image_left, (self.image_left.get_width() * self.images_current_scale, self.image_left.get_height() * self.images_current_scale))

		self.image_right = pygame.image.load("res/splash/splash_bloody_right.png")
		self.image_right = pygame.transform.scale(self.image_right, (self.image_right.get_width() * self.images_current_scale, self.image_right.get_height() * self.images_current_scale))

		# We setup all menu transition.
		self.transition.speed = 1200 * settings.GAME_SCALE
		self.transition.setup_transition(self.back_menu, True, True, False, False)
		self.transition.setup_single_item_transition(self.pyganim_credits, True, True, False, False)
		self.transition.setup_single_item_transition(self.pyganim_credits_source_code, True, True, False, False)
		self.transition.setup_single_item_transition(self.pyganim_credits_author, True, True, False, False)
		self.transition.setup_single_item_transition(self.music_credits_title, True, True, False, False)
		self.transition.setup_single_item_transition(self.music_credits_after_game, True, True, False, False)
		self.transition.setup_single_item_transition(self.music_credits_title_author, True, True, False, False)
		self.transition.setup_single_item_transition(self.music_credits_game, True, True, False, False)
		self.transition.setup_single_item_transition(self.music_credits_game_author, True, True, False, False)
		self.transition.setup_single_item_transition(self.sound_effect_credits, True, True, False, False)
		self.transition.setup_single_item_transition(self.sound_effect_credits_author, True, True, False, False)
		self.transition.setup_single_item_transition(self.more_info_and_licenses, True, True, False, False)
		self.transition.setup_single_item_transition(self.made_by_author, True, True, False, False)
		self.transition.setup_single_item_transition(self.made_by_info, True, True, False, False)

		# And finally, we start the gameloop!
		self.gameloop()

	def back(self, item):
		# This simply ends this scene.
		self.done = True

	def event(self, event):
		if (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == JOYBUTTONDOWN and event.button in settings.JOY_BUTTON_BACK):
			# If the escape key is pressed, we go end this scene.
			self.back(None)

	def update(self):		
		# Handle all transition.
		self.transition.update(self.main_clock)
		
		# Update the back menu.
		self.back_menu.update(self.main_clock)

	def draw(self):
		# Every frame begins by filling the whole screen with the background color.
		self.window_surface.fill(settings.BACKGROUND_COLOR)

		# Blit the two images to the window_surface, in the bottom left and bottom right of the screen.
		self.window_surface.blit(self.image_left, (self.made_by_author.x - self.image_left.get_width() - self.made_by_author.get_height(), self.made_by_author.y - (self.image_left.get_height() / 2)))
		self.window_surface.blit(self.image_right, (self.made_by_author.x + self.made_by_author.get_width() + self.made_by_author.get_height(), self.made_by_author.y - (self.image_left.get_height() / 2)))

		# Draw all the textitems.
		self.pyganim_credits.draw(self.window_surface)
		self.pyganim_credits_source_code.draw(self.window_surface)
		self.pyganim_credits_author.draw(self.window_surface)

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

		# Draw the back menu.
		self.back_menu.draw(self.window_surface)

	def on_exit(self):
		if not self.next_screen is None:
			# If there is a next screen set, start that.
			self.next_screen(self.window_surface, self.main_clock)
		
		# Else, we simply let this scene end.
