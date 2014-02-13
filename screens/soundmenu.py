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
import screens.scene as scene

"""

This is the sound Menu of the game. Here you can set the various sound options.

"""

class SoundMenu(scene.Scene):

	def __init__(self, window_surface, main_clock, title_logo = None):
		# Call the superconstructor.
		scene.Scene.__init__(self, window_surface, main_clock)

		# The next screen to be started when the gameloop ends.
		self.next_screen = None

		# A list of all menus, so we can easily register all menus to all menus (so they know to unselect items in other menus and stuff like that).
		self.all_menus = []

		# Setup all the menu buttons.
		self.setup_sound_menu()

		# The back button, displayed in the middle-bottom of the screen.
		back_button = textitem.TextItem("Back")
		self.back_menu = menu.Menu()
		self.back_menu.x = settings.SCREEN_WIDTH / 2
		self.back_menu.y = settings.SCREEN_HEIGHT - (2 * back_button.get_height())
		self.back_menu.add(back_button, self.back)
		self.back_menu.items[0].selected = True
		self.all_menus.append(self.back_menu)

		# Setup the logo and the variables needed to handle the animation of it.
		self.setup_logo(title_logo)
		self.logo_desired_position = ((settings.SCREEN_WIDTH - self.title_logo.get_width()) / 2, ((settings.SCREEN_HEIGHT - self.title_logo.get_height()) / 4))
		self.logo_transition = transition.Transition(self.main_clock)
		self.logo_transition.speed = 120 * settings.GAME_SCALE

		# Register all menus with each other.
		for a_menu in self.all_menus:
			a_menu.register_other_menus(self.all_menus)

		# Setup the menu transitions.
		self.menu_transition = transition.Transition(self.main_clock)
		self.menu_transition.setup_transition(self.sound_menu, True, True, False, False)
		self.menu_transition.setup_transition(self.back_menu, True, True, False, False)

		# And finally, start the gameloop!
		self.gameloop()

	def setup_sound_menu(self):
		self.sound_menu = menu.Menu(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT / 2)

		# Setup the buttons and make them "on/off" buttons.
		"""sound_button = textitem.TextItem("Sound Effects On")
		sound_button.setup_is_on_off("Sound Effects Off", aaaarrgghh)
		self.sound_menu.add(sound_button, self.sound)"""

		music_button = textitem.TextItem("Music On")
		music_button.setup_is_on_off("Music Off", pygame.mixer.music.get_volume() > 0.0)
		self.sound_menu.add(music_button, self.music)

		self.all_menus.append(self.sound_menu)

	def sound(self, item):
		if item.toggle_on_off():
			pass

	def music(self, item):
		if item.toggle_on_off():
			pygame.mixer.music.set_volume(1.0)
		else:
			pygame.mixer.music.set_volume(0.0)

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

	def back(self, item):
		self.done = True

	def event(self, event):
		if (event.type == KEYDOWN and event.key == K_ESCAPE) or (event.type == JOYBUTTONDOWN and event.button in settings.JOY_BUTTON_BACK):
			# If the ESCAPE key or back button on gamepad is pressed, we go back a level in the menu system.
			self.back(None)
		else:
			traversal.traverse_menus(event, self.all_menus)

	def update(self):
		# Makes sure that the logo always moves to the desired posisition, and stays there.
		self.logo_transition.move_item_to_position(self.title_logo, self.logo_desired_position)

		#  If the logo is in place, show the menu.
		if self.title_logo.x == self.logo_desired_position[0] and self.title_logo.y == self.logo_desired_position[1]:
			# Updates the menu transitions, and the currently active menu.
			self.menu_transition.update()
			for a_menu in self.all_menus:
				a_menu.update(self.main_clock)

	def draw(self):
		# Every frame begins by filling the whole screen with the background color.
		self.window_surface.fill(settings.BACKGROUND_COLOR)

		# Draw the title logo.
		self.title_logo.draw(self.window_surface)

		# If the logo is in place, draw the currently active menu to the screen.
		if self.title_logo.x == self.logo_desired_position[0] and self.title_logo.y == self.logo_desired_position[1]:
			for a_menu in self.all_menus:
				a_menu.draw(self.window_surface)