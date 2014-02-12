__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import other.debug as debug
import gui.textitem as textitem
import gui.logo as logo
import gui.menu as menu
import gui.gridmenu as gridmenu
import gui.transition as transition
import gui.traversal as traversal
import settings.settings as settings
import settings.graphics as graphics
import screens.scene as scene

# These are the screens we can reach directly from the main menu, so we import them here.
import screens.preparemenu as preparemenu
import screens.helpmenu as helpmenu
import screens.aboutmenu as aboutmenu

"""

This is the main menu of the game. From here, we can either continue to the preparation menu, we can change a few graphic options,
or we can reach the help menu or the about menu. We can also quit the game, of course.

The main menu is easily added upon. It has an active_menu object that makes sure that we only display and update/handle the currently active
submenu.

If either the quit button is activated or the ESCAPE key is pressed, we quit the game.

"""

class MainMenu(scene.Scene):

	def __init__(self, window_surface, main_clock, title_logo = None):
		# Call the superconstructor.
		scene.Scene.__init__(self, window_surface, main_clock)

		# The next screen to be started when the gameloop ends.
		self.next_screen = preparemenu.PrepareMenu

		# Setup the logo and the variables needed to handle the animation of it.
		self.setup_logo(title_logo)
		self.logo_desired_position = ((settings.SCREEN_WIDTH - self.title_logo.get_width()) / 2, ((settings.SCREEN_HEIGHT - self.title_logo.get_height()) / 4))
		self.logo_transition = transition.Transition(self.main_clock)
		self.logo_transition.speed = 120 * settings.GAME_SCALE

		# Setup all the menu buttons.
		self.setup_main_menu()
		self.setup_options_menu()
		self.setup_graphics_menu()

		# Set the menu to actually display.
		self.active_menu = [self.main_menu]

		# Setup the menu transitions.
		self.menu_transition = transition.Transition(self.main_clock)
		self.menu_transition.setup_odd_even_transition(self.active_menu[-1], True, True, False, False)

		# Setup and play music.
		self.setup_music()

		# And finally, start the gameloop!
		self.gameloop()

	def setup_main_menu(self):
		self.main_menu = self.setup_menu()
		self.main_menu.add(textitem.TextItem("Start"), self.start)
		self.main_menu.add(textitem.TextItem("Options"), self.options)
		self.main_menu.add(textitem.TextItem("Help"), self.help)
		self.main_menu.add(textitem.TextItem("Quit"), self.quit)
		self.main_menu.items[0].selected = True

	def options(self, item):
		self.active_menu.append(self.options_menu)
		self.menu_transition.setup_odd_even_transition(self.active_menu[-1], True, True, False, False)

	def setup_options_menu(self):
		self.options_menu = self.setup_menu()
		self.options_menu.add(textitem.TextItem("Graphics"), self.graphics)
		self.options_menu.add(textitem.TextItem("About"), self.about)
		self.options_menu.add(textitem.TextItem("Back"), self.back)
		self.options_menu.items[0].selected = True

	def graphics(self, item):
		self.active_menu.append(self.graphics_menu)
		self.menu_transition.setup_odd_even_transition(self.active_menu[-1], True, True, False, False)
		
		# Move the logo so the graphics menu has enough space.
		self.logo_desired_position = ((settings.SCREEN_WIDTH - self.title_logo.get_width()) / 2, ((settings.SCREEN_HEIGHT - self.title_logo.get_height()) / 4) - self.graphics_menu_offset)

	def help(self, item):
		self.done = True
		self.next_screen = helpmenu.HelpMenu

	def about(self, item):
		self.done = True
		self.next_screen = aboutmenu.AboutMenu

	def setup_graphics_menu(self):
		self.graphics_menu = self.setup_menu()

		# Setup the buttons and make them "on/off" buttons.
		shadows_button = textitem.TextItem("Shadows On")
		shadows_button.setup_is_on_off("Shadows Off", graphics.SHADOWS)
		self.graphics_menu.add(shadows_button, self.shadows)

		particles_button = textitem.TextItem("Particles On")
		particles_button.setup_is_on_off("Particles Off", graphics.PARTICLES)
		self.graphics_menu.add(particles_button, self.particles)

		flashes_button = textitem.TextItem("Flashes On")
		flashes_button.setup_is_on_off("Flashes Off", graphics.FLASHES)
		self.graphics_menu.add(flashes_button, self.flashes)

		traces_button = textitem.TextItem("Traces On")
		traces_button.setup_is_on_off("Traces Off", graphics.TRACES)
		self.graphics_menu.add(traces_button, self.traces)
		
		traces_button = textitem.TextItem("Background On")
		traces_button.setup_is_on_off("Background Off", graphics.BACKGROUND)
		self.graphics_menu.add(traces_button, self.background)
		
		# We store the graphics offset so we can offset the logo by this later.
		self.graphics_menu_offset = (shadows_button.get_height() * 3)
		self.graphics_menu.y = (settings.SCREEN_HEIGHT / 2) - self.graphics_menu_offset

		# We add a back button to the menu.
		self.graphics_menu.add(textitem.TextItem("Back"), self.back)
		self.graphics_menu.items[0].selected = True

	def shadows(self, item):
		graphics.SHADOWS = item.toggle_on_off()

	def particles(self, item):
		graphics.PARTICLES = item.toggle_on_off()

	def flashes(self, item):
		graphics.FLASHES = item.toggle_on_off()

	def traces(self, item):
		graphics.TRACES = item.toggle_on_off()
		
	def background(self, item):
		graphics.BACKGROUND = item.toggle_on_off()

	def setup_logo(self, title_logo):
		if title_logo == None:
			# If the title_logo object doesn't exists, creates it and positions it.
			self.title_logo = logo.Logo()
			
			self.title_logo.x = (settings.SCREEN_WIDTH - self.title_logo.get_width()) / 2
			self.title_logo.y = ((settings.SCREEN_HEIGHT - self.title_logo.get_height()) / 4)
			
			self.title_logo.play()
		else:
			# Otherwise, we just save the given title_logo object
			self.title_logo = title_logo
	
	def setup_menu(self):
		# Returns a menu that is positioned in the center of the screen.
		return menu.Menu(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2)

	def setup_music(self):
		if not pygame.mixer.music.get_busy():
			# We only care about loading and playing the music if it isn't already playing.
			pygame.mixer.music.load(settings.TITLE_MUSIC)
			pygame.mixer.music.play(-1)

	def start(self, item):
		self.done = True
		self.next_screen = preparemenu.PrepareMenu

	def back(self, item):
		self.active_menu.pop()
		self.menu_transition.setup_odd_even_transition(self.active_menu[-1], True, True, False, False)
		
		# Restore the logo's position.
		self.logo_desired_position = ((settings.SCREEN_WIDTH - self.title_logo.get_width()) / 2, ((settings.SCREEN_HEIGHT - self.title_logo.get_height()) / 4))
		
	def quit(self, item):
		# Sets next_screen to None so we just quit the game when the gameloop is over.
		self.done = True
		self.next_screen = None

	def event(self, event):
		if (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == JOYBUTTONDOWN and event.button in settings.JOY_BUTTON_BACK):
			# If the ESCAPE key or back button on gamepad is pressed, we go back a level in the menu system.
			if len(self.active_menu) > 1:
				self.back(None)
			else:
				# If we're at the top level, we select the last item in the main menu, which should be the QUIT button.
				for item in self.main_menu.items:
					item.selected = False
				self.main_menu.items[len(self.main_menu.items) - 1].selected = True
		else:
			# The traverse menus function wants a list of menus, so we simply give it a list of one menu!
			traversal.traverse_menus(event, [self.active_menu[-1]])

	def update(self):
		# Makes sure that the logo always moves to the desired posisition, and stays there.
		self.logo_transition.move_item_to_position(self.title_logo, self.logo_desired_position)

		#  If the logo is in place, show the menu.
		if self.title_logo.x == self.logo_desired_position[0] and self.title_logo.y == self.logo_desired_position[1]:
			# Updates the menu transitions, and the currently active menu.
			self.menu_transition.update()
			self.active_menu[-1].update(self.main_clock)

	def draw(self):
		# Every frame begins by filling the whole screen with the background color.
		self.window_surface.fill(settings.BACKGROUND_COLOR)

		# Draw the title logo.
		self.title_logo.draw(self.window_surface)

		# If the logo is in place, draw the currently active menu to the screen.
		if self.title_logo.x == self.logo_desired_position[0] and self.title_logo.y == self.logo_desired_position[1]:
			self.active_menu[-1].draw(self.window_surface)

	def on_exit(self):
		if self.next_screen == None:
			# We save the settings before we quit.
			settings.save()
			graphics.save()
			pygame.quit()
			sys.exit()
		elif self.next_screen == helpmenu.HelpMenu or self.next_screen == aboutmenu.AboutMenu:
			# We start the help screen or the about screen and send them a reference to this instance, so they can return to it later.
			# We also setup the transitions, so when they return they transition in.
			self.menu_transition.setup_odd_even_transition(self.active_menu[-1], True, True, False, False)
			self.next_screen(self.window_surface, self.main_clock, self)
		else:
			# Else, we just start the next screen with the default parameters.
			self.next_screen(self.window_surface, self.main_clock)