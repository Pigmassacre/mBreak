__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import other.debug as debug
import gui.textitem as textitem
import gui.menu as menu
import gui.gridmenu as gridmenu
import gui.imageitem as imageitem
import gui.transition as transition
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

		self.pyganim_credits = textitem.TextItem("Pyganim is used for animating the mBreak logo", pygame.Color(255, 255, 255))
		self.pyganim_credits.set_size(font_size)
		self.pyganim_credits.x = (settings.SCREEN_WIDTH - self.pyganim_credits.get_width()) / 2
		self.pyganim_credits.y = 9 * settings.GAME_SCALE

		self.pyganim_credits_source_code = textitem.TextItem("Pyganim source code is not included in this game", pygame.Color(255, 255, 255))
		self.pyganim_credits_source_code.set_size(font_size)
		self.pyganim_credits_source_code.x = (settings.SCREEN_WIDTH - self.pyganim_credits_source_code.get_width()) / 2
		self.pyganim_credits_source_code.y = self.pyganim_credits.y + self.pyganim_credits_source_code.get_height()

		self.pyganim_credits_author = textitem.TextItem("Pyganim is made by Al Sweigart", pygame.Color(255, 255, 255))
		self.pyganim_credits_author.set_size(font_size)
		self.pyganim_credits_author.x = (settings.SCREEN_WIDTH - self.pyganim_credits_author.get_width()) / 2
		self.pyganim_credits_author.y = self.pyganim_credits_source_code.y + self.pyganim_credits_author.get_height()

		self.made_by_author = textitem.TextItem("Olof Karlsson AKA Pigmassacre", pygame.Color(200, 0, 0))
		self.made_by_author.set_size(font_size)
		self.made_by_author.x = (settings.SCREEN_WIDTH - self.made_by_author.get_width()) / 2
		self.made_by_author.y = self.back_menu.y - (2 * self.made_by_author.get_height())

		self.made_by_info = textitem.TextItem("Everything else made by me", pygame.Color(255, 255, 255))
		self.made_by_info.set_size(font_size)
		self.made_by_info.x = (settings.SCREEN_WIDTH - self.made_by_info.get_width()) / 2
		self.made_by_info.y = self.made_by_author.y - self.made_by_info.get_height()

		# We setup all menu transitions.
		self.transitions = transition.Transition()
		self.transitions.setup_transition(self.back_menu, True, True, False, False)

		# We setup and play music.
		self.setup_music()

		# And finally, we start the gameloop!
		self.gameloop()

	def setup_music(self):
		if not pygame.mixer.music.get_busy():
			# We only care about loading and playing the music if it isn't already playing.
			pygame.mixer.music.load(settings.TITLE_MUSIC)
			pygame.mixer.music.play()

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
				elif event.type == KEYDOWN and event.key == K_RETURN:
					# If ENTER is pressed, figure out what function to call (if any) and call it.
					if self.back_menu.items[0].selected:
						self.back_menu.functions[self.back_menu.items[0]](self.back_menu.items[0])

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

		self.pyganim_credits.draw(self.window_surface)
		self.pyganim_credits_author.draw(self.window_surface)
		self.pyganim_credits_source_code.draw(self.window_surface)

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
