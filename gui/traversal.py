__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *

def traverse_menus(event, list_of_menus):
	if event.type == KEYDOWN and event.key == K_RETURN:
		# If it is a list, check through all menus in the list.
		for a_menu in list_of_menus:
			for item in a_menu.items:
				# And for the first selected item we find, we call the matching function.
				if item.selected:
					a_menu.functions[item](item)
	elif event.type == KEYDOWN and event.key == K_LEFT:
		# We try to traverse the menu to the left.
		select_left_or_right(list_of_menus, True)
	elif event.type == KEYDOWN and event.key == K_RIGHT:
		# To the right...
		select_left_or_right(list_of_menus, False)
	elif event.type == KEYDOWN and event.key == K_UP:
		# Up...
		select_up_or_down(list_of_menus, True)
	elif event.type == KEYDOWN and event.key == K_DOWN:
		# Or down.
		select_up_or_down(list_of_menus, False)

def select_left_or_right(list_of_menus, left):
	# First, we want to get the selected item and fill up a list of possible items to traverse to.
	selected_item = get_selected_item(list_of_menus)
	list_of_possible = fill_list_of_possible(list_of_menus)

	# Depending on if we're going left or right, we filter in different ways.
	if left:
		# If we're going left, we only want the items that have an x-value SMALLER than our selected items x-value.
		list_of_possible = filter(lambda x: x.x < selected_item.x, list_of_possible)
	else:
		# If we're going right, we only want the items that have an x-value LARGER than our selected items x-value.
		list_of_possible = filter(lambda x: x.x > selected_item.x, list_of_possible)

	# Find out if there if any of the possible items are in the same menu as the selected item. If they are
	# we only care about those items.
	same_menu_items = list(list_of_possible)
	for a_menu in list_of_menus:
		same_menu_items = filter(lambda x: x in a_menu.items, same_menu_items)

	if len(list_of_possible) > 0:
		# If there are any items left, we want to retain the item which has the least y-difference AND least x-difference.
		if len(same_menu_items) == 0:
			# However, we only care about the y-difference if we're traveling from one menu to another.
			least_y_difference = 999999
			for an_item in list_of_possible:
				# Find the least y difference.
				if abs(an_item.y - selected_item.y) < least_y_difference:
					least_y_difference = abs(an_item.y - selected_item.y)

			# We want to retain the items which have a y-difference equal to the least y-difference.
			list_of_possible = filter(lambda x: abs(x.y - selected_item.y) == least_y_difference, list_of_possible)
		else:
			# If we're traveling within the same menu, we only care about those menu items and the x-positions.
			list_of_possible = same_menu_items
		
		least_x_difference = 999999
		for an_item in list_of_possible:
			# Find the least x difference.
			if abs(an_item.x - selected_item.x) < least_x_difference:
				least_x_difference = abs(an_item.x - selected_item.x)

		# From these remaining items, we want to pick the item which has the least x difference.
		list_of_possible = filter(lambda x: abs(x.x - selected_item.x) == least_x_difference, list_of_possible)
		
		# Finally, we unselect the selected item, and then select the first item in the FINAL list of possible items. This list
		# SHOULD only ever contain one item, but if it does contain more for some reason we just pick the first.
		selected_item.selected = False
		list_of_possible[0].selected = True

def select_up_or_down(list_of_menus, up):
	# First, we want to get the selected item and fill up a list of possible items to traverse to.
	selected_item = get_selected_item(list_of_menus)
	list_of_possible = fill_list_of_possible(list_of_menus)

	# Depending on if we're going up or down, we want to filter in different ways.
	if up:
		# If we're going up, we only want the items which have a y-value SMALLER than the selected item.
		list_of_possible = filter(lambda x: x.y < selected_item.y, list_of_possible)
	else:
		# If we're going down, we only want the items which have a y-value LARGER than the selected item.
		list_of_possible = filter(lambda x: x.y > selected_item.y, list_of_possible)

	# Find out if there if any of the possible items are in the same menu as the selected item.
	same_menu_items = list(list_of_possible)
	for a_menu in list_of_menus:
		same_menu_items = filter(lambda x: x in a_menu.items, same_menu_items)

	if len(list_of_possible) > 0:
		# If there are any items left, we want to retain the item which has the least y-difference AND least x-difference.
		if len(same_menu_items) == 0:
			# However, we only care about the x difference if we're traveling from one menu to another.
			least_x_difference = 999999
			for an_item in list_of_possible:
				# Find the least x difference.
				if abs(an_item.x - selected_item.x) < least_x_difference:
					least_x_difference = abs(an_item.x - selected_item.x)

			# We want to retain the items which have a x-difference equal to the least x-difference.
			list_of_possible = filter(lambda x: abs(x.x - selected_item.x) == least_x_difference, list_of_possible)
		else:
			# If we're traveling within the same menu, we only care about the items in that menu and the y-positions.
			list_of_possible = same_menu_items

		least_y_difference = 999999
		for an_item in list_of_possible:
			# Find the least y difference.
			if abs(an_item.y - selected_item.y) < least_y_difference:
				least_y_difference = abs(an_item.y - selected_item.y)

		# From these remaining items, we want to pick the item which has the least y difference.
		list_of_possible = filter(lambda x: abs(x.y - selected_item.y) == least_y_difference, list_of_possible)
		
		# Finally, we unselect the selected item, and then select the first item in the FINAL list of possible items. This list
		# SHOULD only ever contain one item, but if it does contain more for some reason we just pick the first.
		selected_item.selected = False
		list_of_possible[0].selected = True


def get_selected_item(list_of_menus):
	"""
	Returns the first selected item in the given list_of_menus.
	"""
	for a_menu in list_of_menus:
		for item in a_menu.items:
			if item.selected:
				return item

def fill_list_of_possible(list_of_menus):
	"""
	Returns a list that contains all the items in all the menus in list_of_menus.
	"""
	list_of_possible = []
	for a_menu in list_of_menus:
		for item in a_menu.items:
			list_of_possible.append(item)
	return list_of_possible