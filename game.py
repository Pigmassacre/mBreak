__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import math
import random
import debug
import ball
import paddle
import player
import multiball
import block
import groupholder
from settings import *

def create_block(x, y, owner):
	width = 16
	height = 32
	health = 2
	image_path = "res/block/block.png"

	return block.Block(x, y, width, height, health, image_path, owner)

def create_paddle(x, y, owner):
	width = 16
	height = 64
	acceleration = 2
	retardation = 4
	max_speed = 8
	image_path = "res/paddle/paddle.png"

	return paddle.Paddle(x, y, width, height, acceleration, retardation, max_speed, image_path, owner)

def create_player_left():
	name = PLAYER_LEFT_NAME
	key_up = PLAYER_LEFT_KEY_UP
	key_down = PLAYER_LEFT_KEY_DOWN
	color = pygame.Color(255, 0, 0, 255)

	player_left = player.Player(name, key_up, key_down, color)

	return player_left

def create_player_right():
	name = PLAYER_RIGHT_NAME
	key_up = PLAYER_RIGHT_KEY_UP
	key_down = PLAYER_RIGHT_KEY_DOWN
	color = pygame.Color(0, 0, 255, 255)

	player_right = player.Player(name, key_up, key_down, color)
	
	return player_right

def create_background():
	width = 64
	height = 64
	tile_width = SCREEN_WIDTH / width
	tile_height = SCREEN_HEIGHT / height
	image_path = "res/background/background_3.png"
	image_surface = pygame.image.load(image_path)
	image_surface = pygame.transform.scale(image_surface, (width, height))

	surface = pygame.Surface((width * tile_width, height * tile_height))
	for x in range(0, tile_width):
		for y in range(0, tile_height):
			surface.blit(image_surface, (x * width, y * height))

	return surface

"""
I should come up with a good way to handle the sprite groups and stick to it.
I can either pass the groups to each method/class as they are needed, or I can have 
a global groupholder module that holds all the groups.
"""
def destroy_groups():
	groupholder.ball_group.empty()
	groupholder.particle_group.empty()
	groupholder.block_group.empty()
	groupholder.powerup_group.empty()
	groupholder.paddle_group.empty()
	groupholder.player_group.empty()
	groupholder.shadow_group.empty()

def main(window_surface, main_clock, debug_font):
	# Variable to keep the gameloop going. Setting this to True will end the gameloop and return to the screen that started this gameloop.
	done = False

	# Create the background image and store it.
	background = create_background()

	# Create the left player.
	player_left = create_player_left()
	# Create and store the players paddle.
	paddle_left = create_paddle(16 * 6, (SCREEN_HEIGHT - 64) / 2, player_left)
	
	# Create the right player.
	player_right = create_player_right()
	# Create and store the players paddle. Flipped.
	paddle_right = create_paddle(SCREEN_WIDTH - 16 * 7, (SCREEN_HEIGHT - 64) / 2, player_right)
	paddle_right.image = pygame.transform.flip(paddle_right.image, True, False)

	# Spawn some blocks.
	for i in range(0, 3):
		for j in range(0, 13):
			create_block(32 + (16 * i), 32 + (32 * j), player_left)
			# Create a flipped right block.
			temp_block_right = create_block((SCREEN_WIDTH - 48) - (16 * i), 32 + (32 * j), player_right)
			temp_block_right.image = pygame.transform.flip(temp_block_right.image, True, False)

	while not done:
		# Begin a frame by blitting the background to the window_surface.
		window_surface.blit(background, (0, 0))
		
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				# Return to intromenu.
				destroy_groups()
				done = True
			elif event.type == KEYDOWN and event.key == K_l:
				debug.create_ball_left(player_left, paddle_left)
			elif event.type == KEYDOWN and event.key == K_r:
				debug.create_ball_right(player_right, paddle_right)
			elif event.type == KEYDOWN and event.key == K_p:
				debug.create_powerup()
		
		# If debug mode is enabled, allow certain commands. This is all done in the debug module.
		if DEBUG_MODE:
			debug.update(player_left, player_right, paddle_left, paddle_right)

		# Update the balls.
		groupholder.ball_group.update()

		# Update the particles.
		groupholder.particle_group.update()

		# Update the players.
		groupholder.player_group.update()

		# Update the shadows.
		groupholder.shadow_group.update(main_clock)

		# Draw the shadows.
		for shadow in groupholder.shadow_group:
			shadow.blit_to(window_surface)

		# Draw the blocks.
		groupholder.block_group.draw(window_surface)

		# Draw the paddles.
		groupholder.paddle_group.draw(window_surface)

		# Draw the powerups.
		groupholder.powerup_group.draw(window_surface)

		# Draw the particles.
		for particle in groupholder.particle_group:
			window_surface.fill(particle.color, particle.rect)

		# Draw the balls.
		groupholder.ball_group.draw(window_surface)

		# Draw the players.
		# groupholder.player_group.draw(window_surface)

		if DEBUG_MODE:
			# Display various debug information.
			debug.display(window_surface, main_clock, debug_font)
		
		pygame.display.update()
		
		# Finally, constrain the game to a set maximum amount of FPS.
		main_clock.tick(MAX_FPS)