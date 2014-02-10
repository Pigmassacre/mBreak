__author__ = "Olof Karlsson"
__license__ = "All Rights Reserved"

import pygame
from pygame.locals import *
import random
import math
import objects.powerups.powerup as powerup
import objects.powerups.multiball as multiball
import objects.powerups.doublespeed as doublespeed
import objects.powerups.fire as fire
import objects.powerups.frost as frost
import objects.powerups.electricity as electricity
import objects.powerups.rocket as rocket
import objects.powerups.enlarger as enlarger
import objects.powerups.reducer as reducer
import objects.ball as ball
import settings.settings as settings

"""

This module contains a few useful methods used when debugging the game. These are by default only called when DEBUG_MODE is True.

It also contains a debug class used to display the FPS counter in the top-left corner of the screen, when DEBUG_MODE is True.

"""

def create_powerup():
	# The P button allows you to spawn a particle at any time you want.
	#powerup_list = [multiball.Multiball, doublespeed.DoubleSpeed, fire.Fire, frost.Frost, electricity.Electricity, rocket.Rocket, enlarger.Enlarger, reducer.Reducer]
	powerup_list = [rocket.Rocket]
	x = random.uniform(settings.LEVEL_X + (settings.LEVEL_WIDTH / 4), settings.LEVEL_X + (3 * (settings.LEVEL_WIDTH / 4)))
	y = random.uniform(settings.LEVEL_Y, settings.LEVEL_MAX_Y - powerup.Powerup.height)
	return random.choice(powerup_list)(x, y)

def create_ball_left(player_left):
	# The L button spawns a ball for the left player.
	for paddle in player_left.paddle_group:
		angle = random.uniform((3 * math.pi) / 2, (5* math.pi) / 2)
		temp_ball = ball.Ball(paddle.x + (paddle.width * 2), paddle.y + (paddle.height / 2), angle, player_left)

def create_ball_right(player_right):
	# The R button spawns a ball for the right player.
	for paddle in player_right.paddle_group:
		angle = random.uniform(math.pi / 2, (3 * math.pi) / 2)
		temp_ball = ball.Ball(paddle.x - (paddle.width), paddle.y + (paddle.height / 2), angle, player_right)

def update(player_left, player_right, main_clock):
	# When hold, the space button spawns balls every frame.
	if pygame.key.get_pressed()[K_SPACE]:
		create_ball_left(player_left)
		create_ball_right(player_right)

	if pygame.key.get_pressed()[K_p]:
		create_powerup()

def change_time_scale(main_clock):
	main_clock.default_time_scale = random.uniform(0, 2)

class Debug:

	# Initialize the font module.
	pygame.font.init()

	# Default variables go here.
	font_size = 9 * settings.GAME_SCALE
	font = pygame.font.Font(settings.DEBUG_FONT, font_size)
	font_color = (255, 255, 255)
	x = font_size
	y = font_size

	@staticmethod
	def display(surface, main_clock):
		# Display the current FPS.
		surface.blit(Debug.font.render(str(int(main_clock.get_fps())), False, Debug.font_color), (Debug.x, Debug.y))
