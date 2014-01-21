__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame

"""

This module (and class) takes care of the groups used to store and update all the game objects while in-game.

"""

def empty_after_round():
	# Empties all groups but the player group, so that when we want to return to the game again, the players are
	# still intact.
	Groups.ball_group.empty()
	Groups.particle_group.empty()
	Groups.block_group.empty()
	Groups.powerup_group.empty()
	Groups.effect_group.empty()
	Groups.paddle_group.empty()
	Groups.shadow_group.empty()
	Groups.trace_group.empty()
	Groups.dummy_group.empty()

def empty_all():
	# This empties ALL the groups, so this is called when we return to the main menu from the game.
	Groups.player_group.empty()
	empty_after_round()

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

	# Define the group that contains all the effects.
	effect_group = pygame.sprite.Group()

	# Define the group that contains all the paddles.
	paddle_group = pygame.sprite.Group()

	# Define the group that contains all the players.
	player_group = pygame.sprite.Group()

	# Define the group that contains all the shadows.
	shadow_group = pygame.sprite.Group()

	# Define the group that contains all the dummy objects.
	dummy_group = pygame.sprite.Group()
	