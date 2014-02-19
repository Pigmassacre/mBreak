__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
import os
import json
from pygame.locals import *
import other.useful as useful
import gui.textitem as textitem
import gui.listmenu as listmenu
import gui.gridmenu as gridmenu
import gui.imageitem as imageitem
import settings.settings as settings
import screens.scene as scene

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

"""
class HelpMenu(scene.Scene):

	def __init__(self, window_surface, main_clock):
		# Call the superconstructor.
		scene.Scene.__init__(self, window_surface, main_clock)

		# The next screen to be started when the gameloop ends.
		self.next_screen = None

		# This is a dictionary that contains information linked to certain imageitems.
		self.info = {}

		# This is a dictionary that maps transition methods to all all items.
		self.transition_method = {}

		# This contains the currently active function that displays the currently active information.
		self.active_info = None

		# This information is used to format the help texts.
		self.distance_from_screen_edge = 6 * settings.GAME_SCALE
		self.font_size = 6 * settings.GAME_SCALE
		self.max_width_of_text_line = (settings.SCREEN_WIDTH - (self.distance_from_screen_edge * 2))

		# We create a gridmenu that allows the player to choose what item they want to read more about.
		self.help_menu = gridmenu.GridMenu(13)
		self.help_menu.y = 9 * settings.GAME_SCALE
		self.menu_list.append(self.help_menu)

		# The back button, displayed in the middle-bottom of the screen.
		back_button = textitem.TextItem("Back")
		self.back_menu = listmenu.ListMenu()
		self.back_menu.x = settings.SCREEN_WIDTH / 2
		self.back_menu.y = settings.SCREEN_HEIGHT - (2 * back_button.get_height())
		self.back_menu.add(back_button, self.back)
		self.back_menu.items[0].selected = True
		self.menu_list.append(self.back_menu)

		# We setup and add all the necessary items to the help_menu.
		root = "res/helpdata"
		for file in os.listdir(root):
			if file.endswith(".json"):
				self.setup_info(os.path.join(root, file))

		self.help_menu.x = (settings.SCREEN_WIDTH - self.help_menu.get_width()) / 2

		# Register all menus with each other.
		for a_menu in self.menu_list:
			a_menu.register_other_menus(self.menu_list)

		# We setup all menu transition.
		self.transition.speed = 20 * settings.GAME_FPS * settings.GAME_SCALE
		self.transition.setup_transition(self.help_menu, True, True, True, False)
		self.transition.setup_transition(self.back_menu, True, True, False, False)

		# Set the first item as the active information.
		if len(self.help_menu.items) > 0:
			self.view_info(self.help_menu.items[0])

		# And finally, we start the gameloop!
		self.gameloop()

	def view_info(self, item):
		# Unless the chosen info is the same as the currently active info, set the active info to the one chosen by the user.
		new_active_info = self.choose_active_info(item, self.help_menu)
		if self.active_info != new_active_info:
			self.active_info = new_active_info

			# Setup the transition for that info.
			self.setup_info_transition(self.active_info)

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
		texts = []

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
			text = textitem.TextItem(parsed_json["title"], pygame.Color(255, 255, 255), 255, self.font_size)
			text.x = (settings.SCREEN_WIDTH - text.get_width()) / 2
			text.y = self.help_menu.y + self.help_menu.get_height() + text.get_height()
			texts.append(text)
			previous_text = text
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

				text = textitem.TextItem(line, color, 255, self.font_size)

				if first_line:
					text.x = self.distance_from_screen_edge
					text.y = previous_text.y + (2 * text.get_height())
					first_line = False
				else:
					text.x = self.distance_from_screen_edge
					text.y = previous_text.y + text.get_height()
				
				texts.append(text)
				previous_text = text

				if line != "":
					odd = not odd
		else:
			raise SyntaxError("Body tag not found in JSON file.")

		if "quote" in parsed_json:
			quote = parsed_json["quote"]

			odd = True

			quotes = []

			font = pygame.font.Font(textitem.TextItem.font_path, self.font_size)
			wrapped_quote = useful.wrap_multi_line(quote, font, self.max_width_of_text_line)

			for line in wrapped_quote:
				if odd:
					color = pygame.Color(200, 0, 200)
				else:
					color = pygame.Color(200, 50, 200)

				text = textitem.TextItem(line, color, 255, self.font_size)
				text.x = settings.SCREEN_WIDTH - text.get_width() - self.distance_from_screen_edge
				
				quotes.append(text)
				texts.append(text)
				previous_text = text

				if line != "":
					odd = not odd

			for quote_line in quotes:
				quote_line.y = (self.back_menu.y - (2 * quote_line.get_height()) - len(quotes) * quote_line.get_height()) + quotes.index(quote_line) * quote_line.get_height()

		self.info[image_item] = texts
		
		return image_item

	def setup_info_transition(self, texts):
		for item in texts:
			self.transition.setup_single_item_transition(item, True, True, False, False)

	def show_info(self, texts, surface):
		if not texts is None:
			for text in texts:
				text.draw(surface)

	def back(self, item):
		# Simply ends this scene.
		self.done = True

	def event(self, event):
		if (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == JOYBUTTONDOWN and event.button in settings.JOY_BUTTON_BACK):
			# If the escape key is pressed, we end this scene.
			self.back(None)

	def update(self):
		# Handle all transition.
		self.transition.update(self.main_clock)

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
		if not self.next_screen is None:
			# If there is a next screen set, start that.
			self.next_screen(self.window_surface, self.main_clock)
		
		# Else, we simply let this scene end.