__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
import os
import json
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
import screens.scene as scene

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
class HelpMenu(scene.Scene):

	def __init__(self, window_surface, main_clock, menu_screen_instance = None):
		# Call the superconstructor.
		scene.Scene.__init__(self, window_surface, main_clock)

		# If we've gotten a main menu instance to return to, then save that.
		self.menu_screen_instance = menu_screen_instance

		# The next screen to be started when the gameloop ends.
		self.next_screen = screens.mainmenu.MainMenu

		# This is a dictionary that contains information linked to certain imageitems.
		self.info = {}

		# This is a dictionary that maps transitions methods to all all items.
		self.transition_method = {}

		# This contains the currently active function that displays the currently active information.
		self.active_info = None

		# This information is used to format the help texts.
		self.distance_from_screen_edge = 6 * settings.GAME_SCALE
		self.font_size = 6 * settings.GAME_SCALE
		self.max_width_of_text_line = (settings.SCREEN_WIDTH - (self.distance_from_screen_edge * 2))

		# A list of all menus, so we can easily register all menus to all menus (so they know to unselect items in other menus and stuff like that).
		self.all_menus = []

		# We create a gridmenu that allows the player to choose what item they want to read more about.
		self.help_menu = gridmenu.GridMenu(13)
		self.help_menu.y = 9 * settings.GAME_SCALE
		self.all_menus.append(self.help_menu)

		# We setup and add all the necessary items to the help_menu.
		root = "res/helpdata"
		for file in os.listdir("res/helpdata"):
			if file.endswith(".json"):
				self.setup_info(os.path.join(root, file))

		self.help_menu.x = (settings.SCREEN_WIDTH - self.help_menu.get_width()) / 2

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
		self.transitions.speed = 20 * settings.GAME_FPS * settings.GAME_SCALE
		self.transitions.setup_transition(self.help_menu, True, True, True, False)
		self.transitions.setup_transition(self.back_menu, True, True, False, False)

		# Set the first item as the active information.
		if len(self.help_menu.items) > 0:
			self.view_info(self.help_menu.items[0])

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
		# Unless the chosen info is the same as the currently active info, set the active info to the one chosen by the user.
		new_active_info = self.choose_active_info(item, self.help_menu)
		if self.active_info != new_active_info:
			self.active_info = new_active_info

			# Setup the transitions for that info.
			self.setup_info_transitions(self.active_info)

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

		# At last, return the matching information in the info dictionary.
		return self.info[item]

	def setup_info(self, file_path):
		info_texts = []

		# Parse the JSON file.
		json_file = open(file_path, "r")
		try:
			parsed_json = json.load(json_file)
		except IOError:
			print("IOError when reading JSON file.")		
		finally:
			json_file.close()

		# We try to parse the image tag in the JSON file. If it isn't found, an error is raised.
		if "image" in parsed_json:
			try:
				image_item = imageitem.ImageItem(parsed_json["image"])
			except:
				raise ValueError("The image path could not be read.")
		else:
			raise SyntaxError("Image key not found in JSON file.")

		# We try to parse the color tag in the JSON file. If it isn't found, we simply ignore it.
		if "color" in parsed_json:
			try:
				color_list = parsed_json["color"]
			except:
				raise ValueError("The color value could not be read.")

			try:
				useful.colorize_image(image_item.image, pygame.Color(color_list[0], color_list[1], color_list[2]))
			except:
				raise ValueError("The given color values cannot be applied: [{0}, {1}, {2}]".format(color_list[0], color_list[1], color_list[2]))

		# We add the image item to the help_menu here, so that the text can be be positioned properly.
		self.help_menu.add(image_item, self.view_info)

		# We try to parse the title tag in the JSON file. If it isn't found, an error is raised.
		if "title" in parsed_json:
			info_text = textitem.TextItem(parsed_json["title"], pygame.Color(255, 255, 255), 255, self.font_size)
			info_text.x = (settings.SCREEN_WIDTH - info_text.get_width()) / 2
			info_text.y = self.help_menu.y + self.help_menu.get_height() + info_text.get_height()
			info_texts.append(info_text)
			previous_info_text = info_text
		else:
			raise SyntaxError("Title key not found in JSON file.")

		if "body" in parsed_json:
			body = parsed_json["body"]

			odd = True
			first_line = True

			wrapped_body = useful.wrap_multi_line(body, pygame.font.Font(textitem.TextItem.font_path, self.font_size), self.max_width_of_text_line)

			for line in wrapped_body:
				if odd:
					color = pygame.Color(255, 255, 255)
				else:
					color = pygame.Color(150, 150, 150)

				info_text = textitem.TextItem(line, color, 255, self.font_size)

				if first_line:
					info_text.x = self.distance_from_screen_edge
					info_text.y = previous_info_text.y + (2 * info_text.get_height())
					first_line = False
				else:
					info_text.x = self.distance_from_screen_edge
					info_text.y = previous_info_text.y + info_text.get_height()
				
				info_texts.append(info_text)
				previous_info_text = info_text

				if line != "":
					odd = not odd
		else:
			raise SyntaxError("Body tag not found in JSON file.")

		self.info[image_item] = info_texts
		
		return image_item

	def setup_info_transitions(self, info_texts):
		for item in info_texts:
			self.transitions.setup_single_item_transition(item, True, True, False, False)

	def show_info(self, info_texts, surface):
		if not info_texts is None:
			for info_text in info_texts:
				info_text.draw(surface)

	def back(self, item = None):
		# Simply moves back to the main menu.
		self.next_screen = screens.mainmenu.MainMenu
		self.done = True

	def event(self, event):
		if (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == JOYBUTTONDOWN and event.button in settings.JOY_BUTTON_BACK):
			# If the escape key is pressed, we go back to the main menu.
			self.back()
		else:
			traversal.traverse_menus(event, self.all_menus)

	def update(self):
		# Handle all transitions.
		self.transitions.update()

		# Update the help menu.
		self.help_menu.update(self.main_clock)	

		# Update the back meenu.
		self.back_menu.update(self.main_clock)	

	def draw(self):
		# Every frame begins by filling the whole screen with the background color.
		self.window_surface.fill(settings.BACKGROUND_COLOR)

		# Draw the help menu.
		self.help_menu.draw(self.window_surface)

		# Draw the active information.
		self.show_info(self.active_info, self.window_surface)

		# Draw the back menu.
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
