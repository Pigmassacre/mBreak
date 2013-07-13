__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import math
import random
import other.debug as debug
import objects.ball as ball
import objects.paddle as paddle
import objects.player as player
import objects.multiball as multiball
import objects.block as block
import objects.groups as groups
from settings.settings import *

# Import any needed game screens here.

def create_block(x, y, owner):
	health = 2
	return block.Block(x, y, health, owner)

def create_strong_block(x, y, owner):
	health = 4
	return block.Block(x, y, health, owner)

def setup_gamefield(player_left, player_right):
	x_amount = 4
	y_amount = (LEVEL_HEIGHT - (block.Block.height * 2)) / block.Block.height

	for x in range(0, 1):
		for y in range(0, y_amount):
			create_strong_block(LEVEL_X + (block.Block.width * 2) + (block.Block.width * x), LEVEL_Y + block.Block.height + (block.Block.height * y), player_left)
			temp_block_right = create_block(LEVEL_MAX_X - (block.Block.width * 3) - (block.Block.width * x), LEVEL_Y + block.Block.height + (block.Block.height * y), player_right)
			temp_block_right.image = pygame.transform.flip(temp_block_right.image, True, False)
	for x in range(0, x_amount):
		for y in range(0, y_amount):
			create_block(LEVEL_X + (block.Block.width * 3) + (block.Block.width * x), LEVEL_Y + block.Block.height + (block.Block.height * y), player_left)
			temp_block_right = create_block(LEVEL_MAX_X - (block.Block.width * 4) - (block.Block.width * x), LEVEL_Y + block.Block.height + (block.Block.height * y), player_right)
			temp_block_right.image = pygame.transform.flip(temp_block_right.image, True, False)

	# Create and store the paddle.
	left_paddle_x = LEVEL_X + (x_amount * paddle.Paddle.width) + paddle.Paddle.width + (paddle.Paddle.width * 3)
	left_paddle_y = (LEVEL_Y + (LEVEL_MAX_Y- paddle.Paddle.height)) / 2.0
	player_left.paddle_group.add(paddle.Paddle(left_paddle_x, left_paddle_y, player_left))

	right_paddle_x = LEVEL_MAX_X - (x_amount * paddle.Paddle.width) - paddle.Paddle.width - (paddle.Paddle.width * 4)
	right_paddle_y = (LEVEL_Y + (LEVEL_MAX_Y- paddle.Paddle.height)) / 2.0
	paddle_right = paddle.Paddle(right_paddle_x, right_paddle_y, player_right)
	paddle_right.image = pygame.transform.flip(paddle_right.image, True, False)
	player_right.paddle_group.add(paddle_right)

	print("paddle y's: " + str(left_paddle_y) + " " + str(right_paddle_y))

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

def main(window_surface, main_clock, debug_font):
	# Variable to keep the gameloop going. Setting this to True will end the gameloop and return to the screen that started this gameloop.
	done = False

	# Setup the background images.
	floor_surface = pygame.image.load("res/background/planks/planks_floor.png")
	floor_surface = pygame.transform.scale(floor_surface, (floor_surface.get_width() * GAME_SCALE, floor_surface.get_height() * GAME_SCALE)).convert()

	wall_vertical = pygame.image.load("res/background/planks/planks_wall_vertical.png")
	wall_vertical = pygame.transform.scale(wall_vertical, (wall_vertical.get_width() * GAME_SCALE, wall_vertical.get_height() * GAME_SCALE)).convert()
	wall_horizontal = pygame.image.load("res/background/planks/planks_wall_horizontal.png")
	wall_horizontal = pygame.transform.scale(wall_horizontal, (wall_horizontal.get_width() * GAME_SCALE, wall_horizontal.get_height() * GAME_SCALE)).convert()
	corner_top_left = pygame.image.load("res/background/planks/planks_corner_top_left.png")
	corner_top_left = pygame.transform.scale(corner_top_left, (corner_top_left.get_width() * GAME_SCALE, corner_top_left.get_height() * GAME_SCALE)).convert()
	corner_top_right = pygame.image.load("res/background/planks/planks_corner_top_right.png")
	corner_top_right = pygame.transform.scale(corner_top_right, (corner_top_right.get_width() * GAME_SCALE, corner_top_right.get_height() * GAME_SCALE)).convert()

	# Setup the objects.
	block.convert()
	paddle.convert()
	ball.convert()
	multiball.convert()

	# Create the left player.
	player_left = create_player_left()
	
	# Create the right player.
	player_right = create_player_right()

	# Setup the game world.
	setup_gamefield(player_left, player_right)

	while not done:
		# Begin a frame by blitting the background to the game_surface.
		window_surface.fill(BACKGROUND_COLOR)
		window_surface.blit(floor_surface, (LEVEL_X, LEVEL_Y))
		
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				# Return to intromenu.
				groups.empty()
				done = True
			elif event.type == KEYDOWN and event.key == K_l:
				debug.create_ball_left(player_left)
			elif event.type == KEYDOWN and event.key == K_r:
				debug.create_ball_right(player_right)
			elif event.type == KEYDOWN and event.key == K_p:
				debug.create_powerup()
		
		# If debug mode is enabled, allow certain commands. This is all done in the debug module.
		if DEBUG_MODE:
			debug.update(player_left, player_right)

		# Update the balls.
		groups.Groups.ball_group.update()
		
		# Update the particles.
		groups.Groups.particle_group.update()
		
		# Update the players.
		groups.Groups.player_group.update()
		
		# Update the shadows.
		groups.Groups.shadow_group.update(main_clock)

		# Draw the shadows.
		for shadow in groups.Groups.shadow_group:
			shadow.blit_to(window_surface)

		# Draw the blocks.
		groups.Groups.block_group.draw(window_surface)

		# Draw the paddles.
		groups.Groups.paddle_group.draw(window_surface)

		# Draw the powerups.
		groups.Groups.powerup_group.draw(window_surface)

		# Draw the particles.
		for particle in groups.Groups.particle_group:
			window_surface.fill(particle.color, particle.rect)

		# Draw the balls.
		groups.Groups.ball_group.draw(window_surface)

		# Draw the background walls and overlying area.
		window_surface.blit(wall_horizontal, (LEVEL_X, LEVEL_Y - (4 * GAME_SCALE)))
		window_surface.blit(wall_horizontal, (LEVEL_X, LEVEL_MAX_Y))
		window_surface.blit(wall_vertical, (LEVEL_X - (4 * GAME_SCALE), LEVEL_Y))
		window_surface.blit(wall_vertical, (LEVEL_MAX_X, LEVEL_Y))
		window_surface.blit(corner_top_left, (LEVEL_X - (4 * GAME_SCALE), LEVEL_Y - (4 * GAME_SCALE)))
		window_surface.blit(corner_top_left, (LEVEL_MAX_X, LEVEL_MAX_Y))
		window_surface.blit(corner_top_right, (LEVEL_MAX_X, LEVEL_Y - (4 * GAME_SCALE)))
		window_surface.blit(corner_top_right, (LEVEL_X - (4 * GAME_SCALE), LEVEL_MAX_Y))

		# Draw the players.
		# groups.Groups.player_group.draw(window_surface)

		if DEBUG_MODE:
			# Display various debug information.
			debug.display(window_surface, main_clock, debug_font)
		
		pygame.display.update()
		
		# Finally, constrain the game to a set maximum amount of FPS.
		main_clock.tick(MAX_FPS)