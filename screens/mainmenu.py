__author__ = "Olof Karlsson"
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
import settings.settings as settings
import settings.graphics as graphics

# Import any needed game screens here.
import screens.preparemenu as preparemenu

class MainMenu:

	def __init__(self, window_surface, main_clock, title_logo = None):
		# Store the game variables.
		self.window_surface = window_surface
		self.main_clock = main_clock

		# The next screen to be started when the gameloop ends.
		self.next_screen = preparemenu.PrepareMenu

		# Setup the logo and the variables needed to handle the animation of it.
		self.setup_logo(title_logo)
		self.logo_desired_position = ((settings.SCREEN_WIDTH - self.title_logo.get_width()) / 2, ((settings.SCREEN_HEIGHT - self.title_logo.get_height()) / 4))
		self.logo_transition = transition.Transition()
		self.logo_transition.speed = 2 * settings.GAME_SCALE

		# Setup all the menu buttons.
		self.setup_main_menu()
		self.setup_options_menu()
		self.setup_graphics_menu()

		# The menu to display.
		self.active_menu = [self.main_menu]

		# Setup the menu transitions.
		self.menu_transition = transition.Transition()
		self.menu_transition.setup_odd_even_transition(self.active_menu[0], True, True, False, False)

		# Setup and play music.
		self.setup_music()

		self.gameloop()

	def setup_main_menu(self):
		self.main_menu = self.setup_menu()
		self.main_menu.add(textitem.TextItem("Start"), self.start)
		self.main_menu.add(textitem.TextItem("Options"), self.options)
		self.main_menu.add(textitem.TextItem("Quit"), self.quit)
		self.main_menu.items[0].selected = True

	def options(self, item):
		self.active_menu.append(self.options_menu)
		self.menu_transition.setup_odd_even_transition(self.active_menu[-1], True, True, False, False)

	def setup_options_menu(self):
		self.options_menu = self.setup_menu()
		self.options_menu.add(textitem.TextItem("Graphics"), self.graphics)
		self.options_menu.add(textitem.TextItem("Back"), self.back)
		self.options_menu.items[0].selected = True

	def graphics(self, item):
		self.active_menu.append(self.graphics_menu)
		self.menu_transition.setup_odd_even_transition(self.active_menu[-1], True, True, False, False)
		
		# Move the logo so the graphics menu has enough space.
		self.logo_desired_position = ((settings.SCREEN_WIDTH - self.title_logo.get_width()) / 2, ((settings.SCREEN_HEIGHT - self.title_logo.get_height()) / 4) - self.graphics_menu_offset)

	def setup_graphics_menu(self):
		self.graphics_menu = self.setup_menu()

		# Setup the buttons and make them "on/off" buttons.
		shadows_button = textitem.TextItem("Shadows On")
		shadows_button.setup_is_on_off("Shadows Off", graphics.SHADOWS)
		self.graphics_menu.add(shadows_button, self.shadows)

		particles_button = textitem.TextItem("Particles On")
		particles_button.setup_is_on_off("Particles Off", graphics.PARTICLES)
		self.graphics_menu.add(particles_button, self.particles)

		traces_button = textitem.TextItem("Traces On")
		traces_button.setup_is_on_off("Traces Off", graphics.TRACES)
		self.graphics_menu.add(traces_button, self.traces)
		
		traces_button = textitem.TextItem("Background On")
		traces_button.setup_is_on_off("Background Off", graphics.BACKGROUND)
		self.graphics_menu.add(traces_button, self.background)
		
		# We store the graphics offset so we can offset the logo by this later.
		self.graphics_menu_offset = (shadows_button.get_height() * 2)
		self.graphics_menu.y = (settings.SCREEN_HEIGHT / 2) - self.graphics_menu_offset

		# We add a back button to the menu.
		self.graphics_menu.add(textitem.TextItem("Back"), self.back)
		self.graphics_menu.items[0].selected = True

	def shadows(self, item):
		graphics.SHADOWS = item.toggle_on_off()

	def particles(self, item):
		graphics.PARTICLES = item.toggle_on_off()

	def traces(self, item):
		graphics.TRACES = item.toggle_on_off()
		
	def background(self, item):
		graphics.BACKGROUND = item.toggle_on_off()

	def setup_logo(self, title_logo):
		if title_logo == None:
			self.title_logo = logo.Logo()
			
			self.title_logo.x = (settings.SCREEN_WIDTH - self.title_logo.get_width()) / 2
			self.title_logo.y = ((settings.SCREEN_HEIGHT - self.title_logo.get_height()) / 4)
			
			self.title_logo.play()
		else:
			self.title_logo = title_logo
	
	def setup_menu(self, x = settings.SCREEN_WIDTH / 2, y = settings.SCREEN_HEIGHT / 2):
		return menu.Menu(x, y)

	def setup_grid_menu(self):
		x = settings.SCREEN_WIDTH / 2
		y = settings.SCREEN_HEIGHT / 2

		grid_menu = gridmenu.GridMenu(x, y)

		return grid_menu

	def setup_music(self):
		if not pygame.mixer.music.get_busy():
			pygame.mixer.music.load(settings.TITLE_MUSIC)
			pygame.mixer.music.play()

	def start(self, item):
		self.done = True

	def back(self, item):
		self.active_menu.pop()
		self.menu_transition.setup_odd_even_transition(self.active_menu[-1], True, True, False, False)
		
		# Restore the logo's position.
		self.logo_desired_position = ((settings.SCREEN_WIDTH - self.title_logo.get_width()) / 2, ((settings.SCREEN_HEIGHT - self.title_logo.get_height()) / 4))
		
	def quit(self, item):
		self.done = True
		self.next_screen = None

	def gameloop(self):
		self.done = False

		while not self.done:
			# Every frame begins by filling the whole screen with the background color.
			self.window_surface.fill(settings.BACKGROUND_COLOR)
			
			for event in pygame.event.get():
				if event.type == QUIT:
					# If the window is closed, the game is shut down.
					sys.exit()
					pygame.quit()
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					# If the escape key is pressed, we go back a level in the menu system. If we're at the lowest level, we quit.
					if len(self.active_menu) > 1:
						self.back(None)
					else:
						sys.exit()
						pygame.quit()
				elif event.type == KEYDOWN and event.key == K_RETURN:
					# If ENTER is pressed, proceed to the next screen, and end this loop.
					for item in self.active_menu[-1].items:
						if item.selected:
							self.active_menu[-1].functions[item](item)
							break
				elif event.type == KEYDOWN and event.key == K_UP:
					for item in self.active_menu[-1].items:
						if item.selected:
							if self.active_menu[-1].items.index(item) - 1 >= 0:
								self.active_menu[-1].items[self.active_menu[-1].items.index(item) - 1].selected = True
								item.selected = False
								break
				elif event.type == KEYDOWN and event.key == K_DOWN:
					for item in self.active_menu[-1].items:
						if item.selected:
							if self.active_menu[-1].items.index(item) + 1 <= len(self.active_menu[-1].items) - 1:
								self.active_menu[-1].items[self.active_menu[-1].items.index(item) + 1].selected = True
								item.selected = False
								break

			# Move the logo to the desired position.
			self.show_logo()

			#  If the logo is in place, show the menu.
			if self.title_logo.x == self.logo_desired_position[0] and self.title_logo.y == self.logo_desired_position[1]:
				self.show_menu()

			if settings.DEBUG_MODE:
				# Display various debug information.
				debug.Debug.display(self.window_surface, self.main_clock)

			pygame.display.update()
			
			# Finally, constrain the game to a set maximum amount of FPS.
			self.main_clock.tick(settings.MAX_FPS)

		# The gameloop is over, so we either start the next screen or quit the game.
		self.on_exit()

	def show_logo(self):
		self.logo_transition.move_item_to_position(self.title_logo, self.logo_desired_position)
		self.title_logo.draw(self.window_surface)

	def show_menu(self):
		self.menu_transition.handle_menu_transition(self.active_menu[-1])
		self.active_menu[-1].update()
		self.active_menu[-1].draw(self.window_surface)

	def on_exit(self):
		if self.next_screen == None:
			# We save the settings before we quit.
			settings.save()
			graphics.save()
			pygame.quit()
			sys.exit()
		else:
			self.next_screen(self.window_surface, self.main_clock)