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
import gui.menu as menu
from settings.settings import *

# Import any needed game screens here.
import screens.game as game

class MainMenu:

	def __init__(self, window_surface, main_clock, debug_font, title_logo):
		self.window_surface = window_surface
		self.main_clock = main_clock
		self.debug_font = debug_font
		self.title_logo = title_logo

		# Setup the logo and store the surface of the logo.
		self.setup_logo(self.title_logo)
		self.title_logo.play()

		# Setup the menu and add the buttons to it.
		self.main_menu = self.setup_menu()
		self.main_menu.add(self.setup_button("Start"), self.start)
		self.main_menu.add(self.setup_button("Options"), self.options)
		self.main_menu.add(self.setup_button("Quit"), self.quit)

		# Setup and play music.
		self.setup_music()
			
		# Keeps track of how much time has passed.
		self.time_passed = 0

		self.gameloop()

	def setup_logo(self, title_logo):
		# Set the logo so it displays in the middle of the screen.
		x = (SCREEN_WIDTH - title_logo.get_width()) / 2
		y = ((SCREEN_HEIGHT - title_logo.get_height()) / 4)
		title_logo.x = x
		title_logo.y = y

		return title_logo

	def setup_menu(self):
		x = SCREEN_WIDTH / 2
		y = SCREEN_HEIGHT / 2

		main_menu = menu.Menu(x, y)

		return main_menu

	def setup_button(self, text):
		font_color = (255, 255, 255)
		alpha_value = 255

		text = textitem.TextItem(text, font_color, alpha_value)

		return text

	def setup_music(self):
		if not pygame.mixer.music.get_busy():
			pygame.mixer.music.load(TITLE_MUSIC)
			pygame.mixer.music.play()

	def start(self):
		pygame.mixer.music.stop()
		game.main(self.window_surface, self.main_clock, self.debug_font)

	def options(self):
		print("Options clicked!")

	def quit(self):
		pygame.quit()
		sys.exit()

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
					self.start()
			
			# If the music isn't playing, start it.
			if not pygame.mixer.music.get_busy():
				pygame.mixer.music.play()

			self.title_logo.draw(self.window_surface)

			self.main_menu.update()
			self.main_menu.draw(self.window_surface)

			if DEBUG_MODE:
				# Display various debug information.
				debug.display(self.window_surface, self.main_clock, self.debug_font)

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(MAX_FPS)