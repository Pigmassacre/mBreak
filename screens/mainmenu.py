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
import gui.gridmenu as gridmenu
import gui.coloritem as coloritem
import gui.transition as transition
from settings.settings import *
import settings.graphics as graphics

# Import any needed game screens here.
import screens.game as game

class MainMenu:

	def __init__(self, window_surface, main_clock, title_logo = None):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock
		self.next_screen = game.Game

		# Setup the logo and the variables needed to handle the animation of it.
		self.setup_logo(title_logo)

		self.logo_speed = 5
		self.logo_desired_x = (SCREEN_WIDTH - self.title_logo.get_width()) / 2
		self.logo_desired_y = ((SCREEN_HEIGHT - self.title_logo.get_height()) / 4)

		# Setup all the menu buttons.
		self.setup_main_menu()
		self.setup_prepare_menu()
		self.setup_options_menu()
		self.setup_graphics_menu()

		# The next screen to be started when gameloop ends.
		self.active_menu = [self.main_menu]

		# Setup the menu transitions.
		self.menu_transition = transition.Transition(48)
		self.menu_transition.setup_menu_transition(self.active_menu[0])

		# Setup and play music.
		self.setup_music()

		self.gameloop()

	def setup_main_menu(self):
		self.main_menu = self.setup_menu()
		self.main_menu.add(self.setup_button("Start"), self.start)
		self.main_menu.add(self.setup_button("Options"), self.options)
		self.main_menu.add(self.setup_button("Quit"), self.quit)

	def setup_prepare_menu(self):
		self.prepare_menu = self.setup_grid_menu()
		self.setup_color_items(self.prepare_menu)
		self.prepare_menu.x = (SCREEN_WIDTH - self.prepare_menu.get_width()) / 2
		self.prepare_menu.y = SCREEN_HEIGHT / 2
		self.prepare_menu.cleanup()

	def setup_color_items(self, grid_menu):
		grid_menu.add(coloritem.ColorItem(pygame.Color(255, 0, 0, 255)), self.color)
		grid_menu.add(coloritem.ColorItem(pygame.Color(0, 255, 0, 255)), self.color)
		grid_menu.add(coloritem.ColorItem(pygame.Color(0, 0, 255, 255)), self.color)
		grid_menu.add(coloritem.ColorItem(pygame.Color(255, 255, 0, 255)), self.color)
		grid_menu.add(coloritem.ColorItem(pygame.Color(255, 0, 255, 255)), self.color)
		grid_menu.add(coloritem.ColorItem(pygame.Color(0, 255, 255, 255)), self.color)

	def setup_options_menu(self):
		self.options_menu = self.setup_menu()
		self.options_menu.add(self.setup_button("Controls"), self.controls)
		self.options_menu.add(self.setup_button("Graphics"), self.graphics)
		self.options_menu.add(self.setup_button("Back"), self.back)

	def setup_graphics_menu(self):
		self.graphics_menu = self.setup_menu()

		shadows_button = self.setup_button("Shadows")
		shadows_button.is_on_off = True
		shadows_button.on = graphics.SHADOWS
		self.graphics_menu.add(shadows_button, self.shadows)

		particles_button = self.setup_button("Particles")
		particles_button.is_on_off = True
		particles_button.on = graphics.PARTICLES
		self.graphics_menu.add(particles_button, self.particles)

		traces_button = self.setup_button("Traces")
		traces_button.is_on_off = True
		traces_button.on = graphics.TRACES
		self.graphics_menu.add(traces_button, self.traces)

		self.graphics_menu.add(self.setup_button("Back"), self.back)

	def setup_logo(self, title_logo):
		if title_logo == None:
			self.title_logo = logo.Logo()

			x = (SCREEN_WIDTH - self.title_logo.get_width()) / 2
			y = ((SCREEN_HEIGHT - self.title_logo.get_height()) / 4)
			self.title_logo.x = x
			self.title_logo.y = y

			self.title_logo.play()
		else:
			self.title_logo = title_logo

	def setup_menu(self):
		x = SCREEN_WIDTH / 2
		y = SCREEN_HEIGHT / 2

		main_menu = menu.Menu(x, y)

		return main_menu

	def setup_grid_menu(self):
		x = SCREEN_WIDTH / 2
		y = SCREEN_HEIGHT / 2

		grid_menu = gridmenu.GridMenu(x, y)

		return grid_menu

	def setup_button(self, text):
		font_color = (255, 255, 255)
		alpha_value = 255

		text = textitem.TextItem(text, font_color, alpha_value)

		return text

	def setup_color_item(self, color):
		return coloritem.ColorItem()

	def setup_music(self):
		if not pygame.mixer.music.get_busy():
			pygame.mixer.music.load(TITLE_MUSIC)
			pygame.mixer.music.play()

	def start(self, item):
		self.active_menu.append(self.prepare_menu)
		self.menu_transition.setup_grid_menu_transition(self.active_menu[-1])

	def start_game(self, item):
		pygame.mixer.music.stop()
		self.done = True

	def options(self, item):
		self.active_menu.append(self.options_menu)
		self.menu_transition.setup_menu_transition(self.active_menu[-1])

	def controls(self, item):
		print("Controls clicked!")

	def graphics(self, item):
		self.active_menu.append(self.graphics_menu)
		self.menu_transition.setup_menu_transition(self.active_menu[-1])

	def shadows(self, item):
		graphics.SHADOWS = item.toggle_on_off()

	def particles(self, item):
		graphics.PARTICLES = item.toggle_on_off()

	def traces(self, item):
		graphics.TRACES = item.toggle_on_off()

	def back(self, item):
		self.active_menu.pop()
		self.menu_transition.setup_menu_transition(self.active_menu[-1])

	def color(self, item):
		print(str(item) + " with color " + str(item.color) + " clicked!")

	def quit(self, item):
		self.done = True
		self.next_screen = None

	def gameloop(self):
		self.done = False

		while not self.done:
			# Every frame begins by filling the whole screen with the background color.
			self.window_surface.fill(BACKGROUND_COLOR)
			
			for event in pygame.event.get():
				if event.type == QUIT:
					# If the window is closed, the game is shut down.
					sys.exit()
					pygame.quit()
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					# If the escape key is pressed, we go back a level in the menu system. If we're at the lowest level, we quit.
					if len(self.active_menu) > 1:
						self.active_menu.pop()
						self.menu_transition.setup_menu_transition(self.active_menu[-1])
					else:
						sys.exit()
						pygame.quit()
				elif event.type == KEYDOWN and event.key == K_RETURN:
					# If ENTER is pressed, proceed to the next screen, and end this loop.
					self.start()

			# Move the logo to the desired position.
			self.update_logo()

			#  If the logo is in place, show the menu.
			if self.title_logo.x == self.logo_desired_x and self.title_logo.y == self.logo_desired_y:
				self.show_menu()

			if DEBUG_MODE:
				# Display various debug information.
				debug.Debug.display(self.window_surface, self.main_clock)

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(MAX_FPS)

		# The gameloop is over, so we either start the next screen or quit the game.
		self.on_exit()

	def update_logo(self):
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

	def show_menu(self):
		self.menu_transition.handle_menu_transition(self.active_menu[-1])
		self.active_menu[-1].update()
		self.active_menu[-1].draw(self.window_surface)

	def on_exit(self):
		if self.next_screen == None:
			pygame.quit()
			sys.exit()
		else:
			self.next_screen(self.window_surface, self.main_clock)