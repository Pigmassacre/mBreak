__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import other.debug as debug
import other.useful as useful
import objects.player as player
import objects.powerup as powerup
import objects.burning as burning
import objects.freezing as freezing
import objects.multiball as multiball
import objects.blocks.weak as weakblock
import objects.blocks.normal as normalblock
import objects.blocks.strong as strongblock
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

		# This is a dictionary that maps transitions methods to certain imageitems.
		self.transition_method = {}

		# This contains the currently active function that displays the currently active information.
		self.active_info = self.show_ball_info

		# Configure the GUI.
		# We create a gridmenu that allows the player to choose what item they want to read more about.
		self.help_menu = gridmenu.GridMenu(7)

		# Setup and add the ball item. Also set it as the default selected item.
		first_item = imageitem.ImageItem("res/ball/ball.png")
		useful.colorize_image(first_item.image, pygame.Color(255, 0, 0))
		self.info_about[first_item] = self.show_ball_info
		self.transition_method[first_item] = self.setup_ball_info_transitions
		self.help_menu.add(first_item, self.view_info)

		temp_item = imageitem.ImageItem("res/block/block.png")
		useful.colorize_image(temp_item.image, pygame.Color(255, 0, 0))
		self.info_about[temp_item] = self.show_block_info
		self.transition_method[temp_item] = self.setup_block_info_transitions
		self.help_menu.add(temp_item, self.view_info)

		temp_item = imageitem.ImageItem("res/paddle/paddle.png")
		useful.colorize_image(temp_item.image, pygame.Color(255, 0, 0))
		self.info_about[temp_item] = self.show_paddle_info
		self.transition_method[temp_item] = self.setup_paddle_info_transitions
		self.help_menu.add(temp_item, self.view_info)

		temp_item = imageitem.ImageItem("res/powerup/fire.png")
		self.info_about[temp_item] = self.show_fire_info
		self.transition_method[temp_item] = self.setup_fire_info_transitions
		self.help_menu.add(temp_item, self.view_info)

		temp_item = imageitem.ImageItem("res/powerup/frost.png")
		self.info_about[temp_item] = self.show_frost_info
		self.transition_method[temp_item] = self.setup_frost_info_transitions
		self.help_menu.add(temp_item, self.view_info)

		temp_item = imageitem.ImageItem("res/powerup/doublespeed.png")
		self.info_about[temp_item] = self.show_doublespeed_info
		self.transition_method[temp_item] = self.setup_doublespeed_info_transitions
		self.help_menu.add(temp_item, self.view_info)

		temp_item = imageitem.ImageItem("res/powerup/multiball.png")
		self.info_about[temp_item] = self.show_multiball_info
		self.transition_method[temp_item] = self.setup_multiball_info_transitions
		self.help_menu.add(temp_item, self.view_info)

		self.help_menu.x = (settings.SCREEN_WIDTH - self.help_menu.get_width()) / 2
		self.help_menu.y = 9 * settings.GAME_SCALE

		# The back button, displayed in the middle-bottom of the screen.
		back_button = textitem.TextItem("Back")
		self.back_menu = menu.Menu()
		self.back_menu.x = settings.SCREEN_WIDTH / 2
		self.back_menu.y = settings.SCREEN_HEIGHT - (2 * back_button.get_height())
		self.back_menu.add(back_button, self.back)
		self.back_menu.items[0].selected = True

		# We setup all menu transitions.
		self.transitions = transition.Transition()
		self.transitions.setup_transition(self.help_menu, True, True, True, False)
		self.transitions.setup_transition(self.back_menu, True, True, False, False)

		# Setup the info items.
		self.distance_from_screen_edge = 6 * settings.GAME_SCALE
		self.setup_ball_info()
		self.setup_block_info()
		self.setup_paddle_info()
		self.setup_fire_info()
		self.setup_frost_info()
		self.setup_doublespeed_info()
		self.setup_multiball_info()

		# Set the first item as the active information.
		self.view_info(first_item)

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
		# Set the active info to the one chosen by the user.
		self.active_info = self.choose_active_info(item, self.help_menu)

		# Setup the transitions for that info.
		self.transition_method[item]()

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
		self.ball_info_texts = []

		self.ball_info_title_text = textitem.TextItem("Ball", pygame.Color(255, 255, 255))
		self.ball_info_title_text.set_size(6 * settings.GAME_SCALE)
		self.ball_info_title_text.x = (settings.SCREEN_WIDTH - self.ball_info_title_text.get_width()) / 2
		self.ball_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.ball_info_title_text.get_height()
		self.ball_info_texts.append(self.ball_info_title_text)

		self.ball_info_text_1 = textitem.TextItem("Both player starts the game with one ball each", pygame.Color(255, 255, 255))
		self.ball_info_text_1.set_size(6 * settings.GAME_SCALE)
		self.ball_info_text_1.x = self.distance_from_screen_edge
		self.ball_info_text_1.y = self.ball_info_title_text.y + (2 * self.ball_info_text_1.get_height())
		self.ball_info_texts.append(self.ball_info_text_1)

		self.ball_info_text_2 = textitem.TextItem("Your goal is to destroy your opponents blocks", pygame.Color(255, 255, 255))
		self.ball_info_text_2.set_size(6 * settings.GAME_SCALE)
		self.ball_info_text_2.x = self.distance_from_screen_edge
		self.ball_info_text_2.y = self.ball_info_text_1.y + self.ball_info_text_2.get_height()
		self.ball_info_texts.append(self.ball_info_text_2)

		self.ball_info_text_3 = textitem.TextItem("while defending your blocks with your paddle", pygame.Color(255, 255, 255))
		self.ball_info_text_3.set_size(6 * settings.GAME_SCALE)
		self.ball_info_text_3.x = self.distance_from_screen_edge
		self.ball_info_text_3.y = self.ball_info_text_2.y + self.ball_info_text_3.get_height()
		self.ball_info_texts.append(self.ball_info_text_3)

		self.ball_info_text_4 = textitem.TextItem("Balls will deal 10 damage to blocks they hit", pygame.Color(255, 255, 255))
		self.ball_info_text_4.set_size(6 * settings.GAME_SCALE)
		self.ball_info_text_4.x = self.distance_from_screen_edge
		self.ball_info_text_4.y = self.ball_info_text_3.y + (2 * self.ball_info_text_4.get_height())
		self.ball_info_texts.append(self.ball_info_text_4)

		self.ball_info_text_5 = textitem.TextItem("Your own balls will damage your own blocks", pygame.Color(255, 255, 255))
		self.ball_info_text_5.set_size(6 * settings.GAME_SCALE)
		self.ball_info_text_5.x = self.distance_from_screen_edge
		self.ball_info_text_5.y = self.ball_info_text_4.y + self.ball_info_text_5.get_height()
		self.ball_info_texts.append(self.ball_info_text_5)

		self.ball_info_text_6 = textitem.TextItem("Balls can acquire powerups by traveling over them", pygame.Color(255, 255, 255))
		self.ball_info_text_6.set_size(6 * settings.GAME_SCALE)
		self.ball_info_text_6.x = self.distance_from_screen_edge
		self.ball_info_text_6.y = self.ball_info_text_5.y + (2 * self.ball_info_text_6.get_height())
		self.ball_info_texts.append(self.ball_info_text_6)

		self.ball_info_text_7 = textitem.TextItem("any powerup gotten will affect all your balls", pygame.Color(255, 255, 255))
		self.ball_info_text_7.set_size(6 * settings.GAME_SCALE)
		self.ball_info_text_7.x = self.distance_from_screen_edge
		self.ball_info_text_7.y = self.ball_info_text_6.y + self.ball_info_text_7.get_height()
		self.ball_info_texts.append(self.ball_info_text_7)

	def setup_ball_info_transitions(self):
		self.transitions.setup_single_item_transition(self.ball_info_title_text, True, True, False, False)
		self.transitions.setup_single_item_transition(self.ball_info_text_1, True, True, False, False)
		self.transitions.setup_single_item_transition(self.ball_info_text_2, True, True, False, False)
		self.transitions.setup_single_item_transition(self.ball_info_text_3, True, True, False, False)
		self.transitions.setup_single_item_transition(self.ball_info_text_4, True, True, False, False)
		self.transitions.setup_single_item_transition(self.ball_info_text_5, True, True, False, False)
		self.transitions.setup_single_item_transition(self.ball_info_text_6, True, True, False, False)
		self.transitions.setup_single_item_transition(self.ball_info_text_7, True, True, False, False)

	def show_ball_info(self, surface):
		for info_text in self.ball_info_texts:
			info_text.draw(surface)

	def setup_block_info(self):
		self.block_info_texts = []

		self.block_info_title_text = textitem.TextItem("Block", pygame.Color(255, 255, 255))
		self.block_info_title_text.set_size(6 * settings.GAME_SCALE)
		self.block_info_title_text.x = (settings.SCREEN_WIDTH - self.block_info_title_text.get_width()) / 2
		self.block_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.block_info_title_text.get_height()
		self.block_info_texts.append(self.block_info_title_text)

		self.block_info_text_1 = textitem.TextItem("Blocks come in different strengths", pygame.Color(255, 255, 255))
		self.block_info_text_1.set_size(6 * settings.GAME_SCALE)
		self.block_info_text_1.x = self.distance_from_screen_edge
		self.block_info_text_1.y = self.block_info_title_text.y + (2 * self.block_info_text_1.get_height())
		self.block_info_texts.append(self.block_info_text_1)

		self.block_info_text_2 = textitem.TextItem("There are three types of blocks", pygame.Color(255, 255, 255))
		self.block_info_text_2.set_size(6 * settings.GAME_SCALE)
		self.block_info_text_2.x = self.distance_from_screen_edge
		self.block_info_text_2.y = self.block_info_text_1.y + self.block_info_text_2.get_height()
		self.block_info_texts.append(self.block_info_text_2)

		self.block_info_text_3_image = imageitem.ImageItem("res/block/block_weak.png", pygame.Color(255, 255, 255))
		useful.colorize_image(self.block_info_text_3_image.image, pygame.Color(255, 0, 0))
		self.block_info_text_3_image.x = self.distance_from_screen_edge
		self.block_info_text_3_image.y = self.block_info_text_2.y + (2 * self.block_info_text_2.get_height())
		self.block_info_texts.append(self.block_info_text_3_image)

		self.block_info_text_3 = textitem.TextItem("Weak blocks have " + str(weakblock.WeakBlock.health) + " health", pygame.Color(255, 255, 255))
		self.block_info_text_3.set_size(6 * settings.GAME_SCALE)
		self.block_info_text_3.x = self.block_info_text_3_image.x + self.block_info_text_3_image.get_width() + self.distance_from_screen_edge
		self.block_info_text_3.y = self.block_info_text_3_image.y + ((self.block_info_text_3_image.get_height() - self.block_info_text_3.get_height()) / 2)
		self.block_info_texts.append(self.block_info_text_3)

		self.block_info_text_4_image = imageitem.ImageItem("res/block/block.png", pygame.Color(255, 255, 255))
		useful.colorize_image(self.block_info_text_4_image.image, pygame.Color(255, 0, 0))
		self.block_info_text_4_image.x = self.distance_from_screen_edge
		self.block_info_text_4_image.y = self.block_info_text_3.y + (2 * self.block_info_text_2.get_height())
		self.block_info_texts.append(self.block_info_text_4_image)

		self.block_info_text_4 = textitem.TextItem("Normal blocks have " + str(normalblock.NormalBlock.health) + " health", pygame.Color(255, 255, 255))
		self.block_info_text_4.set_size(6 * settings.GAME_SCALE)
		self.block_info_text_4.x = self.block_info_text_4_image.x + self.block_info_text_4_image.get_width() + self.distance_from_screen_edge
		self.block_info_text_4.y = self.block_info_text_4_image.y + ((self.block_info_text_4_image.get_height() - self.block_info_text_4.get_height()) / 2)
		self.block_info_texts.append(self.block_info_text_4)

		self.block_info_text_5_image = imageitem.ImageItem("res/block/block_strong.png", pygame.Color(255, 255, 255))
		useful.colorize_image(self.block_info_text_5_image.image, pygame.Color(255, 0, 0))
		self.block_info_text_5_image.x = self.distance_from_screen_edge
		self.block_info_text_5_image.y = self.block_info_text_4.y + (2 * self.block_info_text_2.get_height())
		self.block_info_texts.append(self.block_info_text_5_image)

		self.block_info_text_5 = textitem.TextItem("Strong blocks have " + str(strongblock.StrongBlock.health) + " health", pygame.Color(255, 255, 255))
		self.block_info_text_5.set_size(6 * settings.GAME_SCALE)
		self.block_info_text_5.x = self.block_info_text_5_image.x + self.block_info_text_5_image.get_width() + self.distance_from_screen_edge
		self.block_info_text_5.y = self.block_info_text_5_image.y + ((self.block_info_text_5_image.get_height() - self.block_info_text_5.get_height()) / 2)
		self.block_info_texts.append(self.block_info_text_5)

	def setup_block_info_transitions(self):
		self.transitions.setup_single_item_transition(self.block_info_title_text, True, True, False, False)
		self.transitions.setup_single_item_transition(self.block_info_text_1, True, True, False, False)
		self.transitions.setup_single_item_transition(self.block_info_text_2, True, True, False, False)
		self.transitions.setup_single_item_transition(self.block_info_text_3_image, True, False, False, False)
		self.transitions.setup_single_item_transition(self.block_info_text_3, False, True, False, False)
		self.transitions.setup_single_item_transition(self.block_info_text_4_image, True, False, False, False)
		self.transitions.setup_single_item_transition(self.block_info_text_4, False, True, False, False)
		self.transitions.setup_single_item_transition(self.block_info_text_5_image, True, False, False, False)
		self.transitions.setup_single_item_transition(self.block_info_text_5, False, True, False, False)

	def show_block_info(self, surface):
		for info_text in self.block_info_texts:
			info_text.draw(surface)

	def setup_paddle_info(self):
		self.paddle_info_texts = []

		self.paddle_info_title_text = textitem.TextItem("Paddle", pygame.Color(255, 255, 255))
		self.paddle_info_title_text.set_size(6 * settings.GAME_SCALE)
		self.paddle_info_title_text.x = (settings.SCREEN_WIDTH - self.paddle_info_title_text.get_width()) / 2
		self.paddle_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.paddle_info_title_text.get_height()
		self.paddle_info_texts.append(self.paddle_info_title_text)

		self.paddle_info_text_1 = textitem.TextItem("Both players have one paddle each", pygame.Color(255, 255, 255))
		self.paddle_info_text_1.set_size(6 * settings.GAME_SCALE)
		self.paddle_info_text_1.x = self.distance_from_screen_edge
		self.paddle_info_text_1.y = self.paddle_info_title_text.y + (2 * self.paddle_info_text_1.get_height())
		self.paddle_info_texts.append(self.paddle_info_text_1)

		self.paddle_info_text_2 = textitem.TextItem("Steer your paddle to protect your blocks", pygame.Color(255, 255, 255))
		self.paddle_info_text_2.set_size(6 * settings.GAME_SCALE)
		self.paddle_info_text_2.x = self.distance_from_screen_edge
		self.paddle_info_text_2.y = self.paddle_info_text_1.y + self.paddle_info_text_2.get_height()
		self.paddle_info_texts.append(self.paddle_info_text_2)

		self.paddle_info_text_3 = textitem.TextItem("Player " + settings.PLAYER_ONE_NAME + " moves up and down with the", pygame.Color(255, 255, 255))
		self.paddle_info_text_3.set_size(6 * settings.GAME_SCALE)
		self.paddle_info_text_3.x = self.distance_from_screen_edge
		self.paddle_info_text_3.y = self.paddle_info_text_2.y + (2 * self.paddle_info_text_3.get_height())
		self.paddle_info_texts.append(self.paddle_info_text_3)

		self.paddle_info_text_4 = textitem.TextItem("W and S keys by default", pygame.Color(255, 255, 255))
		self.paddle_info_text_4.set_size(6 * settings.GAME_SCALE)
		self.paddle_info_text_4.x = self.distance_from_screen_edge
		self.paddle_info_text_4.y = self.paddle_info_text_3.y + self.paddle_info_text_4.get_height()
		self.paddle_info_texts.append(self.paddle_info_text_4)

		self.paddle_info_text_5 = textitem.TextItem("Player " + settings.PLAYER_TWO_NAME + " moves up and down with the", pygame.Color(255, 255, 255))
		self.paddle_info_text_5.set_size(6 * settings.GAME_SCALE)
		self.paddle_info_text_5.x = self.distance_from_screen_edge
		self.paddle_info_text_5.y = self.paddle_info_text_4.y + (2 * self.paddle_info_text_5.get_height())
		self.paddle_info_texts.append(self.paddle_info_text_5)

		self.paddle_info_text_6 = textitem.TextItem("UP and DOWN keys by default", pygame.Color(255, 255, 255))
		self.paddle_info_text_6.set_size(6 * settings.GAME_SCALE)
		self.paddle_info_text_6.x = self.distance_from_screen_edge
		self.paddle_info_text_6.y = self.paddle_info_text_5.y + self.paddle_info_text_6.get_height()
		self.paddle_info_texts.append(self.paddle_info_text_6)

		self.paddle_info_text_7 = textitem.TextItem("If your paddle is moving while it collides with a", pygame.Color(255, 255, 255))
		self.paddle_info_text_7.set_size(6 * settings.GAME_SCALE)
		self.paddle_info_text_7.x = self.distance_from_screen_edge
		self.paddle_info_text_7.y = self.paddle_info_text_6.y + (2 * self.paddle_info_text_7.get_height())
		self.paddle_info_texts.append(self.paddle_info_text_7)

		self.paddle_info_text_8 = textitem.TextItem("ball it will cause that ball to change its angle", pygame.Color(255, 255, 255))
		self.paddle_info_text_8.set_size(6 * settings.GAME_SCALE)
		self.paddle_info_text_8.x = self.distance_from_screen_edge
		self.paddle_info_text_8.y = self.paddle_info_text_7.y + self.paddle_info_text_8.get_height()
		self.paddle_info_texts.append(self.paddle_info_text_8)

		self.paddle_info_text_9 = textitem.TextItem("depending on the direction your paddle moved in", pygame.Color(255, 255, 255))
		self.paddle_info_text_9.set_size(6 * settings.GAME_SCALE)
		self.paddle_info_text_9.x = self.distance_from_screen_edge
		self.paddle_info_text_9.y = self.paddle_info_text_8.y + self.paddle_info_text_9.get_height()
		self.paddle_info_texts.append(self.paddle_info_text_9)

		self.paddle_info_text_10 = textitem.TextItem("This is called spinning the ball", pygame.Color(255, 255, 255))
		self.paddle_info_text_10.set_size(6 * settings.GAME_SCALE)
		self.paddle_info_text_10.x = self.distance_from_screen_edge
		self.paddle_info_text_10.y = self.paddle_info_text_9.y + self.paddle_info_text_10.get_height()
		self.paddle_info_texts.append(self.paddle_info_text_10)

	def setup_paddle_info_transitions(self):
		self.transitions.setup_single_item_transition(self.paddle_info_title_text, True, True, False, False)
		self.transitions.setup_single_item_transition(self.paddle_info_text_1, True, True, False, False)
		self.transitions.setup_single_item_transition(self.paddle_info_text_2, True, True, False, False)
		self.transitions.setup_single_item_transition(self.paddle_info_text_3, True, True, False, False)
		self.transitions.setup_single_item_transition(self.paddle_info_text_4, True, True, False, False)
		self.transitions.setup_single_item_transition(self.paddle_info_text_5, True, True, False, False)
		self.transitions.setup_single_item_transition(self.paddle_info_text_6, True, True, False, False)
		self.transitions.setup_single_item_transition(self.paddle_info_text_7, True, True, False, False)
		self.transitions.setup_single_item_transition(self.paddle_info_text_8, True, True, False, False)
		self.transitions.setup_single_item_transition(self.paddle_info_text_9, True, True, False, False)
		self.transitions.setup_single_item_transition(self.paddle_info_text_10, True, True, False, False)

	def show_paddle_info(self, surface):
		for info_text in self.paddle_info_texts:
			info_text.draw(surface)

	def setup_fire_info(self):
		self.fire_info_texts = []

		self.fire_info_title_text = textitem.TextItem("Fire", pygame.Color(255, 255, 255))
		self.fire_info_title_text.set_size(6 * settings.GAME_SCALE)
		self.fire_info_title_text.x = (settings.SCREEN_WIDTH - self.fire_info_title_text.get_width()) / 2
		self.fire_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.fire_info_title_text.get_height()
		self.fire_info_texts.append(self.fire_info_title_text)

		self.fire_info_text_1 = textitem.TextItem("This powerup will make your balls burn", pygame.Color(255, 255, 255))
		self.fire_info_text_1.set_size(6 * settings.GAME_SCALE)
		self.fire_info_text_1.x = self.distance_from_screen_edge
		self.fire_info_text_1.y = self.fire_info_title_text.y + (2 * self.fire_info_text_1.get_height())
		self.fire_info_texts.append(self.fire_info_text_1)

		self.fire_info_text_2 = textitem.TextItem("Any blocks hit by burning balls will also burn", pygame.Color(255, 255, 255))
		self.fire_info_text_2.set_size(6 * settings.GAME_SCALE)
		self.fire_info_text_2.x = self.distance_from_screen_edge
		self.fire_info_text_2.y = self.fire_info_text_1.y + (2 * self.fire_info_text_2.get_height())
		self.fire_info_texts.append(self.fire_info_text_2)

		self.fire_info_text_3 = textitem.TextItem("taking " + str(int(burning.Burning.damage_per_second)) + " damage per second", pygame.Color(255, 255, 255))
		self.fire_info_text_3.set_size(6 * settings.GAME_SCALE)
		self.fire_info_text_3.x = self.distance_from_screen_edge
		self.fire_info_text_3.y = self.fire_info_text_2.y + self.fire_info_text_3.get_height()
		self.fire_info_texts.append(self.fire_info_text_3)

		self.fire_info_text_4 = textitem.TextItem("This effect lasts for " + str(burning.Burning.duration / 1000) + " seconds", pygame.Color(255, 255, 255))
		self.fire_info_text_4.set_size(6 * settings.GAME_SCALE)
		self.fire_info_text_4.x = self.distance_from_screen_edge
		self.fire_info_text_4.y = self.fire_info_text_3.y + (2 * self.fire_info_text_4.get_height())
		self.fire_info_texts.append(self.fire_info_text_4)

		self.fire_info_text_5 = textitem.TextItem("Your balls will not spread the burn to your blocks", pygame.Color(255, 255, 255))
		self.fire_info_text_5.set_size(6 * settings.GAME_SCALE)
		self.fire_info_text_5.x = self.distance_from_screen_edge
		self.fire_info_text_5.y = self.fire_info_text_4.y + (2 * self.fire_info_text_5.get_height())
		self.fire_info_texts.append(self.fire_info_text_5)

	def setup_fire_info_transitions(self):
		self.transitions.setup_single_item_transition(self.fire_info_title_text, True, True, False, False)
		self.transitions.setup_single_item_transition(self.fire_info_text_1, True, True, False, False)
		self.transitions.setup_single_item_transition(self.fire_info_text_2, True, True, False, False)
		self.transitions.setup_single_item_transition(self.fire_info_text_3, True, True, False, False)
		self.transitions.setup_single_item_transition(self.fire_info_text_4, True, True, False, False)
		self.transitions.setup_single_item_transition(self.fire_info_text_5, True, True, False, False)

	def show_fire_info(self, surface):
		for info_text in self.fire_info_texts:
			info_text.draw(surface)

	def setup_frost_info(self):
		self.frost_info_texts = []

		self.frost_info_title_text = textitem.TextItem("Frost", pygame.Color(255, 255, 255))
		self.frost_info_title_text.set_size(6 * settings.GAME_SCALE)
		self.frost_info_title_text.x = (settings.SCREEN_WIDTH - self.frost_info_title_text.get_width()) / 2
		self.frost_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.frost_info_title_text.get_height()
		self.frost_info_texts.append(self.frost_info_title_text)

		self.frost_info_text_1 = textitem.TextItem("This powerup will make your balls ice cold", pygame.Color(255, 255, 255))
		self.frost_info_text_1.set_size(6 * settings.GAME_SCALE)
		self.frost_info_text_1.x = self.distance_from_screen_edge
		self.frost_info_text_1.y = self.frost_info_title_text.y + (2 * self.frost_info_text_1.get_height())
		self.frost_info_texts.append(self.frost_info_text_1)

		self.frost_info_text_2 = textitem.TextItem("Your opponents paddle will frozen by your balls", pygame.Color(255, 255, 255))
		self.frost_info_text_2.set_size(6 * settings.GAME_SCALE)
		self.frost_info_text_2.x = self.distance_from_screen_edge
		self.frost_info_text_2.y = self.frost_info_text_1.y + (2 * self.frost_info_text_2.get_height())
		self.frost_info_texts.append(self.frost_info_text_2)

		self.frost_info_text_3 = textitem.TextItem("This effect lasts for " + str(freezing.Freezing.duration / 1000) + " seconds", pygame.Color(255, 255, 255))
		self.frost_info_text_3.set_size(6 * settings.GAME_SCALE)
		self.frost_info_text_3.x = self.distance_from_screen_edge
		self.frost_info_text_3.y = self.frost_info_text_2.y + (2 * self.frost_info_text_3.get_height())
		self.frost_info_texts.append(self.frost_info_text_3)

		self.frost_info_text_4 = textitem.TextItem("Frozen paddles cannot move", pygame.Color(255, 255, 255))
		self.frost_info_text_4.set_size(6 * settings.GAME_SCALE)
		self.frost_info_text_4.x = self.distance_from_screen_edge
		self.frost_info_text_4.y = self.frost_info_text_3.y + (2 * self.frost_info_text_4.get_height())
		self.frost_info_texts.append(self.frost_info_text_4)

		self.frost_info_text_5 = textitem.TextItem("Your own paddle will not be frozen by your balls", pygame.Color(255, 255, 255))
		self.frost_info_text_5.set_size(6 * settings.GAME_SCALE)
		self.frost_info_text_5.x = self.distance_from_screen_edge
		self.frost_info_text_5.y = self.frost_info_text_4.y + (2 * self.frost_info_text_5.get_height())
		self.frost_info_texts.append(self.frost_info_text_5)

	def setup_frost_info_transitions(self):
		self.transitions.setup_single_item_transition(self.frost_info_title_text, True, True, False, False)
		self.transitions.setup_single_item_transition(self.frost_info_text_1, True, True, False, False)
		self.transitions.setup_single_item_transition(self.frost_info_text_2, True, True, False, False)
		self.transitions.setup_single_item_transition(self.frost_info_text_3, True, True, False, False)
		self.transitions.setup_single_item_transition(self.frost_info_text_4, True, True, False, False)
		self.transitions.setup_single_item_transition(self.frost_info_text_5, True, True, False, False)

	def show_frost_info(self, surface):
		for info_text in self.frost_info_texts:
			info_text.draw(surface)

	def setup_doublespeed_info(self):
		self.doublespeed_info_texts = []

		self.doublespeed_info_title_text = textitem.TextItem("Doublespeed", pygame.Color(255, 255, 255))
		self.doublespeed_info_title_text.set_size(6 * settings.GAME_SCALE)
		self.doublespeed_info_title_text.x = (settings.SCREEN_WIDTH - self.doublespeed_info_title_text.get_width()) / 2
		self.doublespeed_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.doublespeed_info_title_text.get_height()
		self.doublespeed_info_texts.append(self.doublespeed_info_title_text)

		self.doublespeed_info_text_1 = textitem.TextItem("This powerup makes your balls move at double", pygame.Color(255, 255, 255))
		self.doublespeed_info_text_1.set_size(6 * settings.GAME_SCALE)
		self.doublespeed_info_text_1.x = self.distance_from_screen_edge
		self.doublespeed_info_text_1.y = self.doublespeed_info_title_text.y + (2 * self.doublespeed_info_text_1.get_height())
		self.doublespeed_info_texts.append(self.doublespeed_info_text_1)

		self.doublespeed_info_text_2 = textitem.TextItem("their original speed", pygame.Color(255, 255, 255))
		self.doublespeed_info_text_2.set_size(6 * settings.GAME_SCALE)
		self.doublespeed_info_text_2.x = self.distance_from_screen_edge
		self.doublespeed_info_text_2.y = self.doublespeed_info_text_1.y + self.doublespeed_info_text_2.get_height()
		self.doublespeed_info_texts.append(self.doublespeed_info_text_2)

		self.doublespeed_info_text_3 = textitem.TextItem("This effect lasts for " + str(freezing.Freezing.duration / 1000) + " seconds", pygame.Color(255, 255, 255))
		self.doublespeed_info_text_3.set_size(6 * settings.GAME_SCALE)
		self.doublespeed_info_text_3.x = self.distance_from_screen_edge
		self.doublespeed_info_text_3.y = self.doublespeed_info_text_2.y + (2 * self.doublespeed_info_text_3.get_height())
		self.doublespeed_info_texts.append(self.doublespeed_info_text_3)

		self.doublespeed_info_text_4 = textitem.TextItem("Multiple instances of speed will stack additively", pygame.Color(255, 255, 255))
		self.doublespeed_info_text_4.set_size(6 * settings.GAME_SCALE)
		self.doublespeed_info_text_4.x = self.distance_from_screen_edge
		self.doublespeed_info_text_4.y = self.doublespeed_info_text_3.y + (2 * self.doublespeed_info_text_4.get_height())
		self.doublespeed_info_texts.append(self.doublespeed_info_text_4)

	def setup_doublespeed_info_transitions(self):
		self.transitions.setup_single_item_transition(self.doublespeed_info_title_text, True, True, False, False)
		self.transitions.setup_single_item_transition(self.doublespeed_info_text_1, True, True, False, False)
		self.transitions.setup_single_item_transition(self.doublespeed_info_text_2, True, True, False, False)
		self.transitions.setup_single_item_transition(self.doublespeed_info_text_3, True, True, False, False)
		self.transitions.setup_single_item_transition(self.doublespeed_info_text_4, True, True, False, False)
		
	def show_doublespeed_info(self, surface):
		for info_text in self.doublespeed_info_texts:
			info_text.draw(surface)

	def setup_multiball_info(self):
		self.multiball_info_texts = []

		self.multiball_info_title_text = textitem.TextItem("Multiball", pygame.Color(255, 255, 255))
		self.multiball_info_title_text.set_size(6 * settings.GAME_SCALE)
		self.multiball_info_title_text.x = (settings.SCREEN_WIDTH - self.multiball_info_title_text.get_width()) / 2
		self.multiball_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.multiball_info_title_text.get_height()
		self.multiball_info_texts.append(self.multiball_info_title_text)

		self.multiball_info_text_1 = textitem.TextItem("This powerup gives you an extra ball that lasts", pygame.Color(255, 255, 255))
		self.multiball_info_text_1.set_size(6 * settings.GAME_SCALE)
		self.multiball_info_text_1.x = self.distance_from_screen_edge
		self.multiball_info_text_1.y = self.multiball_info_title_text.y + (2 * self.multiball_info_text_1.get_height())
		self.multiball_info_texts.append(self.multiball_info_text_1)

		self.multiball_info_text_2 = textitem.TextItem("for " + str(multiball.Multiball.duration / 1000) + " seconds", pygame.Color(255, 255, 255))
		self.multiball_info_text_2.set_size(6 * settings.GAME_SCALE)
		self.multiball_info_text_2.x = self.distance_from_screen_edge
		self.multiball_info_text_2.y = self.multiball_info_text_1.y + self.multiball_info_text_2.get_height()
		self.multiball_info_texts.append(self.multiball_info_text_2)

	def setup_multiball_info_transitions(self):
		self.transitions.setup_single_item_transition(self.multiball_info_title_text, True, True, False, False)
		self.transitions.setup_single_item_transition(self.multiball_info_text_1, True, True, False, False)
		self.transitions.setup_single_item_transition(self.multiball_info_text_2, True, True, False, False)
		
	def show_multiball_info(self, surface):
		for info_text in self.multiball_info_texts:
			info_text.draw(surface)

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
			self.next_screen(self.window_surface, self.main_clock, None, self.came_from_options, self.__class__)
		else:
			# For any other screen we just call it using the normal variables.
			self.next_screen(self.window_surface, self.main_clock)
