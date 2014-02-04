__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import other.debug as debug
import other.useful as useful
import objects.player as player
import objects.powerups.powerup as powerup
import objects.powerups.multiball as multiball
import objects.effects.burning as burning
import objects.effects.freezing as freezing
import objects.effects.charged as charged
import objects.blocks.weak as weakblock
import objects.blocks.normal as normalblock
import objects.blocks.strong as strongblock
import gui.textitem as textitem
import gui.menu as menu
import gui.gridmenu as gridmenu
import gui.imageitem as imageitem
import gui.transition as transition
import gui.traversal as traversal
import settings.settings as settings
import settings.graphics as graphics

# We import any needed game screens here.
import screens

"""

This class is the Help menu screen, accessible from the options menu in the main menu.

It has a gridmenu object that we call help_menu and several items in that gridmenu.
Each item, when clicked, displays information about stuff in the game, like the balls, the paddles and so forth.

We can return to the options menu by pressing the back button.

NOTE!!!!

For some reason, if you keep entering and leaving this menu (and the aboutmenu) lots of times in a row, the game will crash
with an "IOError: unable to read font filename". I haven't been able to fix this bug, and from what I understand it must
have something to do with creating way too many font objects, and the garbage collector has no chance to keep up with
destroying all objects. Or something. I really don't know, but luckily getting to this crash bug is a kind of inane process.

I don't think anyone should ever go in and out of a menu repeatedly... But if they do, well, then I don't know what to do. :(

This class can take an optional "menu_screen_instance" parameter, which if filled with a menu SCREEN instance, that menu screen instance
will have its gameloop() method restarted when this screen ends.

"""
class HelpMenu:

	def __init__(self, window_surface, main_clock, menu_screen_instance = None):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# If we've gotten a main menu instance to return to, then save that.
		self.menu_screen_instance = menu_screen_instance

		# The next screen to be started when the gameloop ends.
		self.next_screen = screens.mainmenu.MainMenu

		# This is a dictionary that contains information linked to certain imageitems.
		self.info_about = {}

		# This is a dictionary that maps transitions methods to all all items.
		self.transition_method = {}

		# This contains the currently active function that displays the currently active information.
		self.active_info = self.show_ball_info

		# A list of all menus, so we can easily register all menus to all menus (so they know to unselect items in other menus and stuff like that).
		self.all_menus = []

		# We create a gridmenu that allows the player to choose what item they want to read more about.
		self.help_menu = gridmenu.GridMenu(9)
		self.all_menus.append(self.help_menu)

		# We setup and add all the necessary items to the help_menu.
		first_item = imageitem.ImageItem("res/help/questionmark.png")
		self.info_about[first_item] = self.show_start_info
		self.transition_method[first_item] = self.setup_start_info_transitions
		self.help_menu.add(first_item, self.view_info)

		temp_item = imageitem.ImageItem("res/ball/ball.png")
		useful.colorize_image(temp_item.image, pygame.Color(255, 0, 0)) # We color this item, since otherwise it would be just gray.
		self.info_about[temp_item] = self.show_ball_info
		self.transition_method[temp_item] = self.setup_ball_info_transitions
		self.help_menu.add(temp_item, self.view_info)

		temp_item = imageitem.ImageItem("res/block/block.png")
		useful.colorize_image(temp_item.image, pygame.Color(255, 0, 0)) # Same here.
		self.info_about[temp_item] = self.show_block_info
		self.transition_method[temp_item] = self.setup_block_info_transitions
		self.help_menu.add(temp_item, self.view_info)

		temp_item = imageitem.ImageItem("res/paddle/paddle.png")
		useful.colorize_image(temp_item.image, pygame.Color(255, 0, 0))	# And here.
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

		temp_item = imageitem.ImageItem("res/powerup/electricity.png")
		self.info_about[temp_item] = self.show_electricity_info
		self.transition_method[temp_item] = self.setup_electricity_info_transitions
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
		self.all_menus.append(self.back_menu)

		# Register all menus with each other.
		for a_menu in self.all_menus:
			a_menu.register_other_menus(self.all_menus)

		# We setup all menu transitions.
		self.transitions = transition.Transition(self.main_clock)
		self.transitions.speed = 1200 * settings.GAME_SCALE
		self.transitions.setup_transition(self.help_menu, True, True, True, False)
		self.transitions.setup_transition(self.back_menu, True, True, False, False)

		# We setup the info items.
		self.distance_from_screen_edge = 6 * settings.GAME_SCALE
		self.font_size = 6 * settings.GAME_SCALE
		self.setup_start_info()
		self.setup_ball_info()
		self.setup_block_info()
		self.setup_paddle_info()
		self.setup_fire_info()
		self.setup_frost_info()
		self.setup_doublespeed_info()
		self.setup_multiball_info()
		self.setup_electricity_info()

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
			pygame.mixer.music.play(-1)

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

	# All these setup_stuff_info and transitions methods are used to setup all the necessary information surface that are then displayed when the
	# appropriate help_menu item is selected.
	# I wish I didn't have to cram everything into this super-sized file... Atleast this "blob-file" is only for one purpose.
	def setup_start_info(self):
		self.start_info_texts = []

		self.start_info_title_text = textitem.TextItem("Starting the Game", pygame.Color(255, 255, 255), 255, self.font_size)
		#self.start_info_title_text.set_size(self.font_size)
		self.start_info_title_text.x = (settings.SCREEN_WIDTH - self.start_info_title_text.get_width()) / 2
		self.start_info_title_text.y = self.help_menu.y + self.help_menu.get_height() + self.start_info_title_text.get_height()
		self.start_info_texts.append(self.start_info_title_text)

		self.start_info_text_1 = textitem.TextItem("In order to start the game navigate to the start", pygame.Color(150, 150, 150), 255, self.font_size)
		#self.start_info_text_1.set_size(self.font_size)
		self.start_info_text_1.x = self.distance_from_screen_edge
		self.start_info_text_1.y = self.start_info_title_text.y + (2 * self.start_info_text_1.get_height())
		self.start_info_texts.append(self.start_info_text_1)

		self.start_info_text_2 = textitem.TextItem("button in the main menu and press the enter key", pygame.Color(255, 255, 255), 255, self.font_size)
		#self.start_info_text_2.set_size(self.font_size)
		self.start_info_text_2.x = self.distance_from_screen_edge
		self.start_info_text_2.y = self.start_info_text_1.y + self.start_info_text_2.get_height()
		self.start_info_texts.append(self.start_info_text_2)

		self.start_info_text_3 = textitem.TextItem("or click it with your left mouse button", pygame.Color(150, 150, 150), 255, self.font_size)
		#self.start_info_text_3.set_size(self.font_size)
		self.start_info_text_3.x = self.distance_from_screen_edge
		self.start_info_text_3.y = self.start_info_text_2.y + self.start_info_text_3.get_height()
		self.start_info_texts.append(self.start_info_text_3)

		self.start_info_text_4 = textitem.TextItem("After that you will reach a preparation menu", pygame.Color(255, 255, 255), 255, self.font_size)
		#self.start_info_text_4.set_size(self.font_size)
		self.start_info_text_4.x = self.distance_from_screen_edge
		self.start_info_text_4.y = self.start_info_text_3.y + (2 * self.start_info_text_4.get_height())
		self.start_info_texts.append(self.start_info_text_4)

		self.start_info_text_5 = textitem.TextItem("Here you must choose " + settings.PLAYER_ONE_NAME + "s color", pygame.Color(150, 150, 150), 255, self.font_size)
		#self.start_info_text_5.set_size(self.font_size)
		self.start_info_text_5.x = self.distance_from_screen_edge
		self.start_info_text_5.y = self.start_info_text_4.y + self.start_info_text_5.get_height()
		self.start_info_texts.append(self.start_info_text_5)

		self.start_info_text_6 = textitem.TextItem("and " + settings.PLAYER_TWO_NAME + "s color", pygame.Color(255, 255, 255), 255, self.font_size)
		#self.start_info_text_6.set_size(self.font_size)
		self.start_info_text_6.x = self.distance_from_screen_edge
		self.start_info_text_6.y = self.start_info_text_5.y + self.start_info_text_6.get_height()
		self.start_info_texts.append(self.start_info_text_6)

		self.start_info_text_7 = textitem.TextItem("You can also choose the amount of rounds you will", pygame.Color(150, 150, 150), 255, self.font_size)
		#self.start_info_text_7.set_size(self.font_size)
		self.start_info_text_7.x = self.distance_from_screen_edge
		self.start_info_text_7.y = self.start_info_text_6.y + (2 * self.start_info_text_7.get_height())
		self.start_info_texts.append(self.start_info_text_7)

		self.start_info_text_8 = textitem.TextItem("play for", pygame.Color(255, 255, 255), 255, self.font_size)
		#self.start_info_text_8.set_size(self.font_size)
		self.start_info_text_8.x = self.distance_from_screen_edge
		self.start_info_text_8.y = self.start_info_text_7.y + self.start_info_text_8.get_height()
		self.start_info_texts.append(self.start_info_text_8)

		self.start_info_text_9 = textitem.TextItem("The buttons at the top of this screen tell you more", pygame.Color(150, 150, 150), 255, self.font_size)
		#self.start_info_text_9.set_size(self.font_size)
		self.start_info_text_9.x = self.distance_from_screen_edge
		self.start_info_text_9.y = self.start_info_text_8.y + (2 * self.start_info_text_9.get_height())
		self.start_info_texts.append(self.start_info_text_9)

		self.start_info_text_10 = textitem.TextItem("Go ahead and click on one", pygame.Color(255, 255, 255), 255, self.font_size)
		#self.start_info_text_10.set_size(self.font_size)
		self.start_info_text_10.x = self.distance_from_screen_edge
		self.start_info_text_10.y = self.start_info_text_9.y + self.start_info_text_10.get_height()
		self.start_info_texts.append(self.start_info_text_10)

	def setup_start_info_transitions(self):
		for item in self.start_info_texts:
			self.transitions.setup_single_item_transition(item, True, True, False, False)

	def show_start_info(self, surface):
		for info_text in self.start_info_texts:
			info_text.draw(surface)

	def setup_ball_info(self):
		self.ball_info_texts = []

		self.ball_info_title_text = textitem.TextItem("Ball", pygame.Color(255, 255, 255), 255, self.font_size)
		self.ball_info_title_text.x = (settings.SCREEN_WIDTH - self.ball_info_title_text.get_width()) / 2
		self.ball_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.ball_info_title_text.get_height()
		self.ball_info_texts.append(self.ball_info_title_text)

		self.ball_info_text_1 = textitem.TextItem("Both players start the game with one ball each", pygame.Color(150, 150, 150), 255, self.font_size)
		self.ball_info_text_1.x = self.distance_from_screen_edge
		self.ball_info_text_1.y = self.ball_info_title_text.y + (2 * self.ball_info_text_1.get_height())
		self.ball_info_texts.append(self.ball_info_text_1)

		self.ball_info_text_2 = textitem.TextItem("Your goal is to destroy your opponents blocks", pygame.Color(255, 255, 255), 255, self.font_size)
		self.ball_info_text_2.x = self.distance_from_screen_edge
		self.ball_info_text_2.y = self.ball_info_text_1.y + self.ball_info_text_2.get_height()
		self.ball_info_texts.append(self.ball_info_text_2)

		self.ball_info_text_3 = textitem.TextItem("while defending your blocks with your paddle", pygame.Color(150, 150, 150), 255, self.font_size)
		self.ball_info_text_3.x = self.distance_from_screen_edge
		self.ball_info_text_3.y = self.ball_info_text_2.y + self.ball_info_text_3.get_height()
		self.ball_info_texts.append(self.ball_info_text_3)

		self.ball_info_text_4 = textitem.TextItem("Balls will deal 10 damage to blocks they hit", pygame.Color(255, 255, 255), 255, self.font_size)
		self.ball_info_text_4.x = self.distance_from_screen_edge
		self.ball_info_text_4.y = self.ball_info_text_3.y + (2 * self.ball_info_text_4.get_height())
		self.ball_info_texts.append(self.ball_info_text_4)

		self.ball_info_text_5 = textitem.TextItem("Your own balls will damage your own blocks", pygame.Color(150, 150, 150), 255, self.font_size)
		self.ball_info_text_5.x = self.distance_from_screen_edge
		self.ball_info_text_5.y = self.ball_info_text_4.y + self.ball_info_text_5.get_height()
		self.ball_info_texts.append(self.ball_info_text_5)

		self.ball_info_text_6 = textitem.TextItem("but only for half the normal damage", pygame.Color(255, 255, 255), 255, self.font_size)
		self.ball_info_text_6.x = self.distance_from_screen_edge
		self.ball_info_text_6.y = self.ball_info_text_5.y + self.ball_info_text_6.get_height()
		self.ball_info_texts.append(self.ball_info_text_6)

		self.ball_info_text_7 = textitem.TextItem("Balls can acquire powerups by touching them", pygame.Color(150, 150, 150), 255, self.font_size)
		self.ball_info_text_7.x = self.distance_from_screen_edge
		self.ball_info_text_7.y = self.ball_info_text_6.y + (2 * self.ball_info_text_7.get_height())
		self.ball_info_texts.append(self.ball_info_text_7)

		self.ball_info_text_8 = textitem.TextItem("Most powerups acquired will affect all your balls", pygame.Color(255, 255, 255), 255, self.font_size)
		self.ball_info_text_8.x = self.distance_from_screen_edge
		self.ball_info_text_8.y = self.ball_info_text_7.y + self.ball_info_text_8.get_height()
		self.ball_info_texts.append(self.ball_info_text_8)

	def setup_ball_info_transitions(self):
		for item in self.ball_info_texts:
			self.transitions.setup_single_item_transition(item, True, True, False, False)

	def show_ball_info(self, surface):
		for info_text in self.ball_info_texts:
			info_text.draw(surface)

	def setup_block_info(self):
		self.block_info_texts = []

		self.block_info_title_text = textitem.TextItem("Block", pygame.Color(255, 255, 255), 255, self.font_size)
		self.block_info_title_text.x = (settings.SCREEN_WIDTH - self.block_info_title_text.get_width()) / 2
		self.block_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.block_info_title_text.get_height()
		self.block_info_texts.append(self.block_info_title_text)

		self.block_info_text_1 = textitem.TextItem("Blocks come in different strengths", pygame.Color(150, 150, 150), 255, self.font_size)
		self.block_info_text_1.x = self.distance_from_screen_edge
		self.block_info_text_1.y = self.block_info_title_text.y + (2 * self.block_info_text_1.get_height())
		self.block_info_texts.append(self.block_info_text_1)

		self.block_info_text_2 = textitem.TextItem("There are three types of blocks", pygame.Color(255, 255, 255), 255, self.font_size)
		self.block_info_text_2.x = self.distance_from_screen_edge
		self.block_info_text_2.y = self.block_info_text_1.y + self.block_info_text_2.get_height()
		self.block_info_texts.append(self.block_info_text_2)

		self.block_info_text_3_image = imageitem.ImageItem("res/block/block_weak.png", pygame.Color(255, 255, 255))
		useful.colorize_image(self.block_info_text_3_image.image, pygame.Color(255, 0, 0))
		self.block_info_text_3_image.x = self.distance_from_screen_edge
		self.block_info_text_3_image.y = self.block_info_text_2.y + (2 * self.block_info_text_2.get_height())
		self.block_info_texts.append(self.block_info_text_3_image)

		self.block_info_text_3 = textitem.TextItem("Weak blocks have " + str(weakblock.WeakBlock.health) + " health", pygame.Color(150, 150, 150), 255, self.font_size)
		self.block_info_text_3.x = self.block_info_text_3_image.x + self.block_info_text_3_image.get_width() + self.distance_from_screen_edge
		self.block_info_text_3.y = self.block_info_text_3_image.y + ((self.block_info_text_3_image.get_height() - self.block_info_text_3.get_height()) / 2)
		self.block_info_texts.append(self.block_info_text_3)

		self.block_info_text_4_image = imageitem.ImageItem("res/block/block.png", pygame.Color(255, 255, 255))
		useful.colorize_image(self.block_info_text_4_image.image, pygame.Color(255, 0, 0))
		self.block_info_text_4_image.x = self.distance_from_screen_edge
		self.block_info_text_4_image.y = self.block_info_text_3.y + (2 * self.block_info_text_2.get_height())
		self.block_info_texts.append(self.block_info_text_4_image)

		self.block_info_text_4 = textitem.TextItem("Normal blocks have " + str(normalblock.NormalBlock.health) + " health", pygame.Color(255, 255, 255), 255, self.font_size)
		self.block_info_text_4.x = self.block_info_text_4_image.x + self.block_info_text_4_image.get_width() + self.distance_from_screen_edge
		self.block_info_text_4.y = self.block_info_text_4_image.y + ((self.block_info_text_4_image.get_height() - self.block_info_text_4.get_height()) / 2)
		self.block_info_texts.append(self.block_info_text_4)

		self.block_info_text_5_image = imageitem.ImageItem("res/block/block_strong.png", pygame.Color(255, 255, 255))
		useful.colorize_image(self.block_info_text_5_image.image, pygame.Color(255, 0, 0))
		self.block_info_text_5_image.x = self.distance_from_screen_edge
		self.block_info_text_5_image.y = self.block_info_text_4.y + (2 * self.block_info_text_2.get_height())
		self.block_info_texts.append(self.block_info_text_5_image)

		self.block_info_text_5 = textitem.TextItem("Strong blocks have " + str(strongblock.StrongBlock.health) + " health", pygame.Color(150, 150, 150), 255, self.font_size)
		self.block_info_text_5.x = self.block_info_text_5_image.x + self.block_info_text_5_image.get_width() + self.distance_from_screen_edge
		self.block_info_text_5.y = self.block_info_text_5_image.y + ((self.block_info_text_5_image.get_height() - self.block_info_text_5.get_height()) / 2)
		self.block_info_texts.append(self.block_info_text_5)

		self.block_info_text_6 = textitem.TextItem("When blocks reach 0 health they break", pygame.Color(255, 255, 255), 255, self.font_size)
		self.block_info_text_6.x = self.distance_from_screen_edge
		self.block_info_text_6.y = self.block_info_text_5_image.y + self.block_info_text_5_image.get_height() + self.block_info_text_6.get_height()
		self.block_info_texts.append(self.block_info_text_6)

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
		self.transitions.setup_single_item_transition(self.block_info_text_6, False, True, False, False)

	def show_block_info(self, surface):
		for info_text in self.block_info_texts:
			info_text.draw(surface)

	def setup_paddle_info(self):
		self.paddle_info_texts = []

		self.paddle_info_title_text = textitem.TextItem("Paddle", pygame.Color(255, 255, 255), 255, self.font_size)
		self.paddle_info_title_text.x = (settings.SCREEN_WIDTH - self.paddle_info_title_text.get_width()) / 2
		self.paddle_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.paddle_info_title_text.get_height()
		self.paddle_info_texts.append(self.paddle_info_title_text)

		self.paddle_info_text_1 = textitem.TextItem("Both players have one paddle each", pygame.Color(150, 150, 150), 255, self.font_size)
		self.paddle_info_text_1.x = self.distance_from_screen_edge
		self.paddle_info_text_1.y = self.paddle_info_title_text.y + (2 * self.paddle_info_text_1.get_height())
		self.paddle_info_texts.append(self.paddle_info_text_1)

		self.paddle_info_text_2 = textitem.TextItem("Steer your paddle to protect your blocks", pygame.Color(255, 255, 255), 255, self.font_size)
		self.paddle_info_text_2.x = self.distance_from_screen_edge
		self.paddle_info_text_2.y = self.paddle_info_text_1.y + self.paddle_info_text_2.get_height()
		self.paddle_info_texts.append(self.paddle_info_text_2)

		self.paddle_info_text_3 = textitem.TextItem(settings.PLAYER_ONE_NAME + " moves up and down with the", pygame.Color(150, 150, 150), 255, self.font_size)
		self.paddle_info_text_3.x = self.distance_from_screen_edge
		self.paddle_info_text_3.y = self.paddle_info_text_2.y + (2 * self.paddle_info_text_3.get_height())
		self.paddle_info_texts.append(self.paddle_info_text_3)

		self.paddle_info_text_4 = textitem.TextItem("W and S keys by default", pygame.Color(255, 255, 255), 255, self.font_size)
		self.paddle_info_text_4.x = self.distance_from_screen_edge
		self.paddle_info_text_4.y = self.paddle_info_text_3.y + self.paddle_info_text_4.get_height()
		self.paddle_info_texts.append(self.paddle_info_text_4)

		self.paddle_info_text_5 = textitem.TextItem(settings.PLAYER_TWO_NAME + " moves up and down with the", pygame.Color(150, 150, 150), 255, self.font_size)
		self.paddle_info_text_5.x = self.distance_from_screen_edge
		self.paddle_info_text_5.y = self.paddle_info_text_4.y + (2 * self.paddle_info_text_5.get_height())
		self.paddle_info_texts.append(self.paddle_info_text_5)

		self.paddle_info_text_6 = textitem.TextItem("UP and DOWN keys by default", pygame.Color(255, 255, 255), 255, self.font_size)
		self.paddle_info_text_6.x = self.distance_from_screen_edge
		self.paddle_info_text_6.y = self.paddle_info_text_5.y + self.paddle_info_text_6.get_height()
		self.paddle_info_texts.append(self.paddle_info_text_6)

		self.paddle_info_text_7 = textitem.TextItem("If your paddle is moving while it collides with a", pygame.Color(150, 150, 150), 255, self.font_size)
		self.paddle_info_text_7.x = self.distance_from_screen_edge
		self.paddle_info_text_7.y = self.paddle_info_text_6.y + (2 * self.paddle_info_text_7.get_height())
		self.paddle_info_texts.append(self.paddle_info_text_7)

		self.paddle_info_text_8 = textitem.TextItem("ball it will cause that ball to change its angle", pygame.Color(255, 255, 255), 255, self.font_size)
		self.paddle_info_text_8.x = self.distance_from_screen_edge
		self.paddle_info_text_8.y = self.paddle_info_text_7.y + self.paddle_info_text_8.get_height()
		self.paddle_info_texts.append(self.paddle_info_text_8)

		self.paddle_info_text_9 = textitem.TextItem("depending on the direction your paddle moved in", pygame.Color(150, 150, 150), 255, self.font_size)
		self.paddle_info_text_9.x = self.distance_from_screen_edge
		self.paddle_info_text_9.y = self.paddle_info_text_8.y + self.paddle_info_text_9.get_height()
		self.paddle_info_texts.append(self.paddle_info_text_9)

		self.paddle_info_text_10 = textitem.TextItem("relative to the angle of that ball", pygame.Color(255, 255, 255), 255, self.font_size)
		self.paddle_info_text_10.x = self.distance_from_screen_edge
		self.paddle_info_text_10.y = self.paddle_info_text_9.y + self.paddle_info_text_10.get_height()
		self.paddle_info_texts.append(self.paddle_info_text_10)

		self.paddle_info_text_11 = textitem.TextItem("This is called spinning the ball", pygame.Color(150, 150, 150), 255, self.font_size)
		self.paddle_info_text_11.x = self.distance_from_screen_edge
		self.paddle_info_text_11.y = self.paddle_info_text_10.y + self.paddle_info_text_11.get_height()
		self.paddle_info_texts.append(self.paddle_info_text_11)

	def setup_paddle_info_transitions(self):
		for item in self.paddle_info_texts:
			self.transitions.setup_single_item_transition(item, True, True, False, False)

	def show_paddle_info(self, surface):
		for info_text in self.paddle_info_texts:
			info_text.draw(surface)

	def setup_fire_info(self):
		self.fire_info_texts = []

		self.fire_info_title_text = textitem.TextItem("Fire", pygame.Color(255, 255, 255), 255, self.font_size)
		self.fire_info_title_text.x = (settings.SCREEN_WIDTH - self.fire_info_title_text.get_width()) / 2
		self.fire_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.fire_info_title_text.get_height()
		self.fire_info_texts.append(self.fire_info_title_text)

		self.fire_info_text_1 = textitem.TextItem("This powerup will make your balls burn", pygame.Color(150, 150, 150), 255, self.font_size)
		self.fire_info_text_1.x = self.distance_from_screen_edge
		self.fire_info_text_1.y = self.fire_info_title_text.y + (2 * self.fire_info_text_1.get_height())
		self.fire_info_texts.append(self.fire_info_text_1)

		self.fire_info_text_2 = textitem.TextItem("for " + str(burning.Burning.duration / 1000) + " seconds", pygame.Color(255, 255, 255), 255, self.font_size)
		self.fire_info_text_2.x = self.distance_from_screen_edge
		self.fire_info_text_2.y = self.fire_info_text_1.y + self.fire_info_text_2.get_height()
		self.fire_info_texts.append(self.fire_info_text_2)

		self.fire_info_text_3 = textitem.TextItem("Any blocks hit by burning balls will also burn", pygame.Color(150, 150, 150), 255, self.font_size)
		self.fire_info_text_3.x = self.distance_from_screen_edge
		self.fire_info_text_3.y = self.fire_info_text_2.y + (2 * self.fire_info_text_3.get_height())
		self.fire_info_texts.append(self.fire_info_text_3)

		self.fire_info_text_4 = textitem.TextItem("taking " + str(int(burning.Burning.damage_per_second)) + " damage per second", pygame.Color(255, 255, 255), 255, self.font_size)
		self.fire_info_text_4.x = self.distance_from_screen_edge
		self.fire_info_text_4.y = self.fire_info_text_3.y + self.fire_info_text_4.get_height()
		self.fire_info_texts.append(self.fire_info_text_4)

		self.fire_info_text_5 = textitem.TextItem("Your balls will not burn your own blocks", pygame.Color(150, 150, 150), 255, self.font_size)
		self.fire_info_text_5.x = self.distance_from_screen_edge
		self.fire_info_text_5.y = self.fire_info_text_4.y + (2 * self.fire_info_text_5.get_height())
		self.fire_info_texts.append(self.fire_info_text_5)

		self.fire_info_text_6 = textitem.TextItem("This effect stacks additively on blocks", pygame.Color(255, 255, 255), 255, self.font_size)
		self.fire_info_text_6.x = self.distance_from_screen_edge
		self.fire_info_text_6.y = self.fire_info_text_5.y + (2 * self.fire_info_text_6.get_height())
		self.fire_info_texts.append(self.fire_info_text_6)

	def setup_fire_info_transitions(self):
		for item in self.fire_info_texts:
			self.transitions.setup_single_item_transition(item, True, True, False, False)

	def show_fire_info(self, surface):
		for info_text in self.fire_info_texts:
			info_text.draw(surface)

	def setup_frost_info(self):
		self.frost_info_texts = []

		self.frost_info_title_text = textitem.TextItem("Frost", pygame.Color(255, 255, 255), 255, self.font_size)
		self.frost_info_title_text.x = (settings.SCREEN_WIDTH - self.frost_info_title_text.get_width()) / 2
		self.frost_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.frost_info_title_text.get_height()
		self.frost_info_texts.append(self.frost_info_title_text)

		self.frost_info_text_1 = textitem.TextItem("This powerup will make your balls ice cold", pygame.Color(150, 150, 150), 255, self.font_size)
		self.frost_info_text_1.x = self.distance_from_screen_edge
		self.frost_info_text_1.y = self.frost_info_title_text.y + (2 * self.frost_info_text_1.get_height())
		self.frost_info_texts.append(self.frost_info_text_1)

		self.frost_info_text_2 = textitem.TextItem("for " + str(freezing.Freezing.duration / 1000) + " seconds", pygame.Color(255, 255, 255), 255, self.font_size)
		self.frost_info_text_2.x = self.distance_from_screen_edge
		self.frost_info_text_2.y = self.frost_info_text_1.y + self.frost_info_text_2.get_height()
		self.frost_info_texts.append(self.frost_info_text_2)

		self.frost_info_text_3 = textitem.TextItem("Your opponents paddle will frozen by your balls", pygame.Color(150, 150, 150), 255, self.font_size)
		self.frost_info_text_3.x = self.distance_from_screen_edge
		self.frost_info_text_3.y = self.frost_info_text_2.y + (2 * self.frost_info_text_3.get_height())
		self.frost_info_texts.append(self.frost_info_text_3)

		self.frost_info_text_4 = textitem.TextItem("and will move at reduced speed while frozen", pygame.Color(255, 255, 255), 255, self.font_size)
		self.frost_info_text_4.x = self.distance_from_screen_edge
		self.frost_info_text_4.y = self.frost_info_text_3.y + self.frost_info_text_4.get_height()
		self.frost_info_texts.append(self.frost_info_text_4)

		self.frost_info_text_5 = textitem.TextItem("Your own paddle will not be frozen by your balls", pygame.Color(150, 150, 150), 255, self.font_size)
		self.frost_info_text_5.x = self.distance_from_screen_edge
		self.frost_info_text_5.y = self.frost_info_text_4.y + (2 * self.frost_info_text_5.get_height())
		self.frost_info_texts.append(self.frost_info_text_5)

		self.frost_info_text_6 = textitem.TextItem("This effect stacks additively on blocks", pygame.Color(255, 255, 255), 255, self.font_size)
		self.frost_info_text_6.x = self.distance_from_screen_edge
		self.frost_info_text_6.y = self.frost_info_text_5.y + (2 * self.frost_info_text_6.get_height())
		self.frost_info_texts.append(self.frost_info_text_6)

	def setup_frost_info_transitions(self):
		for item in self.frost_info_texts:
			self.transitions.setup_single_item_transition(item, True, True, False, False)

	def show_frost_info(self, surface):
		for info_text in self.frost_info_texts:
			info_text.draw(surface)

	def setup_doublespeed_info(self):
		self.doublespeed_info_texts = []

		self.doublespeed_info_title_text = textitem.TextItem("Doublespeed", pygame.Color(255, 255, 255), 255, self.font_size)
		self.doublespeed_info_title_text.x = (settings.SCREEN_WIDTH - self.doublespeed_info_title_text.get_width()) / 2
		self.doublespeed_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.doublespeed_info_title_text.get_height()
		self.doublespeed_info_texts.append(self.doublespeed_info_title_text)

		self.doublespeed_info_text_1 = textitem.TextItem("This powerup makes your balls move at double", pygame.Color(150, 150, 150), 255, self.font_size)
		self.doublespeed_info_text_1.x = self.distance_from_screen_edge
		self.doublespeed_info_text_1.y = self.doublespeed_info_title_text.y + (2 * self.doublespeed_info_text_1.get_height())
		self.doublespeed_info_texts.append(self.doublespeed_info_text_1)

		self.doublespeed_info_text_2 = textitem.TextItem("their original speed", pygame.Color(255, 255, 255), 255, self.font_size)
		self.doublespeed_info_text_2.x = self.distance_from_screen_edge
		self.doublespeed_info_text_2.y = self.doublespeed_info_text_1.y + self.doublespeed_info_text_2.get_height()
		self.doublespeed_info_texts.append(self.doublespeed_info_text_2)

		self.doublespeed_info_text_3 = textitem.TextItem("This effect lasts for " + str(freezing.Freezing.duration / 1000) + " seconds", pygame.Color(150, 150, 150), 255, self.font_size)
		self.doublespeed_info_text_3.x = self.distance_from_screen_edge
		self.doublespeed_info_text_3.y = self.doublespeed_info_text_2.y + (2 * self.doublespeed_info_text_3.get_height())
		self.doublespeed_info_texts.append(self.doublespeed_info_text_3)

		self.doublespeed_info_text_4 = textitem.TextItem("Multiple instances of speed will stack additively", pygame.Color(255, 255, 255), 255, self.font_size)
		self.doublespeed_info_text_4.x = self.distance_from_screen_edge
		self.doublespeed_info_text_4.y = self.doublespeed_info_text_3.y + (2 * self.doublespeed_info_text_4.get_height())
		self.doublespeed_info_texts.append(self.doublespeed_info_text_4)

	def setup_doublespeed_info_transitions(self):
		for item in self.doublespeed_info_texts:
			self.transitions.setup_single_item_transition(item, True, True, False, False)
		
	def show_doublespeed_info(self, surface):
		for info_text in self.doublespeed_info_texts:
			info_text.draw(surface)

	def setup_multiball_info(self):
		self.multiball_info_texts = []

		self.multiball_info_title_text = textitem.TextItem("Multiball", pygame.Color(255, 255, 255), 255, self.font_size)
		self.multiball_info_title_text.x = (settings.SCREEN_WIDTH - self.multiball_info_title_text.get_width()) / 2
		self.multiball_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.multiball_info_title_text.get_height()
		self.multiball_info_texts.append(self.multiball_info_title_text)

		self.multiball_info_text_1 = textitem.TextItem("This powerup gives you an extra ball that lasts", pygame.Color(150, 150, 150), 255, self.font_size)
		self.multiball_info_text_1.x = self.distance_from_screen_edge
		self.multiball_info_text_1.y = self.multiball_info_title_text.y + (2 * self.multiball_info_text_1.get_height())
		self.multiball_info_texts.append(self.multiball_info_text_1)

		self.multiball_info_text_2 = textitem.TextItem("for " + str(multiball.Multiball.duration / 1000) + " seconds", pygame.Color(255, 255, 255), 255, self.font_size)
		self.multiball_info_text_2.x = self.distance_from_screen_edge
		self.multiball_info_text_2.y = self.multiball_info_text_1.y + self.multiball_info_text_2.get_height()
		self.multiball_info_texts.append(self.multiball_info_text_2)

		self.multiball_info_text_3 = textitem.TextItem("These balls work the same as regular balls", pygame.Color(150, 150, 150), 255, self.font_size)
		self.multiball_info_text_3.x = self.distance_from_screen_edge
		self.multiball_info_text_3.y = self.multiball_info_text_2.y + (2 * self.multiball_info_text_3.get_height())
		self.multiball_info_texts.append(self.multiball_info_text_3)

		self.multiball_info_text_4 = textitem.TextItem("but look slightly different", pygame.Color(255, 255, 255), 255, self.font_size)
		self.multiball_info_text_4.x = self.distance_from_screen_edge
		self.multiball_info_text_4.y = self.multiball_info_text_3.y + self.multiball_info_text_4.get_height()
		self.multiball_info_texts.append(self.multiball_info_text_4)

	def setup_multiball_info_transitions(self):
		for item in self.multiball_info_texts:
			self.transitions.setup_single_item_transition(item, True, True, False, False)
		
	def show_multiball_info(self, surface):
		for info_text in self.multiball_info_texts:
			info_text.draw(surface)

	def setup_electricity_info(self):
		self.electricity_info_texts = []

		self.electricity_info_title_text = textitem.TextItem("Electricity", pygame.Color(255, 255, 255), 255, self.font_size)
		self.electricity_info_title_text.x = (settings.SCREEN_WIDTH - self.electricity_info_title_text.get_width()) / 2
		self.electricity_info_title_text.y = self.help_menu.y + + self.help_menu.get_height() + self.electricity_info_title_text.get_height()
		self.electricity_info_texts.append(self.electricity_info_title_text)

		self.electricity_info_text_1 = textitem.TextItem("This powerup makes the ball that touches it", pygame.Color(150, 150, 150), 255, self.font_size)
		self.electricity_info_text_1.x = self.distance_from_screen_edge
		self.electricity_info_text_1.y = self.electricity_info_title_text.y + (2 * self.electricity_info_text_1.get_height())
		self.electricity_info_texts.append(self.electricity_info_text_1)

		self.electricity_info_text_2 = textitem.TextItem("electrified for " + str(charged.Charged.duration / 1000) + " seconds", pygame.Color(255, 255, 255), 255, self.font_size)
		self.electricity_info_text_2.x = self.distance_from_screen_edge
		self.electricity_info_text_2.y = self.electricity_info_text_1.y + self.electricity_info_text_2.get_height()
		self.electricity_info_texts.append(self.electricity_info_text_2)

		self.electricity_info_text_3 = textitem.TextItem("When an electrified ball hits an enemy block", pygame.Color(150, 150, 150), 255, self.font_size)
		self.electricity_info_text_3.x = self.distance_from_screen_edge
		self.electricity_info_text_3.y = self.electricity_info_text_2.y + (2 * self.electricity_info_text_3.get_height())
		self.electricity_info_texts.append(self.electricity_info_text_3)

		self.electricity_info_text_4 = textitem.TextItem("that block and blocks around it take damage", pygame.Color(255, 255, 255), 255, self.font_size)
		self.electricity_info_text_4.x = self.distance_from_screen_edge
		self.electricity_info_text_4.y = self.electricity_info_text_3.y + self.electricity_info_text_4.get_height()
		self.electricity_info_texts.append(self.electricity_info_text_4)

		self.electricity_info_text_5 = textitem.TextItem("After that the electricity effect disappears", pygame.Color(150, 150, 150), 255, self.font_size)
		self.electricity_info_text_5.x = self.distance_from_screen_edge
		self.electricity_info_text_5.y = self.electricity_info_text_4.y + self.electricity_info_text_5.get_height()
		self.electricity_info_texts.append(self.electricity_info_text_5)

	def setup_electricity_info_transitions(self):
		for item in self.electricity_info_texts:
			self.transitions.setup_single_item_transition(item, True, True, False, False)
		
	def show_electricity_info(self, surface):
		for info_text in self.electricity_info_texts:
			info_text.draw(surface)

	def back(self, item):
		# Simply moves back to the main menu.
		self.next_screen = screens.mainmenu.MainMenu
		self.done = True

	def gameloop(self):
		self.done = False
		while not self.done:
			# Constrain the game to a set maximum amount of FPS, and update the delta time value.
			self.main_clock.tick(graphics.MAX_FPS)

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
					traversal.traverse_menus(event, self.all_menus)

			# We update and draw the menu and the information.
			self.show_menu_and_info()

			if settings.DEBUG_MODE:
				# Display various debug information.
				debug.Debug.display(self.window_surface, self.main_clock)

			# We have to update the display if we want anything we just did to actually display.
			pygame.display.update()

		# The gameloop is over, so we either start the next screen or quit the game.
		self.on_exit()

	def show_menu_and_info(self):
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
			# If we have a main menu instance still going, then start that. Otherwise just start the main menu screen as normal.
			if self.menu_screen_instance != None:
				self.menu_screen_instance.gameloop()
			else:
				self.next_screen(self.window_surface, self.main_clock, None)
		else:
			# For any other screen we just call it using the normal variables.
			self.next_screen(self.window_surface, self.main_clock)
