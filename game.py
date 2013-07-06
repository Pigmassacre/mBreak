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

def create_ball(x, y, owner):
	width = 16
	height = 16
	speed = random.uniform(3, 8)
	max_speed = 8
	angle = random.uniform(0, 2*math.pi)
	damage = 1
	image_path = ("res/ball/ball.png")

	return ball.Ball(x, y, width, height, angle, speed, max_speed, damage, image_path, owner)

def create_powerup():
	width = 32
	height = 32
	x = random.uniform((SCREEN_WIDTH / 2) - 200, (SCREEN_WIDTH / 2) + 200)
	y = random.uniform((SCREEN_HEIGHT / 2) - 200, (SCREEN_HEIGHT / 2) + 200)
	color = pygame.Color(255, 128, 255, 255)

	return multiball.Multiball(x, y, width, height, color)

def create_block(x, y, owner):
	width = 16
	height = 32
	health = 2
	image_path = ("res/block/block.png")

	return block.Block(x, y, width, height, health, image_path, owner)

def create_paddle(x, y, owner):
	width = 16
	height = 64
	acceleration = 2
	retardation = 4
	max_speed = 8
	image_path = ("res/paddle/paddle.png")

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

def main(window_surface, main_clock, debug_font):
	# Variable to keep the gameloop going. Setting this to True will end the gameloop and return to the screen that started this gameloop.
	done = False

	# Create the left player.
	# Create and store the player.
	player_left = create_player_left()
	groupholder.player_group.add(player_left)

	# Create and store the players paddle.
	paddle_left = create_paddle(16 * 6, (SCREEN_HEIGHT - 64) / 2, player_left)
	groupholder.paddle_group.add(paddle_left)
	
	# Create the right player.
	# Create and store the player.
	player_right = create_player_right()
	groupholder.player_group.add(player_right)

	# Create and store the players paddle.
	paddle_right = create_paddle(SCREEN_WIDTH - 16 * 7, (SCREEN_HEIGHT - 64) / 2, player_right)
	groupholder.paddle_group.add(paddle_right)

	# Alternate adding stuff to left och right player. When True, add to left, otherwise add to right.
	order = True

	# Spawn some blocks.
	for i in range(0, 3):
		for j in range(0, 13):
			groupholder.block_group.add(create_block(32 + (16 * i), 32 + (32 * j), player_left))
			groupholder.block_group.add(create_block((SCREEN_WIDTH - 48) - (16 * i), 32 + (32 * j), player_right))

	while not done:
		# Every frame begins by filling the whole screen with the background color.
		window_surface.fill(BACKGROUND_COLOR)
		
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				# Return to intromenu.
				destroy_groups()
				done = True
			elif event.type == KEYDOWN and event.key == K_l:
				temp_ball = create_ball(paddle_left.x + 16, paddle_left.y, player_left)
				temp_ball.owner = player_left
				groupholder.ball_group.add(temp_ball)
				if DEBUG_MODE:
					print("Ball added to Player Left.")
			elif event.type == KEYDOWN and event.key == K_r:
				temp_ball = create_ball(paddle_right.x - 32, paddle_right.y, player_right)
				temp_ball.owner = player_right
				groupholder.ball_group.add(temp_ball)
				if DEBUG_MODE:
					print("Ball added to Player Right.")
			elif event.type == KEYDOWN and event.key == K_p:
				groupholder.powerup_group.add(create_powerup())

		if pygame.key.get_pressed()[K_SPACE]:
			if order:
				temp_ball = create_ball(paddle_left.x + 16, paddle_left.y, player_left)
				temp_ball.owner = player_left
				order = not order
				if DEBUG_MODE:
					print("Ball added to Player Left.")
			else:
				temp_ball = create_ball(paddle_right.x - 32, paddle_right.y, player_right)
				temp_ball.owner = player_right
				order = not order
				if DEBUG_MODE:
					print("Ball added to Player Right.")
			groupholder.ball_group.add(temp_ball)

		# Update the balls.
		groupholder.ball_group.update()

		# Update the particles.
		groupholder.particle_group.update()

		# Update the players.
		groupholder.player_group.update()

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