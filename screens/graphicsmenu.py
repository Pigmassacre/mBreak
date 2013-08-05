__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
from libs import pyganim
import math
import random
import other.debug as debug
import other.useful as useful
import gui.textitem as textitem
import gui.logo as logo
import gui.menu as menu
from settings.settings import *

# Import any needed game screens here.
import screens

class GraphicsMenu:

	def __init__(self, window_surface, main_clock, debug_font, title_logo = None):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock
		self.debug_font = debug_font

		# The next screen to be started when gameloop ends.
		self.next_screen = None

		# Setup the logo and the variables needed to handle the animation of it.
		if title_logo == None:
			self.title_logo = self.setup_logo()
			self.title_logo.play()
		else:
			self.title_logo = title_logo
		
		self.logo_speed = 5
		self.logo_desired_x = (SCREEN_WIDTH - self.title_logo.get_width()) / 2
		self.logo_desired_y = ((SCREEN_HEIGHT - self.title_logo.get_height()) / 4)

		# Setup the menu and add the buttons to it.
		self.graphics_menu = self.setup_menu()
		self.graphics_menu.add(self.setup_button("Shadows"), self.shadows)
		self.graphics_menu.add(self.setup_button("Particles"), self.particles)
		self.graphics_menu.add(self.setup_button("Traces"), self.traces)
		self.graphics_menu.add(self.setup_button("Back"), self.back)

		# Setup the variables needed to handle the animation of the menu.
		self.graphics_menu_speed = 48
		self.graphics_menu_start_positions = {}
		self.odd = random.choice([True, False])
		for item in self.graphics_menu.items:
			self.graphics_menu_start_positions[item] = item.x
			if self.odd:
				item.x = SCREEN_WIDTH
				self.odd = False
			else:
				item. x = -item.get_width()
				self.odd = True

		# Setup and play music.
		self.setup_music()

		self.gameloop()

	def setup_logo(self):
		title_logo = logo.Logo()

		x = (SCREEN_WIDTH - title_logo.get_width()) / 2
		y = ((SCREEN_HEIGHT - title_logo.get_height()) / 4)
		title_logo.x = x
		title_logo.y = y

		return title_logo

	def setup_menu(self):
		x = SCREEN_WIDTH / 2
		y = SCREEN_HEIGHT / 2

		graphics_menu = menu.Menu(x, y)

		return graphics_menu

	def setup_button(self, text):
		font_color = (255, 255, 255)
		alpha_value = 255

		text = textitem.TextItem(text, font_color, alpha_value)

		return text

	def setup_music(self):
		if not pygame.mixer.music.get_busy():
			pygame.mixer.music.load(TITLE_MUSIC)
			pygame.mixer.music.play()

	def shadows(self):
		print("Shadows clicked!")

	def particles(self):
		print("Particles clicked!")

	def traces(self):
		print("Traces clicked!")

	def back(self):
		self.done = True
		self.next_screen = screens.optionsmenu.OptionsMenu

	def gameloop(self):
		self.done = False

		while not self.done:
			# Every frame begins by filling the whole screen with the background color.
			self.window_surface.fill(BACKGROUND_COLOR)
			
			for event in pygame.event.get():
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
					# If the ESCAPE key is pressed or the window is closed, the game is shut down.
					sys.exit()
					pygame.quit()
				elif event.type == KEYDOWN and event.key == K_RETURN:
					# If ENTER is pressed, proceed to the next screen, and end this loop.
					self.start()

			# Move the logo to the desired position.
			if self.logo_desired_x < self.title_logo.x:
				if (self.title_logo.x - self.logo_speed) < self.logo_desired_x:
					self.title_logo.x = self.logo_desired_x
				else:
					self.title_logo.x -= self.logo_speed
			elif self.logo_desired_x > self.title_logo.x:
				if (self.title_logo.x + self.logo_speed) > self.logo_desired_x:
					self.title_logo.x = self.logo_desired_x
				else:
					self.title_logo.x += self.logo_speed

			if self.logo_desired_y < self.title_logo.y:
				if (self.title_logo.y - self.logo_speed) < self.logo_desired_y:
					self.title_logo.y = self.logo_desired_y
				else:
					self.title_logo.y -= self.logo_speed
			elif self.logo_desired_y > self.title_logo.y:
				if (self.title_logo.y + self.logo_speed) > self.logo_desired_y:
					self.title_logo.y = self.logo_desired_y
				else:
					self.title_logo.y += self.logo_speed

			self.title_logo.draw(self.window_surface)

			#  If the logo is in place, show the menu.
			if self.title_logo.x == self.logo_desired_x and self.title_logo.y == self.logo_desired_y:
				for item in self.graphics_menu.items:
					if self.graphics_menu_start_positions[item] < item.x:
						if (item.x - self.graphics_menu_speed) < self.graphics_menu_start_positions[item]:
							item.x = self.graphics_menu_start_positions[item]
						else:
							item.x -= self.graphics_menu_speed
					elif self.graphics_menu_start_positions[item] > item.x:
						if (item.x + self.graphics_menu_speed) > self.graphics_menu_start_positions[item]:
							item.x = self.graphics_menu_start_positions[item]
						else:
							item.x += self.graphics_menu_speed

				self.graphics_menu.update()
				self.graphics_menu.draw(self.window_surface)

			if DEBUG_MODE:
				# Display various debug information.
				debug.display(self.window_surface, self.main_clock, self.debug_font)

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(MAX_FPS)

		# The gameloop is over, so we either start the next screen or quit the game.
		if not self.next_screen == None:
			self.next_screen(self.window_surface, self.main_clock, self.debug_font, self.title_logo)
		else:
			pygame.quit()
			sys.exit()