__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import gui.textitem as textitem
import settings.settings as settings

"""

This class is a simple GUI-item that creates a textitem at a given (or default) position that can then be
activated for a short duration by calling the start method. You must take care of drawing the toast yourself,
but calling the update_and_draw method in your gameloop.

"""

class Toast:

	# We default to positioning the toast in the top-left corner of the screen.
	x = 0
	y = 0

	# Default color is red, since the toast is supposed to be a "warning" message.
	text_color = pygame.Color(255, 0, 0)

	def __init__(self, message, duration, main_clock):
		# We use the main clock to keep track of the time passed.
		self.main_clock = main_clock

		# We keep track of the time passed so we know when to destroy the toast.
		self.time_passed = 0

		# The toast is destroyed when time_passed equals duration.
		self.duration = duration

		# The toast keeps going until done is True. We start by setting done to True so the
		# toast isn't shown.
		self.done = True

		# We load a TextItem to display the message.
		self.message = textitem.TextItem(message, Toast.text_color)

		self.x = Toast.x
		self.y = Toast.y

	def get_width(self):
		return self.message.get_width()

	def get_height(self):
		return self.message.get_height()

	def start(self):
		# Essentially "resets" the toast.
		self.done = False
		self.time_passed = 0

	def update(self):
		if not self.done:
			self.message.x = self.x
			self.message.y = self.y

			self.time_passed += self.main_clock.get_time()
			if self.time_passed > self.duration:
				self.done = True

	def draw(self, surface):
		if self.time_passed <= self.duration and not self.done:
			self.message.draw(surface)