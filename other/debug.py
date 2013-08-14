__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *
import random
import math
import objects.powerup as powerup
import objects.multiball as multiball
import objects.doublespeed as doublespeed
import objects.fire as fire
import objects.frost as frost
import objects.ball as ball
import settings.settings as settings

def create_powerup():
	powerup_list = [multiball.Multiball, doublespeed.DoubleSpeed, fire.Fire, frost.Frost]
	x = random.uniform(settings.LEVEL_X + (settings.LEVEL_WIDTH / 4), settings.LEVEL_X + (3 * (settings.LEVEL_WIDTH / 4)))
	y = random.uniform(settings.LEVEL_Y, settings.LEVEL_MAX_Y - powerup.Powerup.height)
	return random.choice(powerup_list)(x, y)

def create_ball_left(player_left):
	for paddle in player_left.paddle_group:
		angle = random.uniform((3 * math.pi) / 2, (5* math.pi) / 2)
		temp_ball = ball.Ball(paddle.x + (paddle.width * 2), paddle.y + (paddle.height / 2), angle, player_left)

def create_ball_right(player_right):
	for paddle in player_right.paddle_group:
		angle = random.uniform(math.pi / 2, (3 * math.pi) / 2)
		temp_ball = ball.Ball(paddle.x - (paddle.width), paddle.y + (paddle.height / 2), angle, player_right)

def update(player_left, player_right):
	if pygame.key.get_pressed()[K_SPACE]:
		create_ball_left(player_left)
		create_ball_right(player_right)

class Debug:

	# Initialize the font module.
	pygame.font.init()

	# Default variables go here.
	font_path = "fonts/8-BIT WONDER.TTF"
	font_size = 9 * settings.GAME_SCALE
	font = pygame.font.Font(font_path, font_size)
	font_color = (255, 255, 255)
	x = 25
	y = 25

	@staticmethod
	def display(surface, main_clock):
		# Display the current FPS.
		surface.blit(Debug.font.render(str(int(main_clock.get_fps())), False, Debug.font_color), (Debug.x, Debug.y))
