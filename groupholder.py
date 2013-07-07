__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
from settings import *

# Define the group that contains all the balls.
ball_group = pygame.sprite.Group()

# Define the group that contains all the particles.
particle_group = pygame.sprite.Group()

# Define the group that contains all the blocks.
block_group = pygame.sprite.Group()

# Define the group that contains all the powerups.
powerup_group = pygame.sprite.Group()

# Define the group that contains all the paddles.
paddle_group = pygame.sprite.Group()

# Define the group that contains all the players.
player_group = pygame.sprite.Group()

# Define the group that contains all the shadows.
shadow_group = pygame.sprite.Group()