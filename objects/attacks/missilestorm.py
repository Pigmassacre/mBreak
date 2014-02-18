__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.attacks.attack as attack
import objects.minimissile as minimissile
import objects.groups as groups
import settings.settings as settings

"""

MissileStorm.

"""

class MissileStorm(attack.Attack):

	def __init__(self, owner):
		# We start by calling the superconstructor.
		super(MissileStorm, self).__init__(owner)

		self.missiles_to_shoot = 0
		self.missile_shoot_time = 125
		self.time_passed = 0

	def reset(self):
		self.missiles_to_shoot = 0
		self.time_passed = 0

	def attack(self):
		if self.owner.energy == 100:
			self.missiles_to_shoot += 40
		elif self.owner.energy >= 80:
			self.missiles_to_shoot += 20
		elif self.owner.energy >= 60:
			self.missiles_to_shoot += 15
		elif self.owner.energy >= 40:
			self.missiles_to_shoot += 10
		elif self.owner.energy >= 20:
			self.missiles_to_shoot += 5

		if self.owner.energy >= 20:
			self.owner.energy = 0

	def shoot_missile(self):
		# Create a list of all available blocks to target.
		block_list = []
		attack_paddle = None
		for player in groups.Groups.player_group:
			if player != self.owner:
				block_list = player.block_group.sprites()
			else:
				for paddle in player.paddle_group:
					attack_paddle = paddle

		# Create a missile that homes in on a random block in the block list.
		if len(block_list) > 0:
			minimissile.MiniMissile(attack_paddle.rect.centerx, attack_paddle.rect.centery, random.uniform(0, 2*math.pi), self.owner, random.choice(block_list))

	def update(self, main_clock):
		if self.missiles_to_shoot > 0:
			self.time_passed += main_clock.get_time()
			if self.time_passed >= self.missile_shoot_time:
				self.time_passed = 0
				self.shoot_missile()
				self.missiles_to_shoot -= 1
