__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
from pygame.locals import *
import gui.textitem as textitem
import gui.logo as logo
import settings.settings as settings
import screens.scene as scene

# From the intromenu the only screen we can go to is the mainmenu, so we import it here.
import screens.mainmenu as mainmenu

"""

The intromenu is the menu that is displayed after the splash menu.

If the user does nothing, we stay on the intro screen forever. Here we are introduced to the animated mBreak logo,
which stays into the main menu.

If the user presses RETURN or clicks on any part of the game screen, we continue to the main menu.

"""

class IntroMenu(scene.Scene):

	def __init__(self, window_surface, main_clock):
		# Call the superconstructor.
		scene.Scene.__init__(self, window_surface, main_clock)

		# Setup the logo and store the surface of the logo.
		self.setup_title_logo()

		# Setup the message beneath the logo.
		self.setup_title_message()

		# Setup the version message.
		self.setup_version_message()

		# Setup and play music.
		self.setup_music()

		# Start the gameloop, as usual!
		self.gameloop()

	def setup_title_logo(self):
		# Loads the logo, positions it and then returns the logo object.
		self.title_logo = logo.Logo()

		x = (settings.SCREEN_WIDTH - self.title_logo.get_width()) / 2
		y = (settings.SCREEN_HEIGHT / 2) - self.title_logo.get_height()
		self.title_logo.x = x
		self.title_logo.y = y

		self.title_logo.play()

	def setup_title_message(self):
		self.title_message = textitem.generate_list_from_string("Press ENTER to start")

		length_of_title_message = sum(letter_item.get_width() for letter_item in self.title_message)

		last_offset = 0
		for letter_item in self.title_message:
			letter_item.set_color((255, 255, 255))
			letter_item.x = ((settings.SCREEN_WIDTH - length_of_title_message) / 2.0) + last_offset
			letter_item.y = self.title_logo.y + self.title_logo.get_height() + letter_item.get_height()
			last_offset += letter_item.get_width()

			a = letter_item.alpha_value
			a = ((255 / (len(self.title_message) * 2)) * self.title_message.index(letter_item))
			if a > 255:
				a %= 255
			letter_item.alpha_value = a

		self.time_passed = 0

	def setup_version_message(self):
		text = settings.GAME_VERSION
		font_color = (255, 255, 255)
		alpha_value = 255

		self.version_message = textitem.TextItem(text, font_color, alpha_value)
		self.version_message.x = settings.SCREEN_WIDTH - self.version_message.get_width() - self.version_message.font_size
		self.version_message.y = settings.SCREEN_HEIGHT - self.version_message.get_height() - self.version_message.font_size

	def setup_music(self):
		self.__class__.music_list = settings.TITLE_MUSIC
		self.play_music()

	def event(self, event):
		if ((event.type == KEYDOWN and event.key in [K_ESCAPE, K_RETURN]) or (event.type == MOUSEBUTTONDOWN and event.button == 1) or
		     (event.type == JOYBUTTONDOWN and (event.button in settings.JOY_BUTTON_SKIP))):
			# If ENTER, left mouse button or any joystick skip button on a gamepad is pressed, proceed to the main menu.
			self.done = True

	def update(self):
		self.time_passed += self.main_clock.get_time()
		for letter_item in self.title_message:
			bob_height_differentiator = self.title_message.index(letter_item) * 64

			sin_scale = 0.0075

			sin = 0.5 * settings.GAME_SCALE
			sin *= math.sin((self.time_passed + bob_height_differentiator) * (sin_scale / 16.0))
			sin *= math.sin((self.time_passed + bob_height_differentiator) * (sin_scale / 8.0))
			sin *= math.sin((self.time_passed + bob_height_differentiator) * sin_scale)

			letter_item_standard_y = self.title_logo.y + self.title_logo.get_height() + letter_item.get_height()
			letter_item.y = letter_item_standard_y + -math.fabs(sin) * 2.0 * settings.GAME_SCALE

			a = letter_item.alpha_value
			a = ((math.sin((pygame.time.get_ticks() + (self.title_message.index(letter_item) * 64)) * 0.0025) + 1.0) / 2.0) * 255
			if a > 255:
				a %= 255
			letter_item.alpha_value = a
			letter_item.setup_surfaces()

		# Since we've set the title message to blink, we have to update it so it does so.
		for letter_item in self.title_message:
			letter_item.update(self.main_clock)

	def draw(self):
		# Every frame begins by filling the whole screen with the background color.
		self.window_surface.fill(settings.BACKGROUND_COLOR)

		# We draw the logo.
		self.title_logo.draw(self.window_surface)

		# We draw the title message.
		for letter_item in self.title_message:
			letter_item.draw(self.window_surface)

		# Aaand we draw the version message.
		self.version_message.draw(self.window_surface)

	def on_exit(self):
		# We're done, so continue to the main menu.
		mainmenu.MainMenu(self.window_surface, self.main_clock, self.title_logo)