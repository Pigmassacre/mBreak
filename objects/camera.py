__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import random
import settings.settings as settings

CAMERA = None

def create_camera(x, y, width, height):
	global CAMERA
	CAMERA = Camera(x, y, width, height)

class Camera():

	def __init__(self, x, y, width, height):
		self.x = x
		self.y = y
		self.width = width
		self.height = height

		self.origin_x = self.x
		self.origin_y = self.y

		self.shake_time_left = 0
		self.shake_duration = 0
		self.shake_intensity = 0
		self.shake_x_nudge = 0
		self.shake_y_nudge = 0

	def shake(self, duration, intensity):
		self.shake_time_left = duration
		self.shake_duration = duration
		self.shake_intensity = intensity

	def update(self, main_clock):
		if self.shake_time_left > 0:
			self.shake_time_left -= main_clock.get_time()

			self.shake_x_nudge = random.uniform(-1, 1) * self.shake_intensity * settings.GAME_SCALE
			self.shake_y_nudge = random.uniform(-1, 1) * self.shake_intensity * settings.GAME_SCALE
		else:
			self.shake_x_nudge = 0
			self.shake_y_nudge = 0

		self.x = self.origin_x + self.shake_x_nudge
		self.y = self.origin_y + self.shake_y_nudge