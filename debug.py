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

def create_ball_left(player_left, paddle_left):
	temp_ball = create_ball(paddle_left.x + 16, paddle_left.y, player_left)
	temp_ball.owner = player_left
	print("Ball added to Player Left.")

def create_ball_right(player_right, paddle_right):
	temp_ball = create_ball(paddle_right.x - 32, paddle_right.y, player_right)
	temp_ball.owner = player_right
	print("Ball added to Player Right.")

def update(player_left, player_right, paddle_left, paddle_right):
	if pygame.key.get_pressed()[K_SPACE]:
			temp_ball = create_ball(paddle_left.x + 16, paddle_left.y, player_left)
			temp_ball.owner = player_left
			print("Ball added to Player Left.")
			temp_ball = create_ball(paddle_right.x - 32, paddle_right.y, player_right)
			temp_ball.owner = player_right
			print("Ball added to Player Right.")
