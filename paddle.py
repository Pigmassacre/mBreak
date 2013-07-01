__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame

class Paddle:

	def __init__(self, x, y, width, height, velocity):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.velocity = velocity
