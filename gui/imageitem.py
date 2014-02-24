__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import copy
import math
import objects.shadow as shadow
import gui.item as item
import settings.settings as settings

"""

This is an item that, much like TextItem, can be displayed either by itself or added to a menu. It's a 
filled rectangle with an image in the middle of it. It can, much like the other items, we selected and / or chosen.

"""

class ImageItem(item.Item):

	def __init__(self, path, color = pygame.Color(128, 128, 128)):
		super(ImageItem, self).__init__(color)

		# Values can be stored here, for when you want to retrieve it later (via chosing the item, for instance).
		self.value = None

		# Load the image from the path.
		self.image = pygame.image.load(path)

		# Scale image to settings.GAME_SCALE.
		self.image = pygame.transform.scale(self.image, (self.image.get_width() * settings.GAME_SCALE, self.image.get_height() * settings.GAME_SCALE))

	def draw(self, surface):
		super(ImageItem, self).draw(surface)

		# Finally, blit the image to the given surface (on top of everything else drawn in here).
		surface.blit(self.image, ((self.rect.x + (self.rect.width - self.image.get_width()) / 2), self.rect.y + (self.rect.height - self.image.get_height()) / 2))
