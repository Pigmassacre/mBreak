__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import math
from libs import pyganim

class Logo:

	def __init__(self):
		self.logo = pyganim.PygAnimation([("res/logo/mBreakTitle_01.png", 1.00),
											("res/logo/mBreakTitle_02.png", 0.075),
											("res/logo/mBreakTitle_03.png", 0.075),
											("res/logo/mBreakTitle_04.png", 0.075),
											("res/logo/mBreakTitle_05.png", 0.075),
											("res/logo/mBreakTitle_06.png", 0.075),
											("res/logo/mBreakTitle_07.png", 0.075),
											("res/logo/mBreakTitle_01.png", 1.00),
											("res/logo/mBreakTitle_07.png", 0.075),
											("res/logo/mBreakTitle_06.png", 0.075),
											("res/logo/mBreakTitle_05.png", 0.075),
											("res/logo/mBreakTitle_04.png", 0.075),
											("res/logo/mBreakTitle_03.png", 0.075),
											("res/logo/mBreakTitle_02.png", 0.075)])
		self.x = 0
		self.y = 0

	def play(self):
		self.logo.play()

	def pause(self):
		self.logo.pause()

	def stop(self):
		self.logo.stop()

	def get_width(self):
		return self.logo.getMaxSize()[0]

	def get_height(self):
		return self.logo.getMaxSize()[1]