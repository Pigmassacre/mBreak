__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import multiball
import random
import math
import ball
from settings import *

def display(window_surface, main_clock, debug_font):
	# Display the current FPS.
	window_surface.blit(debug_font.render(str(int(main_clock.get_fps())), False, (255, 255, 255)), (25, 25))

def create_ball(x, y, owner):
	speed = random.uniform(1, 3) * GAME_SCALE
	angle = random.uniform(0, 2*math.pi)
	damage = 1

	return ball.Ball(x, y, angle, speed, damage, owner)

def create_powerup():
	x = random.uniform(LEVEL_X + (LEVEL_WIDTH / 2) - 20, LEVEL_X + (LEVEL_WIDTH / 2) + 20)
	y = random.uniform(LEVEL_Y + (LEVEL_HEIGHT / 2) - 20, LEVEL_Y + (LEVEL_HEIGHT / 2) + 20)

	return multiball.Multiball(x, y)

def create_ball_left(player_left, paddle_left):
	temp_ball = create_ball(paddle_left.x + 8, paddle_left.y, player_left)
	temp_ball.owner = player_left

def create_ball_right(player_right, paddle_right):
	temp_ball = create_ball(paddle_right.x - 16, paddle_right.y, player_right)
	temp_ball.owner = player_right

def update(player_left, player_right, paddle_left, paddle_right):
	if pygame.key.get_pressed()[K_SPACE]:
		temp_ball = create_ball(paddle_left.x + 8, paddle_left.y, player_left)
		temp_ball.owner = player_left

		temp_ball = create_ball(paddle_right.x - 16, paddle_right.y, player_right)
		temp_ball.owner = player_right
