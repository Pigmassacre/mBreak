__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
from libs import pyganim
import math
import other.debug as debug
import other.useful as useful
import gui.textitem as textitem
import gui.logo as logo
from settings.settings import *

# Import any needed game screens here.
import screens.mainmenu as mainmenu

class IntroMenu:

	def __init__(self, window_surface, main_clock, debug_font):
		self.window_surface = window_surface
		self.main_clock = main_clock
		self.debug_font = debug_font

		# Setup the logo and store the surface of the logo.
		self.title_logo = self.setup_logo()
		self.title_logo.play()

		# Setup the message beneath the logo and store the surface of the message.
		self.title_message = self.setup_message(self.title_logo)
		# Sets the blink rate of the message.
		self.title_message_blink_rate = 750

		# Setup and play music.
		self.setup_music()
			
		# Keeps track of how much time has passed.
		self.time_passed = 0

		self.gameloop()

	def setup_logo(self):
		title_logo = logo.Logo()

		x = (SCREEN_WIDTH - title_logo.get_width()) / 2
		y = ((SCREEN_HEIGHT - title_logo.get_height()) / 2) - 30
		title_logo.x = x
		title_logo.y = y

		return title_logo

	def setup_message(self, title_logo):
		text = "Press ENTER to start"
		font_color = (255, 255, 255)
		alpha_value = 255
		offset = 50

		text = textitem.TextItem(text, font_color, alpha_value)

		text.x = (SCREEN_WIDTH - text.get_width()) / 2
		text.y = title_logo.y + title_logo.get_height() + offset

		return text

	def setup_music(self):
		pygame.mixer.music.load(TITLE_MUSIC)
		pygame.mixer.music.play()

	def gameloop(self):
		done = False

		while not done:
			# Every frame begins by filling the whole screen with the background color.
			self.window_surface.fill(BACKGROUND_COLOR)
			
			for event in pygame.event.get():
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
					# If the ESCAPE key is pressed or the window is closed, the game is shut down.
					pygame.quit()
					sys.exit()
				elif event.type == KEYDOWN and event.key == K_RETURN:
					# If ENTER is pressed, proceed to the next screen, and end this loop.
					# TODO: Add transition effect (logo moves up).
					done = True
			
			# If the music isn't playing, start it.
			if not pygame.mixer.music.get_busy():
				pygame.mixer.music.play()

			# Draw the logo.
			self.title_logo.draw(self.window_surface)

			# Increment the time passed.
			self.time_passed += self.main_clock.get_time()
			# Blinks the title message.
			self.time_passed = self.title_message.blink(self.time_passed, self.title_message_blink_rate)

			# Draw the title message.
			self.title_message.draw(self.window_surface)
			
			if DEBUG_MODE:
				# Display various debug information.
				debug.display(self.window_surface, self.main_clock, self.debug_font)

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(MAX_FPS)

		mainmenu.MainMenu(self.window_surface, self.main_clock, self.debug_font, self.title_logo)
