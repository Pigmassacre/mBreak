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
import os

"""
This class is the preparation screen that the players encounter before the game can start. Here they must choose their
respective characters, and they can also pick the number of rounds they want to play. Two players cannot pick the same character,
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
		self.player_one_character = None
		self.player_two_character = None
		self.player_one_ai = None
		self.player_two_ai = None

		# Animation state for preview images
		self.animation_duration = 0.15  # Animation duration in seconds
		self.p1_preview_alpha = 0
		self.p2_preview_alpha = 0
		self.p1_preview_offset = 30  # Small offset to the left
		self.p2_preview_offset = -30  # Small offset to the right
		self.p1_animation_time = 0
		self.p2_animation_time = 0

		# Character color mappings
		self.character_colors = {
			"red": pygame.Color(255, 0, 0),
			"green": pygame.Color(0, 255, 0),
			"blue": pygame.Color(0, 0, 255),
			"yellow": pygame.Color(255, 255, 0),
			"magenta": pygame.Color(255, 0, 255),
			"cyan": pygame.Color(0, 255, 255)
		}

		# Configure the GUI.
		distance_from_screen_edge = 9

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

		# The character menu for player one.
		self.character_menu_one = self.setup_character_menu(self.character_one, False)
		self.ai_menu_one = self.setup_ai_menu(self.ai_one)

		ai_menu_offset = 20

		self.character_menu_one.x = (settings.SCREEN_WIDTH - self.character_menu_one.get_width() - self.ai_menu_one.get_width() - ai_menu_offset) / 5.0
		self.character_menu_one.y = settings.SCREEN_HEIGHT / 2.0

		self.ai_menu_one.x = self.character_menu_one.x + self.character_menu_one.get_width() + ai_menu_offset
		self.ai_menu_one.y = self.character_menu_one.y

		self.menu_list.append(self.character_menu_one)
		self.menu_list.append(self.ai_menu_one)

		# The character menu for player two.
		self.character_menu_two = self.setup_character_menu(self.character_two, True)
		self.ai_menu_two = self.setup_ai_menu(self.ai_two)

		self.character_menu_two.x = settings.SCREEN_WIDTH - ((settings.SCREEN_WIDTH - self.character_menu_two.get_width() - self.ai_menu_two.get_width() - ai_menu_offset) / 5.0) - self.character_menu_two.get_width()
		self.character_menu_two.y = settings.SCREEN_HEIGHT / 2.0

		self.ai_menu_two.x = self.character_menu_two.x - self.ai_menu_two.get_width() - ai_menu_offset
		self.ai_menu_two.y = self.character_menu_two.y

		self.menu_list.append(self.character_menu_two)
		self.menu_list.append(self.ai_menu_two)

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
		self.transition.setup_transition(self.character_menu_one, True, False, False, True)
		self.transition.setup_transition(self.ai_menu_one, True, False, False, True)
		self.transition.setup_transition(self.character_menu_two, False, True, False, True)
		self.transition.setup_transition(self.ai_menu_two, True, False, False, True)
		self.transition.setup_transition(self.back_menu, True, False, False, True)
		self.transition.setup_transition(self.start_menu, False, True, False, True)

		# And finally, we start the gameloop!
		self.gameloop()

	def setup_character_menu(self, function, is_player_two=False):
		# Creates a grid menu for character selection (2 rows x 3 columns)
		character_menu = gridmenu.GridMenu(3)  # 3 columns
		self.setup_character_items(character_menu, function, is_player_two)
		return character_menu

	def setup_character_items(self, grid_menu, function, is_player_two):
		# Add 6 different character items to the grid menu
		characters = ["red", "green", "blue", "yellow", "magenta", "cyan"]
		
		for character in characters:
			# Use thumbnail for menu item
			thumbnail_path = os.path.join("res", "character", "thumbnail", f"{character}.png")
			# If thumbnail doesn't exist, fall back to regular image
			if not os.path.exists(thumbnail_path):
				thumbnail_path = os.path.join("res", "character", f"{character}.png")
			character_item = imageitem.ImageItem(thumbnail_path)
			
			# Flip the sprite if this is player two's menu
			if is_player_two:
				character_item.image = pygame.transform.flip(character_item.image, True, False)
			
			character_item.character = character
			character_item.color = self.character_colors[character]
			grid_menu.add(character_item, function)

	def character_one(self, item):
		# Check if this character is already selected by player two
		if self.player_two_character == item.character:
			return  # Cannot select a character that's already chosen
		
		# Set player one's character to the selected character
		self.player_one_character = item.character
		# Reset animation values when character changes
		self.p1_preview_alpha = 0
		self.p1_preview_offset = 30  # Reset to initial offset
		self.p1_animation_time = 0  # Reset animation time
		
		# Update disabled states in player two's menu
		self.update_character_menu_states()

	def character_two(self, item):
		# Check if this character is already selected by player one
		if self.player_one_character == item.character:
			return  # Cannot select a character that's already chosen
		
		# Set player two's character to the selected character
		self.player_two_character = item.character
		# Reset animation values when character changes
		self.p2_preview_alpha = 0
		self.p2_preview_offset = -30  # Reset to initial offset
		self.p2_animation_time = 0  # Reset animation time
		
		# Update disabled states in player one's menu
		self.update_character_menu_states()

	def update_character_menu_states(self):
		# Update player one's menu
		for item in self.character_menu_one.items:
			item.disabled = (self.player_two_character == item.character)

		# Update player two's menu
		for item in self.character_menu_two.items:
			item.disabled = (self.player_one_character == item.character)

	def setup_ai_menu(self, function):
		ai_menu = gridmenu.GridMenu(1)
		self.setup_ai_items(ai_menu, function)
		return ai_menu

	def setup_ai_items(self, grid_menu, function):
		# Easy difficulty
		item = imageitem.ImageItem("res/ai/ai_easy.png")
		item.value = 1
		grid_menu.add(item, function)
		
		# Medium difficulty
		item = imageitem.ImageItem("res/ai/ai_medium.png")
		item.value = 2
		grid_menu.add(item, function)
		
		# Hard difficulty
		item = imageitem.ImageItem("res/ai/ai_hard.png")
		item.value = 3
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
			# If there isn't a chosen item, set the selected item as the chosen item.
			item.chosen = True
			if hasattr(item, "value"):
				return item.value
			elif hasattr(item, "character"):
				return item.character
			return None
		elif chosen_item is item:
			# If the chosen item is clicked again, unselect it.
			if can_unchoose:
				chosen_item.chosen = False
				return None
			return chosen_item.value if hasattr(chosen_item, "value") else chosen_item.character
		else:
			# If a different item is chosen, unselect the old one and select the new one.
			chosen_item.chosen = False
			item.chosen = True
			if hasattr(item, "value"):
				return item.value
			elif hasattr(item, "character"):
				return item.character
			return None

	def start(self, item = None):
		# We need both players to have selected a character.
		if self.player_one_character is None or self.player_two_character is None:
			toast.Toast(self.window_surface, self.main_clock, "Both players must select a character!")
			return

		# Set the next screen and exit
		self.next_screen = game.Game
		self.done = True

	def back(self, item = None):
		# Simply moves back to the main menu.
		self.next_screen = screens.mainmenu.MainMenu
		self.done = True

	def event(self, event):
		if (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == JOYBUTTONDOWN and event.button in settings.JOY_BUTTON_BACK):
			# If the escape key or back button on gamepad is pressed, we go back to the main menu.
			self.back()

	def update(self):
		# Handle all transition.
		self.transition.update(self.main_clock)

		# Update all menus.
		self.number_of_rounds_menu.update(self.main_clock)
		self.character_menu_one.update(self.main_clock)
		self.character_menu_two.update(self.main_clock)
		self.ai_menu_one.update(self.main_clock)
		self.ai_menu_two.update(self.main_clock)
		self.back_menu.update(self.main_clock)
		self.start_menu.update(self.main_clock)

		# Get delta time in seconds
		dt = self.main_clock.get_time() / 1000.0

		# Update preview animations
		if self.player_one_character:
			# Update animation time
			self.p1_animation_time = min(self.animation_duration, self.p1_animation_time + dt)
			# Calculate progress (0 to 1)
			progress = self.p1_animation_time / self.animation_duration
			# Apply to both alpha and position
			self.p1_preview_alpha = int(255 * progress)
			self.p1_preview_offset = max(0, 30 * (1 - progress))

		if self.player_two_character:
			# Update animation time
			self.p2_animation_time = min(self.animation_duration, self.p2_animation_time + dt)
			# Calculate progress (0 to 1)
			progress = self.p2_animation_time / self.animation_duration
			# Apply to both alpha and position
			self.p2_preview_alpha = int(255 * progress)
			self.p2_preview_offset = min(0, -30 * (1 - progress))

	def draw(self):
		# Every frame begins by filling the whole screen with the background color.
		self.window_surface.fill(settings.BACKGROUND_COLOR)

		# Draw the rounds menu at the top
		self.number_of_rounds_text.draw(self.window_surface)
		self.number_of_rounds_menu.draw(self.window_surface)

		# Draw player one's menus on the left
		self.character_menu_one.draw(self.window_surface)
		self.ai_menu_one.draw(self.window_surface)

		# Draw player two's menus on the right
		self.character_menu_two.draw(self.window_surface)
		self.ai_menu_two.draw(self.window_surface)

		# Draw the currently selected character sprites above the menus with animation
		if self.player_one_character:
			# Use full size character image for selected character display
			sprite_path = os.path.join("res", "character", f"{self.player_one_character}.png")
			if os.path.exists(sprite_path):
				sprite = pygame.image.load(sprite_path)
				sprite = pygame.transform.scale(sprite, (64, 64))
				
				# Create a copy for alpha
				sprite_alpha = sprite.copy()
				sprite_alpha.set_alpha(self.p1_preview_alpha)
				
				# Calculate base position (center above menu)
				base_x = self.character_menu_one.x + (self.character_menu_one.get_width() - 64) / 2
				y_pos = self.character_menu_one.y - 80
				
				# Apply offset for animation
				x_pos = base_x - self.p1_preview_offset  # Subtract offset to move from left
				
				self.window_surface.blit(sprite_alpha, (x_pos, y_pos))

		if self.player_two_character:
			# Use full size character image for selected character display
			sprite_path = os.path.join("res", "character", f"{self.player_two_character}.png")
			if os.path.exists(sprite_path):
				sprite = pygame.image.load(sprite_path)
				sprite = pygame.transform.scale(sprite, (64, 64))
				# Flip sprite horizontally for player two
				sprite = pygame.transform.flip(sprite, True, False)
				
				# Create a copy for alpha
				sprite_alpha = sprite.copy()
				sprite_alpha.set_alpha(self.p2_preview_alpha)
				
				# Calculate base position (center above menu)
				base_x = self.character_menu_two.x + (self.character_menu_two.get_width() - 64) / 2
				y_pos = self.character_menu_two.y - 80
				
				# Apply offset for animation
				x_pos = base_x - self.p2_preview_offset  # Subtract offset to move from right
				
				self.window_surface.blit(sprite_alpha, (x_pos, y_pos))

		# Draw the back and start buttons at the bottom
		self.back_menu.draw(self.window_surface)
		self.start_menu.draw(self.window_surface)

	def on_exit(self):
		if self.next_screen is game.Game:
			# If we're going to start the game, we first create both players.
			joystick_count = pygame.joystick.get_count()
			if joystick_count == 0:
				player_one = self.create_player_one(self.character_colors[self.player_one_character])
				player_two = self.create_player_two(self.character_colors[self.player_two_character])
			elif joystick_count == 1:
				player_one = self.create_player_one(self.character_colors[self.player_one_character], gamepad_id=0)
				player_two = self.create_player_two(self.character_colors[self.player_two_character])
			elif joystick_count == 2:
				player_one = self.create_player_one(self.character_colors[self.player_one_character], gamepad_id=0)
				player_two = self.create_player_two(self.character_colors[self.player_two_character], gamepad_id=1)

			# Create the game instance with initial score dictionary mapping players to 0
			score = {player_one: 0, player_two: 0}
			self.next = self.next_screen(self.window_surface, self.main_clock, player_one, player_two, self.number_of_rounds, score)
		elif not self.next_screen is None:
			# For any other screen we just call it using the normal variables.
			self.next = self.next_screen(self.window_surface, self.main_clock)

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
		gamepad_id = kwargs.get("gamepad_id", None)
		# Set AI difficulty to 0 if no AI is selected
		ai_difficulty = self.player_one_ai if self.player_one_ai is not None else 0
		player_one = player.Player(x, y, name, key_up, key_down, key_unleash_energy, joy_unleash_energy, gamepad_id, color, ai_difficulty)
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
		gamepad_id = kwargs.get("gamepad_id", None)
		# Set AI difficulty to 0 if no AI is selected
		ai_difficulty = self.player_two_ai if self.player_two_ai is not None else 0
		player_two = player.Player(x, y, name, key_up, key_down, key_unleash_energy, joy_unleash_energy, gamepad_id, color, ai_difficulty)
		return player_two