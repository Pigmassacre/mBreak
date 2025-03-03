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
		self.laserbeam = None

	def reset(self):
		# Make sure to destroy any existing laserbeam
		if self.laserbeam is not None:
			self.laserbeam.destroy()
			self.laserbeam = None

	def attack(self):
		if self.laserbeam is None:
			# Store the current energy level before creating the laserbeam
			energy_level = self.owner.energy
			
			# Only create a laserbeam if we have at least 20 energy
			if energy_level >= 20:
				# Create the laserbeam with a power level based on energy
				power_level = 1.0
				duration = 0
				energy_to_spend = 0
				if energy_level == 100:
					power_level = 5.0
					duration = 2000
					energy_to_spend = 100
				elif energy_level >= 80:
					power_level = 4.0
					duration = 1800
					energy_to_spend = 80
				elif energy_level >= 60:
					power_level = 3.0
					duration = 1600
					energy_to_spend = 60
				elif energy_level >= 40:
					power_level = 2.0
					duration = 1400
					energy_to_spend = 40
				elif energy_level >= 20:
					power_level = 1.0
					duration = 1000
					energy_to_spend = 20
				
				self.laserbeam = laserbeam.Laserbeam(self.owner, power_level, duration)
				
				# Reset energy to 0
				self.owner.energy = 0
		else:
			# If laserbeam already exists, we can extend its duration if we have energy
			if self.owner.energy >= 20:
				# Add duration based on current energy
				energy_to_spend = 0
				if self.owner.energy == 100:
					self.laserbeam.duration += 2500
					energy_to_spend = 100
				elif self.owner.energy >= 80:
					self.laserbeam.duration += 2000
					energy_to_spend = 80
				elif self.owner.energy >= 60:
					self.laserbeam.duration += 1500
					energy_to_spend = 60
				elif self.owner.energy >= 40:
					self.laserbeam.duration += 1000
					energy_to_spend = 40
				elif self.owner.energy >= 20:
					self.laserbeam.duration += 500
					energy_to_spend = 20
					
				self.owner.energy = 0

	def update(self, main_clock):
		if self.laserbeam is not None:
			# Check if the laserbeam is still alive
			if not self.laserbeam.alive():
				self.laserbeam = None