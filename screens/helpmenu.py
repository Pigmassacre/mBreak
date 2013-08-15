__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import other.debug as debug
import other.useful as useful
import objects.player as player
import objects.powerup as powerup
import gui.textitem as textitem
import gui.menu as menu
import gui.gridmenu as gridmenu
import gui.imageitem as imageitem
import gui.transition as transition
import settings.settings as settings
import settings.graphics as graphics

# Import any needed game screens here.
import screens

class HelpMenu:

	def __init__(self, window_surface, main_clock, came_from_options = False):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# We also store wether or not we've come from the options menu in the main menu or not.
		self.came_from_options = came_from_options

		# The next screen to be started when the gameloop ends.
		self.next_screen = screens.mainmenu.MainMenu

		# This is a dictionary that contains information linked to certain imageitems.
		self.info_about = {}

		# This contains the currently active function that displays the currently active information.
		self.active_info = self.show_ball_info

		# Configure the GUI.
		distance_from_screen_edge = 9 * settings.GAME_SCALE

		# We create a gridmenu that allows the player to choose what item they want to read more about.
		self.help_menu = gridmenu.GridMenu(12)

		# Setup and add the ball item. Also set it as the default selected item.
		temp_item = imageitem.ImageItem("res/ball/ball.png")
		useful.colorize_image(temp_item.image, pygame.Color(255, 0, 0))
		self.info_about[temp_item] = self.show_ball_info
		self.view_info(temp_item)
		self.help_menu.add(temp_item, self.view_info)

		temp_item = imageitem.ImageItem("res/block/block.png")
		useful.colorize_image(temp_item.image, pygame.Color(255, 0, 0))
		self.info_about[temp_item] = self.show_block_info
		self.help_menu.add(temp_item, self.view_info)

		self.help_menu.x = (settings.SCREEN_WIDTH - self.help_menu.get_width()) / 2
		self.help_menu.y = distance_from_screen_edge

		# The back button, displayed in the bottom-left corner of the screen.
		back_button = textitem.TextItem("Back")
		self.back_menu = menu.Menu()
		self.back_menu.x = settings.SCREEN_WIDTH / 2
		self.back_menu.y = settings.SCREEN_HEIGHT - (2 * back_button.get_height())
		self.back_menu.add(back_button, self.back)
		self.back_menu.items[0].selected = True

		# We setup all menu transitions.
		self.transitions = transition.Transition()
		self.transitions.setup_transition(self.help_menu, True, True, True, False)
		self.transitions.setup_transition(self.back_menu, True, False, False, True)

		# We setup and play music.
		self.setup_music()

		# And finally, we start the gameloop!
		self.gameloop()

	def setup_music(self):
		if not pygame.mixer.music.get_busy():
			# We only care about loading and playing the music if it isn't already playing.
			pygame.mixer.music.load(settings.TITLE_MUSIC)
			pygame.mixer.music.play()

	def view_info(self, item):
		# Set the number of rounds to the value of the selected item.
		self.active_info = self.choose_active_info(item, self.help_menu)

	def choose_active_info(self, item, grid_menu):
		# Figure out what item is the chosen item.
		chosen_item = None
		for menu_item in grid_menu.items:
			if menu_item.chosen:
				chosen_item = menu_item
				break

		if chosen_item == None:
			# If there isn't a chosen item, set the selected item as the chosen item
			item.chosen = True
		elif not chosen_item == item:
			# If the chosen item and the selected item doesn't match, unchose the old chosen item and set the selected 
			# item as chosen instead.
			chosen_item.chosen = False
			item.chosen = True

		# At last, return the matching function in the info_about dictionary about the item.
		return self.info_about[item]

	def setup_ball_info(self):
		pass

	def show_ball_info(self, surface):
		print("showing ball info")

	def setup_block_info(self):
		pass

	def show_block_info(self, surface):
		print("showing block info")

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

		# Update and show the gridmenu.
		self.help_menu.update()
		self.help_menu.draw(self.window_surface)

		# Update and show the active information.
		self.active_info(self.window_surface)

		self.back_menu.update()
		self.back_menu.draw(self.window_surface)

	def on_exit(self):
		if self.next_screen == None:
			# If next_screen haven't been set, we just quit.
			pygame.quit()
			sys.exit()
		elif self.next_screen == screens.mainmenu.MainMenu:
			# Start the mainmenu but make sure that we retain the menu history we had when we entered the help menu.
			self.next_screen(self.window_surface, self.main_clock, None, self.came_from_options)
		else:
			# For any other screen we just call it using the normal variables.
			self.next_screen(self.window_surface, self.main_clock)
