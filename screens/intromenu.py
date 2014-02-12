__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import gui.textitem as textitem
import gui.logo as logo
import settings.settings as settings
import settings.graphics as graphics
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
			
		# Keeps track of how much time has passed.
		self.time_passed = 0

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
		text = "Press ENTER to start"
		font_color = (255, 255, 255)
		alpha_value = 255

		self.title_message = textitem.TextItem(text, font_color, alpha_value)
		self.title_message.x = (settings.SCREEN_WIDTH - self.title_message.get_width()) / 2
		self.title_message.y = self.title_logo.y + self.title_logo.get_height() + self.title_message.get_height()

	def setup_version_message(self):
		text = settings.GAME_VERSION
		font_color = (255, 255, 255)
		alpha_value = 255

		self.version_message = textitem.TextItem(text, font_color, alpha_value)
		self.version_message.x = settings.SCREEN_WIDTH - self.version_message.get_width() - self.version_message.font_size
		self.version_message.y = settings.SCREEN_HEIGHT - self.version_message.get_height() - self.version_message.font_size

	def setup_music(self):
		# Loads the title screen music and plays it indefinitely.
		pygame.mixer.music.load(settings.TITLE_MUSIC)
		pygame.mixer.music.play(-1)

	def event(self, event):
		if ((event.type == KEYDOWN and event.key in [K_ESCAPE, K_RETURN]) or (event.type == MOUSEBUTTONDOWN and event.button == 1) or
		     (event.type == JOYBUTTONDOWN and (event.button in settings.JOY_BUTTON_SKIP))):
			# If ENTER, left mouse button or any joystick skip button on a gamepad is pressed, proceed to the main menu.
			self.done = True

	def update(self):
		# Calls the blink method of the title_message object, which will hide the title_message at regular intervals, essentially
		# making it "blink".
		self.time_passed += self.main_clock.get_time()
		self.time_passed = self.title_message.blink(self.time_passed)

	def draw(self):
		# Every frame begins by filling the whole screen with the background color.
		self.window_surface.fill(settings.BACKGROUND_COLOR)

		# We draw the logo.
		self.title_logo.draw(self.window_surface)

		# We draw the title message.
		self.title_message.draw(self.window_surface)

		self.version_message.draw(self.window_surface)

	def on_exit(self):
		# We're done, so continue to the main menu.
		mainmenu.MainMenu(self.window_surface, self.main_clock, self.title_logo)