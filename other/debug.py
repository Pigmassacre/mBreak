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

def create_ball(x, y, angle, owner):
	speed = 2.75 * GAME_SCALE
	damage = 1

	return ball.Ball(x, y, angle, speed, damage, owner)

def create_powerup():
	x = random.uniform(LEVEL_X + (LEVEL_WIDTH / 2) - 20, LEVEL_X + (LEVEL_WIDTH / 2) + 20)
	y = random.uniform(LEVEL_Y + (LEVEL_HEIGHT / 2) - 20, LEVEL_Y + (LEVEL_HEIGHT / 2) + 20)
	return multiball.Multiball(x, y)

def create_ball_left(player_left):
	for paddle in player_left.paddle_group:
		angle = random.uniform((3 * math.pi) / 2, (5* math.pi) / 2)
		print("left angle: " + str(angle))
		temp_ball = create_ball(paddle.x + (paddle.width * 2), paddle.y + (paddle.height / 2), angle, player_left)
		temp_ball.owner = player_left

def create_ball_right(player_right):
	for paddle in player_right.paddle_group:
		angle = random.uniform(math.pi / 2, (3 * math.pi) / 2)
		print("right angle: " + str(angle))
		temp_ball = create_ball(paddle.x - (paddle.width), paddle.y + (paddle.height / 2), angle, player_right)
		temp_ball.owner = player_right

def update(player_left, player_right):
	if pygame.key.get_pressed()[K_SPACE]:
		create_ball_left(player_left)
		create_ball_right(player_right)
