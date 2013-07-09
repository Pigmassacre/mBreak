__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
import random
import math
import objects.multiball as multiball
import objects.ball as ball
from settings.settings import *

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


def create_ball_left(player_left):
	for paddle in player_left.paddle_group:
		temp_ball = create_ball(paddle.x + 8, paddle.y, player_left)
		temp_ball.owner = player_left

def create_ball_right(player_right):
	for paddle in player_right.paddle_group:
		temp_ball = create_ball(paddle.x - 16, paddle.y, player_right)
		temp_ball.owner = player_right

def update(player_left, player_right):
	if pygame.key.get_pressed()[K_SPACE]:
		create_ball_left(player_left)
		create_ball_left(player_right,)
