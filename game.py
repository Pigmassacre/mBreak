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
from settings import *

def create_ball():
	width = 16
	height = 16
	x = random.uniform(SCREEN_WIDTH / 2 - 100, SCREEN_WIDTH / 2 + 100)
	y = random.uniform(SCREEN_HEIGHT / 2 - 100, SCREEN_HEIGHT / 2 + 100)
	speed = random.randint(4, 8)
	angle = random.uniform(0, 2*math.pi)
	image_path = ("res/ball/ball.png")

	return ball.Ball(x, y, width, height, angle, speed, image_path)

def create_paddle():
	width = 16
	height = 64
	x = 100
	y = (SCREEN_HEIGHT - height) / 2
	image_path = ("res/paddle/paddle.png")

	return paddle.Paddle(x, y, width, height, image_path)

def main(window_surface, main_clock, debug_font):
	# Define the group that contains all the balls.
	ball_group = pygame.sprite.Group()

	# Define the group that contains all the paddles.
	paddle_group = pygame.sprite.Group()

	# Spawn a paddle and add it to paddle_group.
	#paddle_group.add(create_paddle())

	while True:
		# Every frame begins by filling the whole screen with the background color.
		window_surface.fill(BACKGROUND_COLOR)
		
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
				# If the ESCAPE key is pressed or the window is closed, the game is shut down.
				pygame.quit()
				sys.exit()
			elif event.type == KEYDOWN and event.key == K_RETURN:
				ball_group.add(create_ball())

		if pygame.key.get_pressed()[K_SPACE]:
			ball_group.add(create_ball())

		# Update the balls.
		ball_group.update(ball_group, paddle_group)

		# Draw the balls.
		ball_group.draw(window_surface)

		# Draw the paddles.
		paddle_group.draw(window_surface)

		if DEBUG_MODE:
			# Display various debug information.
			debug.display(window_surface, main_clock, debug_font)
		
		pygame.display.update()
		
		# Finally, constrain the game to a set maximum amount of FPS.
		main_clock.tick(MAX_FPS)