__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import other.debug as debug
import gui.textitem as textitem
import gui.logo as logo
import settings.settings as settings
import settings.graphics as graphics

# From the intromenu the only screen we can go to is the mainmenu, so we import it here.
import screens.mainmenu as mainmenu

"""

The intromenu is the menu that is displayed after the splash menu.

If the user does nothing, we stay on the intro screen forever. Here we are introduced to the animated mBreak logo,
which stays into the main menu.

If the user presses RETURN or clicks on any part of the game screen, we continue to the main menu.

"""

class IntroMenu:

	def __init__(self, window_surface, main_clock):
		# Save these variables as usual.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# Setup the logo and store the surface of the logo.
		self.title_logo = self.setup_logo()
		self.title_logo.play()

		# Setup the message beneath the logo and store the surface of the message.
		self.title_message = self.setup_message(self.title_logo)

		# Setup and play music.
		self.setup_music()
			
		# Keeps track of how much time has passed.
		self.time_passed = 0

		# Start the gameloop, as usual!
		self.gameloop()

	def setup_logo(self):
		# Loads the logo, positions it and then returns the logo object.
		title_logo = logo.Logo()

		x = (settings.SCREEN_WIDTH - title_logo.get_width()) / 2
		y = (settings.SCREEN_HEIGHT / 2) - title_logo.get_height()
		title_logo.x = x
		title_logo.y = y

		return title_logo

	def setup_message(self, title_logo):
		# Sets up the message, positions it and then returns the message textitem.
		text = "Press ENTER to start"
		font_color = (255, 255, 255)
		alpha_value = 255
		offset = 0

		text = textitem.TextItem(text, font_color, alpha_value)

		text.x = (settings.SCREEN_WIDTH - text.get_width()) / 2
		text.y = title_logo.y + title_logo.get_height() + text.get_height()

		return text

	def setup_music(self):
		# Loads the title screen music and plays it indefinitely.
		pygame.mixer.music.load(settings.TITLE_MUSIC)
		pygame.mixer.music.play(-1)

	def gameloop(self):
		# When done is True, the gameloop ends and the next screen is started.
		self.done = False
		while not self.done:
			# Constrain the game to a set maximum amount of FPS, and update the delta time value.
			self.main_clock.tick(graphics.MAX_FPS)

			# Every frame begins by filling the whole screen with the background color.
			self.window_surface.fill(settings.BACKGROUND_COLOR)
			
			for event in pygame.event.get():
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
					# If the ESCAPE key is pressed or the window is closed, the game is shut down.
					pygame.quit()
					sys.exit()
				elif ((event.type == KEYDOWN and event.key == K_RETURN) or (event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]) or
				     (event.type == JOYBUTTONDOWN and (event.button == 2 or event.button == 9))):
					# If ENTER is pressed or the mouse button is clicked, proceed to the next screen, and end this loop.
					self.done = True

			# We draw the logo.
			self.title_logo.draw(self.window_surface)
			
			# Calls the blink method of the title_message object, which will hide the title_message at regular intervals, essentially
			# making it "blink".
			self.time_passed += self.main_clock.get_time()
			self.time_passed = self.title_message.blink(self.time_passed)

			# We draw the title message.
			self.title_message.draw(self.window_surface)
			
			if settings.DEBUG_MODE:
				# Display various debug information.
				debug.Debug.display(self.window_surface, self.main_clock)

			# Update the display, of course.
			pygame.display.update()

		# We're done, so continue to the main menu.
		mainmenu.MainMenu(self.window_surface, self.main_clock, self.title_logo)
