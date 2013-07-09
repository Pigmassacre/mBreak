__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
from settings import *

class Background():

	# Load the image files here, so any new instance of this class doesn't have to reload it every time, they can just copy the surface.
	floor_surface = pygame.image.load("res/background/planks_floor.png")
	wall_surface = pygame.image.load("res/background/planks_wall.png")
	
	# Scale them to game_scale.
	floor_surface = pygame.transform.scale(floor_surface, (floor_surface.get_width() * GAME_SCALE, floor_surface.get_height() * GAME_SCALE))
	wall_surface = pygame.transform.scale(wall_surface, (wall_surface.get_width() * GAME_SCALE, wall_surface.get_height() * GAME_SCALE))
