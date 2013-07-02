__author__ = "Olof Karlsson"
__version__ = "0.1"
__license__ = "All Rights Reserved"

import pygame, sys
from pygame.locals import *
import random
import debug
import ball
from settings import *

def create_ball():
	x = random.uniform(SCREEN_WIDTH / 2 - 100, SCREEN_WIDTH / 2 + 100)
	y = random.uniform(SCREEN_HEIGHT / 2 - 100, SCREEN_HEIGHT / 2 + 100)
	width = 16
	height = 16
	speed = 5
	velocity_x = random.uniform(-1, 1)
	velocity_y = random.uniform(-1, 1)
	image_path = ("res/ball/ball.png")

	return ball.Ball(x, y, width, height, velocity_x, velocity_y, speed, image_path)

def main(window_surface, main_clock, debug_font):
	# Define the group that contains all the balls!
	ball_group = pygame.sprite.Group()

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

		# Update the balls!
		ball_group.update(ball_group)

		# Draw the balls!
		ball_group.draw(window_surface)

		if DEBUG_MODE:
			# Display various debug information.
			debug.display(window_surface, main_clock, debug_font)
		
		pygame.display.update()
		
		# Finally, constrain the game to a set maximum amount of FPS.
		main_clock.tick(MAX_FPS)