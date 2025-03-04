__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import gui.menu as menu

"""

A variant of the menu. Displays items in a top to bottom fashion.

"""

class ListMenu(menu.Menu):

	def position_item(self, item):
		item.x = self.x - (item.get_width() / 2.0)
		item.y = self.y + ((item.get_height() * 2.0) * self.items.index(item))
