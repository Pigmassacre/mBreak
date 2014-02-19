__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import math
import settings.settings as settings

"""

This is the base class of all items. Items can be selected, chosen or disabled.
Each item is drawn differently depending on these states.

"""

class Item(object):

	width = 16 * settings.GAME_SCALE
	height = 16 * settings.GAME_SCALE

	shadow_color = pygame.Color(50, 50, 50)
	selected_color = pygame.Color(255, 255, 255)
	chosen_color = pygame.Color(200, 200, 200)
	disabled_color = pygame.Color(75, 75, 75, 240)

	shadow_offset_x = 0 * settings.GAME_SCALE
	shadow_offset_y = 1 * settings.GAME_SCALE
	selected_border_size = 2 * settings.GAME_SCALE
	chosen_border_size = 2 * settings.GAME_SCALE

	def __init__(self, color = pygame.Color(128, 128, 128)):
		# An item has a position and size.
		self.x = 0
		self.y = 0
		self.width = self.__class__.width
		self.height = self.__class__.height

		# There a a couple of different states an item can be in. We store whether or not the item is those states here.
		self.selected = False
		self.chosen = False
		self.disabled = False

		# All these states have different colors.
		self.color = color
		self.shadow_color = self.__class__.shadow_color
		self.shadow_offset_x = self.__class__.shadow_offset_x
		self.shadow_offset_y = self.__class__.shadow_offset_y
		self.selected_color = self.__class__.selected_color
		self.chosen_color = self.__class__.chosen_color
		self.disabled_color = self.__class__.disabled_color

		# Create the rect used for drawing the item.
		self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
		self.selected_rect = pygame.rect.Rect(self.x - (self.__class__.selected_border_size / 2), self.y - (self.__class__.selected_border_size / 2), self.width + self.__class__.selected_border_size, self.height + self.__class__.selected_border_size)
		self.chosen_rect = pygame.rect.Rect(self.x - (self.__class__.chosen_border_size / 2), self.y - (self.__class__.chosen_border_size / 2), self.width + self.__class__.chosen_border_size, self.height + self.__class__.chosen_border_size)
		self.shadow_rect = pygame.rect.Rect(self.x + self.shadow_offset_x, self.y + self.shadow_offset_y, self.width, self.height)

		# We create a surface used to handle alpha blitting.
		self.surface = pygame.Surface((self.rect.width, self.rect.height), pygame.locals.SRCALPHA)

		# These values are used to animate the items.
		self.x_nudge = 0
		self.y_nudge = 0
		self.max_x_nudge = 2 * settings.GAME_SCALE
		self.max_y_nudge = 2 * settings.GAME_SCALE
		self.x_nudge_retreat_speed = 0.1 * settings.GAME_FPS * settings.GAME_SCALE
		self.y_nudge_retreat_speed = 0.1 * settings.GAME_FPS * settings.GAME_SCALE
		self.time_passed = 0
		
	def get_width(self):
		return self.rect.width

	def get_height(self):
		return self.rect.height

	def update(self, main_clock):
		if self.selected:
			#self.x_nudge = -((math.sin(self.time_passed * 0.0075) + 1) / 2.0) * self.max_x_nudge
			self.y_nudge = -((math.sin(self.time_passed * 0.0075) + 1) / 2.0) * self.max_y_nudge
			self.time_passed += main_clock.get_time()
		else:
			self.time_passed = 0
			if self.y_nudge < 0:
				self.y_nudge += self.y_nudge_retreat_speed * main_clock.delta_time
				if self.y_nudge > 0:
					self.y_nudge = 0
			elif self.y_nudge > 0:
				self.y_nudge -= self.y_nudge_retreat_speed * main_clock.delta_time
				if self.y_nudge < 0:
					self.y_nudge = 0

		if self.x_nudge < -self.max_x_nudge:
			self.x_nudge = -self.max_x_nudge
		elif self.x_nudge > self.max_x_nudge:
			self.x_nudge = self.max_x_nudge

		if self.y_nudge < -self.max_y_nudge:
			self.y_nudge = -self.max_y_nudge
		elif self.y_nudge > self.max_y_nudge:
			self.y_nudge = self.max_y_nudge

		# Update the position of the rects.
		self.rect.x = self.x + self.x_nudge
		self.rect.y = self.y + self.y_nudge
		self.selected_rect.x = self.x - (self.__class__.selected_border_size / 2.0) + self.x_nudge
		self.selected_rect.y = self.y - (self.__class__.selected_border_size / 2.0) + self.y_nudge
		self.chosen_rect.x = self.x - (self.__class__.chosen_border_size / 2.0) + self.x_nudge
		self.chosen_rect.y = self.y - (self.__class__.chosen_border_size / 2.0) + self.y_nudge
		self.shadow_rect.x = self.x + self.shadow_offset_x + self.x_nudge
		self.shadow_rect.y = self.y + self.shadow_offset_y + self.y_nudge
			
	def draw(self, surface):
		# Draw the shadow.
		surface.fill(self.shadow_color, self.shadow_rect)

		# If chosen, draw the chosen border around the item.
		if self.chosen:
			surface.fill(self.chosen_color, self.chosen_rect)

			# If also selected, draw a smaller selected border around the item.
			if self.selected:
				surface.fill(self.selected_color, self.rect)

		elif self.selected:
			# If selected, draw the selected border around the item.
			surface.fill(self.selected_color, self.selected_rect)

		# Draw the color of the item.
		surface.fill(self.color, self.rect)

		#self.draw_before_disabled(self, surface)

		if self.disabled:
			# If we're disabled, we draw the disabled color.
			self.surface.fill(self.disabled_color)
			surface.blit(self.surface, self.rect)

	def draw_before_disabled(self, surface):
		pass