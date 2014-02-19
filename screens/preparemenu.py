__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import objects.player as player
import objects.powerups.powerup as powerup
import gui.textitem as textitem
import gui.listmenu as listmenu
import gui.gridmenu as gridmenu
import gui.item as item
import gui.choiceitem as choiceitem
import gui.imageitem as imageitem
import screens.toast as toast
import settings.settings as settings
import screens.scene as scene
import screens.game as game
import screens

"""

This class is the preparation screen that the players encounter before the game can start. Here they must choose their
respective colors, and they can also pick the number of rounds they want to play. Two players cannot pick the same color,
and this class handles this.

This class is also responsible for creating the two player objects that are then passed around (until the game returns
to the main menu).

"""

class PrepareMenu(scene.Scene):

	def __init__(self, window_surface, main_clock):
		# Call the superconstructor.
		scene.Scene.__init__(self, window_surface, main_clock)

		# These are the connected and active joysticks.
		self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

		# The next screen to be started when the gameloop ends.
		self.next_screen = game.Game
		self.player_one_color = None
		self.player_two_color = None
		self.player_one_ai = None
		self.player_two_ai = None

		# Configure the GUI.
		distance_from_screen_edge = 9 * settings.GAME_SCALE

		# We create a gridmenu that allows the player to select the number of rounds they want to play.
		self.number_of_rounds_menu = gridmenu.GridMenu(5)

		# We set the default number of rounds to 1.
		temp_item = choiceitem.ChoiceItem(1)
		self.rounds(temp_item)

		# Add that item, and the other items to the menu.
		self.number_of_rounds_menu.add(temp_item, self.rounds)
		self.number_of_rounds_menu.add(choiceitem.ChoiceItem(3), self.rounds)
		self.number_of_rounds_menu.add(choiceitem.ChoiceItem(5), self.rounds)
		self.number_of_rounds_menu.add(choiceitem.ChoiceItem(7), self.rounds)
		self.number_of_rounds_menu.add(choiceitem.ChoiceItem(9), self.rounds)
		self.number_of_rounds_menu.x = (settings.SCREEN_WIDTH - self.number_of_rounds_menu.get_width()) / 2.0
		self.number_of_rounds_menu.y = distance_from_screen_edge * 3
		self.menu_list.append(self.number_of_rounds_menu)

		# The text displayed over the rounds menu.
		self.number_of_rounds_text = textitem.TextItem("Rounds", pygame.Color(255, 255, 255))
		self.number_of_rounds_text.x = (settings.SCREEN_WIDTH - self.number_of_rounds_text.get_width()) / 2.0
		self.number_of_rounds_text.y = self.number_of_rounds_menu.y - (self.number_of_rounds_text.get_height() * 2)

		# The color menu for player one.
		self.color_menu_one = self.setup_color_menu(self.color_one)
		self.ai_menu_one = self.setup_ai_menu(self.ai_one)

		ai_menu_offset = self.color_menu_one.offset * 2

		self.color_menu_one.x = (settings.SCREEN_WIDTH - self.color_menu_one.get_width() - self.ai_menu_one.get_width() - ai_menu_offset) / 5.0
		self.color_menu_one.y = settings.SCREEN_HEIGHT / 2.0

		self.ai_menu_one.x = self.color_menu_one.x + self.color_menu_one.get_width() + ai_menu_offset
		self.ai_menu_one.y = self.color_menu_one.y

		self.menu_list.append(self.color_menu_one)
		self.menu_list.append(self.ai_menu_one)

		# The text above the color menu for player one.
		self.player_one_text = textitem.TextItem(settings.PLAYER_ONE_NAME, pygame.Color(255, 255, 255))
		self.player_one_text.x = self.color_menu_one.x + (((self.color_menu_one.get_width() + self.ai_menu_one.get_width() + ai_menu_offset) - self.player_one_text.get_width()) / 2.0)
		self.player_one_text.y = self.color_menu_one.y - (self.player_one_text.get_height() * 2)
		
		# The color menu for player two.
		self.color_menu_two = self.setup_color_menu(self.color_two)
		self.ai_menu_two = self.setup_ai_menu(self.ai_two)

		ai_menu_offset = self.color_menu_two.offset * 2

		self.color_menu_two.x = settings.SCREEN_WIDTH - ((settings.SCREEN_WIDTH - self.color_menu_two.get_width() - self.ai_menu_two.get_width() - ai_menu_offset) / 5.0) - self.color_menu_two.get_width()
		self.color_menu_two.y = settings.SCREEN_HEIGHT / 2.0

		self.ai_menu_two.x = self.color_menu_two.x - self.ai_menu_two.get_width() - self.color_menu_two.offset * 2
		self.ai_menu_two.y = self.color_menu_two.y

		self.menu_list.append(self.color_menu_two)
		self.menu_list.append(self.ai_menu_two)

		# The text above the color menu for player two.
		self.player_two_text = textitem.TextItem(settings.PLAYER_TWO_NAME, pygame.Color(255, 255, 255))
		self.player_two_text.x = self.ai_menu_two.x + (((self.color_menu_two.get_width() + self.ai_menu_two.get_width() + ai_menu_offset) - self.player_two_text.get_width()) / 2.0)
		self.player_two_text.y = self.color_menu_two.y - (self.player_two_text.get_height() * 2)

		# The back button, displayed in the bottom-left corner of the screen.
		back_button = textitem.TextItem("Back")
		self.back_menu = listmenu.ListMenu()
		self.back_menu.x = distance_from_screen_edge + (back_button.get_width() / 2.0)
		self.back_menu.y = settings.SCREEN_HEIGHT - (2 * back_button.get_height())
		self.back_menu.add(back_button, self.back)
		self.back_menu.items[0].selected = True
		self.menu_list.append(self.back_menu)
		
		# The start button, displayed in the bottom-right corner of the screen.
		start_button = textitem.TextItem("Start")
		self.start_menu = listmenu.ListMenu()
		self.start_menu.x = settings.SCREEN_WIDTH - distance_from_screen_edge - (start_button.get_width() / 2.0)
		self.start_menu.y = settings.SCREEN_HEIGHT - (2 * start_button.get_height())
		self.start_menu.add(start_button, self.start)
		self.menu_list.append(self.start_menu)

		# Register all menus with each other.
		for a_menu in self.menu_list:
			a_menu.register_other_menus(self.menu_list)

		# We setup all menu transition.
		self.transition.setup_transition(self.number_of_rounds_menu, True, True, False, False)
		self.transition.setup_single_item_transition(self.number_of_rounds_text, True, True, True, False)
		self.transition.setup_transition(self.color_menu_one, True, False, False, True)
		self.transition.setup_transition(self.ai_menu_one, True, False, False, True)
		self.transition.setup_single_item_transition(self.player_one_text, True, False, True, False)
		self.transition.setup_transition(self.color_menu_two, False, True, False, True)
		self.transition.setup_transition(self.ai_menu_two, True, False, False, True)
		self.transition.setup_single_item_transition(self.player_two_text, False, True, True, False)
		self.transition.setup_transition(self.back_menu, True, False, False, True)
		self.transition.setup_transition(self.start_menu, False, True, False, True)

		# And finally, we start the gameloop!
		self.gameloop()

	def setup_color_menu(self, function):
		# Creates a gridmenu and adds all standard color items to that menu.
		color_menu = gridmenu.GridMenu()
		self.setup_color_items(color_menu, function)
		return color_menu

	def setup_color_items(self, grid_menu, function):
		# Adds all standard color items to the given grid_menu.
		grid_menu.add(item.Item(pygame.Color(255, 0, 0, 255)), function)
		grid_menu.add(item.Item(pygame.Color(0, 255, 0, 255)), function)
		grid_menu.add(item.Item(pygame.Color(0, 0, 255, 255)), function)
		grid_menu.add(item.Item(pygame.Color(255, 255, 0, 255)), function)
		grid_menu.add(item.Item(pygame.Color(255, 0, 255, 255)), function)
		grid_menu.add(item.Item(pygame.Color(0, 255, 255, 255)), function)

	def color_one(self, item):
		# Figures out what color to set player one's color to.
		self.player_one_color = self.toggle_color(item, self.color_menu_one, self.color_menu_two)

	def color_two(self, item):
		# Figures out what color to set player two's color to.
		self.player_two_color = self.toggle_color(item, self.color_menu_two, self.color_menu_one)

	def toggle_color(self, item, primary_menu, secondary_menu):
		# Figure out what item is chosen.
		chosen_item = None
		for menu_item in primary_menu.items:
			if menu_item.chosen:
				chosen_item = menu_item
				break

		if chosen_item is None:
			# If there is no chosen item and the item is available, set the selected item as chosen and set it's match on the secondary menu as disabled.
			if not item.disabled:
				item.chosen = True
				secondary_menu.items[primary_menu.items.index(item)].disabled = True
				return item.color
		elif chosen_item is item:
			# If the chosen item is the same as the selected item, set that item as not chosen and restore the availability
			# of the matching item on the secondary menu.
			chosen_item.chosen = False
			secondary_menu.items[primary_menu.items.index(item)].disabled = False
			return None
		elif not chosen_item is item:
			# If the chosen item isn't the same as the selected item, check if it is available first.
			if not item.disabled:
				# If the item is available, set the chosen item to not be chosen, and set the selected item to be chosen.
				# Also fix the availability, ofcourse.
				chosen_item.chosen = False
				secondary_menu.items[primary_menu.items.index(chosen_item)].disabled = False
				item.chosen = True
				secondary_menu.items[primary_menu.items.index(item)].disabled = True
				# We also return the color of the newly chosen item.
				return item.color
			# If the item is unavailible, we return the color of the chosen item instead.
			return chosen_item.color

	def setup_ai_menu(self, function):
		ai_menu = gridmenu.GridMenu(1)
		self.setup_ai_items(ai_menu, function)
		return ai_menu

	def setup_ai_items(self, grid_menu, function):
		item = imageitem.ImageItem("res/ai/ai_easy.png")
		item.value = 1
		grid_menu.add(item, function)
		item = imageitem.ImageItem("res/ai/ai_hard.png")
		item.value = 2
		grid_menu.add(item, function)

	def ai_one(self, item):
		self.player_one_ai = self.choose_item_from_menu(item, self.ai_menu_one, True)

	def ai_two(self, item):
		self.player_two_ai = self.choose_item_from_menu(item, self.ai_menu_two, True)

	def rounds(self, item):
		# Set the number of rounds to the value of the selected item.
		self.number_of_rounds = self.choose_item_from_menu(item, self.number_of_rounds_menu)

	def choose_item_from_menu(self, item, grid_menu, can_unchoose = False):
		# Figure out what item is the chosen item.
		chosen_item = None
		for menu_item in grid_menu.items:
			if menu_item.chosen:
				chosen_item = menu_item
				break

		if chosen_item is None:
			# If there isn't a chosen item, set the selected item as the chosen item
			item.chosen = True
		elif chosen_item is item and can_unchoose:
			# Unchose the chosen item.
			chosen_item.chosen = False
			return 0 # There is no value to be returned, so we simply return 0.
		elif not chosen_item is item:
			# If the chosen item and the selected item doesn't match, unchose the old chosen item and set the selected 
			# item as chosen instead.
			chosen_item.chosen = False
			item.chosen = True

		# At last, return the value of the selected item.
		return item.value

	def start(self, item = None):
		if not self.player_one_color is None and not self.player_two_color is None:
			if self.player_one_ai is None:
				self.player_one_ai = 0
			if self.player_two_ai is None:
				self.player_two_ai = 0

			# The game can only be started if both players have picked a color.
			pygame.mixer.music.stop()
			self.done = True
		else:
			# If a player haven't picked his or hers color, we show a toast that informs the players of this.
			toast.Toast(self.window_surface, self.main_clock, "Both players need to pick a color before the game can begin.")

	def back(self, item = None):
		# Simply moves back to the main menu.
		self.next_screen = screens.mainmenu.MainMenu
		self.done = True

	def event(self, event):
		if (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == JOYBUTTONDOWN and event.button in settings.JOY_BUTTON_BACK):
			# If the escape key is pressed, we go back to the main menu.
			self.back()

	def update(self):
		# Handle all transition.
		self.transition.update(self.main_clock)

		# Update all menus and items.
		self.number_of_rounds_menu.update(self.main_clock)
		self.color_menu_one.update(self.main_clock)
		self.color_menu_two.update(self.main_clock)
		self.ai_menu_one.update(self.main_clock)
		self.ai_menu_two.update(self.main_clock)
		self.back_menu.update(self.main_clock)
		self.start_menu.update(self.main_clock)

	def draw(self):
		# Every frame begins by filling the whole screen with the background color.
		self.window_surface.fill(settings.BACKGROUND_COLOR)

		# Draw the number of rounds menu.
		self.number_of_rounds_menu.draw(self.window_surface)
		self.number_of_rounds_text.draw(self.window_surface)
		
		# Draw the menus for player one.
		self.color_menu_one.draw(self.window_surface)
		self.player_one_text.draw(self.window_surface)
		self.ai_menu_one.draw(self.window_surface)

		# Draw the menus for player two.
		self.color_menu_two.draw(self.window_surface)
		self.player_two_text.draw(self.window_surface)
		self.ai_menu_two.draw(self.window_surface)

		# Draw the back and start menus.
		self.back_menu.draw(self.window_surface)
		self.start_menu.draw(self.window_surface)

	def on_exit(self):
		if self.next_screen is game.Game:
			# If we're going to start the game, we first create both players.
			joystick_count = pygame.joystick.get_count()
			if joystick_count == 0:
				player_one = self.create_player_one(self.player_one_color)
				player_two = self.create_player_two(self.player_two_color)
			elif joystick_count == 1:
				player_one = self.create_player_one(self.player_one_color, gamepad_id = 0)
				player_two = self.create_player_two(self.player_two_color)
			elif joystick_count == 2:
				player_one = self.create_player_one(self.player_one_color, gamepad_id = 0)
				player_two = self.create_player_two(self.player_two_color, gamepad_id = 1)

			# We also create and setup the score.
			score = {}
			score[player_one] = 0
			score[player_two] = 0

			# And finally, we start the game!
			self.next_screen(self.window_surface, self.main_clock, player_one, player_two, self.number_of_rounds, score)
		elif not self.next_screen is None:
			# For any other screen we just call it using the normal variables.
			self.next_screen(self.window_surface, self.main_clock)

		# Otherwise, we just let this scene end.

	def create_player_one(self, color, **kwargs):
		# Creates player one, and sets the position of the player to the top-left corner of the screen.
		# This is where the powerups the player collects will display.
		x = powerup.Powerup.width / 2
		y = powerup.Powerup.height / 2
		name = settings.PLAYER_ONE_NAME
		key_up = settings.PLAYER_ONE_KEY_UP
		key_down = settings.PLAYER_ONE_KEY_DOWN
		key_unleash_energy = settings.PLAYER_ONE_KEY_UNLEASH_ENERGY
		joy_unleash_energy = settings.PLAYER_ONE_JOY_UNLEASH_ENERGY
		player_one = player.Player(x, y, name, key_up, key_down, key_unleash_energy, joy_unleash_energy, kwargs.get("gamepad_id", None), color, self.player_one_ai)
		return player_one

	def create_player_two(self, color, **kwargs):
		# Creates player two, and sets the position of the player to the bottom-right corner of the screen.
		# This is where the powerups the player collects will display.
		x = settings.SCREEN_WIDTH - (powerup.Powerup.width / 2) - powerup.Powerup.width
		y = settings.SCREEN_HEIGHT - (powerup.Powerup.height / 2) - powerup.Powerup.height
		name = settings.PLAYER_TWO_NAME
		key_up = settings.PLAYER_TWO_KEY_UP
		key_down = settings.PLAYER_TWO_KEY_DOWN
		key_unleash_energy = settings.PLAYER_TWO_KEY_UNLEASH_ENERGY
		joy_unleash_energy = settings.PLAYER_TWO_JOY_UNLEASH_ENERGY
		player_two = player.Player(x, y, name, key_up, key_down, key_unleash_energy, joy_unleash_energy, kwargs.get("gamepad_id", None), color, self.player_two_ai)
		return player_two