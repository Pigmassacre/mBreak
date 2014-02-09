__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import settings.settings as settings
import settings.graphics as graphics
import screens.scene as scene

# We need to be able to proceed to the intromenu, so we import it.
import screens.intromenu as intromenu

"""

This class takes care of displaying the Splash that is displayed when you start the game.
It's nothing fancy, it just splits the splash image into two parts and moves them back and forth across the screen.
They cross once, and the second time they're supposed to cross the join to form a complete image, revealing the mighty
"Pigmassacre"! ;P

"""

class Splash(scene.Scene):

	# The splash image is loaded, scaled so it fits the SCREEN_HEIGHT and then split into two halves.
	splash = pygame.image.load("res/splash/splash_color.png")
	splash = pygame.transform.scale(splash, (settings.SCREEN_HEIGHT, settings.SCREEN_HEIGHT))
	splash_top_half = splash.subsurface(pygame.Rect((0, 0), (splash.get_width(), splash.get_height() / 2)))
	splash_bottom_half = splash.subsurface(pygame.Rect((0, (splash.get_height()) / 2), (splash.get_width(), splash.get_height() / 2)))

	# These are the values that affect the movement of the splash images.
	splash_time = 1750
	top_half_speed = 600 * settings.GAME_SCALE
	bottom_half_speed = -600 * settings.GAME_SCALE

	# We use this instead of the standard background color (even if they happen to be the same) since we always want the background to
	# be black here.
	background_color = pygame.Color(0, 0, 0)

	def __init__(self, window_surface, main_clock):
		# Call the superconstructor.
		scene.Scene.__init__(self, window_surface, main_clock)

		# This is the position that the full image has (it's in the middle of the screen).
		self.x = (settings.SCREEN_WIDTH - Splash.splash.get_width()) / 2
		self.y = (settings.SCREEN_HEIGHT - Splash.splash.get_height()) / 2

		# These are the positions of the two halves at the start.
		self.top_half_x = -Splash.splash_top_half.get_width()
		self.top_half_y = (settings.SCREEN_HEIGHT - Splash.splash.get_height()) / 2
		self.bottom_half_x = settings.SCREEN_WIDTH
		self.bottom_half_y = (settings.SCREEN_HEIGHT / 2)

		# We start by letting the top half to right, and the bottom half go left.
		self.top_go_right = True
		self.bottom_go_left = True

		# These keep track of when both parts have completed their movements.
		self.top_done = False
		self.bottom_done = False

		# Keeps track of how much time has passed.
		self.time_passed = 0

		# And finally we start the gameloop!
		self.gameloop()

	def event(self, event):
		if ((event.type == KEYDOWN and event.key in [K_ESCAPE, K_RETURN]) or 
		   (event.type == JOYBUTTONDOWN and event.button in settings.JOY_BUTTON_SKIP)):
			# If ENTER or ESCAPE or joystick skip button is pressed, we end this loop and proceed to the next screen.
			self.done = True

	def update(self):
		# After a certain amount of time, the splash ends automatically.
		if self.time_passed >= Splash.splash_time:
			self.done = True

		# The following code moves the top half.
		if self.top_go_right:
			self.top_half_x += Splash.top_half_speed * self.main_clock.delta_time
		else:
			self.top_half_x -= Splash.top_half_speed * self.main_clock.delta_time

		if self.top_half_x > (2 * settings.SCREEN_WIDTH) - Splash.splash_top_half.get_width():
			self.top_go_right = False
		elif self.top_half_x <= (settings.SCREEN_WIDTH - Splash.splash_top_half.get_width()) / 2 and not self.top_go_right:
			self.top_half_x = (settings.SCREEN_WIDTH - Splash.splash_top_half.get_width()) / 2
			self.top_done = True

		# And the following moves the bottom half.
		if self.bottom_go_left:
			self.bottom_half_x += Splash.bottom_half_speed * self.main_clock.delta_time
		else:
			self.bottom_half_x -= Splash.bottom_half_speed * self.main_clock.delta_time

		if self.bottom_half_x < -settings.SCREEN_WIDTH:
			self.bottom_go_left = False
		elif self.bottom_half_x >= (settings.SCREEN_WIDTH - Splash.splash_bottom_half.get_width()) / 2 and not self.bottom_go_left:
			self.bottom_half_x = (settings.SCREEN_WIDTH - Splash.splash_bottom_half.get_width()) / 2
			self.bottom_done = True

	def draw(self):
		# Every frame begins by filling the whole screen with the background color.
		self.window_surface.fill(Splash.background_color)

		# And this takes care of displaying either the two bottom halves or the complete image.
		if self.top_done and self.bottom_done:
			self.time_passed += self.main_clock.get_time()
			self.window_surface.blit(Splash.splash, (self.x, self.y))
		else:
			self.window_surface.blit(Splash.splash_top_half, (self.top_half_x, self.top_half_y))
			self.window_surface.blit(Splash.splash_bottom_half, (self.bottom_half_x, self.bottom_half_y))

	def on_exit(self):
		# The gameloop is over, so we proceed to the intromenu!
		intromenu.IntroMenu(self.window_surface, self.main_clock)