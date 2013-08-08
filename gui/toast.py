__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import gui.textitem as textitem
from settings.settings import *

class Toast:

	x = 0
	y = 0

	def __init__(self, message, duration, main_clock):
		# We use the main clock to keep track of the time passed.
		self.main_clock = main_clock

		# We keep track of the time passed so we know when to destroy the toast.
		self.time_passed = 0

		# The toast is destroyed when time_passed equals duration.
		self.duration = duration

		# The toast keeps going until done is True.
		self.done = True

		# We load a TextItem to display the message.
		self.message = textitem.TextItem(message)

		self.x = Toast.x
		self.y = Toast.y

	def get_width(self):
		return self.message.get_width()

	def get_height(self):
		return self.message.get_height()

	def start(self):
		self.done = False
		self.time_passed = 0

	def update_and_draw(self, surface):
		if not self.done:
			self.message.x = self.x
			self.message.y = self.y

			self.time_passed += self.main_clock.get_time()
			if self.time_passed <= self.duration:
				self.message.draw(surface)
			else:
				self.done = True
