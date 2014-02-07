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

		self.shake_group = pygame.sprite.Group()

	def shake(self, duration, intensity):
		self.shake_group.add(CameraShake(self, duration, intensity))

	def update(self, main_clock):
		self.x = self.origin_x
		self.y = self.origin_y
		
		self.shake_group.update(main_clock)

class CameraShake(pygame.sprite.Sprite):

	def __init__(self, camera, duration, intensity):
		pygame.sprite.Sprite.__init__(self)

		self.camera = camera
		self.time_left = duration
		self.intensity = intensity
		self.time_passed = 0

		self.x_shake_amount = 0
		self.y_shake_amount = 0

	def update(self, main_clock):
		if self.time_left > 0:
			self.time_passed += main_clock.delta_time
			
			# Only shake GAME_FPS amount of times per second. (If time_scale slows down, we shake less often).
			if self.time_passed > (1 / float(settings.GAME_FPS)):
				self.x_shake_amount = random.uniform(-1, 1) * self.intensity * settings.GAME_SCALE
				self.y_shake_amount = random.uniform(-1, 1) * self.intensity * settings.GAME_SCALE

				# Reset time passed to 0, since we've just shook the screen.
				self.time_passed = 0

			# Offset the cameras position by the last set shake amount.
			self.camera.x += self.x_shake_amount
			self.camera.y += self.y_shake_amount
		else:
			self.kill()

		self.time_left -= main_clock.get_time()