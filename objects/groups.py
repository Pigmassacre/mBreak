__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame

def empty_after_round():
	Groups.ball_group.empty()
	Groups.particle_group.empty()
	Groups.block_group.empty()
	Groups.powerup_group.empty()
	Groups.paddle_group.empty()
	Groups.shadow_group.empty()
	Groups.trace_group.empty()

def empty_all():
	Groups.ball_group.empty()
	Groups.particle_group.empty()
	Groups.block_group.empty()
	Groups.powerup_group.empty()
	Groups.paddle_group.empty()
	Groups.player_group.empty()
	Groups.shadow_group.empty()
	Groups.trace_group.empty()

class Groups:

	# Define the group that contains all the balls.
	ball_group = pygame.sprite.Group()

	# Define the group that contains all the particles.
	particle_group = pygame.sprite.Group()

	# Define the group that contains all the traces.
	trace_group = pygame.sprite.Group()

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
	