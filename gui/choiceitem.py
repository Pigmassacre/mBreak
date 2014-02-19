__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
import copy
import objects.shadow as shadow
import gui.item as item
import settings.settings as settings

"""

This is an item that, much like the other items, can be displayed on its on or added to a menu. It can be selected and / or chosen, much
like the other items. The thing about this item is that a font item is displayed in the middle of this item.


"""

class ChoiceItem(item.Item):

	# Initialize the font module.
	pygame.font.init()

	# The standard text values are stored here, such as standard font, font size and so on.
	font_path = "fonts/ADDLG___.TTF"
	font_size = 9 * settings.GAME_SCALE
	font = pygame.font.Font(font_path, font_size)

	def __init__(self, value, color = pygame.Color(128, 128, 128), font_color = pygame.Color(255, 255, 255), alpha_value = 255):
		super(ChoiceItem, self).__init__(color)

		# Setup font values.
		self.font = self.__class__.font
		self.font_color = font_color
		self.value = value
		self.alpha_value = alpha_value

		# Render the font surface.
		self.font_surface = self.font.render(str(self.value), False, self.font_color)
		self.font_surface.set_alpha(self.alpha_value)
		
		# Setup the color values.
		self.color = copy.copy(color)

	def draw(self, surface):
		super(ChoiceItem, self).draw(surface)

		# Draw the font surface in the middle of this item.
		surface.blit(self.font_surface, ((self.rect.x + (self.rect.width - self.font_surface.get_width()) / 2) + 0.5 * settings.GAME_SCALE, self.rect.y + (self.rect.height - self.font_surface.get_height()) / 2))
