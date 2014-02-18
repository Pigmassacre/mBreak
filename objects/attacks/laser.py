__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.attacks.attack as attack
import objects.laserbeam as laserbeam
import objects.groups as groups
import settings.settings as settings

"""

Laser.

"""

class Laser(attack.Attack):

	def __init__(self, owner):
		# We start by calling the superconstructor.
		super(Laser, self).__init__(owner)

		self.time_passed = 0
		self.laserbeam_duration = 0

		self.laserbeam = None

	def reset(self):
		pass

	def attack(self):
		if self.laserbeam is None:
			print("creating new laserbeam")
			self.laserbeam = laserbeam.Laserbeam(self.owner)
		self.laserbeam_duration += 1000
		self.owner.energy = 0
		print("duration set to " + str(self.laserbeam_duration))

	def update(self, main_clock):
		if not self.laserbeam is None:
			self.time_passed += main_clock.get_time()
			if self.time_passed >= self.laserbeam_duration:
				print("destroying laserbeam")
				self.laserbeam.destroy()
				self.laserbeam = None