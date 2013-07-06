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
from settings import *

def create_ball(owner):
	width = 16
	height = 16
	x = random.uniform(0, SCREEN_WIDTH)
	y = random.uniform(0, SCREEN_HEIGHT)
	speed = random.uniform(3, 8)
	max_speed = 8
	angle = random.uniform(0, 2*math.pi)
	damage = 1
	image_path = ("res/ball/ball.png")
	color = pygame.Color(255, 0, 0, 255)

	return ball.Ball(x, y, width, height, angle, speed, max_speed, damage, image_path, color, owner)

def create_powerup():
	width = 16
	height = 16
	x = random.uniform(0, SCREEN_WIDTH)
	y = random.uniform(0, SCREEN_HEIGHT)
	image_path = ("res/ball/ball.png")

	return multiball.Multiball(x, y, width, height)

def create_block(x, y, owner):
	width = 16
	height = 32
	health = 2
	image_path = ("res/block/block.png")

	return block.Block(x, y, width, height, health, image_path, owner)

def create_paddle(x, y):
	width = 16
	height = 64
	acceleration = 2
	retardation = 4
	max_speed = 8
	image_path = ("res/paddle/paddle.png")

	return paddle.Paddle(x, y, width, height, acceleration, retardation, max_speed, image_path)

def create_player_left(paddle):
	name = PLAYER_LEFT_NAME
	key_up = PLAYER_LEFT_KEY_UP
	key_down = PLAYER_LEFT_KEY_DOWN

	player_left = player.Player(name, key_up, key_down)

	player_left.add_paddle(paddle)

	return player_left

def create_player_right(paddle):
	name = PLAYER_RIGHT_NAME
	key_up = PLAYER_RIGHT_KEY_UP
	key_down = PLAYER_RIGHT_KEY_DOWN

	player_right = player.Player(name, key_up, key_down)
	
	player_right.add_paddle(paddle)

	return player_right

def main(window_surface, main_clock, debug_font):
	# Variable to keep the gameloop going. Setting this to True will end the gameloop and return to the screen that started this gameloop.
	done = False

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

	# Create the players.
	paddle_left = create_paddle(16 * 5, (SCREEN_HEIGHT - 64) / 2)
	paddle_group.add(paddle_left)
	player_left = create_player_left(paddle_left)
	player_group.add(player_left)

	paddle_right = create_paddle(SCREEN_WIDTH - 16 * 6, (SCREEN_HEIGHT - 64) / 2)
	paddle_group.add(paddle_right)
	player_right = create_player_right(paddle_right)
	player_group.add(player_right)

	# Spawn some blocks.
	for i in range(0, 3):
		for j in range(0, 13):
			block_group.add(create_block(32 + (16 * i), 32 + (32 * j), player_left))
			block_group.add(create_block((SCREEN_WIDTH - 48) - (16 * i), 32 + (32 * j), player_right))

	while not done:
		# Every frame begins by filling the whole screen with the background color.
		window_surface.fill(BACKGROUND_COLOR)
		
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				# Return to intromenu.
				done = True
			elif event.type == KEYDOWN and event.key == K_RETURN:
				if random.randint(0, 1) == 0:
					temp_ball = create_ball(player_left)
					player_left.add_ball(temp_ball)
					temp_ball.owner = player_left
					if DEBUG_MODE:
						print("Ball added to Player Left.")
				else:
					temp_ball = create_ball(player_right)
					player_right.add_ball(temp_ball)
					temp_ball.owner = player_right
					if DEBUG_MODE:
						print("Ball added to Player Right.")
				ball_group.add(temp_ball)
			elif event.type == KEYDOWN and event.key == K_p:
				powerup_group.add(create_powerup())

		if pygame.key.get_pressed()[K_SPACE]:
			if random.randint(0, 1) == 0:
				temp_ball = create_ball(player_left)
				player_left.add_ball(temp_ball)
				temp_ball.owner = player_left
				if DEBUG_MODE:
					print("Ball added to Player Left.")
			else:
				temp_ball = create_ball(player_right)
				player_right.add_ball(temp_ball)
				temp_ball.owner = player_right
				if DEBUG_MODE:
					print("Ball added to Player Right.")
			ball_group.add(temp_ball)

		# Update the balls.
		ball_group.update(ball_group, paddle_group, block_group, particle_group)

		# Update the particles.
		particle_group.update()

		# Update the players.
		player_group.update()

		# Draw the particles.
		for particle in particle_group:
			window_surface.fill(particle.color, particle.rect)

		# Draw the balls.
		ball_group.draw(window_surface)

		# Draw the powerups.
		powerup_group.draw(window_surface)

		# Draw the blocks.
		block_group.draw(window_surface)

		# Draw the paddles.
		paddle_group.draw(window_surface)

		# Draw the players.
		# player_group.draw(window_surface)

		if DEBUG_MODE:
			# Display various debug information.
			debug.display(window_surface, main_clock, debug_font)
		
		pygame.display.update()
		
		# Finally, constrain the game to a set maximum amount of FPS.
		main_clock.tick(MAX_FPS)